from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

DATA = Path("data")
OBS = DATA / "monthly_observations.csv"
CONFIG = DATA / "metrics_config.csv"
SCORES = DATA / "scenario_scores.csv"

st.set_page_config(page_title="AI Macro Regime Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    obs = pd.read_csv(OBS)
    config = pd.read_csv(CONFIG)
    scores = pd.read_csv(SCORES)
    obs["Date"] = obs["Date"].astype(str)
    scores["Date"] = scores["Date"].astype(str)
    df = obs.merge(config[["MetricID", "Cluster", "Metric", "PublicSourceURL", "AutoStatus", "Interpretation"]], on="MetricID", how="left", suffixes=("", "_Config"))
    return df, config, scores

df, config, scores = load_data()
dates = sorted(df["Date"].dropna().unique())

st.sidebar.title("AI macro dashboard")
selected_date = st.sidebar.selectbox("Selected month", dates, index=max(0, len(dates)-1))
page = st.sidebar.radio(
    "Page",
    ["Overview", "Regime map", "Scenario detail", "Metric table", "Top movers", "Data sources", "Methodology"],
)

current = df[df["Date"] == selected_date].copy()
score_row = scores[scores["Date"] == selected_date]
if not score_row.empty:
    score_row = score_row.iloc[0]
else:
    score_row = pd.Series({"Citrini":0, "Green":0, "Alden":0, "Other":0, "Leader":"Insufficient data", "Confidence":"Low"})

def scenario_bar_chart(score_row):
    chart_df = pd.DataFrame({
        "Scenario": ["Citrini", "Green", "Alden", "Other/Mixed"],
        "Score": [score_row["Citrini"], score_row["Green"], score_row["Alden"], score_row["Other"]],
    })
    fig = px.bar(chart_df, x="Score", y="Scenario", orientation="h", title="Scenario strength")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10))
    return fig

def score_trend_chart(scores):
    long = scores.melt(id_vars=["Date"], value_vars=["Citrini", "Green", "Alden", "Other"], var_name="Scenario", value_name="Score")
    fig = px.line(long, x="Date", y="Score", color="Scenario", markers=True, title="Scenario score trend")
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=50, b=10))
    return fig

def regime_map(current):
    # Simplified proxy:
    # Long bond proxy = M06 monthly change.
    # Gold proxy = M07 monthly change.
    def get_change(metric_id):
        s = current[current["MetricID"] == metric_id]["MonthlyChange"]
        if s.empty:
            return 0
        return pd.to_numeric(s, errors="coerce").fillna(0).iloc[0]
    bond = get_change("M06")
    gold = get_change("M07")
    fig = go.Figure()
    fig.add_hline(y=0, line_width=1)
    fig.add_vline(x=0, line_width=1)
    fig.add_trace(go.Scatter(x=[bond], y=[gold], mode="markers+text", text=[selected_date], textposition="top center", marker=dict(size=18)))
    fig.update_layout(
        title="Regime map: long bonds vs gold",
        xaxis_title="Long bond proxy monthly change",
        yaxis_title="Gold proxy monthly change",
        height=520,
        margin=dict(l=10, r=10, t=50, b=10),
        annotations=[
            dict(x=0.75, y=0.85, xref="paper", yref="paper", text="Citrini + policy rescue<br>Bonds up / gold up", showarrow=False),
            dict(x=0.25, y=0.85, xref="paper", yref="paper", text="Alden<br>Bonds down / gold up", showarrow=False),
            dict(x=0.75, y=0.15, xref="paper", yref="paper", text="Green<br>Bonds up / gold flat/down", showarrow=False),
            dict(x=0.25, y=0.15, xref="paper", yref="paper", text="Other<br>Higher real-rate/liquidity tightening", showarrow=False),
        ],
    )
    return fig

def metric_heatmap(current):
    by_cluster = current.groupby("Cluster", as_index=False)[["CitriniScore","GreenScore","AldenScore","OtherScore"]].sum()
    long = by_cluster.melt(id_vars="Cluster", var_name="Scenario", value_name="Score")
    long["Scenario"] = long["Scenario"].str.replace("Score", "", regex=False)
    fig = px.density_heatmap(long, x="Scenario", y="Cluster", z="Score", text_auto=True, title="Metric cluster heatmap")
    fig.update_layout(height=500, margin=dict(l=10, r=10, t=50, b=10))
    return fig

st.title("AI Macro Regime Dashboard")
st.caption("Tracks public macro/market metrics to compare Citrini, Green, Alden, and Other/Mixed regimes.")

if page == "Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Citrini", f"{score_row['Citrini']:.0f}")
    c2.metric("Green", f"{score_row['Green']:.0f}")
    c3.metric("Alden", f"{score_row['Alden']:.0f}")
    c4.metric("Other/Mixed", f"{score_row['Other']:.0f}")
    c5.metric("Leader", str(score_row["Leader"]), help=f"Confidence: {score_row['Confidence']}")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(scenario_bar_chart(score_row), use_container_width=True)
    with col2:
        st.plotly_chart(score_trend_chart(scores), use_container_width=True)

    st.subheader("Evidence heatmap")
    st.plotly_chart(metric_heatmap(current), use_container_width=True)

elif page == "Regime map":
    st.subheader("Cross-asset regime map")
    st.write("This simplified map uses the monthly change in the long-bond proxy and gold proxy. It is a first-pass visual, not a full scenario classifier.")
    st.plotly_chart(regime_map(current), use_container_width=True)

elif page == "Scenario detail":
    tabs = st.tabs(["Citrini", "Green", "Alden", "Other/Mixed"])
    for tab, scen, col in zip(tabs, ["CitriniScore","GreenScore","AldenScore","OtherScore"], ["Citrini","Green","Alden","Other"]):
        with tab:
            st.metric(f"{col} score", f"{float(score_row[col]):.0f}" if col in score_row else "0")
            detail = current[current[scen] > 0].copy().sort_values(scen, ascending=False)
            if detail.empty:
                st.info("No positive metric contributions for this scenario in the selected month.")
            else:
                st.dataframe(
                    detail[["MetricID","Metric","Cluster","Value","MonthlyChange","Unit",scen,"Tilt","Strength","Notes","SourceURL"]],
                    use_container_width=True,
                    hide_index=True,
                )

elif page == "Metric table":
    st.subheader("All metrics")
    st.dataframe(
        current[[
            "MetricID","Metric","Cluster","Value","PriorValue","MonthlyChange","Unit","Tilt","Strength",
            "CitriniScore","GreenScore","AldenScore","OtherScore","Notes","SourceURL","IsManual"
        ]].sort_values(["Cluster","MetricID"]),
        use_container_width=True,
        hide_index=True,
    )

elif page == "Top movers":
    st.subheader("Top score contributors this month")
    tmp = current.copy()
    tmp["MaxContribution"] = tmp[["CitriniScore","GreenScore","AldenScore","OtherScore"]].max(axis=1)
    tmp = tmp.sort_values("MaxContribution", ascending=False).head(12)
    st.dataframe(
        tmp[["MetricID","Metric","Cluster","Value","MonthlyChange","Tilt","Strength","MaxContribution","Notes"]],
        use_container_width=True,
        hide_index=True,
    )

elif page == "Data sources":
    st.subheader("Metric configuration and sources")
    st.dataframe(config, use_container_width=True, hide_index=True)
    st.download_button("Download metric configuration CSV", config.to_csv(index=False), file_name="metrics_config.csv")

elif page == "Methodology":
    st.subheader("Methodology")
    st.markdown("""
### What the scores mean

- **Citrini** rises when labor, income, consumption, and credit stress suggest AI-driven demand impairment.
- **Green** rises when high real yields, contained inflation expectations, and improving long-bond behavior support the long-duration opportunity thesis.
- **Alden** rises when gold/fiscal/reserve data suggest fiscal dominance, debasement pressure, or Treasury-demand stress.
- **Other/Mixed** rises when markets look like higher-real-rate tightening, liquidity stress, or an AI-capex boom that does not cleanly fit the three named scenarios.

### Important limitation

This is a monitoring tool, not a trading system. It is intentionally transparent and mechanical. The scoring rules should be reviewed after a few months of live data.
""")
