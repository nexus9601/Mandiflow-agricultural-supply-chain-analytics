"""
filters.py
----------
Centralized filter logic for the MandiFlow dashboard.
apply_filters() is the single entry point — no per-chart filtering.
"""

import pandas as pd
import streamlit as st


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply global filter selections to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset loaded by data_loader.load_data()
    filters : dict
        Keys: date_range, crops, districts, mandis, warehouses

    Returns
    -------
    pd.DataFrame  (filtered copy — never modifies original)
    """
    out = df.copy()

    # ── Date range ────────────────────────────────────────────────────────────
    date_range = filters.get("date_range")
    if date_range and len(date_range) == 2 and "date" in out.columns:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask = out["date"].notna()
        out = out[mask & (out["date"] >= start) & (out["date"] <= end)]

    # ── Crop ─────────────────────────────────────────────────────────────────
    crops = filters.get("crops")
    if crops and len(crops) > 0 and "crop_name" in out.columns:
        out = out[out["crop_name"].isin(crops)]

    # ── District ──────────────────────────────────────────────────────────────
    districts = filters.get("districts")
    if districts and len(districts) > 0 and "district" in out.columns:
        out = out[out["district"].isin(districts)]

    # ── Mandi ─────────────────────────────────────────────────────────────────
    mandis = filters.get("mandis")
    if mandis and len(mandis) > 0 and "mandi_name" in out.columns:
        out = out[out["mandi_name"].isin(mandis)]

    # ── Warehouse (approximated as mandi for this dataset) ────────────────────
    warehouses = filters.get("warehouses")
    if warehouses and len(warehouses) > 0 and "mandi_name" in out.columns:
        out = out[out["mandi_name"].isin(warehouses)]

    return out.reset_index(drop=True)


def is_empty(df: pd.DataFrame) -> bool:
    return df is None or len(df) == 0


def empty_state(message: str = "No data matches the selected filters."):
    """Render a clean empty-state message."""
    st.markdown(
        f"""
        <div style="
            padding: 3rem 2rem;
            text-align: center;
            background: #f8faf7;
            border: 1px dashed #c8d8b4;
            border-radius: 10px;
            color: #6b7c5a;
            font-size: 0.95rem;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌾</div>
            <strong>No data to display</strong><br>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
