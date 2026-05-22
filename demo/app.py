"""
revive-companion Demo — deploy to HuggingFace Spaces.

Upload this file + requirements.txt to a new HuggingFace Space (Streamlit).
"""

import os
import sys

# Add the package to path (for HF Spaces)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from revive_companion import PoissonLove

# Page config
st.set_page_config(
    page_title="💘 revive-companion Demo",
    page_icon="💘",
    layout="wide",
)

st.title("💘 revive-companion")
st.markdown("**让 AI 主动找你时，像真人一样'想你了'，而不是'该发消息了'。**")
st.markdown("用泊松过程 + 贝叶斯推断 + 信息增益，决定**该不该**打扰用户。")

st.markdown(
    "[![GitHub](https://img.shields.io/badge/GitHub-revive--companion-blue?logo=github)](https://github.com/pearthink123/revive-companion) "
    "[![PyPI](https://img.shields.io/pypi/v/revive-companion?logo=python)](https://pypi.org/project/revive-companion/)"
)

# Sidebar
st.sidebar.header("⚙️ 参数设置")

st.sidebar.subheader("🎲 Poisson 参数")
lam = st.sidebar.slider("λ (触达率)", 0.05, 0.50, 0.15, 0.01, help="泊松过程的事件率。越高=越频繁触发。")
check_interval = st.sidebar.slider("检查间隔 (分钟)", 10, 60, 30, 5)
growth_factor = st.sidebar.slider("增长因子", 0.01, 0.20, 0.08, 0.01, help="每次 miss 后概率增长量。")

st.sidebar.subheader("⏱️ 模拟设置")
sim_hours = st.sidebar.slider("模拟时长 (小时)", 12, 168, 48, 12)
seed = st.sidebar.number_input("随机种子", 0, 1000, 42)


@st.cache_data
def run_simulation(lam, check_interval, growth_factor, sim_hours, seed):
    love = PoissonLove(seed=seed)
    love._engine.config.engagement.lambda_rate = lam
    love._engine.config.engagement.check_interval_minutes = check_interval
    love._engine.config.engagement.growth_factor = growth_factor

    results = []
    now = datetime.now()
    total_ticks = int(sim_hours * 60 / check_interval)

    for i in range(total_ticks):
        tick_time = now + timedelta(minutes=i * check_interval)
        result = love.tick(now=tick_time)

        hour = tick_time.hour
        if 9 <= hour < 17:
            love.record_reply(reply_speed=0.2, reply_length=0.2) if random.random() < 0.3 else None
        elif 18 <= hour < 22:
            love.record_reply(reply_speed=0.8, reply_length=0.7) if random.random() < 0.6 else None

        if result.should_send:
            love.record_send()

        results.append({
            "time": tick_time,
            "hour": hour,
            "probability": result.probability,
            "should_send": result.should_send,
            "stage": result.stage,
            "user_state": result.user_state,
            "utility": result.send_utility,
            "info_gain": result.info_gain,
        })

    return pd.DataFrame(results)


with st.spinner("正在模拟..."):
    df = run_simulation(lam, check_interval, growth_factor, sim_hours, seed)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总检查次数", len(df))
with col2:
    st.metric("发送次数", int(df["should_send"].sum()))
with col3:
    st.metric("最高渴望度", f"{df['probability'].max():.0%}")
with col4:
    st.metric("平均效用", f"{df['utility'].mean():.2f}")

st.markdown("---")

# 1. Longing Curve
st.subheader("🎲 渴望曲线 (Poisson Probability)")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df["time"], y=df["probability"], mode="lines", name="渴望度",
    line=dict(color="#FF6B6B", width=2), fill="tozeroy", fillcolor="rgba(255,107,107,0.1)",
))
sent_df = df[df["should_send"]]
fig1.add_trace(go.Scatter(
    x=sent_df["time"], y=sent_df["probability"], mode="markers", name="发送",
    marker=dict(color="#4ECDC4", size=10, symbol="star"),
))
fig1.update_layout(xaxis_title="时间", yaxis_title="渴望度", yaxis_range=[0, 1], height=300)
st.plotly_chart(fig1, use_container_width=True)

# 2. State Distribution
st.subheader("🧠 用户状态分布 (Bayesian)")
state_counts = df["user_state"].value_counts()
fig2 = go.Figure(data=[go.Pie(
    labels=state_counts.index, values=state_counts.values, hole=0.3,
    marker_colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"],
)])
fig2.update_layout(height=300)
st.plotly_chart(fig2, use_container_width=True)

# 3. Hourly Pattern
st.subheader("⏰ 按小时分布")
hourly = df.groupby("hour").agg({
    "should_send": "sum", "probability": "mean", "utility": "mean",
}).reset_index()
fig3 = make_subplots(specs=[[{"secondary_y": True}]])
fig3.add_trace(go.Bar(x=hourly["hour"], y=hourly["should_send"], name="发送次数", marker_color="#4ECDC4"), secondary_y=False)
fig3.add_trace(go.Scatter(x=hourly["hour"], y=hourly["probability"], name="平均渴望度", line=dict(color="#FF6B6B", width=2)), secondary_y=True)
fig3.update_layout(xaxis_title="小时", height=300)
fig3.update_yaxes(title_text="发送次数", secondary_y=False)
fig3.update_yaxes(title_text="渴望度", range=[0, 1], secondary_y=True)
st.plotly_chart(fig3, use_container_width=True)

# 4. Decision Log
st.subheader("📋 决策日志")
recent = df.tail(20).copy()
recent["时间"] = recent["time"].dt.strftime("%H:%M")
recent["决策"] = recent["should_send"].apply(lambda x: "✅ 发送" if x else "❌ 等待")
recent["渴望度"] = recent["probability"].apply(lambda x: f"{x:.0%}")
recent["效用"] = recent["utility"].apply(lambda x: f"{x:.2f}")
st.dataframe(recent[["时间", "决策", "user_state", "渴望度", "效用"]], use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(
    "💘 **revive-companion** | "
    "[GitHub](https://github.com/pearthink123/revive-companion) | "
    "[PyPI](https://pypi.org/project/revive-companion/) | "
    "Math models that make AI engagement feel human",
    unsafe_allow_html=True,
)
