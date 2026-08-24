# dashboard.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.simulation import SonarSimulationEngine, SCENARIOS
from src.config import CONFIG
from benchmark import run_comparative_benchmark

st.set_page_config(
    page_title="SonarSDR-AUV Control Center",
    page_icon="⚓",
    layout="wide"
)

if "engine" not in st.session_state:
    st.session_state.engine = SonarSimulationEngine(seed=42)

st.title("⚓ SonarSDR-AUV: Cognitive Software-Defined Sonar Command Suite")
st.caption("Real-Time Waveform Adaptation, 2D Range-Doppler Ambiguity Mapping & EKF Target Tracking")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🌊 Underwater Channel Controls")
scenario_choice = st.sidebar.selectbox("Load Scenario Preset", options=[sc["name"] for sc in SCENARIOS], index=0)
preset = next(sc for sc in SCENARIOS if sc["name"] == scenario_choice)

snr_slider = st.sidebar.slider("SNR (dB)", -5.0, 25.0, float(preset["snr"]), 0.5)
reverb_slider = st.sidebar.slider("Reverberation Index", 0.0, 1.0, float(preset["reverberation"]), 0.05)
doppler_slider = st.sidebar.slider("Doppler Shift (Hz)", -10.0, 10.0, float(preset["doppler"]), 0.5)
multipath_slider = st.sidebar.slider("Multipath Intensity", 0.0, 0.8, float(preset["multipath"]), 0.05)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Target Dynamics")
target_range = st.sidebar.slider("Target Range (m)", 10.0, 250.0, float(preset["target_range_m"]), 5.0)
target_vel = st.sidebar.slider("Radial Velocity (m/s)", -10.0, 10.0, float(preset["target_velocity_mps"]), 0.5)

current_scenario = {
    "name": f"CUSTOM_{scenario_choice}",
    "snr": snr_slider,
    "reverberation": reverb_slider,
    "doppler": doppler_slider,
    "multipath": multipath_slider,
    "target_range_m": target_range,
    "target_velocity_mps": target_vel,
    "temperature_c": 25.0
}

# Run Ping execution
frame, t_tx, tx_sig, rx_sig, env, rd_map, rd_ranges, rd_dopplers = st.session_state.engine.run_ping(current_scenario)

# --- PANEL METRICS ---
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.subheader("1. AUV Mission")
    st.metric("Depth", "48 m")
    st.metric("Battery", "82 %")
    st.metric("Status", "ACTIVE")

with col2:
    st.subheader("2. Channel")
    st.metric("SNR", f"{frame.snr_db:.1f} dB")
    st.metric("Reverb Index", f"{frame.reverberation:.2f}")
    st.metric("Doppler Shift", f"{frame.doppler_hz:.1f} Hz")

with col3:
    st.subheader("3. AI Decision")
    st.metric("Selected Waveform", frame.selected_waveform)
    st.write(f"**Reason:** {frame.decision_reason}")
    st.caption(f"Decision Latency: {frame.decision_latency_ms:.2f} ms")

with col4:
    st.subheader("4. EKF Target Tracking")
    status_str = "TRACKING ✅" if frame.target_detected else "SEARCHING ❌"
    st.metric("Status", status_str)
    st.metric("EKF Range", f"{frame.estimated_range_m:.1f} m" if frame.target_detected else "N/A")
    st.metric("Range Error", f"{frame.range_error_m:.2f} m" if frame.target_detected else "N/A")

with col5:
    st.subheader("5. Energy & Safety")
    st.metric("Power Mode", frame.power_mode)
    st.metric("Avg Power", f"{frame.average_power_w:.2f} W")
    st.metric("Safety Status", frame.safety_status)

st.markdown("---")

# --- 2D RANGE-DOPPLER HEATMAP & 1D ENVELOPE ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌌 2D Range-Doppler Ambiguity Map")
    fig_rd = go.Figure(data=go.Heatmap(
        z=rd_map,
        x=rd_ranges,
        y=rd_dopplers,
        colorscale="Viridis"
    ))
    fig_rd.update_layout(
        xaxis_title="Range (m)",
        yaxis_title="Doppler Shift (Hz)",
        height=400,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_rd, use_container_width=True)

with col_right:
    st.subheader("📡 Matched Filter Envelope Signal")
    fig_env = go.Figure()
    fig_env.add_trace(go.Scatter(x=rd_ranges, y=env[:len(rd_ranges)], name="MF Envelope", line=dict(color="#00FFCC", width=1.5)))
    if frame.target_detected:
        fig_env.add_vline(x=frame.estimated_range_m, line_dash="dash", line_color="red", annotation_text=f"EKF: {frame.estimated_range_m:.1f}m")
    fig_env.update_layout(
        xaxis_title="Range (m)",
        yaxis_title="Magnitude",
        height=400,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_env, use_container_width=True)

# --- BENCHMARK ---
st.markdown("---")
st.subheader("📊 Performance Verification Suite")
if st.button("RUN BENCHMARK COMPARISON"):
    with st.spinner("Running Monte Carlo Scenario Evaluations across fixed vs adaptive architectures..."):
        bench_df = run_comparative_benchmark(num_pings_per_scenario=25)
        st.dataframe(bench_df, use_container_width=True)