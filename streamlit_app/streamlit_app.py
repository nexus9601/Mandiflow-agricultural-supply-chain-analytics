"""
MandiFlow | Agricultural Supply Chain Analytics
================================================
Streamlit entry point.

Run with:
    streamlit run streamlit_app.py
"""

import sys
import os

# Make src importable from this file's directory
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pandas as pd
import streamlit as st

from src import styles
from src.data_loader import (
    load_main_df,
    load_transport_df,
    load_prices_df,
    compute_weather_daily,
)
from src.filters import apply_filters, apply_transport_filters
from src.pages import overview, mandi_analysis, crop_price, transport, weather, data_quality, ai_analytics

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MandiFlow | Agricultural Supply Chain Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Custom CSS ─────────────────────────────────────────────────────────
st.markdown(styles.CUSTOM_CSS, unsafe_allow_html=True)

# ── Load Data (Cached) ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_all():
    main_df = load_main_df()
    transport_df = load_transport_df()
    prices_df = load_prices_df()
    daily_weather = compute_weather_daily(main_df)
    return main_df, transport_df, prices_df, daily_weather


main_df, transport_df, prices_df, daily_weather = _load_all()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand Header
    st.markdown(
        """
<div class="sidebar-brand-box">
  <div class="sidebar-brand-title">🌾 MandiFlow</div>
  <div class="sidebar-brand-subtitle">Agricultural Supply Chain Analytics</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Navigation
    st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Page",
        options=["Overview", "Mandi Analysis", "Crop & Price", "Transport", "Weather Impact", "Data Quality", "AI Analytics ✨"],
        label_visibility="collapsed",
        key="nav_page",
    )

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:1rem 0;'>", unsafe_allow_html=True)

    # ── Global Filters ─────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section-title">Global Filters</div>', unsafe_allow_html=True)

    # Date range
    date_col = "date"
    if date_col in main_df.columns and main_df[date_col].notna().any():
        min_date = main_df[date_col].min().date()
        max_date = main_df[date_col].max().date()
    else:
        from datetime import date
        min_date = date(2026, 1, 1)
        max_date = date(2026, 12, 31)

    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filter_date",
    )
    # Normalise to tuple of two dates
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Crop
    crop_opts = ["All"] + sorted(main_df["crop_name"].dropna().unique().tolist()) if "crop_name" in main_df.columns else ["All"]
    sel_crop = st.selectbox("Commodity / Crop", crop_opts, key="filter_crop")

    # District
    dist_opts = ["All"] + sorted(main_df["district"].dropna().unique().tolist()) if "district" in main_df.columns else ["All"]
    sel_district = st.selectbox("Catchment District", dist_opts, key="filter_district")

    # Mandi (depends on district)
    if sel_district != "All" and "district" in main_df.columns:
        _mandi_pool = main_df[main_df["district"] == sel_district]["mandi_name"].dropna().unique()
    else:
        _mandi_pool = main_df["mandi_name"].dropna().unique() if "mandi_name" in main_df.columns else []
    mandi_opts = ["All"] + sorted(_mandi_pool.tolist())
    sel_mandi = st.selectbox("Trading Mandi", mandi_opts, key="filter_mandi")

    # Warehouse (transport only)
    if not transport_df.empty and "warehouse" in transport_df.columns:
        wh_opts = ["All"] + sorted(transport_df["warehouse"].dropna().unique().tolist())
    else:
        wh_opts = ["All"]
    sel_warehouse = st.selectbox("Logistics Warehouse", wh_opts, key="filter_warehouse")

    # Reset button
    st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
    if st.button("↺ Reset All Filters", key="reset_filters", use_container_width=True):
        st.session_state.update({
            "filter_crop": "All",
            "filter_district": "All",
            "filter_mandi": "All",
            "filter_warehouse": "All",
        })
        st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:1rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"""
<div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 12px;">
  <div style="font-size: 0.62rem; font-weight: 700; color: #6ee7b7; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px; opacity:0.8;">Dataset</div>
  <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
    {len(main_df):,} <span style="font-size: 0.72rem; font-weight: 500; color: #94a3b8;">records</span>
  </div>
  <div style="font-size: 0.67rem; color: #86efac; font-weight: 600; margin-top: 3px;">&#9679; Validated &amp; Harmonized</div>
</div>
""",
        unsafe_allow_html=True,
    )

# ── Apply Filters ─────────────────────────────────────────────────────────────
filters = dict(
    date_range=(start_date, end_date),
    crop=sel_crop,
    district=sel_district,
    mandi=sel_mandi,
)

filtered_df = apply_filters(
    main_df,
    date_range=(start_date, end_date),
    crop=sel_crop if sel_crop != "All" else None,
    district=sel_district if sel_district != "All" else None,
    mandi=sel_mandi if sel_mandi != "All" else None,
)

# Filter transport df (date not available in transport, just warehouse/mandi)
filtered_transport = apply_transport_filters(
    transport_df,
    warehouse=sel_warehouse if sel_warehouse != "All" else None,
)

# ── Empty state guard ─────────────────────────────────────────────────────────
def _show_page(page_name: str) -> None:
    if filtered_df.empty and page_name not in ("Data Quality", "Transport", "Weather Impact", "AI Analytics ✨"):
        st.markdown(
            styles.page_header(page_name, ""),
            unsafe_allow_html=True,
        )
        st.markdown(
            styles.empty_state("No records match the selected filters. Adjust the sidebar filters and try again."),
            unsafe_allow_html=True,
        )
        return

    if page_name == "Overview":
        overview.render(filtered_df, filtered_transport, prices_df)

    elif page_name == "Mandi Analysis":
        mandi_analysis.render(filtered_df, filters)

    elif page_name == "Crop & Price":
        crop_price.render(filtered_df, prices_df, filters)

    elif page_name == "Transport":
        transport.render(filtered_df, filtered_transport)

    elif page_name == "Weather Impact":
        # Weather uses daily aggregation; recompute if date filtered
        weather_to_use = compute_weather_daily(filtered_df) if not filtered_df.empty else daily_weather
        weather.render(filtered_df, weather_to_use)

    elif page_name == "Data Quality":
        data_quality.render(main_df, transport_df)  # always show on full dataset

    elif page_name == "AI Analytics ✨":
        ai_analytics.render(main_df)  # always full dataset for AI queries


_show_page(page)

# ── Methodology Expander ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("About this analysis – Methodology"):
    st.markdown(
        """
<div class="methodology-box">

**MandiFlow | Agricultural Supply Chain Analytics**

This dashboard is built on the cleaned, integrated dataset produced by the project pipeline:

- **Arrival quantities** standardised to quintals (Qtl)
- **Prices** cleaned to numeric INR values (₹); symbols and commas removed
- **Temperatures** converted to Celsius (°C)
- **Rainfall** converted to millimeters (mm)
- **Weather timestamps** normalised to Indian Standard Time (IST)
- **Distances** standardised to kilometers (km)
- **Invalid negative transit values** excluded; calculated transit hours preferred over self-reported
- **Price crash** = Modal Price < MSP (Minimum Support Price)
- **Long transit** = Transit Time > 24 hours
- **MSP gap** = Modal Price − MSP
- **Price spread** = Max Price − Min Price
- **Weather** is aggregated at the daily level; no direct sensor-to-mandi mapping exists in the current schema
- **Correlation** in the Weather Impact page is Pearson correlation of daily rainfall and daily total arrivals.
  Correlation indicates statistical association only — it does not establish causation.

</div>
""",
        unsafe_allow_html=True,
    )
