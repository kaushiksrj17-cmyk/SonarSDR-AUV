# main.py
import time
from src.simulation import SonarSimulationEngine, SCENARIOS

def main():
    print("Starting SonarSDR-AUV Modular Simulation Baseline...\n")
    engine = SonarSimulationEngine(seed=42)

    for sc in SCENARIOS:
        print(f"Executing Scenario: {sc['name']} ({sc['description']})")
        frame, _, _, _, _, _, _, _ = engine.run_ping(sc)

        print(f"  ├─ Waveform Selected : {frame.selected_waveform}")
        print(f"  ├─ Decision Reason   : {frame.decision_reason}")
        print(f"  ├─ Power Mode        : {frame.power_mode} ({frame.average_power_w:.2f} W avg)")
        print(f"  ├─ Target Detected   : {frame.target_detected}")
        if frame.target_detected:
            print(f"  ├─ True / EKF Range  : {frame.true_range_m:.1f} m / {frame.estimated_range_m:.1f} m")
            print(f"  ├─ Range Error       : {frame.range_error_m:.2f} m")
        print(f"  └─ Total Latency     : {frame.total_pipeline_latency_ms:.2f} ms (Decision: {frame.decision_latency_ms:.3f} ms)")
        print("-" * 65)

    print("\nSimulation execution completed successfully.")

if __name__ == "__main__":
    main()