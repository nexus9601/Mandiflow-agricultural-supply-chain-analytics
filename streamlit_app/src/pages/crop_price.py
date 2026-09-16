"""MandiFlow – Crop & Price Page"""

import numpy as np
import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, prices_df: pd.DataFrame, filters: dict) -> None:
    st.markdown(styles.page_header(
        "Crop & Price",
        "Analyze crop-level arrivals, modal prices, MSP gaps and price risks.",
    ), unsafe_allow_html=True)

    if df.empty:
        st.markdown(styles.empty_state(), unsafe_allow_html=True)
        return

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpis = metrics.price_kpis(df, prices_df)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    gap_val = kpis["avg_msp_gap"] or 0
    kpi_data = [
        (c1, "Avg Modal Price",   metrics.fmt_inr(kpis["avg_modal_price"]),   "emerald", "Modal Realization"),
        (c2, "Average MSP",       metrics.fmt_inr(kpis["avg_msp"]),           "amber",   "Support Floor"),
        (c3, "Average MSP Gap",   metrics.fmt_inr(kpis["avg_msp_gap"]),
         "danger" if gap_val < 0 else "emerald", "Spread to MSP"),
        (c4, "Crash Instances",   metrics.fmt_int(kpis["price_crash_count"]), "danger",  "Below Floor"),
        (c5, "Price Crash Rate",  metrics.fmt_pct(kpis["price_crash_rate"]),  "amber",   "Risk Percentage"),
        (c6, "Avg Price Spread",  metrics.fmt_inr(kpis["avg_price_spread"]),  "sky",     "Market Volatility"),
    ]
    for col, label, val, variant, delta in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant=variant, delta=delta), unsafe_allow_html=True)

    st.markdown("<hr class='mf-divider'>", unsafe_allow_html=True)

    # ── Chart Row 1 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Price vs MSP Analysis"), unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l:
        st.markdown(
            "<p style='font-family:\"Plus Jakarta Sans\",sans-serif; font-size:0.84rem; "
            "font-weight:700; color:#0f172a; margin:0 0 4px 2px; letter-spacing:-0.01em;'>"
            "Average Modal Price vs MSP by Crop</p>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(charts.create_price_vs_msp_grouped(df),
                        use_container_width=True, config={"displayModeBar": False})
    with c_r:
        st.plotly_chart(charts.create_msp_gap_chart(df),
                        width='stretch', config={"displayModeBar": False})

    # ── Chart Row 2 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Price Risk"), unsafe_allow_html=True)
    c_l2, c_r2 = st.columns(2)
    with c_l2:
        st.plotly_chart(charts.create_price_crash_rate(df),
                        width='stretch', config={"displayModeBar": False})
    with c_r2:
        st.plotly_chart(charts.create_price_spread(df, prices_df),
                        width='stretch', config={"displayModeBar": False})

    # ── Price Trend ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Price Trend"), unsafe_allow_html=True)
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        crop_opts = ["All"] + sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else ["All"]
        trend_crop = st.selectbox("Crop", crop_opts, key="price_trend_crop")
    with fc2:
        mandi_opts = ["All"] + sorted(df["mandi_name"].dropna().unique().tolist()) if "mandi_name" in df.columns else ["All"]
        trend_mandi = st.selectbox("Mandi", mandi_opts, key="price_trend_mandi")

    trend_df = df.copy()
    if trend_crop != "All":
        trend_df = trend_df[trend_df["crop_name"] == trend_crop]
    if trend_mandi != "All":
        trend_df = trend_df[trend_df["mandi_name"] == trend_mandi]

    if trend_df.empty:
        st.markdown(styles.empty_state(), unsafe_allow_html=True)
    else:
        st.plotly_chart(charts.create_price_trend(trend_df, trend_crop, trend_mandi),
                        width='stretch', config={"displayModeBar": False})

    # ── Price Risk Table ──────────────────────────────────────────────────────
    st.markdown(styles.section_header("Price Risk Summary Table"), unsafe_allow_html=True)

    if "price_vs_msp" not in df.columns or "crop_name" not in df.columns:
        st.info("Price risk data unavailable in current dataset.")
    else:
        agg = (
            df.dropna(subset=["modal_price", "msp"])
            .groupby("crop_name")
            .agg(
                Avg_Modal_Price=("modal_price", "mean"),
                Avg_MSP=("msp", "mean"),
                MSP_Gap=("price_vs_msp", "mean"),
                MSP_Gap_Pct=("price_vs_msp_pct", "mean"),
                Crash_Count=("price_crash", "sum"),
                Crash_Rate=("price_crash", "mean"),
            )
            .reset_index()
            .rename(columns={"crop_name": "Crop"})
            .sort_values("MSP_Gap")
        )

        agg["Crash_Rate"] = (agg["Crash_Rate"] * 100).round(1).astype(str) + "%"
        agg["MSP_Gap_Pct"] = agg["MSP_Gap_Pct"].map(lambda x: f"{x:.1f}%" if not np.isnan(x) else "—")
        for col in ["Avg_Modal_Price", "Avg_MSP", "MSP_Gap"]:
            agg[col] = agg[col].map(lambda x: f"₹{x:,.0f}" if not np.isnan(x) else "—")
        agg["Crash_Count"] = agg["Crash_Count"].astype(int)

        agg.columns = ["Crop", "Avg Modal Price", "Avg MSP", "MSP Gap", "MSP Gap %", "Crash Count", "Crash Rate"]
        st.dataframe(agg, width='stretch', hide_index=True)

        # Download summary
        st.download_button(
            "Download Price Summary (CSV)",
            data=agg.to_csv(index=False).encode("utf-8"),
            file_name="mandiflow_price_summary.csv",
            mime="text/csv",
        )

    st.download_button(
        "Download Filtered Data (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="mandiflow_crop_price.csv",
        mime="text/csv",
        key="cp_dl_main",
    )
