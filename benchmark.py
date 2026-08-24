# benchmark.py
import pandas as pd
import numpy as np
from src.simulation import SonarSimulationEngine, SCENARIOS

def run_comparative_benchmark(num_pings_per_scenario=20):
    print("=" * 70)
    print(" Running SonarSDR-AUV Comparative Performance Benchmark")
    print("=" * 70)

    systems = {
        "Fixed LFM": "LFM",
        "Fixed CW": "CW",
        "SonarSDR AI": None
    }

    results = []

    for sys_name, waveform_override in systems.items():
        engine = SonarSimulationEngine(seed=42)

        pings_run = 0
        detections = 0
        total_range_err = 0.0
        total_power = 0.0
        total_latency = 0.0

        for sc in SCENARIOS:
            for _ in range(num_pings_per_scenario):
                frame, _, _, _, _, _, _, _ = engine.run_ping(sc, override_waveform=waveform_override)
                pings_run += 1
                if frame.target_detected:
                    detections += 1
                    total_range_err += frame.range_error_m
                total_power += frame.average_power_w
                total_latency += frame.total_pipeline_latency_ms

        det_rate = (detections / pings_run) * 100.0
        avg_err = (total_range_err / detections) if detections > 0 else 0.0
        avg_pwr = total_power / pings_run
        avg_lat = total_latency / pings_run
        energy_per_ping_j = avg_pwr * 0.050

        results.append({
            "System Architecture": sys_name,
            "Detection Rate (%)": round(det_rate, 1),
            "Mean Range Error (m)": round(avg_err, 2),
            "Average Power (W)": round(avg_pwr, 2),
            "Energy / Ping (J)": round(energy_per_ping_j, 3),
            "Pipeline Latency (ms)": round(avg_lat, 2),
            "Adaptive": "Yes" if sys_name == "SonarSDR AI" else "No"
        })

    df = pd.DataFrame(results)
    print("\nBENCHMARK SUMMARY RESULTS:\n")
    print(df.to_string(index=False))
    print("\n" + "=" * 70)
    return df

if __name__ == "__main__":
    run_comparative_benchmark()