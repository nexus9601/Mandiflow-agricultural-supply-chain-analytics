"""MandiFlow – Transport Page"""

import numpy as np
import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, transport_df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "Logistics & Transit Optimization",
        "Monitor fleet dispatch efficiency, long-transit corridor risks (>24h), warehouse reception throughput, and transit bottlenecks.",
        badge="LOGISTICS INTELLIGENCE",
    ), unsafe_allow_html=True)

    use_transport = not transport_df.empty

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpis = metrics.transport_kpis(transport_df, df)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_data = [
        (c1, "Total Trips",       metrics.fmt_int(kpis["total_trips"]),        "emerald", "Fleet Dispatches", "🚛"),
        (c2, "Avg Transit Time",  metrics.fmt_hrs(kpis["avg_transit"]),        "sky",     "Door-to-Mandi", "⏱️"),
        (c3, "Average Distance",  metrics.fmt_km(kpis["avg_distance"]),        "default", "Haul Distance", "🛣️"),
        (c4, "Long Transit Rate", metrics.fmt_pct(kpis["long_transit_rate"]), "amber",   "> 24h Threshold", "⚠️"),
        (c5, "Longest Corridor",  str(kpis["longest_route"]),                  "sky",     "Max Distance", "📍"),
        (c6, "Top Warehouse",     str(kpis["top_warehouse"]),                  "emerald", "Primary Hub", "🏭"),
    ]
    for col, label, val, variant, delta, icon in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant=variant, delta=delta, icon=icon), unsafe_allow_html=True)

    if not use_transport:
        st.info("Raw transport data not found. Showing aggregated values from integrated dataset.")
        _render_from_integrated(df)
        return

    # ── Chart Row 1 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Warehouse Fleet Performance", "LOGISTICS HUBS"), unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l:
        st.plotly_chart(charts.create_transit_by_warehouse(transport_df),
                        width='stretch', config={"displayModeBar": False})
    with c_r:
        st.plotly_chart(charts.create_distance_by_warehouse(transport_df),
                        width='stretch', config={"displayModeBar": False})

    # ── Chart Row 2 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Transit Duration Distribution & Volumes", "CORRIDOR VELOCITY"), unsafe_allow_html=True)
    c_l2, c_r2 = st.columns(2)
    with c_l2:
        st.plotly_chart(charts.create_transit_distribution(transport_df),
                        width='stretch', config={"displayModeBar": False})
    with c_r2:
        st.plotly_chart(charts.create_warehouse_volume(transport_df, df),
                        width='stretch', config={"displayModeBar": False})

    # ── Mandi-to-Warehouse Route Table ────────────────────────────────────────
    st.markdown(styles.section_header("Mandi-to-Warehouse Corridor Performance", "ROUTE BENCHMARKS"), unsafe_allow_html=True)

    route_grp_cols = [c for c in ["mandi_id", "warehouse"] if c in transport_df.columns]
    if route_grp_cols:
        route = (
            transport_df
            .groupby(route_grp_cols, as_index=False)
            .agg(
                trip_count=("mandi_id", "count"),
                avg_distance_km=("distance_km", "mean"),
                avg_transit_hours=("transit_hours_clean", "mean"),
                long_transit_count=("long_transit_flag", "sum"),
                long_transit_rate=("long_transit_flag", "mean"),
            )
            .sort_values("long_transit_rate", ascending=False)
        )
        route_display = route.copy()
        route_display["long_transit_rate"] = (route_display["long_transit_rate"] * 100).round(1).astype(str) + "%"
        route_display["avg_distance_km"] = route_display["avg_distance_km"].map(
            lambda x: f"{x:.1f} km" if not np.isnan(x) else "—"
        )
        route_display["avg_transit_hours"] = route_display["avg_transit_hours"].map(
            lambda x: f"{x:.1f} hrs" if not np.isnan(x) else "—"
        )
        route_display.columns = [c.replace("_", " ").title() for c in route_display.columns]
        st.dataframe(route_display, use_container_width=True, hide_index=True)

    # ── Logistics Risk Section ────────────────────────────────────────────────
    _logistics_risk(transport_df)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        "📥 Download Transport Logistics Data (CSV)",
        data=transport_df.to_csv(index=False).encode("utf-8"),
        file_name="mandiflow_transport.csv",
        mime="text/csv",
    )


def _render_from_integrated(df: pd.DataFrame) -> None:
    """Fallback charts using integrated df averages."""
    if "avg_transit_hours" in df.columns and "mandi_name" in df.columns:
        import plotly.express as px
        from src.styles import COLORS, CHART_THEME, AXIS_STYLE

        grp = (
            df.dropna(subset=["avg_transit_hours"])
            .groupby("mandi_name")["avg_transit_hours"]
            .mean()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )
        grp.columns = ["Mandi", "Avg Transit (hrs)"]
        fig = px.bar(grp, x="Mandi", y="Avg Transit (hrs)",
                     color_discrete_sequence=[COLORS["primary"]],
                     title="Average Transit Hours by Mandi (from integrated dataset)")
        fig.update_traces(marker=dict(cornerradius=6))
        fig.update_layout(**CHART_THEME, xaxis=dict(**AXIS_STYLE), yaxis=dict(**AXIS_STYLE))
        st.plotly_chart(fig, width='stretch')


def _logistics_risk(transport_df: pd.DataFrame) -> None:
    """Display automated logistics risk insights."""
    if transport_df.empty:
        return

    parts = []

    if "warehouse" in transport_df.columns and "mandi_id" in transport_df.columns and "long_transit_flag" in transport_df.columns:
        route_risk = (
            transport_df
            .groupby(["mandi_id", "warehouse"])["long_transit_flag"]
            .mean()
        )
        if not route_risk.empty:
            worst = route_risk.idxmax()
            rate = route_risk.max() * 100
            parts.append(
                f'<div class="insight-item">'
                f'<div class="insight-label">Critical Long-Transit Route</div>'
                f'<div style="font-weight: 700; color: #dc2626; margin-top: 2px;">{worst[0]} → {worst[1]}</div>'
                f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{rate:.1f}% trips exceed the 24h operational limit</div>'
                f'</div>'
            )

    if "warehouse" in transport_df.columns:
        wh_vol = transport_df["warehouse"].value_counts()
        if not wh_vol.empty:
            parts.append(
                f'<div class="insight-item">'
                f'<div class="insight-label">Highest Throughput Warehouse</div>'
                f'<div style="font-weight: 700; color: #0f172a; margin-top: 2px;">{wh_vol.index[0]}</div>'
                f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{wh_vol.iloc[0]:,} dispatches handled</div>'
                f'</div>'
            )

    if "mandi_id" in transport_df.columns and "transit_hours_clean" in transport_df.columns:
        mandi_avg = transport_df.groupby("mandi_id")["transit_hours_clean"].mean()
        if not mandi_avg.empty:
            worst_mandi = mandi_avg.idxmax()
            parts.append(
                f'<div class="insight-item">'
                f'<div class="insight-label">Mandi with Peak Transit Latency</div>'
                f'<div style="font-weight: 700; color: #d97706; margin-top: 2px;">{worst_mandi}</div>'
                f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{mandi_avg.max():.1f} hrs average transit duration</div>'
                f'</div>'
            )

    if parts:
        st.markdown(
            f"""
<div class="insight-card">
  <h4>🚛 Automated Logistics Risk Intelligence</h4>
  <div class="insight-grid">
    {''.join(parts)}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
