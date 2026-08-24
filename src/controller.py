import time


class AdaptiveController:

    def __init__(
        self,
        bandit
    ):

        self.bandit = bandit

    def decide(
        self,
        snr,
        reverberation,
        doppler
    ):

        start = time.perf_counter()

        # Deterministic safety/robustness rules.

        if reverberation > 0.70:

            waveform = "BARKER"
            reason = "High reverberation"

        elif abs(doppler) > 4.0:

            waveform = "HFM"
            reason = "High Doppler"

        elif snr < 6.0:

            waveform = "LFM"
            reason = "Low SNR"

        else:

            waveform = self.bandit.select(
                snr,
                reverberation,
                doppler
            )

            reason = (
                "Contextual bandit optimization"
            )

        latency_ms = (
            time.perf_counter()
            - start
        ) * 1000

        return (
            waveform,
            reason,
            latency_ms
        )