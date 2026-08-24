import numpy as np
from scipy.signal import chirp

from .config import CONFIG


def time_vector(duration):
    return np.arange(
        0.0,
        duration,
        1.0 / CONFIG.sample_rate
    )


def normalize(signal):
    signal = np.asarray(signal, dtype=np.float64)

    peak = np.max(np.abs(signal))

    if peak == 0:
        return signal

    return signal / peak


def lfm(
    f0=30_000,
    f1=100_000,
    duration=0.008
):
    t = time_vector(duration)

    signal = chirp(
        t,
        f0=f0,
        f1=f1,
        t1=duration,
        method="linear"
    )

    return t, normalize(signal)


def hfm(
    f0=30_000,
    f1=100_000,
    duration=0.008
):
    t = time_vector(duration)

    signal = chirp(
        t,
        f0=f0,
        f1=f1,
        t1=duration,
        method="hyperbolic"
    )

    return t, normalize(signal)


def barker13(
    chip_duration=0.00025
):
    code = np.array([
        1, 1, 1, 1, 1,
        -1, -1,
        1, 1,
        -1,
        1,
        -1,
        1
    ])

    samples_per_chip = max(
        1,
        int(chip_duration * CONFIG.sample_rate)
    )

    signal = np.repeat(
        code,
        samples_per_chip
    )

    t = np.arange(len(signal)) / CONFIG.sample_rate

    return t, normalize(signal)


def golay():
    a = np.array([
        1, 1, 1, -1,
        1, 1, -1, 1
    ])

    b = np.array([
        1, 1, -1, 1,
        1, -1, -1, -1
    ])

    signal = np.concatenate([a, b])

    samples_per_chip = int(
        0.00025 * CONFIG.sample_rate
    )

    signal = np.repeat(
        signal,
        samples_per_chip
    )

    t = np.arange(len(signal)) / CONFIG.sample_rate

    return t, normalize(signal)


def cw(
    frequency=75_000,
    duration=0.002
):
    t = time_vector(duration)

    signal = np.sin(
        2 * np.pi * frequency * t
    )

    return t, normalize(signal)


WAVEFORM_GENERATORS = {
    "LFM": lfm,
    "HFM": hfm,
    "BARKER": barker13,
    "GOLAY": golay,
    "CW": cw,
}


def generate_waveform(name):
    name = name.upper()

    if name not in WAVEFORM_GENERATORS:
        raise ValueError(
            f"Unsupported waveform: {name}"
        )

    return WAVEFORM_GENERATORS[name]()