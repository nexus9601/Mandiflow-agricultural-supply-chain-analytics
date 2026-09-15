"""
MandiFlow — Agricultural Supply Chain Analytics
================================================
Streamlit dashboard entry point.

Run with:
    streamlit run streamlit_app/mandiflow_app.py

Pages:
    1. Overview
    2. Mandi Analysis
    3. Crop & Price
    4. Transport
    5. Weather Impact
    6. Data Quality
"""

import sys, os

# Allow imports from the project root and streamlit_app dir
_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_APP_DIR, ".."))
for _p in [_APP_DIR, _ROOT_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.data_loader import load_data, get_filter_options
from src.filters    import apply_filters, is_empty, empty_state
from src.metrics    import (
    calc_overview_kpis, calc_price_kpis, calc_transport_kpis,
    calc_weather_kpis, build_insight_facts,
    fmt_qty, fmt_price, fmt_pct, fmt_hrs, fmt_km, fmt_temp, fmt_rain, fmt_humidity,
)
from src.styles import apply_styles, CHART_COLORS, GREEN_PRIMARY, AMBER, RED_SOFT
from src.utils  import (
    render_kpi_row, page_header, section_title, divider, download_csv_button, chart_config,
)
from src import charts


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MandiFlow | Agricultural Supply Chain Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


# ── Load data (cached) ────────────────────────────────────────────────────────
with st.spinner("Loading MandiFlow dataset…"):
    df_raw = load_data()

filter_opts = get_filter_options(df_raw)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-icon">🌾</div>
        <div>
            <div class="sb-brand-name">MandiFlow</div>
            <div class="sb-brand-sub">Agricultural Supply Chain Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Page navigation
    st.markdown('<div class="sb-section-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Page",
        options=[
            "Overview",
            "Mandi Analysis",
            "Crop & Price",
            "Transport",
            "Weather Impact",
            "Data Quality",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<hr style="border-color:#2d4a2d; margin: 1rem 0;">', unsafe_allow_html=True)

    # ── Global Filters ────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-label">Global Filters</div>', unsafe_allow_html=True)

    # Date range
    date_min = filter_opts.get("date_min")
    date_max = filter_opts.get("date_max")
    if date_min and date_max:
        date_range = st.date_input(
            "Date Range",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max,
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            selected_dates = list(date_range)
        else:
            selected_dates = [date_min, date_max]
    else:
        selected_dates = None

    # Crop
    crop_opts = filter_opts.get("crop_name", [])
    selected_crops = st.multiselect("Crop", options=crop_opts, default=[])

    # District
    district_opts = filter_opts.get("district", [])
    selected_districts = st.multiselect("District", options=district_opts, default=[])

    # Mandi
    mandi_opts = filter_opts.get("mandi_name", [])
    selected_mandis = st.multiselect("Mandi", options=mandi_opts, default=[])

    # Warehouse
    warehouse_opts = filter_opts.get("warehouse", [])
    selected_warehouses = st.multiselect("Warehouse", options=warehouse_opts, default=[])

    st.markdown('<hr style="border-color:#2d4a2d; margin: 1rem 0;">', unsafe_allow_html=True)

    # Reset filters
    if st.button("Reset Filters"):
        st.rerun()

    # Record count
    total_records = f"{len(df_raw):,}"
    st.caption(f"Dataset: {total_records} records")


# ── Build active filters dict ─────────────────────────────────────────────────
active_filters = {
    "date_range": selected_dates,
    "crops":      selected_crops  if selected_crops      else None,
    "districts":  selected_districts if selected_districts else None,
    "mandis":     selected_mandis if selected_mandis      else None,
    "warehouses": selected_warehouses if selected_warehouses else None,
}

df = apply_filters(df_raw, active_filters)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if page == "Overview":
    page_header(
        "MandiFlow — Overview",
        "Monitor agricultural arrivals, market prices, MSP performance, logistics and weather conditions.",
    )

    if is_empty(df):
        empty_state("Adjust the filters in the sidebar to see data.")
        st.stop()

    kpis = calc_overview_kpis(df)

    # ── KPI row ───────────────────────────────────────────────────────────────
    render_kpi_row([
        {
            "label": "Total Crop Arrivals",
            "value": fmt_qty(kpis["total_arrivals"]),
        },
        {
            "label": "Avg Modal Price",
            "value": fmt_price(kpis["avg_modal_price"]),
        },
        {
            "label": "Avg MSP",
            "value": fmt_price(kpis["avg_msp"]),
        },
        {
            "label": "Price Crash Instances",
            "value": f"{kpis['price_crash_count']:,}",
            "card_class": "kpi-danger" if kpis["price_crash_count"] > 100 else "",
            "delta": "Records where Modal Price < MSP",
        },
        {
            "label": "Avg Transit Time",
            "value": fmt_hrs(kpis["avg_transit_hrs"]),
        },
        {
            "label": "Long Transit Rate (>24h)",
            "value": fmt_pct(kpis["long_transit_rate"]),
            "card_class": "kpi-warn" if (kpis["long_transit_rate"] or 0) > 30 else "",
            "delta": "Trips exceeding 24 hours",
        },
    ])

    divider()

    # ── Row 1: Arrival trend + Crop distribution ───────────────────────────────
    section_title("Supply & Arrival Patterns")
    col1, col2 = st.columns([3, 2])

    with col1:
        # Crop selector for trend chart
        all_crops = ["All"] + sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else ["All"]
        trend_crop = st.selectbox("Filter trend by crop", all_crops, key="ov_trend_crop")
        fig_trend = charts.create_arrival_trend(df, crop=trend_crop if trend_crop != "All" else None)
        st.plotly_chart(fig_trend, use_container_width=True, config=chart_config())

    with col2:
        fig_crop_dist = charts.create_crop_distribution(df, top_n=12)
        st.plotly_chart(fig_crop_dist, use_container_width=True, config=chart_config())

    # ── Row 2: Top mandis + Price vs MSP ──────────────────────────────────────
    section_title("Market & Mandi Performance")
    col3, col4 = st.columns(2)

    with col3:
        fig_mandis = charts.create_top_mandis(df, top_n=10)
        st.plotly_chart(fig_mandis, use_container_width=True, config=chart_config())

    with col4:
        fig_price_msp = charts.create_price_msp_grouped(df)
        st.plotly_chart(fig_price_msp, use_container_width=True, config=chart_config())

    divider()

    # ── Key Insights card ──────────────────────────────────────────────────────
    section_title("Key Insights")
    facts = build_insight_facts(df)

    insight_items = []
    if "top_arrival_crop" in facts:
        insight_items.append({
            "dot": "",
            "text": f"<strong>{facts['top_arrival_crop']}</strong> leads in total arrivals with {fmt_qty(facts['top_arrival_crop_qty'])}.",
        })
    if "top_mandi" in facts:
        insight_items.append({
            "dot": "",
            "text": f"Highest-volume mandi: <strong>{facts['top_mandi']}</strong> ({fmt_qty(facts['top_mandi_qty'])}).",
        })
    if "worst_msp_gap_crop" in facts:
        insight_items.append({
            "dot": "danger",
            "text": f"<strong>{facts['worst_msp_gap_crop']}</strong> shows the largest average negative MSP gap "
                    f"({fmt_price(facts['worst_msp_gap_val'])} below MSP).",
        })
    if "worst_transit_warehouse" in facts:
        dot = "warn" if facts.get("worst_transit_rate", 0) > 50 else ""
        insight_items.append({
            "dot": dot,
            "text": f"<strong>{facts['worst_transit_warehouse']}</strong> has the highest long-transit rate "
                    f"({fmt_pct(facts.get('worst_transit_rate', 0))}).",
        })

    rows_html = "".join(
        f'<div class="insight-row">'
        f'<div class="insight-dot {it["dot"]}"></div>'
        f'<span>{it["text"]}</span>'
        f'</div>'
        for it in insight_items
    ) if insight_items else "<p style='color:#6b7c5a;font-size:0.85rem;'>Insufficient data for auto-insights with current filters.</p>"

    st.markdown(
        f'<div class="insight-card"><h4>Auto-generated Insights</h4>{rows_html}</div>',
        unsafe_allow_html=True,
    )

    divider()
    download_csv_button(df, "mandiflow_overview.csv", "Download Filtered Data")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MANDI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Mandi Analysis":
    page_header(
        "Mandi Analysis",
        "Compare mandi activity, geographical distribution and arrival volumes.",
    )

    if is_empty(df):
        empty_state()
        st.stop()

    # ── KPI Row ────────────────────────────────────────────────────────────────
    n_mandis = df["mandi_name"].nunique() if "mandi_name" in df.columns else 0
    total_arr = df["arrival_quantity_qtl"].sum() if "arrival_quantity_qtl" in df.columns else 0
    top_mandi_val = (
        df.groupby("mandi_name")["arrival_quantity_qtl"].sum().idxmax()
        if "mandi_name" in df.columns and "arrival_quantity_qtl" in df.columns and len(df) > 0
        else "N/A"
    )
    top_district_val = (
        df.groupby("district")["arrival_quantity_qtl"].sum().idxmax()
        if "district" in df.columns and "arrival_quantity_qtl" in df.columns and len(df) > 0
        else "N/A"
    )

    render_kpi_row([
        {"label": "Active Mandis",        "value": f"{n_mandis:,}"},
        {"label": "Total Arrival Volume", "value": fmt_qty(total_arr)},
        {"label": "Top Mandi",            "value": str(top_mandi_val)},
        {"label": "Top District",         "value": str(top_district_val)},
    ])

    divider()

    # ── Charts row 1 ───────────────────────────────────────────────────────────
    section_title("Volume Distribution")
    col1, col2 = st.columns(2)

    with col1:
        top_n_mandis = st.slider("Show top N mandis", 5, 30, 15, key="mandi_topn")
        fig_top_mandi = charts.create_top_mandis(df, top_n=top_n_mandis)
        st.plotly_chart(fig_top_mandi, use_container_width=True, config=chart_config())

    with col2:
        fig_district = charts.create_district_arrivals(df, top_n=20)
        st.plotly_chart(fig_district, use_container_width=True, config=chart_config())

    divider()

    # ── Mandi arrival trend ────────────────────────────────────────────────────
    section_title("Mandi Arrival Trend")
    col_m, col_c = st.columns(2)

    with col_m:
        mandi_list = sorted(df["mandi_name"].dropna().unique().tolist()) if "mandi_name" in df.columns else []
        sel_mandi = st.selectbox("Select Mandi", ["All"] + mandi_list, key="mandi_sel")

    with col_c:
        crop_list = sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else []
        sel_crop_m = st.selectbox("Select Crop", ["All"] + crop_list, key="mandi_crop_sel")

    fig_trend = charts.create_mandi_trend(
        df,
        mandi=sel_mandi if sel_mandi != "All" else None,
        crop=sel_crop_m if sel_crop_m != "All" else None,
    )
    st.plotly_chart(fig_trend, use_container_width=True, config=chart_config())

    divider()

    # ── Mandi Performance Table ────────────────────────────────────────────────
    section_title("Mandi Performance Summary")

    if "mandi_name" in df.columns:
        grp_cols = {"arrival_quantity_qtl": "sum", "modal_price": "mean", "msp": "mean"}
        avail_grp = {k: v for k, v in grp_cols.items() if k in df.columns}

        if avail_grp:
            perf = df.groupby("mandi_name").agg(**{k: (k, v) for k, v in avail_grp.items()}).reset_index()
            perf.columns = ["Mandi"] + list(avail_grp.keys())

            if "mandi_id" in df.columns:
                id_map = df.groupby("mandi_name")["mandi_id"].first()
                perf["Mandi ID"] = perf["Mandi"].map(id_map)

            if "district" in df.columns:
                d_map = df.groupby("mandi_name")["district"].first()
                perf["District"] = perf["Mandi"].map(d_map)

            if "price_crash" in df.columns:
                crash_grp = df.groupby("mandi_name")["price_crash"].agg(["sum", "mean"])
                perf["Price Crash Count"] = perf["Mandi"].map(crash_grp["sum"]).astype(int)
                perf["Price Crash Rate"] = perf["Mandi"].map(crash_grp["mean"]) * 100

            # Rename and format
            rename_map = {
                "arrival_quantity_qtl": "Total Arrivals (Qtl)",
                "modal_price": "Avg Modal Price (₹)",
                "msp": "Avg MSP (₹)",
            }
            perf = perf.rename(columns=rename_map)
            perf = perf.sort_values("Total Arrivals (Qtl)", ascending=False)

            st.dataframe(
                perf.style.format({
                    "Total Arrivals (Qtl)": "{:,.0f}",
                    "Avg Modal Price (₹)": "₹{:,.0f}",
                    "Avg MSP (₹)": "₹{:,.0f}",
                    "Price Crash Rate": "{:.1f}%",
                    "Price Crash Count": "{:,.0f}",
                }),
                use_container_width=True,
                height=420,
            )
            download_csv_button(perf, "mandi_performance.csv", "Download Mandi Summary")
    else:
        st.info("Mandi name column not found in dataset.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CROP & PRICE
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Crop & Price":
    page_header(
        "Crop & Price Analysis",
        "Analyze crop-level arrivals, modal prices, MSP gaps and price risks.",
    )

    if is_empty(df):
        empty_state()
        st.stop()

    kpis = calc_price_kpis(df)

    # ── KPI row ────────────────────────────────────────────────────────────────
    msp_gap_class = "kpi-danger" if (kpis.get("avg_msp_gap") or 0) < -200 else (
        "kpi-warn" if (kpis.get("avg_msp_gap") or 0) < 0 else ""
    )
    render_kpi_row([
        {"label": "Avg Modal Price",    "value": fmt_price(kpis["avg_modal_price"])},
        {"label": "Avg MSP",            "value": fmt_price(kpis["avg_msp"])},
        {
            "label": "Avg MSP Gap",
            "value": fmt_price(kpis["avg_msp_gap"]),
            "card_class": msp_gap_class,
            "delta": "Modal Price − MSP",
        },
        {
            "label": "Price Crash Count",
            "value": f"{kpis['price_crash_count']:,}",
            "card_class": "kpi-danger" if kpis["price_crash_count"] > 50 else "",
        },
        {
            "label": "Price Crash Rate",
            "value": fmt_pct(kpis["price_crash_rate"]),
            "card_class": "kpi-danger" if (kpis.get("price_crash_rate") or 0) > 30 else "",
        },
        {
            "label": "Avg Price Spread",
            "value": fmt_price(kpis["avg_price_spread"]),
            "delta": "Max − Min Price",
        },
    ])

    divider()

    # ── Row 1: Price vs MSP + MSP Gap ─────────────────────────────────────────
    section_title("Price vs MSP Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(charts.create_price_msp_grouped(df), use_container_width=True, config=chart_config())

    with col2:
        st.plotly_chart(charts.create_msp_gap_chart(df), use_container_width=True, config=chart_config())

    divider()

    # ── Row 2: Price crash rate + Spread ──────────────────────────────────────
    section_title("Price Risk")
    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(charts.create_price_crash_rate(df), use_container_width=True, config=chart_config())

    with col4:
        st.plotly_chart(charts.create_price_spread(df), use_container_width=True, config=chart_config())

    divider()

    # ── Price trend (interactive) ──────────────────────────────────────────────
    section_title("Price Trend Over Time")
    col_pt1, col_pt2 = st.columns(2)

    with col_pt1:
        crops_list = sorted(df["crop_name"].dropna().unique().tolist()) if "crop_name" in df.columns else []
        sel_crop_pt = st.selectbox("Crop", ["All"] + crops_list, key="pt_crop")

    with col_pt2:
        mandis_list = sorted(df["mandi_name"].dropna().unique().tolist()) if "mandi_name" in df.columns else []
        sel_mandi_pt = st.selectbox("Mandi", ["All"] + mandis_list, key="pt_mandi")

    fig_pt = charts.create_price_trend(
        df,
        crop=sel_crop_pt if sel_crop_pt != "All" else None,
        mandi=sel_mandi_pt if sel_mandi_pt != "All" else None,
    )
    st.plotly_chart(fig_pt, use_container_width=True, config=chart_config())

    divider()

    # ── Price Risk Table ───────────────────────────────────────────────────────
    section_title("Price Risk by Crop")

    if "crop_name" in df.columns and "modal_price" in df.columns:
        price_grp = df.groupby("crop_name").agg(
            avg_modal=("modal_price", "mean"),
            avg_msp=("msp", "mean") if "msp" in df.columns else ("modal_price", "count"),
        )

        if "price_vs_msp" in df.columns:
            price_grp["msp_gap"]     = df.groupby("crop_name")["price_vs_msp"].mean()
            price_grp["msp_gap_pct"] = df.groupby("crop_name")["price_vs_msp_pct"].mean()

        if "price_crash" in df.columns:
            price_grp["crash_count"] = df.groupby("crop_name")["price_crash"].sum()
            price_grp["crash_rate"]  = df.groupby("crop_name")["price_crash"].mean() * 100

        price_grp = price_grp.reset_index().rename(columns={
            "crop_name":  "Crop",
            "avg_modal":  "Avg Modal Price (₹)",
            "avg_msp":    "Avg MSP (₹)",
            "msp_gap":    "MSP Gap (₹)",
            "msp_gap_pct":"MSP Gap (%)",
            "crash_count":"Crash Count",
            "crash_rate": "Crash Rate (%)",
        })

        fmt_dict = {
            "Avg Modal Price (₹)": "₹{:,.0f}",
            "Avg MSP (₹)": "₹{:,.0f}",
        }
        if "MSP Gap (₹)" in price_grp.columns:
            fmt_dict["MSP Gap (₹)"] = "₹{:,.0f}"
            fmt_dict["MSP Gap (%)"] = "{:.1f}%"
        if "Crash Rate (%)" in price_grp.columns:
            fmt_dict["Crash Rate (%)"] = "{:.1f}%"

        price_grp_sorted = price_grp.sort_values("Avg Modal Price (₹)", ascending=False)

        st.dataframe(
            price_grp_sorted.style.format(fmt_dict),
            use_container_width=True,
            height=400,
        )
        download_csv_button(price_grp_sorted, "crop_price_risk.csv", "Download Price Risk Table")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — TRANSPORT
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Transport":
    page_header(
        "Transport & Logistics",
        "Monitor transportation efficiency, travel distance and long-transit routes.",
    )

    if is_empty(df):
        empty_state()
        st.stop()

    kpis = calc_transport_kpis(df)

    # ── KPI row ────────────────────────────────────────────────────────────────
    render_kpi_row([
        {"label": "Total Records",           "value": f"{kpis['total_trips']:,}"},
        {"label": "Avg Transit Time",        "value": fmt_hrs(kpis["avg_transit_hrs"])},
        {"label": "Avg Distance",            "value": fmt_km(kpis["avg_distance_km"])},
        {
            "label": "Long Transit Rate (>24h)",
            "value": fmt_pct(kpis["long_transit_rate"]),
            "card_class": "kpi-danger" if (kpis.get("long_transit_rate") or 0) > 30 else "kpi-warn",
        },
        {"label": "Longest Route (Avg km)", "value": fmt_km(kpis["max_distance_km"])},
        {"label": "Highest Volume Mandi",   "value": str(kpis["highest_vol_warehouse"])},
    ])

    divider()

    # ── Charts row 1 ───────────────────────────────────────────────────────────
    section_title("Transit Time Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(charts.create_transit_by_warehouse(df), use_container_width=True, config=chart_config())

    with col2:
        st.plotly_chart(charts.create_transit_distribution(df), use_container_width=True, config=chart_config())

    divider()

    # ── Charts row 2 ───────────────────────────────────────────────────────────
    section_title("Distance & Volume")
    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(charts.create_distance_by_warehouse(df), use_container_width=True, config=chart_config())

    with col4:
        st.plotly_chart(charts.create_warehouse_volume(df), use_container_width=True, config=chart_config())

    divider()

    # ── Route Performance Table ────────────────────────────────────────────────
    section_title("Mandi-to-Warehouse Route Performance")

    route_cols = {"avg_distance_km": "mean", "transit_hours_clean": "mean", "long_transit_flag": ["sum", "mean"]}
    avail_route = {k: v for k, v in route_cols.items() if k in df.columns}

    if "mandi_name" in df.columns and avail_route:
        agg_spec = {}
        for col, func in avail_route.items():
            if isinstance(func, list):
                for f in func:
                    agg_spec[f"{col}_{f}"] = (col, f)
            else:
                agg_spec[col] = (col, func)

        agg_spec["trip_count"] = ("arrival_quantity_qtl", "count") if "arrival_quantity_qtl" in df.columns else ("mandi_name", "count")

        route_perf = df.groupby("mandi_name").agg(**agg_spec).reset_index()
        route_perf.columns = [c.replace("transit_hours_clean", "transit").replace("long_transit_flag_", "lt_") for c in route_perf.columns]

        rename_rt = {
            "mandi_name": "Mandi / Warehouse",
            "avg_distance_km": "Avg Distance (km)",
            "transit": "Avg Transit (hrs)",
            "lt_sum": "Long Transit Count",
            "lt_mean": "Long Transit Rate",
            "trip_count": "Trip Count",
        }
        route_perf = route_perf.rename(columns=rename_rt)

        if "Long Transit Rate" in route_perf.columns:
            route_perf["Long Transit Rate"] = route_perf["Long Transit Rate"] * 100
            route_perf = route_perf.sort_values("Long Transit Rate", ascending=False)

        fmt_rt = {}
        if "Avg Distance (km)" in route_perf.columns:
            fmt_rt["Avg Distance (km)"] = "{:.1f}"
        if "Avg Transit (hrs)" in route_perf.columns:
            fmt_rt["Avg Transit (hrs)"] = "{:.1f}"
        if "Long Transit Rate" in route_perf.columns:
            fmt_rt["Long Transit Rate"] = "{:.1f}%"

        st.dataframe(route_perf.style.format(fmt_rt), use_container_width=True, height=380)
        download_csv_button(route_perf, "route_performance.csv", "Download Route Performance")

    divider()

    # ── Logistics Risk section ─────────────────────────────────────────────────
    section_title("Logistics Risk Highlights")

    risk_items = []

    if "mandi_name" in df.columns and "long_transit_flag" in df.columns:
        lt_by_mandi = df.groupby("mandi_name")["long_transit_flag"].mean()
        if len(lt_by_mandi) > 0:
            worst_route = lt_by_mandi.idxmax()
            worst_rate  = lt_by_mandi.max() * 100
            risk_items.append({
                "dot": "danger",
                "text": f"<strong>{worst_route}</strong> has the highest long-transit rate: {fmt_pct(worst_rate)}.",
            })

    if "mandi_name" in df.columns and "arrival_quantity_qtl" in df.columns:
        vol_by_mandi = df.groupby("mandi_name")["arrival_quantity_qtl"].sum()
        if len(vol_by_mandi) > 0:
            top_vol_mandi = vol_by_mandi.idxmax()
            risk_items.append({
                "dot": "",
                "text": f"<strong>{top_vol_mandi}</strong> receives the highest crop volume: {fmt_qty(vol_by_mandi.max())}.",
            })

    if "mandi_name" in df.columns and "transit_hours_clean" in df.columns:
        avg_trans_by_mandi = df.groupby("mandi_name")["transit_hours_clean"].mean()
        if len(avg_trans_by_mandi) > 0:
            worst_transit_mandi = avg_trans_by_mandi.idxmax()
            risk_items.append({
                "dot": "warn",
                "text": f"<strong>{worst_transit_mandi}</strong> has the highest average transit time: "
                        f"{fmt_hrs(avg_trans_by_mandi.max())}.",
            })

    if risk_items:
        rows_html = "".join(
            f'<div class="insight-row">'
            f'<div class="insight-dot {it["dot"]}"></div>'
            f'<span>{it["text"]}</span>'
            f'</div>'
            for it in risk_items
        )
        st.markdown(
            f'<div class="insight-card"><h4>Risk Highlights</h4>{rows_html}</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — WEATHER IMPACT
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Weather Impact":
    page_header(
        "Weather Impact Analysis",
        "Explore relationships between weather conditions and agricultural arrivals.",
    )

    if is_empty(df):
        empty_state()
        st.stop()

    weather_available = any(c in df.columns for c in ["avg_temperature_c", "total_rainfall_mm", "avg_humidity_percent"])

    if not weather_available:
        st.info("Weather data columns are not available in the filtered dataset.")
        st.stop()

    kpis = calc_weather_kpis(df)

    # ── KPI row ────────────────────────────────────────────────────────────────
    corr_str = f"{kpis['rain_arrival_corr']:.3f}" if not pd.isna(kpis.get("rain_arrival_corr", float("nan"))) else "N/A"
    render_kpi_row([
        {"label": "Avg Temperature",               "value": fmt_temp(kpis["avg_temp"])},
        {"label": "Total Rainfall",                "value": fmt_rain(kpis["total_rainfall"])},
        {"label": "Avg Humidity",                  "value": fmt_humidity(kpis["avg_humidity"])},
        {
            "label": "Rainfall-Arrival Correlation",
            "value": corr_str,
            "delta": "Association, not causation",
        },
    ])

    divider()

    # ── Rainfall & arrivals dual-axis ──────────────────────────────────────────
    section_title("Rainfall and Crop Arrivals")
    st.plotly_chart(charts.create_rainfall_arrival_trend(df), use_container_width=True, config=chart_config())

    # ── Rainfall scatter ──────────────────────────────────────────────────────
    section_title("Rainfall vs Arrivals Relationship")
    st.plotly_chart(charts.create_rainfall_scatter(df), use_container_width=True, config=chart_config())

    divider()

    # ── Temperature and Humidity ───────────────────────────────────────────────
    section_title("Temperature & Humidity Conditions")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(charts.create_temperature_trend(df), use_container_width=True, config=chart_config())

    with col2:
        st.plotly_chart(charts.create_humidity_trend(df), use_container_width=True, config=chart_config())

    divider()

    # ── Weather Summary Facts ─────────────────────────────────────────────────
    section_title("Weather Impact Summary")

    summary_items = []
    if "date" in df.columns and "total_rainfall_mm" in df.columns:
        daily_rain = df.dropna(subset=["date"]).groupby("date")["total_rainfall_mm"].mean()
        if len(daily_rain) > 0:
            rainiest_day = daily_rain.idxmax().strftime("%d %b %Y")
            summary_items.append({
                "dot": "",
                "text": f"Rainiest day: <strong>{rainiest_day}</strong> ({daily_rain.max():.1f} mm).",
            })

    if "date" in df.columns and "arrival_quantity_qtl" in df.columns:
        daily_arr = df.dropna(subset=["date"]).groupby("date")["arrival_quantity_qtl"].sum()
        if len(daily_arr) > 0:
            highest_arr_day = daily_arr.idxmax().strftime("%d %b %Y")
            lowest_arr_day  = daily_arr.idxmin().strftime("%d %b %Y")
            summary_items.append({
                "dot": "",
                "text": f"Highest arrival day: <strong>{highest_arr_day}</strong> ({fmt_qty(daily_arr.max())}).",
            })
            summary_items.append({
                "dot": "warn",
                "text": f"Lowest arrival day: <strong>{lowest_arr_day}</strong> ({fmt_qty(daily_arr.min())}).",
            })

    if not pd.isna(kpis.get("rain_arrival_corr", float("nan"))):
        c = kpis["rain_arrival_corr"]
        direction = "positive" if c > 0 else "negative"
        strength  = "strong" if abs(c) > 0.5 else "moderate" if abs(c) > 0.3 else "weak"
        summary_items.append({
            "dot": "",
            "text": f"Rainfall-arrival correlation: <strong>{c:.3f}</strong> ({strength} {direction} association). "
                    f"Note: correlation indicates association, not causation.",
        })

    if summary_items:
        rows_html = "".join(
            f'<div class="insight-row">'
            f'<div class="insight-dot {it["dot"]}"></div>'
            f'<span>{it["text"]}</span>'
            f'</div>'
            for it in summary_items
        )
        st.markdown(
            f'<div class="insight-card"><h4>Summary</h4>{rows_html}</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Data Quality":
    page_header(
        "Data Quality",
        "Transparency report: missing values, invalid records, and quality checks across all datasets.",
    )

    df_full = df_raw  # Always show full dataset quality, not filtered

    # ── Quality checks ────────────────────────────────────────────────────────
    def _count_missing(col: str) -> int:
        return int(df_full[col].isna().sum()) if col in df_full.columns else -1

    def _count_negative(col: str) -> int:
        if col not in df_full.columns:
            return -1
        return int((df_full[col].dropna() < 0).sum())

    def _status(count: int, warn_threshold: int = 50, crit_threshold: int = 500) -> str:
        if count < 0:
            return "N/A"
        if count == 0:
            return '<span class="status-good">Good</span>'
        if count < warn_threshold:
            return '<span class="status-good">Good</span>'
        if count < crit_threshold:
            return '<span class="status-warn">Warning</span>'
        return '<span class="status-critical">Critical</span>'

    checks = [
        ("Arrivals",    "Missing Arrival Dates",          _count_missing("date")),
        ("Arrivals",    "Missing Arrival Quantity (Qtl)", _count_missing("arrival_quantity_qtl")),
        ("Prices",      "Missing Modal Prices",           _count_missing("modal_price")),
        ("Prices",      "Missing MSP Values",             _count_missing("msp")),
        ("Weather",     "Missing Temperature",            _count_missing("avg_temperature_c")),
        ("Weather",     "Missing Rainfall",               _count_missing("total_rainfall_mm")),
        ("Weather",     "Missing Humidity",               _count_missing("avg_humidity_percent")),
        ("Transport",   "Missing Transit Hours",          _count_missing("avg_transit_hours")),
        ("Transport",   "Missing Distance (km)",          _count_missing("avg_distance_km")),
        ("Transport",   "Negative Transit Hours",         _count_negative("avg_transit_hours")),
        ("Transport",   "Negative Distance (km)",         _count_negative("avg_distance_km")),
        ("Arrivals",    "Negative Arrival Quantities",    _count_negative("arrival_quantity_qtl")),
    ]

    # ── KPI cards for top checks ───────────────────────────────────────────────
    missing_arrivals    = _count_missing("date")
    missing_price       = _count_missing("modal_price")
    missing_weather     = _count_missing("avg_temperature_c")
    negative_transit    = _count_negative("avg_transit_hours")
    total_records_full  = len(df_full)

    render_kpi_row([
        {
            "label": "Total Records",
            "value": f"{total_records_full:,}",
        },
        {
            "label": "Missing Arrival Dates",
            "value": f"{missing_arrivals:,}",
            "card_class": "kpi-danger" if missing_arrivals > 500 else "kpi-warn" if missing_arrivals > 50 else "",
        },
        {
            "label": "Missing Modal Prices",
            "value": f"{missing_price:,}",
            "card_class": "kpi-danger" if missing_price > 500 else "kpi-warn" if missing_price > 50 else "",
        },
        {
            "label": "Missing Weather Data",
            "value": f"{missing_weather:,}",
            "card_class": "kpi-warn" if missing_weather > 50 else "",
        },
        {
            "label": "Negative Transit Records",
            "value": f"{negative_transit:,}",
            "card_class": "kpi-danger" if negative_transit > 100 else "kpi-warn" if negative_transit > 0 else "",
        },
    ])

    divider()

    # ── Quality table ──────────────────────────────────────────────────────────
    section_title("Detailed Quality Checks")

    table_rows = []
    for dataset, check_name, count in checks:
        if count < 0:
            count_str = "N/A"
            status_html = "N/A"
        else:
            count_str = f"{count:,}"
            status_html = _status(count)
        table_rows.append({
            "Dataset": dataset,
            "Quality Check": check_name,
            "Invalid / Missing": count_str,
            "Status": status_html,
        })

    quality_df = pd.DataFrame(table_rows)
    st.markdown(
        quality_df.to_html(escape=False, index=False, classes=""),
        unsafe_allow_html=True,
    )

    divider()

    # ── Column coverage ────────────────────────────────────────────────────────
    section_title("Column Completeness")

    numeric_cols = df_full.select_dtypes(include="number").columns.tolist()
    coverage_data = []
    for col in df_full.columns:
        total = len(df_full)
        non_null = df_full[col].notna().sum()
        pct = (non_null / total * 100) if total > 0 else 0
        coverage_data.append({
            "Column": col,
            "Non-null Count": f"{non_null:,}",
            "Coverage": f"{pct:.1f}%",
        })

    cov_df = pd.DataFrame(coverage_data)
    st.dataframe(cov_df, use_container_width=True, height=400)

    divider()

    # ── Missing values visual ──────────────────────────────────────────────────
    section_title("Missing Values by Column")

    missing_counts = df_full.isna().sum()
    missing_counts = missing_counts[missing_counts > 0].sort_values(ascending=True)

    if len(missing_counts) > 0:
        import plotly.graph_objects as go2
        fig_missing = go2.Figure(go2.Bar(
            y=missing_counts.index,
            x=missing_counts.values,
            orientation="h",
            marker_color=[RED_SOFT if v > 500 else AMBER if v > 50 else GREEN_PRIMARY for v in missing_counts.values],
            hovertemplate="<b>%{y}</b><br>Missing: %{x:,}<extra></extra>",
        ))

        from src.styles import PLOTLY_LAYOUT
        layout = dict(PLOTLY_LAYOUT)
        layout.update({
            "height": max(250, len(missing_counts) * 30),
            "title": dict(text="Missing Values per Column", font=dict(size=14, color="#1e4d2b"), x=0),
            "margin": dict(l=180, r=30, t=50, b=40),
        })
        fig_missing.update_layout(**layout)
        fig_missing.update_xaxes(title_text="Missing Count")
        fig_missing.update_yaxes(title_text="")

        st.plotly_chart(fig_missing, use_container_width=True, config=chart_config())
    else:
        st.success("No missing values detected in the dataset.")


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER — Methodology
# ══════════════════════════════════════════════════════════════════════════════

divider()

with st.expander("About this Analysis & Methodology"):
    st.markdown("""
    **Data Preparation**
    - Arrival quantities standardized to quintals (Qtl)
    - Prices cleaned and converted to numeric INR values (₹/Qtl)
    - Temperatures converted to Celsius (°C)
    - Rainfall converted to millimeters (mm)
    - Weather timestamps normalized to IST (UTC+5:30)
    - Distances standardized to kilometers (km)
    - Invalid negative transit values replaced with NaN

    **Derived Metrics**
    - **Price Crash**: `modal_price < msp` — indicates the market price fell below the minimum support price
    - **MSP Gap**: `modal_price − msp` — positive means above MSP, negative means below MSP
    - **MSP Gap %**: `(modal_price − msp) / msp × 100`
    - **Long Transit**: `transit_hours_clean > 24` — trips exceeding 24 hours
    - **Price Spread**: `max_price − min_price` (where available)

    **Weather Aggregation**
    Weather observations are aggregated at the daily level:
    average temperature (°C), total rainfall (mm), average humidity (%).
    The current dataset does not include a direct sensor-to-mandi mapping;
    weather data is used at an aggregate daily level.

    **Correlation Disclaimer**
    All correlation coefficients indicate statistical association between variables.
    Correlation does not establish or imply causation.

    **Source Data**
    MandiFlow uses the integrated analytical dataset generated by the project pipeline
    from APMC mandi arrival records, wholesale price data, MSP schedules,
    mandi/district master data, weather sensor observations, and transport logistics records.
    """)

st.markdown(
    '<div style="text-align:center;color:#9aab8a;font-size:0.78rem;padding:1rem 0 0.5rem;">'
    'MandiFlow · Agricultural Supply Chain Analytics · Built with Streamlit & Plotly'
    '</div>',
    unsafe_allow_html=True,
)
