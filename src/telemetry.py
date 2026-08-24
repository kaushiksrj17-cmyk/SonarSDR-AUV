import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class TelemetryFrame:
    timestamp: float
    scenario_name: str
    snr_db: float
    reverberation: float
    doppler_hz: float
    multipath: float
    selected_waveform: str
    decision_reason: str
    power_mode: str
    instantaneous_power_w: float
    average_power_w: float
    target_detected: bool
    true_range_m: float
    estimated_range_m: float
    range_error_m: float
    decision_latency_ms: float
    total_pipeline_latency_ms: float
    safety_status: str

class TelemetryLogger:
    def __init__(self):
        self.history: List[TelemetryFrame] = []

    def log(self, frame: TelemetryFrame):
        self.history.append(frame)

    def clear(self):
        self.history.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [f.__dict__ for f in self.history]