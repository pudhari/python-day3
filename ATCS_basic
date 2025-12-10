# atcs_app.py
"""
Streamlit ATCS (Intermediate) demo app
Option B: Inputs: Volume, Speed, Queue, Vehicle Mix
Computes: density estimate, traffic state, weighted congestion index
Outputs: recommended green time and charts

Usage:
    pip install streamlit pandas numpy plotly
    streamlit run atcs_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="ATCS Simulator (Intermediate)", layout="wide")

# -------------------------
# Helper functions
# -------------------------
def compute_flow_per_hour(count_per_interval, interval_seconds=60):
    """Convert counts per interval (e.g., per minute) to veh/hr."""
    return count_per_interval * (3600 / interval_seconds)

def estimate_density(flow_vph, avg_speed_kph):
    """
    Very simple density estimate: k = q / v
    where q = flow (veh/hr) and v = speed (km/hr)
    density in veh/km (approx per lane). This is a simplified proxy.
    """
    # avoid division by zero
    return np.where(avg_speed_kph > 0, flow_vph / avg_speed_kph, np.nan)

def congestion_index(volume, speed, queue, heavy_pct, weights=None):
    """
    Weighted congestion index combining:
      - Volume effect (normalized)
      - Speed effect (lower speed increases index)
      - Queue effect (direct)
      - Heavy vehicle mix effect (heavy vehicles -> higher index)
    weights: dict with keys 'vol','spd','que','veh'
    """
    if weights is None:
        weights = {'vol': 0.35, 'spd': 0.25, 'que': 0.30, 'veh': 0.10}
    # Normalize volume by a typical max (user may change)
    vol_norm = volume / (volume.max() if hasattr(volume, 'max') else max(volume,1))
    # Speed effect: low speed -> high score. We invert and normalize to 0-1 using 0-60 kph scale
    spd_norm = (60 - speed.clip(0,60)) / 60.0
    # Queue normalization: assume typical max queue 30 vehicles
    que_norm = queue / 30.0
    veh_norm = heavy_pct / 100.0
    idx = (weights['vol'] * vol_norm +
           weights['spd'] * spd_norm +
           weights['que'] * que_norm +
           weights['veh'] * veh_norm)
    # scale to 0-100 for readability
    return idx * 100

def traffic_state_from_index(idx):
    """Simple mapping of congestion index to traffic state."""
    if np.isnan(idx):
        return "Unknown"
    if idx < 25:
        return "Free flow"
    if idx < 50:
        return "Stable / Moderate"
    return "Congested"

def recommend_green_time(cong_idx, min_green=15, max_green=60, cycle_time=90):
    """
    Recommend green time (sec) using a piecewise + proportional logic:
      - low congestion -> min_green
      - moderate -> proportion of cycle based on index
      - high -> cap near max_green
    """
    if np.isnan(cong_idx):
        return min_green
    if cong_idx < 25:
        return min_green
    if cong_idx >= 75:
        return max_green
    # scale between min and max for indices between 25 and 75
    t = (cong_idx - 25) / (75 - 25)  # 0..1
    return float(min_green + t * (max_green - min_green))

# -------------------------
# UI - sidebar
# -------------------------
st.sidebar.header("ATCS Simulator — Inputs")

mode = st.sidebar.selectbox("Mode", ["Interactive single scenario", "Upload CSV (batch)"])

st.sidebar.markdown("**Model parameters**")
interval_sec = st.sidebar.number_input("Sensor interval (seconds)", value=60, min_value=10, max_value=300, step=10)
cycle_time = st.sidebar.number_input("Total cycle time (sec, for proportioning)", value=90, min_value=30)
min_green = st.sidebar.number_input("Minimum green (sec)", value=15, min_value=5)
max_green = st.sidebar.number_input("Maximum green (sec)", value=60, min_value=15)

st.sidebar.markdown("---")
st.sidebar.markdown("**Index weights (vol, spd, que, veh)**")
w_vol = st.sidebar.slider("Volume weight", 0.0, 1.0, 0.35)
w_spd = st.sidebar.slider("Speed weight", 0.0, 1.0, 0.25)
w_que = st.sidebar.slider("Queue weight", 0.0, 1.0, 0.30)
w_veh = st.sidebar.slider("Vehicle mix weight", 0.0, 1.0, 0.10)
# normalize weights to sum 1
w_sum = w_vol + w_spd + w_que + w_veh
weights = {'vol': w_vol / w_sum, 'spd': w_spd / w_sum, 'que': w_que / w_sum, 'veh': w_veh / w_sum}

# -------------------------
# Interactive single scenario
# -------------------------
if mode == "Interactive single scenario":
    st.title("ATCS Simulator — Interactive Scenario (Intermediate)")
    st.markdown("Enter sensor-like values for one approach (e.g., NS). The app will compute derived indicators and recommend green time.")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Traffic inputs (this approach)")
        volume = st.number_input("Vehicle count per interval (e.g., vehicles per minute)", value=15, min_value=0)
        avg_speed = st.number_input("Average speed (km/h)", value=30.0, min_value=0.0, step=0.5)
        queue_len = st.number_input("Queue length (vehicles)", value=5, min_value=0)
        heavy_pct = st.slider("Heavy vehicle % (trucks/buses)", 0, 100, 10)
    with col2:
        st.subheader("Context / opposing approach (for normalization)")
        opp_volume = st.number_input("Opposing approach count per interval", value=25, min_value=0)
        opp_speed = st.number_input("Opposing avg speed (km/h)", value=22.0, min_value=0.0, step=0.5)
        opp_queue = st.number_input("Opposing queue length (vehicles)", value=12, min_value=0)
        opp_heavy_pct = st.slider("Opposing heavy vehicle %", 0, 100, 15)

    # Build a small dataframe for display and vectorized calculation
    df = pd.DataFrame({
        "approach": ["This", "Opposing"],
        "count_per_interval": [volume, opp_volume],
        "avg_speed": [avg_speed, opp_speed],
        "queue": [queue_len, opp_queue],
        "heavy_pct": [heavy_pct, opp_heavy_pct]
    })

    # Derived measures
    df["flow_vph"] = compute_flow_per_hour(df["count_per_interval"], interval_seconds=interval_sec)
    df["density_veh_per_km"] = estimate_density(df["flow_vph"], df["avg_speed"])
    df["cong_index"] = congestion_index(df["count_per_interval"], df["avg_speed"], df["queue"], df["heavy_pct"], weights=weights)
    df["traffic_state"] = df["cong_index"].apply(traffic_state_from_index)
    df["recommended_green_sec"] = df["cong_index"].apply(lambda x: recommend_green_time(x, min_green=min_green, max_green=max_green, cycle_time=cycle_time))

    # Show results
    st.subheader("Derived Indicators & ATCS Decision")
    st.dataframe(df.style.format({
        "flow_vph": "{:,.1f}",
        "density_veh_per_km": "{:,.2f}",
        "cong_index": "{:,.2f}",
        "recommended_green_sec": "{:.1f}"
    }), height=240)

    # Charts
    st.subheader("Visualization")
    col3, col4 = st.columns([1,1])
    fig1 = px.bar(df, x="approach", y=["flow_vph","queue"], barmode="group", title="Flow (vph) and Queue")
    col3.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(df, x="approach", y="cong_index", title="Congestion Index")
    col4.plotly_chart(fig2, use_container_width=True)

    # Explanation / How it maps to ATCS
    st.markdown("---")
    st.markdown("**How the model maps to ATCS (explainable):**")
    st.markdown(
        "- Flow (vehicles/hour) shows demand. ATCS increases green time when demand is larger.\n"
        "- Low average speed increases the congestion score because it signals slowing / bottleneck.\n"
        "- Queue length directly increases the score (queues are the visible problem ATCS must clear).\n"
        "- Heavy vehicles reduce capacity, increasing the effective congestion.\n"
        "- The congestion index is a weighted combination; ATCS uses it to proportionally allocate green time."
    )

# -------------------------
# CSV / Batch mode
# -------------------------
else:
    st.title("ATCS Simulator — Batch CSV mode")
    st.markdown("Upload a CSV with columns: time (optional), count_per_interval, avg_speed, queue, heavy_pct. The app will compute derived indicators for each row.")

    uploaded = st.file_uploader("Upload CSV", type=["csv", "xlsx"])
    sample = pd.DataFrame({
        "time": ["09:00","09:01","09:02"],
        "count_per_interval": [12,15,10],
        "avg_speed": [35,32,40],
        "queue": [5,7,3],
        "heavy_pct":[10,12,8]
    })
    st.markdown("### Sample input format")
    st.dataframe(sample, height=160)

    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                user_df = pd.read_csv(uploaded)
            else:
                user_df = pd.read_excel(uploaded)
            # basic validation
            required = {"count_per_interval","avg_speed","queue","heavy_pct"}
            if not required.issubset(set(user_df.columns)):
                st.error(f"CSV must contain columns: {required}")
            else:
                df2 = user_df.copy()
                df2["flow_vph"] = compute_flow_per_hour(df2["count_per_interval"], interval_seconds=interval_sec)
                df2["density_veh_per_km"] = estimate_density(df2["flow_vph"], df2["avg_speed"])
                df2["cong_index"] = congestion_index(df2["count_per_interval"], df2["avg_speed"], df2["queue"], df2["heavy_pct"], weights=weights)
                df2["traffic_state"] = df2["cong_index"].apply(traffic_state_from_index)
                df2["recommended_green_sec"] = df2["cong_index"].apply(lambda x: recommend_green_time(x, min_green=min_green, max_green=max_green, cycle_time=cycle_time))
                st.success("Computed derived indicators")
                st.dataframe(df2, height=300)
                # plot congestion over time if time column exists
                if "time" in df2.columns:
                    fig = px.line(df2, x="time", y="cong_index", title="Congestion Index over time")
                    st.plotly_chart(fig, use_container_width=True)
                # allow download
                st.download_button("Download results as CSV", df2.to_csv(index=False).encode('utf-8'), file_name="atcs_results.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.caption("This is an educational, simplified ATCS model (intermediate). The congestion formulas are illustrative; a production ATCS uses more advanced traffic flow models, shorter intervals, and robust ML or control-theory logic.")
