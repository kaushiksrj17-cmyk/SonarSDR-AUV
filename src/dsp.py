# src/dsp.py
import numpy as np
from scipy.signal import correlate
from .config import CONFIG

try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

def matched_filter(received, transmitted):
    reference = np.asarray(transmitted, dtype=np.float64)
    signal = np.asarray(received, dtype=np.float64)
    reference = reference - np.mean(reference)

    return correlate(signal, reference, mode="full", method="fft")

def envelope(signal):
    return np.abs(signal)

def peak_to_range(peak_index, reference_length, sample_rate, sound_speed):
    lag = peak_index - reference_length + 1
    delay = lag / sample_rate
    if delay <= 0:
        return 0.0
    return sound_speed * delay / 2.0

def compute_range_doppler_map(rx_signal, tx_signal, doppler_bins=31, max_doppler_hz=10.0):
    """Constructs a 2D Range-Doppler Ambiguity Matrix."""
    doppler_freqs = np.linspace(-max_doppler_hz, max_doppler_hz, doppler_bins)
    t = np.arange(len(rx_signal)) / CONFIG.sample_rate

    rd_map = np.zeros((doppler_bins, len(rx_signal) + len(tx_signal) - 1))

    for i, fd in enumerate(doppler_freqs):
        demodulated_rx = rx_signal * np.exp(-1j * 2.0 * np.pi * fd * t)
        corr = matched_filter(np.real(demodulated_rx), tx_signal)
        rd_map[i, :] = np.abs(corr)

    ranges = (np.arange(rd_map.shape[1]) - len(tx_signal) + 1) * CONFIG.sound_speed / (2.0 * CONFIG.sample_rate)
    valid_mask = (ranges >= 0) & (ranges <= 250)

    return rd_map[:, valid_mask], ranges[valid_mask], doppler_freqs