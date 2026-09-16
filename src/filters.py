"""
MandiFlow Dashboard – Filters
Centralised filtering logic; all pages call apply_filters().
"""

from __future__ import annotations

import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    date_range: tuple | None = None,
    crop: str | list | None = None,
    district: str | list | None = None,
    mandi: str | list | None = None,
) -> pd.DataFrame:
    """
    Apply zero or more filters to a DataFrame.

    Parameters
    ----------
    df          : The DataFrame to filter (copy-on-write safe).
    date_range  : (start_date, end_date) – both inclusive. Ignored if None.
    crop        : crop name string or list of crop names. Ignored if None or 'All'.
    district    : district string or list. Ignored if None or 'All'.
    mandi       : mandi_name string or list. Ignored if None or 'All'.

    Returns
    -------
    Filtered DataFrame (may be empty).
    """
    mask = pd.Series(True, index=df.index)

    # ── Date range ─────────────────────────────────────────────────────────
    if date_range is not None and "date" in df.columns:
        start, end = date_range
        if start is not None:
            mask &= df["date"] >= pd.Timestamp(start)
        if end is not None:
            mask &= df["date"] <= pd.Timestamp(end)

    # ── Crop ───────────────────────────────────────────────────────────────
    if crop and "crop_name" in df.columns:
        if isinstance(crop, str):
            if crop not in ("All", ""):
                mask &= df["crop_name"] == crop
        else:
            crops = [c for c in crop if c not in ("All", "")]
            if crops:
                mask &= df["crop_name"].isin(crops)

    # ── District ───────────────────────────────────────────────────────────
    if district and "district" in df.columns:
        if isinstance(district, str):
            if district not in ("All", ""):
                mask &= df["district"] == district
        else:
            districts = [d for d in district if d not in ("All", "")]
            if districts:
                mask &= df["district"].isin(districts)

    # ── Mandi ──────────────────────────────────────────────────────────────
    if mandi and "mandi_name" in df.columns:
        if isinstance(mandi, str):
            if mandi not in ("All", ""):
                mask &= df["mandi_name"] == mandi
        else:
            mandis = [m for m in mandi if m not in ("All", "")]
            if mandis:
                mask &= df["mandi_name"].isin(mandis)

    return df.loc[mask].copy()


def apply_transport_filters(
    df: pd.DataFrame,
    warehouse: str | list | None = None,
    mandi_id: str | list | None = None,
) -> pd.DataFrame:
    """Filter raw transport DataFrame."""
    mask = pd.Series(True, index=df.index)

    if warehouse and "warehouse" in df.columns:
        if isinstance(warehouse, str):
            if warehouse not in ("All", ""):
                mask &= df["warehouse"] == warehouse
        else:
            wh = [w for w in warehouse if w not in ("All", "")]
            if wh:
                mask &= df["warehouse"].isin(wh)

    if mandi_id and "mandi_id" in df.columns:
        if isinstance(mandi_id, str):
            if mandi_id not in ("All", ""):
                mask &= df["mandi_id"] == mandi_id
        else:
            mid = [m for m in mandi_id if m not in ("All", "")]
            if mid:
                mask &= df["mandi_id"].isin(mid)

    return df.loc[mask].copy()
