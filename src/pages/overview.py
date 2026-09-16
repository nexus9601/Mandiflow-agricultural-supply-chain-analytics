"""MandiFlow – Overview Page"""

import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, transport_df: pd.DataFrame, prices_df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "Overview",
        "Unified cross-domain analytics integrating mandi arrivals, wholesale modal prices, MSP compliance, and logistics.",
        badge="EXECUTIVE DASHBOARD",
    ), unsafe_allow_html=True)

    if df.empty:
        st.markdown(styles.empty_state("No data available for the current filter criteria."), unsafe_allow_html=True)
        return

    # ── KPI Row ──────────────────────────────────────────────────────────────
    kpis = metrics.overview_kpis(df, transport_df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_data = [
        (c1, "Total Arrivals",      metrics.fmt_qty(kpis["total_arrivals"]),    "emerald", "Total Inflow Volume"),
        (c2, "Avg Modal Price",     metrics.fmt_inr(kpis["avg_modal_price"]),   "emerald", "Market Average"),
        (c3, "Average MSP",         metrics.fmt_inr(kpis["avg_msp"]),           "amber",   "Support Floor"),
        (c4, "Price Crash Count",   metrics.fmt_int(kpis["price_crash_count"]), "danger",  "Below MSP Floor"),
        (c5, "Avg Transit Time",    metrics.fmt_hrs(kpis["avg_transit_hours"]), "sky",     "Dispatch to Mandi"),
        (c6, "Long Transit Rate",   metrics.fmt_pct(kpis["long_transit_rate"]), "amber",   "> 24h Threshold"),
    ]
    for col, label, val, variant, delta in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant=variant, delta=delta), unsafe_allow_html=True)

    # ── Chart Row 1 ──────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Arrival Dynamics & Commodity Distribution"), unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        crop_opts = ["All"] + sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else ["All"]
        sel_crop = st.selectbox("Filter by Crop", crop_opts, key="ov_crop_sel")
        fdf = df if sel_crop == "All" else df[df["crop_name"] == sel_crop]
        st.plotly_chart(charts.create_arrival_trend(fdf, sel_crop), use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.plotly_chart(charts.create_crop_distribution(df), use_container_width=True, config={"displayModeBar": False})

    # ── Chart Row 2 ──────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Mandi Volume & Price vs MSP Parity"), unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.plotly_chart(charts.create_top_mandis(df), use_container_width=True, config={"displayModeBar": False})

    with col_r:
        st.plotly_chart(charts.create_price_vs_msp_grouped(df), use_container_width=True, config={"displayModeBar": False})

    # ── Key Insights ─────────────────────────────────────────────────────────
    insights = metrics.key_insights(df, transport_df)

    st.markdown(f"""
<div class="insight-card">
  <h4>Key Supply Chain Findings</h4>
  <div class="insight-grid">
    <div class="insight-item">
      <div class="insight-label">Highest-Arrival Crop</div>
      <div style="font-weight: 600; font-size: 0.88rem; color: #0f172a; margin-top: 2px;">{insights.get('top_crop', '—')}</div>
    </div>
    <div class="insight-item">
      <div class="insight-label">Highest-Volume Mandi Hub</div>
      <div style="font-weight: 600; font-size: 0.88rem; color: #0f172a; margin-top: 2px;">{insights.get('top_mandi', '—')}</div>
    </div>
    <div class="insight-item">
      <div class="insight-label">Largest Negative MSP Gap</div>
      <div style="font-weight: 600; font-size: 0.88rem; color: #b91c1c; margin-top: 2px;">{insights.get('worst_msp_crop', '—')}</div>
    </div>
    <div class="insight-item">
      <div class="insight-label">Critical Transit Warehouse</div>
      <div style="font-weight: 600; font-size: 0.88rem; color: #0f172a; margin-top: 2px;">{insights.get('worst_transit_warehouse', '—')}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        "Export Filtered Overview Data (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="mandiflow_overview.csv",
        mime="text/csv",
    )
