"""
charts.py
---------
Reusable Plotly chart builders for MandiFlow dashboard.
All functions accept a filtered DataFrame and return a go.Figure.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.styles import CHART_COLORS, PLOTLY_LAYOUT, GREEN_PRIMARY, AMBER, RED_SOFT, GREEN_ACCENT


def _apply_layout(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """Apply standard MandiFlow layout to any figure."""
    layout = dict(PLOTLY_LAYOUT)
    layout["height"] = height
    if title:
        layout["title"] = dict(text=title, font=dict(size=14, color="#1e4d2b"), x=0)
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def create_arrival_trend(df: pd.DataFrame, crop: str = "All") -> go.Figure:
    """Daily crop arrival trend — line chart with area fill."""
    if "date" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    plot_df = df.dropna(subset=["date"])
    if crop and crop != "All" and "crop_name" in df.columns:
        plot_df = plot_df[plot_df["crop_name"] == crop]

    if len(plot_df) == 0:
        return go.Figure()

    daily = plot_df.groupby("date")["arrival_quantity_qtl"].sum().reset_index()
    daily = daily.sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["arrival_quantity_qtl"],
        mode="lines",
        fill="tozeroy",
        fillcolor=f"rgba(82, 183, 136, 0.15)",
        line=dict(color=GREEN_PRIMARY, width=2),
        name="Daily Arrivals",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
    ))

    # 7-day moving average
    if len(daily) >= 7:
        daily["ma7"] = daily["arrival_quantity_qtl"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=daily["date"],
            y=daily["ma7"],
            mode="lines",
            line=dict(color=AMBER, width=1.5, dash="dot"),
            name="7-day Avg",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>7-day Avg: %{y:,.0f} Qtl<extra></extra>",
        ))

    _apply_layout(fig, "Daily Crop Arrival Trend", height=360)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Arrival Quantity (Qtl)")
    return fig


def create_crop_distribution(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar chart: crop-wise total arrivals, sorted descending."""
    if "crop_name" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    by_crop = (
        df.groupby("crop_name")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .nlargest(top_n)
        .sort_values(ascending=True)
    )

    if len(by_crop) == 0:
        return go.Figure()

    fig = go.Figure(go.Bar(
        y=by_crop.index,
        x=by_crop.values,
        orientation="h",
        marker_color=GREEN_PRIMARY,
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Total Arrivals: %{x:,.0f} Qtl<extra></extra>",
    ))

    _apply_layout(fig, "Crop-wise Arrival Distribution", height=max(320, top_n * 28))
    fig.update_xaxes(title_text="Total Arrival Quantity (Qtl)")
    fig.update_yaxes(title_text="")
    return fig


def create_top_mandis(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Top N mandis by total arrival volume — horizontal bar."""
    if "mandi_name" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    by_mandi = (
        df.groupby("mandi_name")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .nlargest(top_n)
        .sort_values(ascending=True)
    )

    if len(by_mandi) == 0:
        return go.Figure()

    fig = go.Figure(go.Bar(
        y=by_mandi.index,
        x=by_mandi.values,
        orientation="h",
        marker_color=GREEN_ACCENT,
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Arrivals: %{x:,.0f} Qtl<extra></extra>",
    ))

    _apply_layout(fig, f"Top {top_n} Mandis by Arrival Volume", height=max(300, top_n * 32))
    fig.update_xaxes(title_text="Total Arrival Quantity (Qtl)")
    fig.update_yaxes(title_text="")
    return fig


def create_price_msp_grouped(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart: Average Modal Price vs Average MSP by crop."""
    if "crop_name" not in df.columns:
        return go.Figure()

    needed = ["modal_price", "msp"]
    avail = [c for c in needed if c in df.columns]
    if len(avail) < 2:
        return go.Figure()

    by_crop = (
        df.groupby("crop_name")[avail]
        .mean()
        .dropna()
        .reset_index()
        .sort_values("modal_price", ascending=False)
        .head(20)
    )

    if len(by_crop) == 0:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Modal Price",
        x=by_crop["crop_name"],
        y=by_crop["modal_price"],
        marker_color=GREEN_PRIMARY,
        hovertemplate="<b>%{x}</b><br>Modal Price: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="MSP",
        x=by_crop["crop_name"],
        y=by_crop["msp"],
        marker_color=AMBER,
        hovertemplate="<b>%{x}</b><br>MSP: ₹%{y:,.0f}<extra></extra>",
    ))

    _apply_layout(fig, "Modal Price vs MSP by Crop (Average)", height=400)
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Crop", tickangle=-35)
    fig.update_yaxes(title_text="Price (₹/Qtl)")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# MANDI ANALYSIS CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def create_district_arrivals(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Bar chart: district-wise total arrivals, sorted descending."""
    if "district" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    by_district = (
        df.groupby("district")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .nlargest(top_n)
        .sort_values(ascending=False)
    )

    if len(by_district) == 0:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=by_district.index,
        y=by_district.values,
        marker_color=GREEN_PRIMARY,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
    ))

    _apply_layout(fig, "District-wise Arrival Distribution", height=380)
    fig.update_xaxes(title_text="District", tickangle=-40)
    fig.update_yaxes(title_text="Total Arrival Quantity (Qtl)")
    return fig


def create_mandi_trend(df: pd.DataFrame, mandi: str = None, crop: str = None) -> go.Figure:
    """Line chart: arrival trend for a specific mandi/crop."""
    if "date" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    plot_df = df.dropna(subset=["date"])

    if mandi and "mandi_name" in df.columns:
        plot_df = plot_df[plot_df["mandi_name"] == mandi]
    if crop and "crop_name" in df.columns:
        plot_df = plot_df[plot_df["crop_name"] == crop]

    if len(plot_df) == 0:
        return go.Figure()

    daily = plot_df.groupby("date")["arrival_quantity_qtl"].sum().reset_index().sort_values("date")

    fig = go.Figure(go.Scatter(
        x=daily["date"],
        y=daily["arrival_quantity_qtl"],
        mode="lines+markers",
        line=dict(color=GREEN_PRIMARY, width=2),
        marker=dict(size=4, color=GREEN_PRIMARY),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
    ))

    title = "Mandi Arrival Trend"
    if mandi:
        title = f"Arrival Trend — {mandi}"
    _apply_layout(fig, title, height=340)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Arrival Quantity (Qtl)")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# CROP & PRICE CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def create_msp_gap_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: average MSP gap (price_vs_msp) by crop."""
    if "price_vs_msp" not in df.columns or "crop_name" not in df.columns:
        return go.Figure()

    by_crop = (
        df.groupby("crop_name")["price_vs_msp"]
        .mean()
        .dropna()
        .sort_values()
    )

    if len(by_crop) == 0:
        return go.Figure()

    colors = [RED_SOFT if v < 0 else GREEN_PRIMARY for v in by_crop.values]

    fig = go.Figure(go.Bar(
        y=by_crop.index,
        x=by_crop.values,
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Avg MSP Gap: ₹%{x:,.0f}<extra></extra>",
    ))

    fig.add_vline(x=0, line_color="#666", line_width=1, line_dash="dot")

    _apply_layout(fig, "Average MSP Gap by Crop (Price − MSP)", height=max(320, len(by_crop) * 28))
    fig.update_xaxes(title_text="Price − MSP (₹/Qtl)")
    fig.update_yaxes(title_text="")
    return fig


def create_price_crash_rate(df: pd.DataFrame) -> go.Figure:
    """Bar chart: price crash rate by crop."""
    if "price_crash" not in df.columns or "crop_name" not in df.columns:
        return go.Figure()

    crash_rate = (
        df.groupby("crop_name")["price_crash"]
        .mean()
        .dropna()
        .mul(100)
        .sort_values(ascending=False)
    )

    if len(crash_rate) == 0:
        return go.Figure()

    colors = [RED_SOFT if v > 50 else AMBER if v > 20 else GREEN_PRIMARY for v in crash_rate.values]

    fig = go.Figure(go.Bar(
        x=crash_rate.index,
        y=crash_rate.values,
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Price Crash Rate: %{y:.1f}%<extra></extra>",
    ))

    _apply_layout(fig, "Price Crash Rate by Crop (Modal Price < MSP)", height=360)
    fig.update_xaxes(title_text="Crop", tickangle=-35)
    fig.update_yaxes(title_text="Price Crash Rate (%)")
    return fig


def create_price_trend(df: pd.DataFrame, crop: str = None, mandi: str = None) -> go.Figure:
    """Line chart: Modal Price and MSP over time."""
    if "date" not in df.columns or "modal_price" not in df.columns:
        return go.Figure()

    plot_df = df.dropna(subset=["date"])
    if crop and "crop_name" in df.columns:
        plot_df = plot_df[plot_df["crop_name"] == crop]
    if mandi and "mandi_name" in df.columns:
        plot_df = plot_df[plot_df["mandi_name"] == mandi]

    if len(plot_df) == 0:
        return go.Figure()

    daily = plot_df.groupby("date").agg(
        modal_price=("modal_price", "mean"),
        msp=("msp", "mean") if "msp" in plot_df.columns else ("modal_price", "mean"),
    ).reset_index().sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["modal_price"],
        mode="lines",
        name="Modal Price",
        line=dict(color=GREEN_PRIMARY, width=2),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Modal Price: ₹%{y:,.0f}<extra></extra>",
    ))

    if "msp" in daily.columns and daily["msp"].notna().any():
        fig.add_trace(go.Scatter(
            x=daily["date"],
            y=daily["msp"],
            mode="lines",
            name="MSP",
            line=dict(color=AMBER, width=1.5, dash="dash"),
            hovertemplate="<b>%{x|%d %b %Y}</b><br>MSP: ₹%{y:,.0f}<extra></extra>",
        ))

    title = "Price Trend"
    if crop:
        title = f"Price Trend — {crop}"
    _apply_layout(fig, title, height=360)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Price (₹/Qtl)")
    return fig


def create_price_spread(df: pd.DataFrame) -> go.Figure:
    """Box / bar chart showing price spread (max_price - min_price) by crop."""
    # If we have price_spread column
    if "price_spread" in df.columns and df["price_spread"].notna().any() and "crop_name" in df.columns:
        by_crop = (
            df.groupby("crop_name")["price_spread"]
            .mean()
            .dropna()
            .sort_values(ascending=False)
            .head(20)
        )
        fig = go.Figure(go.Bar(
            x=by_crop.index,
            y=by_crop.values,
            marker_color=GREEN_PRIMARY,
            hovertemplate="<b>%{x}</b><br>Avg Price Spread: ₹%{y:,.0f}<extra></extra>",
        ))
        _apply_layout(fig, "Average Price Spread by Crop (Max − Min Price)", height=360)
        fig.update_xaxes(title_text="Crop", tickangle=-35)
        fig.update_yaxes(title_text="Price Spread (₹/Qtl)")
        return fig

    # Fallback: show modal price std as proxy for spread
    if "modal_price" in df.columns and "crop_name" in df.columns:
        spread = (
            df.groupby("crop_name")["modal_price"]
            .std()
            .dropna()
            .sort_values(ascending=False)
            .head(20)
        )
        fig = go.Figure(go.Bar(
            x=spread.index,
            y=spread.values,
            marker_color=AMBER,
            hovertemplate="<b>%{x}</b><br>Price Std Dev: ₹%{y:,.0f}<extra></extra>",
        ))
        _apply_layout(fig, "Price Volatility by Crop (Modal Price Std Dev)", height=360)
        fig.update_xaxes(title_text="Crop", tickangle=-35)
        fig.update_yaxes(title_text="Price Std Dev (₹/Qtl)")
        return fig

    return go.Figure()


# ─────────────────────────────────────────────────────────────────────────────
# TRANSPORT CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def create_transit_by_warehouse(df: pd.DataFrame) -> go.Figure:
    """Bar chart: average transit time by mandi/warehouse."""
    col = "transit_hours_clean" if "transit_hours_clean" in df.columns else "avg_transit_hours"
    if col not in df.columns or "mandi_name" not in df.columns:
        return go.Figure()

    by_mandi = (
        df.groupby("mandi_name")[col]
        .mean()
        .dropna()
        .sort_values(ascending=False)
        .head(20)
    )

    if len(by_mandi) == 0:
        return go.Figure()

    colors = [RED_SOFT if v > 24 else AMBER if v > 18 else GREEN_PRIMARY for v in by_mandi.values]

    fig = go.Figure(go.Bar(
        x=by_mandi.index,
        y=by_mandi.values,
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Avg Transit: %{y:.1f} hrs<extra></extra>",
    ))

    fig.add_hline(y=24, line_color=RED_SOFT, line_dash="dot", line_width=1.5,
                  annotation_text="24h threshold", annotation_position="top right",
                  annotation_font_color=RED_SOFT)

    _apply_layout(fig, "Average Transit Time by Mandi/Warehouse", height=380)
    fig.update_xaxes(title_text="Mandi / Warehouse", tickangle=-40)
    fig.update_yaxes(title_text="Average Transit Time (hrs)")
    return fig


def create_distance_by_warehouse(df: pd.DataFrame) -> go.Figure:
    """Bar chart: average distance by mandi."""
    if "avg_distance_km" not in df.columns or "mandi_name" not in df.columns:
        return go.Figure()

    by_mandi = (
        df.groupby("mandi_name")["avg_distance_km"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
        .head(20)
    )

    if len(by_mandi) == 0:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=by_mandi.index,
        y=by_mandi.values,
        marker_color=GREEN_ACCENT,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Avg Distance: %{y:.1f} km<extra></extra>",
    ))

    _apply_layout(fig, "Average Distance by Mandi/Warehouse", height=380)
    fig.update_xaxes(title_text="Mandi / Warehouse", tickangle=-40)
    fig.update_yaxes(title_text="Average Distance (km)")
    return fig


def create_transit_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram of transit_hours_clean with 24h threshold annotation."""
    col = "transit_hours_clean" if "transit_hours_clean" in df.columns else "avg_transit_hours"
    if col not in df.columns:
        return go.Figure()

    vals = df[col].dropna()
    vals = vals[vals > 0]

    if len(vals) == 0:
        return go.Figure()

    fig = go.Figure(go.Histogram(
        x=vals,
        nbinsx=40,
        marker_color=GREEN_PRIMARY,
        marker_line_color="#ffffff",
        marker_line_width=0.5,
        hovertemplate="Transit: %{x:.0f}–%{x:.0f} hrs<br>Count: %{y}<extra></extra>",
    ))

    fig.add_vline(x=24, line_color=RED_SOFT, line_dash="dash", line_width=2,
                  annotation_text="24h (Long Transit)", annotation_position="top right",
                  annotation_font_color=RED_SOFT)

    _apply_layout(fig, "Transit Time Distribution", height=340)
    fig.update_xaxes(title_text="Transit Time (hrs)")
    fig.update_yaxes(title_text="Number of Records")
    return fig


def create_warehouse_volume(df: pd.DataFrame) -> go.Figure:
    """Bar chart: total arrival volume by mandi (as warehouse proxy)."""
    if "mandi_name" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    by_mandi = (
        df.groupby("mandi_name")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .sort_values(ascending=False)
        .head(20)
    )

    if len(by_mandi) == 0:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=by_mandi.index,
        y=by_mandi.values,
        marker_color=GREEN_PRIMARY,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Volume: %{y:,.0f} Qtl<extra></extra>",
    ))

    _apply_layout(fig, "Total Crop Volume by Warehouse/Mandi", height=380)
    fig.update_xaxes(title_text="Mandi / Warehouse", tickangle=-40)
    fig.update_yaxes(title_text="Total Arrival Volume (Qtl)")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# WEATHER CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def create_rainfall_arrival_trend(df: pd.DataFrame) -> go.Figure:
    """Dual-axis chart: daily rainfall and daily arrivals."""
    if "date" not in df.columns:
        return go.Figure()

    rain_col = "total_rainfall_mm" if "total_rainfall_mm" in df.columns else None
    arr_col = "arrival_quantity_qtl" if "arrival_quantity_qtl" in df.columns else None

    if not rain_col and not arr_col:
        return go.Figure()

    agg = {"date": "first"}
    if rain_col:
        agg[rain_col] = "mean"
    if arr_col:
        agg[arr_col] = "sum"

    daily = (
        df.dropna(subset=["date"])
        .groupby("date")
        .agg(**{k: (k, v) for k, v in agg.items() if k != "date"})
        .reset_index()
        .sort_values("date")
    )

    fig = go.Figure()

    if arr_col and arr_col in daily.columns:
        fig.add_trace(go.Scatter(
            x=daily["date"], y=daily[arr_col],
            name="Crop Arrivals (Qtl)",
            line=dict(color=GREEN_PRIMARY, width=2),
            yaxis="y1",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
        ))

    if rain_col and rain_col in daily.columns:
        fig.add_trace(go.Bar(
            x=daily["date"], y=daily[rain_col],
            name="Rainfall (mm)",
            marker_color="rgba(70, 130, 180, 0.45)",
            yaxis="y2",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Rainfall: %{y:.1f} mm<extra></extra>",
        ))

    layout = dict(PLOTLY_LAYOUT)
    layout.update({
        "height": 380,
        "title": dict(text="Daily Rainfall & Crop Arrivals", font=dict(size=14, color="#1e4d2b"), x=0),
        "yaxis": dict(title="Arrival Quantity (Qtl)", gridcolor="#e8f0e4", linecolor="#dde8d5"),
        "yaxis2": dict(
            title="Rainfall (mm)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        "legend": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    })
    fig.update_layout(**layout)
    return fig


def create_rainfall_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: daily rainfall vs daily arrival quantity with trendline."""
    if "date" not in df.columns or "total_rainfall_mm" not in df.columns or "arrival_quantity_qtl" not in df.columns:
        return go.Figure()

    daily = (
        df.dropna(subset=["date"])
        .groupby("date")
        .agg(rain=("total_rainfall_mm", "mean"), arrivals=("arrival_quantity_qtl", "sum"))
        .dropna()
        .reset_index()
    )

    if len(daily) < 3:
        return go.Figure()

    corr = daily["rain"].corr(daily["arrivals"])

    fig = px.scatter(
        daily, x="rain", y="arrivals",
        trendline="ols",
        color_discrete_sequence=[GREEN_PRIMARY],
    )
    fig.update_traces(
        selector=dict(mode="markers"),
        marker=dict(size=7, opacity=0.65),
        hovertemplate="Rainfall: %{x:.1f} mm<br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
    )
    # Style trendline
    fig.update_traces(
        selector=dict(mode="lines"),
        line=dict(color=AMBER, width=2, dash="dot"),
    )

    _apply_layout(fig, f"Rainfall vs Crop Arrivals  (Correlation: {corr:.3f})", height=380)
    fig.update_xaxes(title_text="Total Rainfall (mm)")
    fig.update_yaxes(title_text="Total Arrival Quantity (Qtl)")

    fig.add_annotation(
        text="Correlation indicates association, not causation.",
        xref="paper", yref="paper",
        x=0.01, y=-0.15,
        showarrow=False,
        font=dict(size=10, color="#8a8a8a"),
        align="left",
    )

    return fig


def create_temperature_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart: average daily temperature."""
    if "date" not in df.columns or "avg_temperature_c" not in df.columns:
        return go.Figure()

    daily = (
        df.dropna(subset=["date"])
        .groupby("date")["avg_temperature_c"]
        .mean()
        .reset_index()
        .sort_values("date")
    )

    if len(daily) == 0:
        return go.Figure()

    fig = go.Figure(go.Scatter(
        x=daily["date"],
        y=daily["avg_temperature_c"],
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(255, 140, 0, 0.1)",
        line=dict(color="#e07a2f", width=2),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Avg Temp: %{y:.1f} °C<extra></extra>",
    ))

    _apply_layout(fig, "Average Temperature Trend", height=320)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Temperature (°C)")
    return fig


def create_humidity_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart: average daily humidity."""
    if "date" not in df.columns or "avg_humidity_percent" not in df.columns:
        return go.Figure()

    daily = (
        df.dropna(subset=["date"])
        .groupby("date")["avg_humidity_percent"]
        .mean()
        .reset_index()
        .sort_values("date")
    )

    if len(daily) == 0:
        return go.Figure()

    fig = go.Figure(go.Scatter(
        x=daily["date"],
        y=daily["avg_humidity_percent"],
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(70, 130, 180, 0.1)",
        line=dict(color="#4682b4", width=2),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Avg Humidity: %{y:.1f}%<extra></extra>",
    ))

    _apply_layout(fig, "Average Humidity Trend", height=320)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Relative Humidity (%)")
    return fig
