"""
manual_dashboard_view.py
------------------------
MandiFlow — Manual Dashboard (Streamlit Edition)

The full-featured MandiFlow Streamlit dashboard is built in:
    streamlit_app/mandiflow_app.py

It provides:
  • Overview KPIs (arrivals, prices, MSP, transit, long-transit rate)
  • Mandi Analysis  (top mandis, district distribution, trend, performance table)
  • Crop & Price    (MSP gap, price crash rate, price trend, risk table)
  • Transport       (transit time, distance, distribution, route performance)
  • Weather Impact  (rainfall-arrival trend, scatter, temperature, humidity)
  • Data Quality    (missing values, negative records, column coverage)

Launch with:
    streamlit run streamlit_app/mandiflow_app.py

This Dash module renders a dashboard gateway card for users arriving
via the existing Dash application navigation.
"""

from dash import html, dcc
import pandas as pd
from utils.data_store import get_data


# ──────────────────────────────────────────────────────────────────────────────
# Helper: quick stat from loaded df
# ──────────────────────────────────────────────────────────────────────────────

def _safe_fmt_price(val):
    try:
        return f"₹{float(val):,.0f}"
    except Exception:
        return "N/A"


def _safe_fmt_qty(val):
    try:
        v = float(val)
        if v >= 1_000_000:
            return f"{v / 1_000_000:.2f} M Qtl"
        return f"{v:,.0f} Qtl"
    except Exception:
        return "N/A"


def _stat_card(label, value, accent="#2d6a4f"):
    return html.Div([
        html.Div(label, style={
            "fontSize": "0.7rem", "fontWeight": "600", "color": "#6b7c5a",
            "textTransform": "uppercase", "letterSpacing": "0.06em",
            "marginBottom": "0.3rem",
        }),
        html.Div(value, style={
            "fontSize": "1.5rem", "fontWeight": "700", "color": accent,
            "lineHeight": "1.1", "letterSpacing": "-0.02em",
        }),
    ], style={
        "background": "#fff",
        "border": "1px solid #dde8d5",
        "borderTop": f"3px solid {accent}",
        "borderRadius": "8px",
        "padding": "1rem 1.2rem",
        "flex": "1",
        "boxShadow": "0 1px 4px rgba(30,77,43,0.06)",
        "minWidth": "140px",
    })


def layout():
    # Load quick stats from the dataset
    df = get_data()

    total_arrivals = df["arrival_quantity_qtl"].sum() if "arrival_quantity_qtl" in df.columns else None
    avg_price      = df["modal_price"].mean() if "modal_price" in df.columns else None
    avg_msp        = df["msp"].mean() if "msp" in df.columns else None
    n_mandis       = df["mandi_name"].nunique() if "mandi_name" in df.columns else None
    n_crops        = df["crop_name"].nunique() if "crop_name" in df.columns else None
    n_records      = len(df)

    price_crash_count = 0
    if "modal_price" in df.columns and "msp" in df.columns:
        mask = df["modal_price"].notna() & df["msp"].notna()
        price_crash_count = int((df.loc[mask, "modal_price"] < df.loc[mask, "msp"]).sum())

    long_transit_rate = None
    if "avg_transit_hours" in df.columns:
        clean = df["avg_transit_hours"].copy()
        clean = clean[clean >= 0]
        if len(clean) > 0:
            long_transit_rate = (clean > 24).mean() * 100

    # ──────────────────────────────────────────────────────────────────────────
    return html.Div([

        # ── Page header ──────────────────────────────────────────────────────
        html.Div([
            html.Div("MandiFlow", style={
                "fontSize": "1.5rem", "fontWeight": "700", "color": "var(--cream)",
                "letterSpacing": "-0.02em",
            }),
            html.Div("Agricultural Supply Chain Analytics — Manual Dashboard", style={
                "fontSize": "0.85rem", "color": "var(--text-muted)", "marginTop": "0.15rem",
            }),
        ], style={
            "marginBottom": "1.5rem",
            "paddingBottom": "1rem",
            "borderBottom": "2px solid #2d4a2d",
        }),

        # ── Quick stats row ───────────────────────────────────────────────────
        html.Div([
            _stat_card("Total Arrivals",      _safe_fmt_qty(total_arrivals)),
            _stat_card("Avg Modal Price",     _safe_fmt_price(avg_price)),
            _stat_card("Avg MSP",             _safe_fmt_price(avg_msp)),
            _stat_card("Price Crash Records", f"{price_crash_count:,}", accent="#c0392b"),
            _stat_card("Active Mandis",       f"{n_mandis:,}" if n_mandis else "N/A"),
            _stat_card("Crops Tracked",       f"{n_crops:,}" if n_crops else "N/A"),
            _stat_card("Long Transit Rate",
                       f"{long_transit_rate:.1f}%" if long_transit_rate is not None else "N/A",
                       accent="#d4a017"),
        ], style={
            "display": "flex", "gap": "0.8rem", "flexWrap": "wrap", "marginBottom": "1.5rem",
        }),

        # ── Streamlit dashboard gateway card ──────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("🌾", style={"fontSize": "2.2rem"}),
                    html.Div([
                        html.Span("MandiFlow Streamlit Dashboard", style={
                            "fontSize": "1.1rem", "fontWeight": "700",
                            "color": "var(--text-primary)", "display": "block",
                        }),
                        html.Span("6-page interactive analytics application", style={
                            "fontSize": "0.82rem", "color": "var(--text-muted)",
                        }),
                    ]),
                ], style={"display": "flex", "alignItems": "center", "gap": "0.8rem",
                          "marginBottom": "1.2rem"}),

                html.P(
                    "The full MandiFlow analytics dashboard is available as a standalone Streamlit application. "
                    "It includes all analytical pages, global filters, interactive Plotly charts, "
                    "KPI cards, data quality monitoring, and methodology documentation.",
                    style={"color": "var(--text-muted)", "fontSize": "0.87rem",
                           "marginBottom": "1.2rem", "lineHeight": "1.6"},
                ),

                # ── Feature list ─────────────────────────────────────────────
                html.Div([
                    html.Div("Dashboard Pages:", style={
                        "fontSize": "0.78rem", "fontWeight": "600", "color": "var(--text-muted)",
                        "textTransform": "uppercase", "letterSpacing": "0.05em",
                        "marginBottom": "0.7rem",
                    }),
                    html.Div([
                        _feature_pill("Overview",       "#2d6a4f"),
                        _feature_pill("Mandi Analysis", "#2d6a4f"),
                        _feature_pill("Crop & Price",   "#2d6a4f"),
                        _feature_pill("Transport",      "#2d6a4f"),
                        _feature_pill("Weather Impact", "#2d6a4f"),
                        _feature_pill("Data Quality",   "#2d6a4f"),
                    ], style={"display": "flex", "flexWrap": "wrap", "gap": "0.5rem",
                              "marginBottom": "1.4rem"}),
                ]),

                # ── Launch instructions ───────────────────────────────────────
                html.Div([
                    html.Div("Launch Command", style={
                        "fontSize": "0.78rem", "fontWeight": "600", "color": "var(--text-muted)",
                        "textTransform": "uppercase", "letterSpacing": "0.05em",
                        "marginBottom": "0.5rem",
                    }),
                    html.Pre(
                        "streamlit run streamlit_app/mandiflow_app.py",
                        style={
                            "background": "#1a2e1a",
                            "color": "#95d5b2",
                            "fontFamily": "monospace",
                            "fontSize": "0.88rem",
                            "padding": "0.8rem 1.1rem",
                            "borderRadius": "6px",
                            "margin": "0 0 1.2rem 0",
                            "overflowX": "auto",
                        },
                    ),
                    html.P(
                        "Or use the convenience script: run_dashboard.bat",
                        style={"fontSize": "0.8rem", "color": "var(--text-muted)", "margin": "0"},
                    ),
                ]),

            ], style={
                "padding": "1.6rem",
                "background": "rgba(45, 106, 79, 0.05)",
                "border": "1px solid #3a6040",
                "borderRadius": "10px",
                "maxWidth": "800px",
            }),

        ], className="mandi-card"),

        # ── Dataset summary footer ────────────────────────────────────────────
        html.Div([
            html.Span(f"Dataset: {n_records:,} records", style={
                "fontSize": "0.78rem", "color": "var(--text-muted)",
            }),
            html.Span(" · ", style={"color": "var(--text-muted)"}),
            html.Span(f"{n_mandis:,} mandis", style={"fontSize": "0.78rem", "color": "var(--text-muted)"}),
            html.Span(" · ", style={"color": "var(--text-muted)"}),
            html.Span(f"{n_crops:,} crops", style={"fontSize": "0.78rem", "color": "var(--text-muted)"}),
        ], style={"marginTop": "1rem", "textAlign": "center", "padding": "0.8rem 0"}),

    ])


def _feature_pill(label: str, color: str = "#2d6a4f"):
    return html.Span(label, style={
        "background": f"rgba(45,106,79,0.12)",
        "color": color,
        "border": f"1px solid rgba(45,106,79,0.3)",
        "padding": "0.2rem 0.7rem",
        "borderRadius": "20px",
        "fontSize": "0.78rem",
        "fontWeight": "500",
    })

