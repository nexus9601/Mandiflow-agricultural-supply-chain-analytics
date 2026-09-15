"""
MandiFlow Dashboard – Data Loader
Loads and caches the integrated dataset and raw transport CSV.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

def _find_data_file(*subpaths: str) -> str:
    candidates = [
        os.path.join(os.getcwd(), *subpaths),
        os.path.join(os.path.dirname(__file__), "..", *subpaths),
        os.path.join(os.path.dirname(__file__), "..", "..", *subpaths),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", *subpaths))

INTEGRATED_PATH = _find_data_file("Datasets", "Cleaned", "final_integrated_dataset.csv")
TRANSPORT_RAW_PATH = _find_data_file("Datasets", "Raw", "track3_transport_logistics.csv")
PRICES_RAW_PATH = _find_data_file("Datasets", "Raw", "track3_price_and_msp.json")

# ── Numeric columns in the integrated file ────────────────────────────────────
_NUMERIC_COLS = [
    "arrival_quantity_qtl",
    "farmer_count",
    "modal_price",
    "msp",
    "avg_temperature_c",
    "total_rainfall_mm",
    "avg_humidity_percent",
    "avg_distance_km",
    "avg_transit_hours",
    "avg_speed_kmph",
    "transit_delay_rate",
]


@st.cache_data(show_spinner="Loading dataset…")
def load_main_df() -> pd.DataFrame:
    """Load and clean the integrated dataset."""
    df = pd.read_csv(INTEGRATED_PATH, low_memory=False)

    # Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Clean numeric columns
    for col in _NUMERIC_COLS:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.extract(r"([-+]?\d*\.?\d+)")[0]
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived analytics columns -------------------------------------------------

    # Price analytics (only where both prices are present)
    price_mask = df["modal_price"].notna() & df["msp"].notna()
    df["price_vs_msp"] = np.nan
    df["price_vs_msp_pct"] = np.nan
    df["price_crash"] = False

    df.loc[price_mask, "price_vs_msp"] = (
        df.loc[price_mask, "modal_price"] - df.loc[price_mask, "msp"]
    )
    df.loc[price_mask, "price_vs_msp_pct"] = (
        df.loc[price_mask, "price_vs_msp"] / df.loc[price_mask, "msp"] * 100
    )
    df.loc[price_mask, "price_crash"] = (
        df.loc[price_mask, "modal_price"] < df.loc[price_mask, "msp"]
    )

    # Transit analytics  -------------------------------------------------------
    # Use avg_transit_hours as transit_hours_clean (it's the cleaned aggregate)
    df["transit_hours_clean"] = df["avg_transit_hours"].copy()
    # Mask out negative values
    neg_transit = df["transit_hours_clean"] < 0
    df.loc[neg_transit, "transit_hours_clean"] = np.nan

    df["long_transit_flag"] = df["transit_hours_clean"] > 24

    # Distance -----------------------------------------------------------------
    df["distance_km"] = df["avg_distance_km"].copy()
    df.loc[df["distance_km"] < 0, "distance_km"] = np.nan

    # Standardise text columns -------------------------------------------------
    for col in ["crop_name", "mandi_name", "district", "mandi_type"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            df.loc[df[col].isin(["Nan", "None", ""]), col] = np.nan

    return df


@st.cache_data(show_spinner="Loading transport data…")
def load_transport_df() -> pd.DataFrame:
    """Load and clean raw transport logistics for warehouse-level analysis."""
    if not os.path.exists(TRANSPORT_RAW_PATH):
        return pd.DataFrame()

    df = pd.read_csv(TRANSPORT_RAW_PATH, low_memory=False)

    # Parse transit hours
    df["transit_hours"] = pd.to_numeric(df["transit_hours"], errors="coerce")

    # Parse distance to km
    def _to_km(row):
        d = pd.to_numeric(row.get("distance", np.nan), errors="coerce")
        u = str(row.get("distance_unit", "km")).strip().lower()
        if pd.isna(d):
            return np.nan
        if u in ("m", "meter", "meters"):
            return d / 1000
        if u in ("mile", "miles", "mi"):
            return d * 1.60934
        return d  # km

    df["distance_km"] = df.apply(_to_km, axis=1)

    # Parse times
    for col in ["departure_time", "arrival_time"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # Calculated transit hours
    calc = (df["arrival_time"] - df["departure_time"]).dt.total_seconds() / 3600
    df["transit_hours_clean"] = np.where(
        calc.notna() & (calc >= 0), calc,
        np.where(df["transit_hours"].notna() & (df["transit_hours"] >= 0),
                 df["transit_hours"], np.nan)
    )

    df["long_transit_flag"] = df["transit_hours_clean"] > 24

    # Warehouse name cleanup
    if "destination_warehouse" in df.columns:
        df["warehouse"] = (
            df["destination_warehouse"].astype(str).str.strip().str.title()
        )
    else:
        df["warehouse"] = np.nan

    # Mandi id cleanup
    if "mandi_id" in df.columns:
        df["mandi_id"] = df["mandi_id"].astype(str).str.strip().str.upper()

    return df


@st.cache_data(show_spinner="Loading price/MSP data…")
def load_prices_df() -> pd.DataFrame:
    """Load price & MSP data for max/min price spread."""
    if not os.path.exists(PRICES_RAW_PATH):
        return pd.DataFrame()

    import re as _re

    df = pd.read_json(PRICES_RAW_PATH)

    def _clean_price(val) -> float:
        """Strip currency symbols, commas, suffixes; return float or NaN."""
        if pd.isna(val):
            return np.nan
        s = str(val).strip()
        # Remove leading currency markers: ₹, Rs., INR (case-insensitive)
        s = _re.sub(r"^(₹|Rs\.?\s*|INR\s*)", "", s, flags=_re.IGNORECASE)
        # Remove commas and trailing /- or spaces
        s = s.replace(",", "").rstrip("/-").strip()
        try:
            return float(s)
        except ValueError:
            return np.nan

    for col in ["min_price", "max_price", "modal_price", "msp"]:
        if col in df.columns:
            df[col] = df[col].apply(_clean_price)

    # Compute spread only where both are valid and spread is in a sane range (< 100k)
    df["price_spread"] = np.where(
        df["max_price"].notna() & df["min_price"].notna() & (df["max_price"] - df["min_price"] < 100_000),
        df["max_price"] - df["min_price"],
        np.nan,
    )

    for col in ["crop_name"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    return df


@st.cache_data(show_spinner="Computing daily weather aggregation…")
def compute_weather_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weather columns to daily level from the integrated df."""
    weather_cols = [
        c for c in ["avg_temperature_c", "total_rainfall_mm", "avg_humidity_percent"]
        if c in df.columns
    ]
    if not weather_cols or "date" not in df.columns:
        return pd.DataFrame()

    agg = {
        "avg_temperature_c": "mean",
        "total_rainfall_mm": "mean",   # already a daily aggregate per row
        "avg_humidity_percent": "mean",
    }
    agg = {k: v for k, v in agg.items() if k in df.columns}

    daily = (
        df.dropna(subset=["date"])
        .groupby("date", as_index=False)
        .agg(
            **{k: (k, v) for k, v in agg.items()},
            total_arrival_qtl=("arrival_quantity_qtl", "sum"),
        )
    )
    return daily
