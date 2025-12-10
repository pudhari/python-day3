import streamlit as st
import pandas as pd
import numpy as np

st.title("Adaptive Traffic Control System (ATCS) – Intermediate Model")
st.write("This model simulates how ATCS uses real-time variables to adjust signal timings.")

# --- INPUTS ---
st.subheader("Traffic Inputs")

volume = st.slider("Traffic Volume (veh/min)", 5, 80, 30)
speed = st.slider("Average Speed (km/h)", 5, 60, 25)
queue = st.slider("Queue Length (vehicles)", 0, 40, 10)
heavy_pct = st.slider("Heavy Vehicle Percentage (%)", 0, 60, 20)

# --- CALCULATIONS ---
st.subheader("Computed Values")

# Density (simple formula)
density = volume / max(speed, 1)

# Congestion score
congestion = (
    (volume / 80) * 0.4 +
    (queue / 40) * 0.4 +
    ((60 - speed) / 60) * 0.2
)

# Vehicle mix adjustment
mix_factor = 1 + (heavy_pct / 100)

adj_congestion = congestion * mix_factor

# Determine traffic state
if adj_congestion < 0.35:
    state = "Free Flow"
elif adj_congestion < 0.7:
    state = "Moderate"
else:
    state = "Congested"

# Base cycle time (typical signal cycle)
base_cycle = 90  # seconds

# Green time is proportional to congestion
green_time = int(base_cycle * adj_congestion)

# Red time = remaining cycle
red_time = base_cycle - green_time

# --- OUTPUTS ---
st.write("### Traffic State:", state)

st.write("**Density:**", round(density, 2), "veh/km")
st.write("**Congestion Index:**", round(adj_congestion, 3))

# Clear green light duration
st.subheader("🔵 Signal Timing Output (ATCS Decision)")
st.write(f"### 🟢 Green Light Duration: **{green_time} seconds**")
st.write(f"### 🔴 Red Light Duration: **{red_time} seconds**")

st.info("""
The ATCS assigns a longer green time when:
- Volume is high  
- Queue length increases  
- Speed is low  
- Heavy vehicles increase congestion  
""")

st.success("ATCS adjusts signal timings in real time based on the above calculations.")
