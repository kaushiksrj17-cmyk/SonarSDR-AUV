# src/channel.py
import numpy as np
from .config import CONFIG
from .target import Target

class UnderwaterChannel:
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(
            seed if seed is not None else CONFIG.random_seed
        )

    def absorption_coefficient_db_per_km(self, freq_hz, temp_c=15.0, salinity_ppt=35.0, depth_m=10.0, ph=8.0):
        """Ainslie & McColm ocean sound absorption formula (dB/km)."""
        f_khz = freq_hz / 1000.0
        depth_km = depth_m / 1000.0

        # Boric acid relaxation frequency
        f1 = 0.78 * np.sqrt(salinity_ppt / 35.0) * np.exp(temp_c / 26.0)
        # Magnesium sulphate relaxation frequency
        f2 = 42.0 * np.exp(temp_c / 17.0)

        # Absorption components
        boric = 0.106 * (f1 * f_khz**2 / (f_khz**2 + f1**2)) * np.exp((ph - 8.0) / 0.56)
        mgso4 = 0.52 * (1.0 + temp_c / 43.0) * (salinity_ppt / 35.0) * (f2 * f_khz**2 / (f_khz**2 + f2**2)) * np.exp(-depth_km / 6.0)
        viscous = 0.00049 * f_khz**2 * np.exp(-(temp_c / 27.0 + depth_km / 17.0))

        return boric + mgso4 + viscous

    def _fractional_delay(self, signal, delay_samples):
        integer_delay = int(np.floor(delay_samples))
        fraction = delay_samples - integer_delay

        if integer_delay >= len(signal):
            return np.zeros_like(signal)

        shifted = np.zeros_like(signal)
        shifted[integer_delay:] = signal[:len(signal) - integer_delay]

        if fraction == 0:
            return shifted

        previous = np.zeros_like(signal)
        previous[1:] = shifted[:-1]
        return (1.0 - fraction) * shifted + fraction * previous

    def propagate(self, transmitted, target: Target, snr_db=10.0, reverberation=0.2, multipath=0.1, center_freq_hz=60000.0, temp_c=15.0):
        signal = np.asarray(transmitted, dtype=np.float64)

        # Physical absorption loss
        alpha_db_km = self.absorption_coefficient_db_per_km(center_freq_hz, temp_c=temp_c)
        dist_km = (2.0 * target.range_m) / 1000.0
        absorption_loss_db = alpha_db_km * dist_km
        absorption_linear = 10.0 ** (-absorption_loss_db / 20.0)

        # Spreading loss + absorption
        spherical_spreading = target.amplitude / max(target.range_m, 1.0)
        attenuation = spherical_spreading * absorption_linear

        delay_seconds = target.propagation_delay(CONFIG.sound_speed)
        delay_samples = delay_seconds * CONFIG.sample_rate

        # Doppler phase shift & time shift
        doppler_hz = target.doppler_shift(center_freq_hz, CONFIG.sound_speed)
        t = np.arange(len(signal)) / CONFIG.sample_rate
        doppler_carrier = np.cos(2.0 * np.pi * doppler_hz * t)

        echo = self._fractional_delay(signal * doppler_carrier, delay_samples)
        result = attenuation * echo

        # Multipath
        if multipath > 0:
            multipath_delay = delay_samples + (0.001 * CONFIG.sample_rate)
            reflected = self._fractional_delay(signal * doppler_carrier, multipath_delay)
            result += multipath * attenuation * reflected

        # Reverberation & AWGN
        reverb = self.rng.normal(0, reverberation * 0.05, len(signal))
        result += reverb

        signal_power = np.mean(result ** 2) + 1e-12
        noise_power = signal_power / (10 ** (snr_db / 10.0))
        noise = self.rng.normal(0, np.sqrt(noise_power), len(signal))

        return result + noise