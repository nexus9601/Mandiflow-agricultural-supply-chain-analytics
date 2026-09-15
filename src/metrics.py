"""
MandiFlow Dashboard – Metrics / KPI Calculations
All KPI calculations live here, keeping UI code clean.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ── Formatting helpers ─────────────────────────────────────────────────────────

def fmt_qty(val: float) -> str:
    """Format arrival quantity in a compact readable form."""
    if pd.isna(val):
        return "—"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M Qtl"
    if val >= 1_000:
        return f"{val / 1_000:.1f}K Qtl"
    return f"{val:,.0f} Qtl"


def fmt_inr(val: float) -> str:
    if pd.isna(val):
        return "—"
    return f"₹{val:,.0f}"


def fmt_pct(val: float, decimals: int = 2) -> str:
    if pd.isna(val):
        return "—"
    return f"{val:.{decimals}f}%"


def fmt_hrs(val: float) -> str:
    if pd.isna(val):
        return "—"
    return f"{val:.1f} hrs"


def fmt_km(val: float) -> str:
    if pd.isna(val):
        return "—"
    return f"{val:.1f} km"


def fmt_int(val) -> str:
    if pd.isna(val):
        return "—"
    return f"{int(val):,}"


# ── Overview KPIs ──────────────────────────────────────────────────────────────

def overview_kpis(df: pd.DataFrame, transport_df: pd.DataFrame) -> dict:
    """Calculate the six Overview KPIs."""
    total_arrivals = df["arrival_quantity_qtl"].sum()

    price_mask = df["modal_price"].notna()
    avg_modal = df.loc[price_mask, "modal_price"].mean()

    msp_mask = df["msp"].notna()
    avg_msp = df.loc[msp_mask, "msp"].mean()

    price_crash = int(df["price_crash"].sum()) if "price_crash" in df.columns else 0

    # Transit from transport df (richer)
    if not transport_df.empty and "transit_hours_clean" in transport_df.columns:
        t = transport_df["transit_hours_clean"].dropna()
        avg_transit = t.mean()
        long_rate = (transport_df["long_transit_flag"].mean() * 100
                     if "long_transit_flag" in transport_df.columns else np.nan)
    else:
        # Fall back to integrated df
        t = df["transit_hours_clean"].dropna() if "transit_hours_clean" in df.columns else pd.Series(dtype=float)
        avg_transit = t.mean() if len(t) else np.nan
        long_rate = (
            (df["long_transit_flag"].mean() * 100)
            if "long_transit_flag" in df.columns else np.nan
        )

    return {
        "total_arrivals": total_arrivals,
        "avg_modal_price": avg_modal,
        "avg_msp": avg_msp,
        "price_crash_count": price_crash,
        "avg_transit_hours": avg_transit,
        "long_transit_rate": long_rate,
    }


# ── Mandi Analysis KPIs ────────────────────────────────────────────────────────

def mandi_kpis(df: pd.DataFrame) -> dict:
    n_mandis = df["mandi_name"].nunique() if "mandi_name" in df.columns else 0
    total_vol = df["arrival_quantity_qtl"].sum()

    top_mandi = "—"
    top_district = "—"
    if "mandi_name" in df.columns and not df.empty:
        top_mandi = (
            df.groupby("mandi_name")["arrival_quantity_qtl"].sum().idxmax()
        )
    if "district" in df.columns and not df.empty:
        top_district = (
            df.groupby("district")["arrival_quantity_qtl"].sum().idxmax()
        )

    return {
        "n_mandis": n_mandis,
        "total_volume": total_vol,
        "top_mandi": top_mandi,
        "top_district": top_district,
    }


# ── Crop & Price KPIs ─────────────────────────────────────────────────────────

def price_kpis(df: pd.DataFrame, prices_df: pd.DataFrame) -> dict:
    pm = df["modal_price"].notna()
    avg_modal = df.loc[pm, "modal_price"].mean()
    avg_msp = df.loc[df["msp"].notna(), "msp"].mean()

    gap_mask = df["price_vs_msp"].notna() if "price_vs_msp" in df.columns else pd.Series(False, index=df.index)
    avg_gap = df.loc[gap_mask, "price_vs_msp"].mean() if "price_vs_msp" in df.columns else np.nan

    crash_count = int(df["price_crash"].sum()) if "price_crash" in df.columns else 0
    total_with_price = int(df[["modal_price", "msp"]].dropna().shape[0])
    crash_rate = (crash_count / total_with_price * 100) if total_with_price else np.nan

    # Price spread from prices_df if available, else approximate from integrated df
    if not prices_df.empty and "price_spread" in prices_df.columns:
        avg_spread = prices_df["price_spread"].dropna().mean()
    else:
        avg_spread = np.nan

    return {
        "avg_modal_price": avg_modal,
        "avg_msp": avg_msp,
        "avg_msp_gap": avg_gap,
        "price_crash_count": crash_count,
        "price_crash_rate": crash_rate,
        "avg_price_spread": avg_spread,
    }


# ── Transport KPIs ────────────────────────────────────────────────────────────

def transport_kpis(transport_df: pd.DataFrame, main_df: pd.DataFrame) -> dict:
    if transport_df.empty:
        # Fall back to integrated df averages
        avg_transit = main_df["transit_hours_clean"].dropna().mean() if "transit_hours_clean" in main_df.columns else np.nan
        avg_dist = main_df["distance_km"].dropna().mean() if "distance_km" in main_df.columns else np.nan
        long_rate = (main_df["long_transit_flag"].mean() * 100) if "long_transit_flag" in main_df.columns else np.nan
        return {
            "total_trips": len(main_df),
            "avg_transit": avg_transit,
            "avg_distance": avg_dist,
            "long_transit_rate": long_rate,
            "longest_route": "—",
            "top_warehouse": "—",
        }

    total_trips = len(transport_df)
    avg_transit = transport_df["transit_hours_clean"].dropna().mean()
    avg_dist = transport_df["distance_km"].dropna().mean()
    long_rate = transport_df["long_transit_flag"].mean() * 100 if "long_transit_flag" in transport_df.columns else np.nan

    longest = "—"
    if "distance_km" in transport_df.columns and transport_df["distance_km"].notna().any():
        idx = transport_df["distance_km"].idxmax()
        src = transport_df.loc[idx, "mandi_id"] if "mandi_id" in transport_df.columns else "?"
        dst = transport_df.loc[idx, "warehouse"] if "warehouse" in transport_df.columns else "?"
        longest = f"{src} → {dst}"

    top_wh = "—"
    if "warehouse" in transport_df.columns:
        wh_counts = transport_df.groupby("warehouse").size()
        if not wh_counts.empty:
            top_wh = str(wh_counts.idxmax())

    return {
        "total_trips": total_trips,
        "avg_transit": avg_transit,
        "avg_distance": avg_dist,
        "long_transit_rate": long_rate,
        "longest_route": longest,
        "top_warehouse": top_wh,
    }


# ── Weather KPIs ──────────────────────────────────────────────────────────────

def weather_kpis(daily_df: pd.DataFrame) -> dict:
    if daily_df.empty:
        return {
            "avg_temp": np.nan,
            "total_rainfall": np.nan,
            "avg_humidity": np.nan,
            "rain_arrival_corr": np.nan,
        }

    avg_temp = daily_df["avg_temperature_c"].dropna().mean() if "avg_temperature_c" in daily_df.columns else np.nan
    total_rain = daily_df["total_rainfall_mm"].dropna().sum() if "total_rainfall_mm" in daily_df.columns else np.nan
    avg_hum = daily_df["avg_humidity_percent"].dropna().mean() if "avg_humidity_percent" in daily_df.columns else np.nan

    corr = np.nan
    if (
        "total_rainfall_mm" in daily_df.columns
        and "total_arrival_qtl" in daily_df.columns
    ):
        paired = daily_df[["total_rainfall_mm", "total_arrival_qtl"]].dropna()
        if len(paired) >= 3:
            corr = paired["total_rainfall_mm"].corr(paired["total_arrival_qtl"])

    return {
        "avg_temp": avg_temp,
        "total_rainfall": total_rain,
        "avg_humidity": avg_hum,
        "rain_arrival_corr": corr,
    }


# ── Key Insights (Overview page) ──────────────────────────────────────────────

def key_insights(df: pd.DataFrame, transport_df: pd.DataFrame) -> dict:
    """Compute the four automatic insights for the Overview key-insights card."""
    insights = {}

    # Highest-arrival crop
    if "crop_name" in df.columns and not df.empty:
        grp = df.groupby("crop_name")["arrival_quantity_qtl"].sum()
        if not grp.empty:
            crop = grp.idxmax()
            insights["top_crop"] = f"{crop} ({fmt_qty(grp[crop])})"
        else:
            insights["top_crop"] = "—"
    else:
        insights["top_crop"] = "—"

    # Highest-volume mandi
    if "mandi_name" in df.columns and not df.empty:
        grp = df.groupby("mandi_name")["arrival_quantity_qtl"].sum()
        if not grp.empty:
            m = grp.idxmax()
            insights["top_mandi"] = f"{m} ({fmt_qty(grp[m])})"
        else:
            insights["top_mandi"] = "—"
    else:
        insights["top_mandi"] = "—"

    # Crop with largest average negative MSP gap
    insights["worst_msp_crop"] = "—"
    if "price_vs_msp" in df.columns and "crop_name" in df.columns:
        neg = df[df["price_vs_msp"] < 0]
        if not neg.empty:
            grp = neg.groupby("crop_name")["price_vs_msp"].mean()
            if not grp.empty:
                worst = grp.idxmin()
                insights["worst_msp_crop"] = f"{worst} (avg gap {fmt_inr(grp[worst])})"

    # Highest long-transit warehouse
    insights["worst_transit_warehouse"] = "—"
    if not transport_df.empty and "long_transit_flag" in transport_df.columns and "warehouse" in transport_df.columns:
        wh_grp = transport_df.groupby("warehouse")["long_transit_flag"].mean()
        if not wh_grp.empty:
            wh = wh_grp.idxmax()
            insights["worst_transit_warehouse"] = f"{wh} ({fmt_pct(wh_grp[wh]*100)} long-transit rate)"

    return insights
