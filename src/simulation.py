import time
import numpy as np

from .config import CONFIG
from .target import Target
from .channel import UnderwaterChannel
from .waveforms import generate_waveform
from .dsp import matched_filter, envelope, peak_to_range
from .detector import cfar_detect
from .bandit import ContextualBandit
from .controller import AdaptiveController
from .power import PowerManager, PowerTelemetryMonitor
from .safety import SafetySupervisor
from .tracker import AlphaBetaTracker
from .telemetry import TelemetryFrame, TelemetryLogger

SCENARIOS = [
    {
        "name": "OPEN_WATER",
        "description": "Deep water, low clutter, high SNR",
        "snr": 16.0,
        "reverberation": 0.10,
        "doppler": 0.5,
        "multipath": 0.05,
        "target_range_m": 120.0,
        "target_velocity_mps": -1.0,
        "temperature_c": 22.0,
    },
    {
        "name": "SHALLOW_WATER",
        "description": "High seabed reverberation & multipath",
        "snr": 8.0,
        "reverberation": 0.75,
        "doppler": 1.5,
        "multipath": 0.35,
        "target_range_m": 85.0,
        "target_velocity_mps": -0.5,
        "temperature_c": 25.0,
    },
    {
        "name": "FAST_TARGET",
        "description": "Rapid target approaching, high Doppler shift",
        "snr": 12.0,
        "reverberation": 0.25,
        "doppler": 6.0,
        "multipath": 0.15,
        "target_range_m": 150.0,
        "target_velocity_mps": -4.0,
        "temperature_c": 23.0,
    },
    {
        "name": "LOW_SNR_DEEP",
        "description": "Weak echo buried in ambient noise",
        "snr": 3.0,
        "reverberation": 0.50,
        "doppler": 2.0,
        "multipath": 0.25,
        "target_range_m": 130.0,
        "target_velocity_mps": 1.5,
        "temperature_c": 18.0,
    }
]

class SonarSimulationEngine:
    """Executes full end-to-end ping loop measuring exact pipeline latency."""

    def __init__(self, seed=CONFIG.random_seed):
        self.channel = UnderwaterChannel(seed=seed)
        self.bandit = ContextualBandit(waveforms=["LFM", "HFM", "BARKER", "GOLAY", "CW"])
        self.controller = AdaptiveController(self.bandit)
        self.power_mgr = PowerManager()
        self.safety = SafetySupervisor()
        self.tracker = AlphaBetaTracker()
        self.logger = TelemetryLogger()

    def run_ping(self, scenario: dict, override_waveform=None):
        pipeline_start = time.perf_counter()

        snr = scenario["snr"]
        reverb = scenario["reverberation"]
        doppler = scenario["doppler"]
        multipath = scenario["multipath"]
        temp_c = scenario.get("temperature_c", 25.0)

        # 1. AI / Controller Decision
        if override_waveform is None:
            waveform, reason, dec_lat_ms = self.controller.decide(snr, reverb, doppler)
        else:
            waveform = override_waveform
            reason = f"Fixed override ({waveform})"
            dec_lat_ms = 0.05

        # 2. Power Management & Safety Validation
        power_state = self.power_mgr.select(waveform, snr)
        is_safe, safety_msg = self.safety.check(
            power_state.average_power_w,
            temp_c,
            dec_lat_ms
        )

        if not is_safe:
            waveform = "CW"
            power_state = self.power_mgr.select("CW", snr)
            reason = f"Failsafe triggered: {safety_msg}"

        # 3. Waveform Synthesis
        t_tx, tx_signal = generate_waveform(waveform)

        # 4. Target & Channel Propagation
        target = Target(
            range_m=scenario["target_range_m"],
            radial_velocity_mps=scenario["target_velocity_mps"]
        )

        rx_signal = self.channel.propagate(
            tx_signal,
            target=target,
            snr_db=snr,
            reverberation=reverb,
            multipath=multipath
        )

        # 5. DSP: Matched Filter & CFAR Detection
        corr = matched_filter(rx_signal, tx_signal)
        env = envelope(corr)

        detection = cfar_detect(
            env,
            guard_cells=CONFIG.cfar_guard_cells,
            training_cells=CONFIG.cfar_training_cells,
            scale=CONFIG.cfar_scale
        )

        target_detected = False
        est_range = 0.0
        range_err = 0.0

        if detection is not None:
            target_detected = True
            raw_range = peak_to_range(
                detection["index"],
                len(tx_signal),
                CONFIG.sample_rate,
                CONFIG.sound_speed
            )
            # Update tracker state with raw measurement
            est_range, _ = self.tracker.update(raw_range)
            range_err = abs(est_range - target.range_m)
            reward = max(0.0, 10.0 - (range_err * 0.5))
        else:
            reward = -2.0

        # Update Bandit weights if running adaptively
        if override_waveform is None:
            self.bandit.update(waveform, reward)

        total_lat_ms = (time.perf_counter() - pipeline_start) * 1000.0

        # 6. Range-Doppler Matrix Construction
        n_doppler_bins = 64
        rd_ranges = np.linspace(0, CONFIG.max_range_m, len(env))
        rd_dopplers = np.linspace(-CONFIG.max_doppler_hz, CONFIG.max_doppler_hz, n_doppler_bins)

        rd_map = np.outer(np.exp(-np.linspace(0, 2, n_doppler_bins)), env)
        if target_detected and detection is not None:
            peak_idx = min(detection["index"], len(env) - 1)
            rd_map[n_doppler_bins // 2, peak_idx] *= 3.0

        # 7. Log Telemetry Frame
        frame = TelemetryFrame(
            timestamp=time.time(),
            scenario_name=scenario["name"],
            snr_db=snr,
            reverberation=reverb,
            doppler_hz=doppler,
            multipath=multipath,
            selected_waveform=waveform,
            decision_reason=reason,
            power_mode=power_state.mode,
            instantaneous_power_w=power_state.instantaneous_power_w,
            average_power_w=power_state.average_power_w,
            target_detected=target_detected,
            true_range_m=target.range_m,
            estimated_range_m=est_range,
            range_error_m=range_err if target_detected else 0.0,
            decision_latency_ms=dec_lat_ms,
            total_pipeline_latency_ms=total_lat_ms,
            safety_status=safety_msg
        )

        self.logger.log(frame)

        return frame, t_tx, tx_signal, rx_signal, env, rd_map, rd_ranges, rd_dopplers