"""
metrics.py
----------
Reusable KPI calculation functions for MandiFlow dashboard.
All functions accept a filtered DataFrame and return scalar values or dicts.
"""

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────────────────────────────────────

def fmt_qty(val: float) -> str:
    """Format arrival quantity in Qtl. Shows M for millions."""
    if pd.isna(val):
        return "N/A"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.2f} M Qtl"
    if val >= 1_000:
        return f"{val:,.0f} Qtl"
    return f"{val:.1f} Qtl"


def fmt_price(val: float) -> str:
    """Format price in INR with rupee symbol."""
    if pd.isna(val):
        return "N/A"
    return f"₹{val:,.0f}"


def fmt_pct(val: float) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:.2f}%"


def fmt_hrs(val: float) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:.1f} hrs"


def fmt_km(val: float) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:.1f} km"


def fmt_temp(val: float) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:.1f} °C"


def fmt_rain(val: float) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:.1f} mm"


def fmt_humidity(val: float) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:.1f}%"


# ──────────────────────────────────────────────────────────────────────────────
# KPI calculations
# ──────────────────────────────────────────────────────────────────────────────

def calc_overview_kpis(df: pd.DataFrame) -> dict:
    """Calculate all KPIs for the Overview page."""
    kpis = {}

    # Total crop arrivals
    if "arrival_quantity_qtl" in df.columns:
        kpis["total_arrivals"] = df["arrival_quantity_qtl"].sum()
    else:
        kpis["total_arrivals"] = np.nan

    # Average modal price
    if "modal_price" in df.columns:
        kpis["avg_modal_price"] = df["modal_price"].mean()
    else:
        kpis["avg_modal_price"] = np.nan

    # Average MSP
    if "msp" in df.columns:
        kpis["avg_msp"] = df["msp"].mean()
    else:
        kpis["avg_msp"] = np.nan

    # Price crash instances
    if "price_crash" in df.columns:
        kpis["price_crash_count"] = int(df["price_crash"].sum())
    else:
        kpis["price_crash_count"] = 0

    # Average transit time (clean)
    if "transit_hours_clean" in df.columns:
        kpis["avg_transit_hrs"] = df["transit_hours_clean"].mean()
    elif "avg_transit_hours" in df.columns:
        kpis["avg_transit_hrs"] = df[df["avg_transit_hours"] >= 0]["avg_transit_hours"].mean()
    else:
        kpis["avg_transit_hrs"] = np.nan

    # Long transit rate (>24h)
    if "long_transit_flag" in df.columns:
        kpis["long_transit_rate"] = df["long_transit_flag"].mean() * 100
    else:
        kpis["long_transit_rate"] = np.nan

    return kpis


def calc_price_kpis(df: pd.DataFrame) -> dict:
    """Calculate KPIs for the Crop & Price page."""
    kpis = {}

    kpis["avg_modal_price"] = df["modal_price"].mean() if "modal_price" in df.columns else np.nan
    kpis["avg_msp"] = df["msp"].mean() if "msp" in df.columns else np.nan

    if "price_vs_msp" in df.columns:
        kpis["avg_msp_gap"] = df["price_vs_msp"].mean()
    else:
        kpis["avg_msp_gap"] = np.nan

    if "price_crash" in df.columns:
        kpis["price_crash_count"] = int(df["price_crash"].sum())
        total = df["price_crash"].notna().sum()
        kpis["price_crash_rate"] = (df["price_crash"].sum() / total * 100) if total > 0 else 0.0
    else:
        kpis["price_crash_count"] = 0
        kpis["price_crash_rate"] = 0.0

    if "price_spread" in df.columns:
        kpis["avg_price_spread"] = df["price_spread"].mean()
    elif "modal_price" in df.columns:
        kpis["avg_price_spread"] = np.nan
    else:
        kpis["avg_price_spread"] = np.nan

    return kpis


def calc_transport_kpis(df: pd.DataFrame) -> dict:
    """Calculate KPIs for the Transport page."""
    kpis = {}

    kpis["total_trips"] = len(df)

    if "transit_hours_clean" in df.columns:
        kpis["avg_transit_hrs"] = df["transit_hours_clean"].mean()
    else:
        kpis["avg_transit_hrs"] = np.nan

    if "avg_distance_km" in df.columns:
        kpis["avg_distance_km"] = df["avg_distance_km"].mean()
        kpis["max_distance_km"] = df["avg_distance_km"].max()
    else:
        kpis["avg_distance_km"] = np.nan
        kpis["max_distance_km"] = np.nan

    if "long_transit_flag" in df.columns:
        kpis["long_transit_rate"] = df["long_transit_flag"].mean() * 100
    else:
        kpis["long_transit_rate"] = np.nan

    if "mandi_name" in df.columns and "arrival_quantity_qtl" in df.columns:
        vol_by_mandi = df.groupby("mandi_name")["arrival_quantity_qtl"].sum()
        if len(vol_by_mandi) > 0:
            kpis["highest_vol_warehouse"] = vol_by_mandi.idxmax()
        else:
            kpis["highest_vol_warehouse"] = "N/A"
    else:
        kpis["highest_vol_warehouse"] = "N/A"

    return kpis


def calc_weather_kpis(df: pd.DataFrame) -> dict:
    """Calculate KPIs for the Weather Impact page."""
    kpis = {}

    if "avg_temperature_c" in df.columns:
        kpis["avg_temp"] = df["avg_temperature_c"].mean()
    else:
        kpis["avg_temp"] = np.nan

    if "total_rainfall_mm" in df.columns:
        kpis["total_rainfall"] = df["total_rainfall_mm"].sum()
        kpis["avg_rainfall"] = df["total_rainfall_mm"].mean()
    else:
        kpis["total_rainfall"] = np.nan
        kpis["avg_rainfall"] = np.nan

    if "avg_humidity_percent" in df.columns:
        kpis["avg_humidity"] = df["avg_humidity_percent"].mean()
    else:
        kpis["avg_humidity"] = np.nan

    # Rainfall-arrival correlation (daily aggregation)
    if "date" in df.columns and "total_rainfall_mm" in df.columns and "arrival_quantity_qtl" in df.columns:
        daily = (
            df.dropna(subset=["date"])
            .groupby("date")
            .agg(
                rain=("total_rainfall_mm", "mean"),
                arrivals=("arrival_quantity_qtl", "sum"),
            )
            .dropna()
        )
        if len(daily) >= 3:
            kpis["rain_arrival_corr"] = daily["rain"].corr(daily["arrivals"])
        else:
            kpis["rain_arrival_corr"] = np.nan
    else:
        kpis["rain_arrival_corr"] = np.nan

    return kpis


def build_insight_facts(df: pd.DataFrame) -> dict:
    """Compute auto-insight facts for the Overview Key Insights card."""
    facts = {}

    # Highest arrival crop
    if "crop_name" in df.columns and "arrival_quantity_qtl" in df.columns:
        by_crop = df.groupby("crop_name")["arrival_quantity_qtl"].sum()
        if len(by_crop) > 0:
            facts["top_arrival_crop"] = by_crop.idxmax()
            facts["top_arrival_crop_qty"] = by_crop.max()

    # Highest volume mandi
    if "mandi_name" in df.columns and "arrival_quantity_qtl" in df.columns:
        by_mandi = df.groupby("mandi_name")["arrival_quantity_qtl"].sum()
        if len(by_mandi) > 0:
            facts["top_mandi"] = by_mandi.idxmax()
            facts["top_mandi_qty"] = by_mandi.max()

    # Crop with largest average negative MSP gap
    if "crop_name" in df.columns and "price_vs_msp" in df.columns:
        gap_by_crop = df.groupby("crop_name")["price_vs_msp"].mean().dropna()
        neg_gaps = gap_by_crop[gap_by_crop < 0]
        if len(neg_gaps) > 0:
            facts["worst_msp_gap_crop"] = neg_gaps.idxmin()
            facts["worst_msp_gap_val"] = neg_gaps.min()

    # Highest long-transit warehouse
    if "mandi_name" in df.columns and "long_transit_flag" in df.columns:
        lt_by_mandi = df.groupby("mandi_name")["long_transit_flag"].mean()
        if len(lt_by_mandi) > 0:
            facts["worst_transit_warehouse"] = lt_by_mandi.idxmax()
            facts["worst_transit_rate"] = lt_by_mandi.max() * 100

    return facts
