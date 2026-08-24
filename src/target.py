from dataclasses import dataclass


@dataclass
class Target:
    range_m: float
    radial_velocity_mps: float
    amplitude: float = 1.0

    def propagation_delay(self, sound_speed):
        return (
            2.0 * self.range_m
            / sound_speed
        )

    def doppler_shift(
        self,
        carrier_frequency,
        sound_speed
    ):
        return (
            2.0
            * self.radial_velocity_mps
            * carrier_frequency
            / sound_speed
        )