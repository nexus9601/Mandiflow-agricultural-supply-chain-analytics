"""MandiFlow – Mandi Analysis Page"""

import numpy as np
import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, filters: dict) -> None:
    st.markdown(styles.page_header(
        "Mandi Activity & Geographical Benchmarking",
        "Comparative evaluation of trading hubs, catchment district concentration, and throughput velocity.",
        badge="MANDI INTELLIGENCE",
    ), unsafe_allow_html=True)

    if df.empty:
        st.markdown(styles.empty_state(), unsafe_allow_html=True)
        return

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpis = metrics.mandi_kpis(df)
    c1, c2, c3, c4 = st.columns(4)
    kpi_data = [
        (c1, "Active Mandis",       metrics.fmt_int(kpis["n_mandis"]),   "emerald", "Reporting Centers", "🏛️"),
        (c2, "Total Inflow Volume", metrics.fmt_qty(kpis["total_volume"]), "emerald", "Quintals Aggregated", "📦"),
        (c3, "Top Volume Mandi",    str(kpis["top_mandi"]),              "sky",     "Highest Inflow Hub", "🏆"),
        (c4, "Dominant District",   str(kpis["top_district"]),           "amber",   "Catchment Hub", "📍"),
    ]
    for col, label, val, variant, delta, icon in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant=variant, delta=delta, icon=icon), unsafe_allow_html=True)

    # ── Top Mandis + District Distribution ───────────────────────────────────
    st.markdown(styles.section_header("Arrival Volume Concentration", "DISTRIBUTION"), unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l:
        top_n = st.slider("Number of mandis to rank", 5, 20, 10, key="mandi_topn")
        st.plotly_chart(charts.create_top_mandis(df, top_n=top_n), width='stretch', config={"displayModeBar": False})
    with c_r:
        st.plotly_chart(charts.create_district_distribution(df), width='stretch', config={"displayModeBar": False})

    # ── Mandi Arrival Trend ───────────────────────────────────────────────────
    st.markdown(styles.section_header("Mandi Arrival Time Series", "HISTORICAL TRENDS"), unsafe_allow_html=True)
    tc1, tc2 = st.columns([2, 1])
    with tc1:
        mandi_opts = ["All"] + sorted(df["mandi_name"].dropna().unique().tolist()) if "mandi_name" in df.columns else ["All"]
        sel_mandi = st.selectbox("Trading Mandi", mandi_opts, key="mandi_trend_mandi")
    with tc2:
        crop_opts = ["All"] + sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else ["All"]
        sel_crop = st.selectbox("Crop Filter", crop_opts, key="mandi_trend_crop")

    trend_df = df.copy()
    if sel_mandi != "All":
        trend_df = trend_df[trend_df["mandi_name"] == sel_mandi]
    if sel_crop != "All":
        trend_df = trend_df[trend_df["crop_name"] == sel_crop]

    if trend_df.empty:
        st.markdown(styles.empty_state("No time-series data available for the chosen Mandi and Crop."), unsafe_allow_html=True)
    else:
        st.plotly_chart(charts.create_mandi_trend(trend_df, sel_mandi, sel_crop),
                        width='stretch', config={"displayModeBar": False})

    # ── Mandi Performance Table ───────────────────────────────────────────────
    st.markdown(styles.section_header("Mandi Operational Performance Summary", "DATA TABLE"), unsafe_allow_html=True)

    perf_cols = {
        "mandi_id": "Mandi ID",
        "mandi_name": "Mandi Name",
        "district": "District",
    }
    agg_dict: dict = {"arrival_quantity_qtl": "sum"}
    if "modal_price" in df.columns:
        agg_dict["modal_price"] = "mean"
    if "msp" in df.columns:
        agg_dict["msp"] = "mean"
    if "price_crash" in df.columns:
        agg_dict["price_crash"] = ["sum", "mean"]

    group_cols = [c for c in ["mandi_id", "mandi_name", "district"] if c in df.columns]
    if not group_cols:
        st.info("Mandi grouping columns not found in the dataset.")
        return

    perf = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # Flatten multi-level columns
    perf.columns = [
        "_".join(c).strip("_") if isinstance(c, tuple) else c
        for c in perf.columns
    ]

    # Rename for display
    rename_map = {
        "arrival_quantity_qtl_sum": "Total Arrivals (Qtl)",
        "arrival_quantity_qtl": "Total Arrivals (Qtl)",
        "modal_price_mean": "Avg Modal Price (₹)",
        "modal_price": "Avg Modal Price (₹)",
        "msp_mean": "Avg MSP (₹)",
        "msp": "Avg MSP (₹)",
        "price_crash_sum": "Price Crash Count",
        "price_crash_mean": "Crash Rate",
        "mandi_id": "Mandi ID",
        "mandi_name": "Mandi Name",
        "district": "District",
    }
    perf = perf.rename(columns={k: v for k, v in rename_map.items() if k in perf.columns})
    raw_sorted = perf.sort_values("Total Arrivals (Qtl)", ascending=False)

    display_perf = raw_sorted.copy()
    if "Crash Rate" in display_perf.columns:
        display_perf["Crash Rate"] = (display_perf["Crash Rate"] * 100).round(1).astype(str) + "%"
    if "Total Arrivals (Qtl)" in display_perf.columns:
        display_perf["Total Arrivals (Qtl)"] = display_perf["Total Arrivals (Qtl)"].map(lambda x: f"{x:,.0f}")
    if "Avg Modal Price (₹)" in display_perf.columns:
        display_perf["Avg Modal Price (₹)"] = display_perf["Avg Modal Price (₹)"].map(
            lambda x: f"₹{x:,.0f}" if not np.isnan(x) else "—"
        )
    if "Avg MSP (₹)" in display_perf.columns:
        display_perf["Avg MSP (₹)"] = display_perf["Avg MSP (₹)"].map(
            lambda x: f"₹{x:,.0f}" if not np.isnan(x) else "—"
        )

    st.dataframe(display_perf, use_container_width=True, hide_index=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        "📥 Download Mandi Performance Data (CSV)",
        data=raw_sorted.to_csv(index=False).encode("utf-8"),
        file_name="mandiflow_mandi_analysis.csv",
        mime="text/csv",
    )
