from dataclasses import dataclass

@dataclass
class PowerState:
    """Dataclass holding power metrics returned during a simulation ping."""
    mode: str
    instantaneous_power_w: float
    average_power_w: float

class PowerTelemetryMonitor:
    """Monitors telemetry calculations for base and power amplifier (PA) draw."""
    def __init__(self, base_power_mw=180.0, max_pa_mw=1200.0):
        self.base_power_mw = base_power_mw
        self.max_pa_mw = max_pa_mw

    def calculate_telemetry(self, power_scale: float) -> dict:
        pa_power_mw = self.max_pa_mw * (power_scale ** 2)
        total_power_mw = self.base_power_mw + pa_power_mw
        duty_extension_pct = (1.0 - power_scale) * 100.0
        
        return {
            "base_mw": self.base_power_mw,
            "pa_mw": pa_power_mw,
            "total_mw": total_power_mw,
            "duty_extension_pct": duty_extension_pct
        }

class PowerManager:
    """Manages power mode selection and calculates power consumption per ping."""
    def __init__(self, base_power_w=0.180, max_pa_w=1.200):
        self.base_power_w = base_power_w
        self.max_pa_w = max_pa_w
        self.telemetry_monitor = PowerTelemetryMonitor(
            base_power_mw=base_power_w * 1000.0,
            max_pa_mw=max_pa_w * 1000.0
        )

    def select(self, waveform: str, snr_db: float) -> PowerState:
        """Selects power mode based on SNR and computes active power consumption."""
        if snr_db > 12.0:
            mode = "ECO"
            power_scale = 0.5
        elif snr_db < 6.0:
            mode = "BOOST"
            power_scale = 1.0
        else:
            mode = "BALANCED"
            power_scale = 0.75

        telemetry = self.telemetry_monitor.calculate_telemetry(power_scale)
        inst_power_w = telemetry["total_mw"] / 1000.0
        
        # Duty cycle adjustment based on waveform characteristics
        duty_factor = 0.8 if waveform == "CW" else 0.3
        avg_power_w = self.base_power_w + ((inst_power_w - self.base_power_w) * duty_factor)

        return PowerState(
            mode=mode,
            instantaneous_power_w=inst_power_w,
            average_power_w=avg_power_w
        )