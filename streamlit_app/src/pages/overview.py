"""MandiFlow – Overview Page"""

import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, transport_df: pd.DataFrame, prices_df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "Overview",
        "Monitor agricultural arrivals, market prices, MSP performance, logistics and weather conditions.",
    ), unsafe_allow_html=True)

    if df.empty:
        st.markdown(styles.empty_state("No data available. Check dataset path."), unsafe_allow_html=True)
        return

    # ── KPI Row ──────────────────────────────────────────────────────────────
    kpis = metrics.overview_kpis(df, transport_df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_data = [
        (c1, "Total Crop Arrivals",     metrics.fmt_qty(kpis["total_arrivals"]),           "default"),
        (c2, "Avg Modal Price",          metrics.fmt_inr(kpis["avg_modal_price"]),          "default"),
        (c3, "Avg MSP",                  metrics.fmt_inr(kpis["avg_msp"]),                  "default"),
        (c4, "Price Crash Instances",   metrics.fmt_int(kpis["price_crash_count"]),        "danger"),
        (c5, "Avg Transit Time",         metrics.fmt_hrs(kpis["avg_transit_hours"]),        "default"),
        (c6, "Long Transit Rate (>24h)", metrics.fmt_pct(kpis["long_transit_rate"]),        "amber"),
    ]
    for col, label, val, variant in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant), unsafe_allow_html=True)

    st.markdown("<hr class='mf-divider'>", unsafe_allow_html=True)

    # ── Chart Row 1 ──────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Arrival Trends"), unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        crop_opts = ["All"] + sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else ["All"]
        sel_crop = st.selectbox("Select Crop", crop_opts, key="ov_crop_sel", label_visibility="collapsed")
        fdf = df if sel_crop == "All" else df[df["crop_name"] == sel_crop]
        st.plotly_chart(charts.create_arrival_trend(fdf, sel_crop), width='stretch', config={"displayModeBar": False})

    with col_right:
        st.plotly_chart(charts.create_crop_distribution(df), width='stretch', config={"displayModeBar": False})

    # ── Chart Row 2 ──────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Mandi & Price Overview"), unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.plotly_chart(charts.create_top_mandis(df), width='stretch', config={"displayModeBar": False})

    with col_r:
        st.plotly_chart(charts.create_price_vs_msp_grouped(df), width='stretch', config={"displayModeBar": False})

    # ── Key Insights ─────────────────────────────────────────────────────────
    st.markdown("<hr class='mf-divider'>", unsafe_allow_html=True)
    insights = metrics.key_insights(df, transport_df)

    st.markdown(f"""
<div class="insight-card">
  <h4>Key Insights</h4>
  <div class="insight-item">
    <span class="insight-label">Highest-Arrival Crop:</span> {insights.get('top_crop', '—')}
  </div>
  <div class="insight-item">
    <span class="insight-label">Highest-Volume Mandi:</span> {insights.get('top_mandi', '—')}
  </div>
  <div class="insight-item">
    <span class="insight-label">Crop with Largest Negative MSP Gap:</span> {insights.get('worst_msp_crop', '—')}
  </div>
  <div class="insight-item">
    <span class="insight-label">Highest Long-Transit Warehouse:</span> {insights.get('worst_transit_warehouse', '—')}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "Download Filtered Data (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="mandiflow_overview.csv",
        mime="text/csv",
    )
