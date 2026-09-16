"""
MandiFlow | Agricultural Supply Chain Analytics
================================================
Modernized executive dashboard entry point.

Run with:
    streamlit run streamlit_app.py
"""

import sys
import os

# Make src and project root importable from this file's directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_HERE, _PARENT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

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
  <div class="sidebar-brand-subtitle">Agricultural Supply Chain Intelligence</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Navigation – Categorized, high-contrast native buttons
    NAV_SECTIONS = [
        ("Core Market Discovery", [
            ("🏠", "Overview"),
            ("📊", "Mandi Analysis"),
            ("💰", "Crop & Price"),
        ]),
        ("Logistics & Climate", [
            ("🚛", "Transport"),
            ("🌦️", "Weather Impact"),
        ]),
        ("Data & AI Intelligence", [
            ("🔍", "Data Quality"),
            ("✨", "AI Analytics ✨"),
        ]),
    ]
    ALL_PAGES = [
        ("🏠", "Overview"),
        ("📊", "Mandi Analysis"),
        ("💰", "Crop & Price"),
        ("🚛", "Transport"),
        ("🌦️", "Weather Impact"),
        ("🔍", "Data Quality"),
        ("✨", "AI Analytics ✨"),
    ]
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Overview"

    for section_label, pages in NAV_SECTIONS:
        st.markdown(f'<div class="sidebar-section-title">{section_label}</div>', unsafe_allow_html=True)
        for icon, label in pages:
            is_active = (st.session_state["nav_page"] == label)
            if st.button(
                f"{icon}  {label}",
                key=f"sb_nav_{label}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["nav_page"] = label
                st.rerun()

    page = st.session_state["nav_page"]

    # ── Global Filters ─────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section-title">Global Dimensions</div>', unsafe_allow_html=True)

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
    st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
    if st.button("↺ Reset All Filters", key="reset_filters", use_container_width=True):
        st.session_state.update({
            "filter_crop": "All",
            "filter_district": "All",
            "filter_mandi": "All",
            "filter_warehouse": "All",
        })
        st.rerun()

    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 14px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);">
  <div class="mf-live-pulse-badge" style="margin-bottom: 6px;">
    <span class="pulse-dot"></span> Live Data Feed
  </div>
  <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 800; color: #0f172a;">
    {len(main_df):,} <span style="font-size: 0.74rem; font-weight: 600; color: #64748b;">Records</span>
  </div>
  <div style="font-size: 0.72rem; color: #059669; font-weight: 700; margin-top: 4px;">✓ Harmonized &amp; Verified</div>
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
            styles.empty_state("No records match the selected filters. Broaden your date range or reset filters."),
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
        weather_to_use = compute_weather_daily(filtered_df) if not filtered_df.empty else daily_weather
        weather.render(filtered_df, weather_to_use)

    elif page_name == "Data Quality":
        data_quality.render(main_df, transport_df)

    elif page_name == "AI Analytics ✨":
        ai_analytics.render(main_df)


# ── Top Hero Bar ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="mf-hero-bar">
  <div class="mf-hero-brand">
    <span class="mf-hero-logo">🌾 MandiFlow</span>
    <span class="mf-live-pulse-badge"><span class="pulse-dot"></span> Live Pipeline • 591K Records</span>
  </div>
  <div class="mf-current-module-badge">
    Active Workspace: <strong>{page}</strong>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Top Module Navigation Pills ───────────────────────────────────────────────
st.markdown('<div class="top-menu-bar-container">', unsafe_allow_html=True)
top_cols = st.columns(len(ALL_PAGES))
for idx, (icon, label) in enumerate(ALL_PAGES):
    is_active = (page == label)
    short_label = label.replace(" ✨", "")
    with top_cols[idx]:
        if st.button(
            f"{icon} {short_label}",
            key=f"topbar_nav_{label}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state["nav_page"] = label
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Active Filters Breadcrumb (if any filter is active)
active_filter_tags = []
if sel_crop != "All":
    active_filter_tags.append(f"Crop: <b>{sel_crop}</b>")
if sel_district != "All":
    active_filter_tags.append(f"District: <b>{sel_district}</b>")
if sel_mandi != "All":
    active_filter_tags.append(f"Mandi: <b>{sel_mandi}</b>")
if sel_warehouse != "All":
    active_filter_tags.append(f"Warehouse: <b>{sel_warehouse}</b>")

if active_filter_tags:
    st.markdown(
        f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 6px 12px;">
  <span style="font-size: 0.72rem; font-weight: 700; color: #047857; text-transform: uppercase;">Active Filters:</span>
  {' '.join(f'<span style="background: #ffffff; border: 1px solid #bbf7d0; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; color: #065f46;">{tag}</span>' for tag in active_filter_tags)}
</div>
""",
        unsafe_allow_html=True,
    )

# ── Page Content ──────────────────────────────────────────────────────────────
_show_page(page)

# ── Methodology Expander ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("ℹ️ About MandiFlow Architecture & Methodology"):
    st.markdown(
        """
<div class="insight-card" style="margin-top: 0.5rem;">
  <h4>Data Architecture & Standardization Methodology</h4>
  <p style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
    This executive intelligence platform operates upon harmonized, integrated agricultural supply chain data streams:
  </p>
  <ul style="font-size: 0.84rem; color: #334155; line-height: 1.7; margin-left: 1.2rem;">
    <li><strong>Standardized Units:</strong> Arrival volumes normalized to Quintals (Qtl); distances in kilometers (km); temperatures in Celsius (°C); rainfall in millimeters (mm).</li>
    <li><strong>Realization Pricing:</strong> Prices cleansed to numeric INR (₹) values with currency symbol artifacts and outliers removed.</li>
    <li><strong>Parity Analytics:</strong> MSP Gap = Modal Price − MSP floor. Price crash occurs when realized Modal Price breaches below guaranteed MSP.</li>
    <li><strong>Transit &amp; Speed:</strong> Calculated transit hours derived from timestamps with negative values filtered; speeds in km/h. Long transit threshold flagged at >24 hours.</li>
    <li><strong>Agro-Climatic Integration:</strong> Daily temporal aggregation joins atmospheric readings with physical mandi receipts.</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
