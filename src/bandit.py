# src/bandit.py
import numpy as np

class ContextualBandit:
    def __init__(self, waveforms):
        self.waveforms = list(waveforms)
        self.counts = {w: 0 for w in self.waveforms}
        self.values = {w: 0.0 for w in self.waveforms}

    def score(self, waveform, snr, reverberation, doppler):
        return (
            self.values[waveform]
            + 0.03 * snr
            - 0.15 * reverberation
            - 0.03 * abs(doppler)
        )

    def select(self, snr, reverberation, doppler):
        unexplored = [w for w in self.waveforms if self.counts[w] == 0]
        if unexplored:
            return unexplored[0]

        scores = {w: self.score(w, snr, reverberation, doppler) for w in self.waveforms}
        return max(scores, key=scores.get)

    def compute_multi_objective_reward(self, detected, range_error_m, power_w, temp_c, w_det=10.0, w_err=0.5, w_pwr=0.8, w_temp=0.1):
        """Calculates multi-objective Pareto reward."""
        r_det = w_det if detected else -5.0
        r_err = -w_err * range_error_m if detected else 0.0
        r_pwr = -w_pwr * power_w
        r_temp = -w_temp * max(0.0, temp_c - 50.0)

        return r_det + r_err + r_pwr + r_temp

    def update(self, waveform, reward):
        self.counts[waveform] += 1
        n = self.counts[waveform]
        old = self.values[waveform]
        self.values[waveform] = old + (reward - old) / n