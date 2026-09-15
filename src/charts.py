"""
MandiFlow Dashboard – Charts
All Plotly chart factory functions. No Streamlit calls here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.styles import COLORS, CHART_THEME, AXIS_STYLE


def _base_layout(**kwargs) -> dict:
    layout = dict(**CHART_THEME)
    layout.update(kwargs)
    return layout


def _apply_theme(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    fig.update_layout(
        **CHART_THEME,
        height=height,
        title=dict(
            text=title,
            font=dict(size=13, color=COLORS["text"], weight=700),
            x=0,
            xanchor="left",
            pad=dict(l=4),
        ),
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE),
    )
    return fig


# ── Overview Charts ───────────────────────────────────────────────────────────

def create_arrival_trend(df: pd.DataFrame, crop: str = "All") -> go.Figure:
    """Daily crop arrival trend line chart."""
    if df.empty or "date" not in df.columns:
        return _empty_fig("No arrival data available.")

    grp = df.groupby("date")["arrival_quantity_qtl"].sum().reset_index()
    grp.columns = ["date", "arrivals"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grp["date"], y=grp["arrivals"],
        mode="lines",
        fill="tozeroy",
        fillcolor=f"rgba(26,107,60,0.10)",
        line=dict(color=COLORS["primary"], width=2),
        name="Arrivals",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
    ))

    label = f" – {crop}" if crop and crop != "All" else ""
    fig = _apply_theme(fig, f"Daily Crop Arrival Trend{label}", height=350)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Arrival Quantity (Qtl)",
        showlegend=False,
    )
    return fig


def create_crop_distribution(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar – crop-wise arrival distribution."""
    if df.empty or "crop_name" not in df.columns:
        return _empty_fig("No crop data available.")

    grp = (
        df.groupby("crop_name")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .sort_values(ascending=True)
        .tail(top_n)
        .reset_index()
    )
    grp.columns = ["Crop", "Arrivals"]

    fig = px.bar(
        grp, x="Arrivals", y="Crop",
        orientation="h",
        color_discrete_sequence=[COLORS["primary"]],
        labels={"Arrivals": "Total Arrivals (Qtl)", "Crop": ""},
        text="Arrivals",
    )
    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        textfont_size=10,
    )
    fig = _apply_theme(fig, "Crop-wise Arrival Distribution", height=400)
    fig.update_layout(xaxis_title="Total Arrivals (Qtl)", yaxis_title="")
    return fig


def create_top_mandis(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar – top mandis by arrival volume."""
    if df.empty or "mandi_name" not in df.columns:
        return _empty_fig("No mandi data available.")

    grp = (
        df.groupby("mandi_name")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .sort_values(ascending=True)
        .tail(top_n)
        .reset_index()
    )
    grp.columns = ["Mandi", "Arrivals"]

    fig = px.bar(
        grp, x="Arrivals", y="Mandi",
        orientation="h",
        color_discrete_sequence=[COLORS["secondary"]],
        labels={"Arrivals": "Total Arrivals (Qtl)", "Mandi": ""},
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} Qtl<extra></extra>",
    )
    fig = _apply_theme(fig, f"Top {top_n} Mandis by Arrival Volume", height=400)
    fig.update_layout(xaxis_title="Total Arrivals (Qtl)", yaxis_title="")
    return fig


def create_price_vs_msp_grouped(df: pd.DataFrame) -> go.Figure:
    """Grouped bar – Average Modal Price vs MSP by crop."""
    needed = {"crop_name", "modal_price", "msp"}
    if df.empty or not needed.issubset(df.columns):
        return _empty_fig("Price vs MSP data unavailable.")

    grp = (
        df.dropna(subset=["modal_price", "msp"])
        .groupby("crop_name")[["modal_price", "msp"]]
        .mean()
        .reset_index()
        .sort_values("modal_price", ascending=False)
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Avg Modal Price",
        x=grp["crop_name"], y=grp["modal_price"],
        marker_color=COLORS["primary"],
        hovertemplate="<b>%{x}</b><br>Modal Price: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Avg MSP",
        x=grp["crop_name"], y=grp["msp"],
        marker_color=COLORS["accent"],
        hovertemplate="<b>%{x}</b><br>MSP: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(barmode="group")
    fig = _apply_theme(fig, "Average Modal Price vs MSP by Crop", height=380)
    fig.update_layout(
        xaxis_title="Crop",
        yaxis_title="Price (₹/Qtl)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ── Mandi Analysis Charts ─────────────────────────────────────────────────────

def create_district_distribution(df: pd.DataFrame) -> go.Figure:
    """Bar chart – district arrival distribution."""
    if df.empty or "district" not in df.columns:
        return _empty_fig("No district data available.")

    grp = (
        df.groupby("district")["arrival_quantity_qtl"]
        .sum()
        .dropna()
        .sort_values(ascending=False)
        .reset_index()
    )
    grp.columns = ["District", "Arrivals"]

    fig = px.bar(
        grp, x="District", y="Arrivals",
        color_discrete_sequence=[COLORS["primary"]],
        labels={"Arrivals": "Total Arrivals (Qtl)", "District": "District"},
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} Qtl<extra></extra>",
    )
    fig = _apply_theme(fig, "Arrival Volume by District", height=380)
    fig.update_layout(xaxis_title="District", yaxis_title="Total Arrivals (Qtl)")
    return fig


def create_mandi_trend(df: pd.DataFrame, mandi: str, crop: str) -> go.Figure:
    """Line chart – arrival trend for a selected mandi."""
    if df.empty or "date" not in df.columns:
        return _empty_fig("No data for the selected mandi/crop.")

    grp = df.groupby("date")["arrival_quantity_qtl"].sum().reset_index()
    grp.columns = ["date", "arrivals"]

    label_parts = []
    if mandi and mandi != "All":
        label_parts.append(mandi)
    if crop and crop != "All":
        label_parts.append(crop)
    subtitle = " – " + " / ".join(label_parts) if label_parts else ""

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grp["date"], y=grp["arrivals"],
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=4, color=COLORS["primary"]),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:,.0f} Qtl<extra></extra>",
    ))
    fig = _apply_theme(fig, f"Mandi Arrival Trend{subtitle}", height=340)
    fig.update_layout(xaxis_title="Date", yaxis_title="Arrival Quantity (Qtl)", showlegend=False)
    return fig


# ── Crop & Price Charts ───────────────────────────────────────────────────────

def create_msp_gap_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar – average MSP gap by crop with pos/neg coloring."""
    if df.empty or "price_vs_msp" not in df.columns:
        return _empty_fig("MSP gap data unavailable.")

    grp = (
        df.dropna(subset=["price_vs_msp"])
        .groupby("crop_name")["price_vs_msp"]
        .mean()
        .sort_values()
        .reset_index()
    )
    grp.columns = ["Crop", "MSP Gap"]
    grp["Color"] = grp["MSP Gap"].apply(
        lambda x: COLORS["positive"] if x >= 0 else COLORS["negative"]
    )

    fig = go.Figure(go.Bar(
        x=grp["MSP Gap"], y=grp["Crop"],
        orientation="h",
        marker_color=grp["Color"],
        hovertemplate="<b>%{y}</b><br>MSP Gap: ₹%{x:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_dash="dash", line_color=COLORS["neutral"], line_width=1.5)
    fig = _apply_theme(fig, "Average MSP Gap by Crop (Modal Price − MSP)", height=380)
    fig.update_layout(xaxis_title="MSP Gap (₹/Qtl)  |  + Above MSP  |  − Below MSP", yaxis_title="")
    return fig


def create_price_crash_rate(df: pd.DataFrame) -> go.Figure:
    """Bar chart – price crash rate by crop."""
    if df.empty or "price_crash" not in df.columns:
        return _empty_fig("Price crash data unavailable.")

    grp = (
        df.dropna(subset=["modal_price", "msp"])
        .groupby("crop_name")["price_crash"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .reset_index()
    )
    grp.columns = ["Crop", "Crash Rate %"]

    colors = [
        COLORS["danger"] if v > 50 else (COLORS["accent"] if v > 20 else COLORS["secondary"])
        for v in grp["Crash Rate %"]
    ]

    fig = px.bar(
        grp, x="Crop", y="Crash Rate %",
        color_discrete_sequence=[COLORS["danger"]],
        labels={"Crash Rate %": "Price Crash Rate (%)", "Crop": "Crop"},
    )
    fig.update_traces(
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>Crash Rate: %{y:.1f}%<extra></extra>",
    )
    fig = _apply_theme(fig, "Price Crash Rate by Crop (Modal Price < MSP)", height=340)
    fig.update_layout(xaxis_title="Crop", yaxis_title="Price Crash Rate (%)")
    return fig


def create_price_trend(df: pd.DataFrame, crop: str, mandi: str) -> go.Figure:
    """Line chart – modal price and MSP trend over time."""
    if df.empty or "date" not in df.columns:
        return _empty_fig("No price trend data available.")

    grp = (
        df.dropna(subset=["modal_price"])
        .groupby("date")[["modal_price", "msp"]]
        .mean()
        .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grp["date"], y=grp["modal_price"],
        mode="lines", name="Modal Price",
        line=dict(color=COLORS["primary"], width=2),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Modal: ₹%{y:,.0f}<extra></extra>",
    ))
    if "msp" in grp.columns and grp["msp"].notna().any():
        fig.add_trace(go.Scatter(
            x=grp["date"], y=grp["msp"],
            mode="lines", name="MSP",
            line=dict(color=COLORS["accent"], width=2, dash="dot"),
            hovertemplate="<b>%{x|%d %b %Y}</b><br>MSP: ₹%{y:,.0f}<extra></extra>",
        ))

    label_parts = []
    if crop and crop != "All":
        label_parts.append(crop)
    if mandi and mandi != "All":
        label_parts.append(mandi)
    subtitle = " – " + " / ".join(label_parts) if label_parts else ""

    fig = _apply_theme(fig, f"Price Trend: Modal Price vs MSP{subtitle}", height=360)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (₹/Qtl)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_price_spread(df: pd.DataFrame, prices_df: pd.DataFrame) -> go.Figure:
    """Box/bar chart – price spread by crop."""
    # Use prices_df if available; fall back to approximation
    if not prices_df.empty and "price_spread" in prices_df.columns and "crop_name" in prices_df.columns:
        src = prices_df.dropna(subset=["price_spread", "crop_name"])
        fig = px.box(
            src, x="crop_name", y="price_spread",
            color_discrete_sequence=[COLORS["primary"]],
            labels={"price_spread": "Price Spread (₹/Qtl)", "crop_name": "Crop"},
        )
        fig = _apply_theme(fig, "Price Spread (Max − Min) by Crop", height=360)
        fig.update_layout(xaxis_title="Crop", yaxis_title="Price Spread (₹/Qtl)")
        return fig

    # Approximation: use price_vs_msp range per crop
    if df.empty or "price_vs_msp" not in df.columns:
        return _empty_fig("Price spread data unavailable.")

    grp = (
        df.dropna(subset=["modal_price"])
        .groupby("crop_name")["modal_price"]
        .agg(["max", "min"])
        .reset_index()
    )
    grp["spread"] = grp["max"] - grp["min"]
    grp = grp.sort_values("spread", ascending=False)

    fig = px.bar(
        grp, x="crop_name", y="spread",
        color_discrete_sequence=[COLORS["secondary"]],
        labels={"spread": "Price Spread (₹/Qtl)", "crop_name": "Crop"},
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Spread: ₹%{y:,.0f}<extra></extra>",
    )
    fig = _apply_theme(fig, "Price Spread (Max − Min Modal Price) by Crop", height=360)
    fig.update_layout(xaxis_title="Crop", yaxis_title="Price Spread (₹/Qtl)")
    return fig


# ── Transport Charts ──────────────────────────────────────────────────────────

def create_transit_by_warehouse(transport_df: pd.DataFrame) -> go.Figure:
    """Bar – average transit time by warehouse."""
    if transport_df.empty or "warehouse" not in transport_df.columns:
        return _empty_fig("Transport data unavailable.")

    grp = (
        transport_df.dropna(subset=["transit_hours_clean", "warehouse"])
        .groupby("warehouse")["transit_hours_clean"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    grp.columns = ["Warehouse", "Avg Transit (hrs)"]

    fig = px.bar(
        grp, x="Warehouse", y="Avg Transit (hrs)",
        color_discrete_sequence=[COLORS["primary"]],
        labels={"Avg Transit (hrs)": "Avg Transit Time (hrs)"},
    )
    fig.add_hline(y=24, line_dash="dash", line_color=COLORS["danger"],
                  annotation_text="24h threshold", annotation_position="top right")
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Avg Transit: %{y:.1f} hrs<extra></extra>",
    )
    fig = _apply_theme(fig, "Average Transit Time by Warehouse", height=360)
    fig.update_layout(xaxis_title="Warehouse", yaxis_title="Avg Transit Time (hrs)")
    return fig


def create_distance_by_warehouse(transport_df: pd.DataFrame) -> go.Figure:
    """Bar – average distance by warehouse."""
    if transport_df.empty or "warehouse" not in transport_df.columns:
        return _empty_fig("Distance data unavailable.")

    grp = (
        transport_df.dropna(subset=["distance_km", "warehouse"])
        .groupby("warehouse")["distance_km"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    grp.columns = ["Warehouse", "Avg Distance (km)"]

    fig = px.bar(
        grp, x="Warehouse", y="Avg Distance (km)",
        color_discrete_sequence=[COLORS["secondary"]],
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Avg Distance: %{y:.1f} km<extra></extra>",
    )
    fig = _apply_theme(fig, "Average Distance by Warehouse", height=340)
    fig.update_layout(xaxis_title="Warehouse", yaxis_title="Avg Distance (km)")
    return fig


def create_transit_distribution(transport_df: pd.DataFrame) -> go.Figure:
    """Histogram – transit hours distribution."""
    if transport_df.empty or "transit_hours_clean" not in transport_df.columns:
        return _empty_fig("Transit distribution data unavailable.")

    vals = transport_df["transit_hours_clean"].dropna()
    if vals.empty:
        return _empty_fig("No valid transit hour values.")

    fig = go.Figure(go.Histogram(
        x=vals,
        nbinsx=40,
        marker_color=COLORS["primary"],
        opacity=0.82,
        hovertemplate="Hours: %{x:.1f}<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=24, line_dash="dash", line_color=COLORS["danger"], line_width=2,
                  annotation_text="24h threshold", annotation_position="top right",
                  annotation_font_color=COLORS["danger"])
    fig = _apply_theme(fig, "Transit Time Distribution", height=340)
    fig.update_layout(xaxis_title="Transit Hours", yaxis_title="Trip Count")
    return fig


def create_warehouse_volume(transport_df: pd.DataFrame, main_df: pd.DataFrame) -> go.Figure:
    """Bar – warehouse volume from transport or approximated."""
    if not transport_df.empty and "warehouse" in transport_df.columns:
        grp = transport_df.groupby("warehouse").size().sort_values(ascending=False).reset_index()
        grp.columns = ["Warehouse", "Trip Count"]
        y_col, y_label = "Trip Count", "Number of Trips"
    else:
        return _empty_fig("Warehouse volume data unavailable.")

    fig = px.bar(
        grp, x="Warehouse", y=y_col,
        color_discrete_sequence=[COLORS["primary"]],
        labels={y_col: y_label},
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>" + y_label + ": %{y:,}<extra></extra>",
    )
    fig = _apply_theme(fig, "Trip Volume by Warehouse", height=320)
    fig.update_layout(xaxis_title="Warehouse", yaxis_title=y_label)
    return fig


# ── Weather Charts ────────────────────────────────────────────────────────────

def create_rainfall_arrival_dual(daily_df: pd.DataFrame) -> go.Figure:
    """Dual-axis line – rainfall vs daily arrivals."""
    if daily_df.empty:
        return _empty_fig("No weather data available.")

    fig = go.Figure()

    if "total_rainfall_mm" in daily_df.columns:
        fig.add_trace(go.Bar(
            x=daily_df["date"], y=daily_df["total_rainfall_mm"],
            name="Rainfall (mm)",
            marker_color=COLORS["secondary"],
            opacity=0.65,
            yaxis="y",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Rainfall: %{y:.1f} mm<extra></extra>",
        ))

    if "total_arrival_qtl" in daily_df.columns:
        fig.add_trace(go.Scatter(
            x=daily_df["date"], y=daily_df["total_arrival_qtl"],
            name="Daily Arrivals (Qtl)",
            mode="lines",
            line=dict(color=COLORS["primary"], width=2),
            yaxis="y2",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
        ))

    fig = _apply_theme(fig, "Rainfall and Crop Arrival Trend", height=360)
    _axis_base = dict(
        gridcolor=COLORS["border"],
        gridwidth=1,
        linecolor=COLORS["border"],
        tickfont=dict(size=11, color=COLORS["text_muted"]),
        title_font=dict(size=12, color=COLORS["text"]),
        zeroline=False,
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis=dict(**_axis_base, title="Rainfall (mm)", showgrid=True),
        yaxis2=dict(**_axis_base, title="Daily Arrivals (Qtl)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_rainfall_scatter(daily_df: pd.DataFrame) -> go.Figure:
    """Scatter – rainfall vs arrivals with trendline."""
    if daily_df.empty:
        return _empty_fig("No weather data available.")

    cols = [c for c in ["total_rainfall_mm", "total_arrival_qtl"] if c in daily_df.columns]
    if len(cols) < 2:
        return _empty_fig("Missing rainfall or arrival columns.")

    src = daily_df[cols].dropna()
    if len(src) < 3:
        return _empty_fig("Insufficient data for scatter analysis.")

    corr = src["total_rainfall_mm"].corr(src["total_arrival_qtl"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=src["total_rainfall_mm"],
        y=src["total_arrival_qtl"],
        mode="markers",
        marker=dict(color=COLORS["primary"], size=7, opacity=0.65),
        hovertemplate="Rainfall: %{x:.1f} mm<br>Arrivals: %{y:,.0f} Qtl<extra></extra>",
        name="Daily",
    ))

    # Manual OLS trendline via numpy
    try:
        x = src["total_rainfall_mm"].to_numpy(dtype=float)
        y = src["total_arrival_qtl"].to_numpy(dtype=float)
        m, b = np.polyfit(x, y, 1)
        x_range = np.linspace(x.min(), x.max(), 100)
        fig.add_trace(go.Scatter(
            x=x_range, y=m * x_range + b,
            mode="lines",
            line=dict(color=COLORS["accent"], width=2, dash="dash"),
            name="Trend (OLS)",
            hoverinfo="skip",
        ))
    except Exception:
        pass
    fig = _apply_theme(fig, f"Rainfall vs Crop Arrivals  |  Correlation: {corr:.3f}", height=360)
    fig.update_layout(
        xaxis_title="Total Rainfall (mm)",
        yaxis_title="Total Arrivals (Qtl)",
        annotations=[dict(
            x=0.02, y=-0.18, xref="paper", yref="paper",
            text="Note: Correlation indicates statistical association, not causation.",
            showarrow=False,
            font=dict(size=10, color=COLORS["neutral"]),
            align="left",
        )],
    )
    return fig


def create_temperature_trend(daily_df: pd.DataFrame) -> go.Figure:
    """Line – temperature over time."""
    if daily_df.empty or "avg_temperature_c" not in daily_df.columns:
        return _empty_fig("Temperature data unavailable.")

    fig = go.Figure(go.Scatter(
        x=daily_df["date"], y=daily_df["avg_temperature_c"],
        mode="lines",
        line=dict(color="#e05c2e", width=2),
        fill="tozeroy",
        fillcolor="rgba(224,92,46,0.08)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Temp: %{y:.1f}°C<extra></extra>",
    ))
    fig = _apply_theme(fig, "Average Daily Temperature (°C)", height=300)
    fig.update_layout(xaxis_title="Date", yaxis_title="Temperature (°C)", showlegend=False)
    return fig


def create_humidity_trend(daily_df: pd.DataFrame) -> go.Figure:
    """Line – humidity over time."""
    if daily_df.empty or "avg_humidity_percent" not in daily_df.columns:
        return _empty_fig("Humidity data unavailable.")

    fig = go.Figure(go.Scatter(
        x=daily_df["date"], y=daily_df["avg_humidity_percent"],
        mode="lines",
        line=dict(color="#3d7ab5", width=2),
        fill="tozeroy",
        fillcolor="rgba(61,122,181,0.08)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Humidity: %{y:.1f}%<extra></extra>",
    ))
    fig = _apply_theme(fig, "Average Daily Humidity (%)", height=300)
    fig.update_layout(xaxis_title="Date", yaxis_title="Humidity (%)", showlegend=False)
    return fig


# ── Helper ────────────────────────────────────────────────────────────────────

def _empty_fig(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        **CHART_THEME,
        height=280,
        annotations=[dict(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=13, color=COLORS["neutral"]),
        )],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig
