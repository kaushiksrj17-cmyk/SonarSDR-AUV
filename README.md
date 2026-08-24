# ⚓ SonarSDR-AUV: Cognitive Software-Defined Sonar Command Suite

An end-to-end cognitive Software-Defined Sonar (SDR) simulation and real-time command suite built for Autonomous Underwater Vehicles (AUVs). The platform integrates adaptive multi-waveform switching (LFM, HFM, Barker, Golay, CW), contextual bandit decision engines, power-constrained safety supervision, CFAR target detection, and Alpha-Beta target tracking paired with a 2D Range-Doppler ambiguity dashboard.

---

## 🌟 Key Features

* **Cognitive Waveform Adaptation**: Real-time adaptive switching between LFM, HFM, Barker Code, Golay Pairs, and CW waveforms driven by a Contextual Bandit reinforcement framework.
* **Environmental Channel Simulation**: Models realistic underwater acoustic phenomena including multipath propagation, seabed reverberation, Doppler shift, and acoustic SNR decay.
* **2D Range-Doppler Ambiguity Mapping**: Computes dynamic 2D Range-Doppler ambiguity surfaces and matched-filter signal envelopes.
* **Adaptive Power Management & Safety Supervisor**: Dynamic power scaling (ECO, BALANCED, BOOST) enforcing continuous average thermal and power constraints.
* **Alpha-Beta Target Tracking**: Range-rate filtering to estimate true target trajectory amidst reverberation clutter.
* **Streamlit Control Center**: Interactive real-time dashboard for operational scenario modulation, telemetry analysis, and Monte Carlo benchmarking.

---

## 🏗 System Architecture
