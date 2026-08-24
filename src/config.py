from dataclasses import dataclass

@dataclass(frozen=True)
class SonarConfig:
    # DSP
    sample_rate: int = 500_000

    # Acoustic operating band
    min_frequency: float = 20_000.0
    max_frequency: float = 200_000.0

    # Environment & Display
    sound_speed: float = 1500.0
    max_range_m: float = 250.0
    max_doppler_hz: float = 10.0

    # Safety
    max_average_power_w: float = 5.0
    max_temperature_c: float = 70.0

    # Adaptive controller
    decision_deadline_ms: float = 10.0

    # Detection
    cfar_guard_cells: int = 8
    cfar_training_cells: int = 24
    cfar_scale: float = 4.5

    # Simulation
    random_seed: int = 42

CONFIG = SonarConfig()