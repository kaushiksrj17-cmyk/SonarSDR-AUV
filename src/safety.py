import time


class SafetySupervisor:

    def __init__(
        self,
        max_power_w=5.0,
        max_temperature_c=70.0,
        watchdog_timeout_ms=50.0
    ):

        self.max_power_w = max_power_w
        self.max_temperature_c = max_temperature_c
        self.watchdog_timeout_ms = watchdog_timeout_ms

    def check(
        self,
        power_w,
        temperature_c,
        decision_latency_ms
    ):

        if power_w > self.max_power_w:

            return False, "POWER_LIMIT"

        if temperature_c > self.max_temperature_c:

            return False, "THERMAL_LIMIT"

        if decision_latency_ms > self.watchdog_timeout_ms:

            return False, "WATCHDOG_TIMEOUT"

        return True, "SAFE"