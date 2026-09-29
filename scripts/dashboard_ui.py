import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="LLMOps Dashboard", layout="wide")
st.title("📊 LLMOps Monitoring Dashboard (CP2)")
st.markdown("Time Range: **Last 60 minutes**")

# Đọc dữ liệu từ file log
logs = []
try:
    with open("data/logs.jsonl", "r") as f:
        for line in f:
            logs.append(json.loads(line))
except FileNotFoundError:
    st.error("Chưa có data/logs.jsonl. Hãy chạy scripts/load_test.py trước.")
    st.stop()

df = pd.DataFrame(logs)
if df.empty or 'event' not in df.columns:
    st.warning("File log trống hoặc không hợp lệ.")
    st.stop()

# Lọc các sự kiện response
df_response = df[df['event'] == 'response_sent'].copy()

# Layout 2 cột cho 6 Panel
col1, col2 = st.columns(2)

with col1:
    # Panel 1: Traffic
    st.subheader("1. Traffic (Requests/min)")
    traffic = df[df['event'] == 'request_received'].shape[0]
    st.metric(label="Total Requests", value=traffic)

    # Panel 3: Error Rate & Retrieval
    st.subheader("3. Errors & Retrieval")
    error_count = df[df['event'] == 'request_failed'].shape[0]
    total_reqs = traffic if traffic > 0 else 1
    st.metric(label="Error Rate", value=f"{(error_count/total_reqs)*100:.2f} %", delta="SLO max: 2.0%", delta_color="inverse")

    # Panel 5: Tokens
    st.subheader("5. Token Usage")
    if 'tokens_in' in df_response.columns and 'tokens_out' in df_response.columns:
        total_in = df_response['tokens_in'].sum()
        total_out = df_response['tokens_out'].sum()
        st.metric(label="Total Tokens (In / Out)", value=f"{total_in} / {total_out}")

with col2:
    # Panel 2: Latency
    st.subheader("2. Latency (ms)")
    if 'latency_ms' in df_response.columns:
        p50 = df_response['latency_ms'].quantile(0.5)
        p95 = df_response['latency_ms'].quantile(0.95)
        st.metric(label="Latency P95", value=f"{p95:.0f} ms", delta="SLO limit: 3000 ms", delta_color="inverse")
        st.write(f"P50: {p50:.0f} ms")

    # Panel 4: Cost
    st.subheader("4. Cost (USD)")
    if 'cost_usd' in df_response.columns:
        total_cost = df_response['cost_usd'].sum()
        st.metric(label="Total Cost", value=f"${total_cost:.6f}", delta="SLO max: $2.5", delta_color="inverse")

    # Panel 6: Quality Proxy
    st.subheader("6. Quality Score")
    if 'quality_score' in df_response.columns:
        avg_quality = df_response['quality_score'].mean()
        st.metric(label="Average Quality", value=f"{avg_quality:.2f}", delta="SLO min: 0.75")