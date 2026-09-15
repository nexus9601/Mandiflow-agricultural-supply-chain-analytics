"""MandiFlow – Weather Impact Page"""

import numpy as np
import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, daily_df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "Weather Impact",
        "Explore relationships between weather conditions and agricultural arrivals.",
    ), unsafe_allow_html=True)

    if daily_df.empty:
        st.markdown(styles.empty_state("Weather data not available."), unsafe_allow_html=True)
        return

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpis = metrics.weather_kpis(daily_df)
    c1, c2, c3, c4 = st.columns(4)
    corr_val = kpis["rain_arrival_corr"]
    corr_str = f"{corr_val:.3f}" if not np.isnan(corr_val) else "—"
    kpi_data = [
        (c1, "Avg Temperature",            f"{kpis['avg_temp']:.1f} °C" if not np.isnan(kpis['avg_temp']) else "—", "default"),
        (c2, "Total Rainfall",             f"{kpis['total_rainfall']:.0f} mm" if not np.isnan(kpis['total_rainfall']) else "—", "default"),
        (c3, "Avg Humidity",               f"{kpis['avg_humidity']:.1f}%" if not np.isnan(kpis['avg_humidity']) else "—", "default"),
        (c4, "Rainfall–Arrival Correlation", corr_str, "default"),
    ]
    for col, label, val, variant in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant), unsafe_allow_html=True)

    st.info(
        "Correlation indicates statistical association, not causation. "
        "Weather is aggregated at the daily level as there is no direct sensor-to-mandi mapping.",
        icon="ℹ️",
    )

    st.markdown("<hr class='mf-divider'>", unsafe_allow_html=True)

    # ── Chart Row 1 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Rainfall & Arrival Trends"), unsafe_allow_html=True)
    st.plotly_chart(charts.create_rainfall_arrival_dual(daily_df),
                    width='stretch', config={"displayModeBar": False})

    # ── Chart Row 2 ───────────────────────────────────────────────────────────
    c_l, c_r = st.columns(2)
    with c_l:
        st.plotly_chart(charts.create_rainfall_scatter(daily_df),
                        width='stretch', config={"displayModeBar": False})
    with c_r:
        st.plotly_chart(charts.create_temperature_trend(daily_df),
                        width='stretch', config={"displayModeBar": False})

    # ── Humidity ──────────────────────────────────────────────────────────────
    st.plotly_chart(charts.create_humidity_trend(daily_df),
                    width='stretch', config={"displayModeBar": False})

    # ── Weather Impact Summary ────────────────────────────────────────────────
    st.markdown(styles.section_header("Weather Impact Summary"), unsafe_allow_html=True)

    insights_html = _weather_summary(daily_df, kpis)
    st.markdown(
        f'<div class="insight-card"><h4>Summary</h4>{insights_html}</div>',
        unsafe_allow_html=True,
    )


def _weather_summary(daily_df: pd.DataFrame, kpis: dict) -> str:
    parts = []

    if "total_rainfall_mm" in daily_df.columns and daily_df["total_rainfall_mm"].notna().any():
        rainiest_row = daily_df.loc[daily_df["total_rainfall_mm"].idxmax()]
        parts.append(
            f'<div class="insight-item"><span class="insight-label">Rainiest Day:</span> '
            f'{str(rainiest_row["date"])[:10]} — {rainiest_row["total_rainfall_mm"]:.1f} mm</div>'
        )

    if "total_arrival_qtl" in daily_df.columns and daily_df["total_arrival_qtl"].notna().any():
        hi_idx = daily_df["total_arrival_qtl"].idxmax()
        lo_idx = daily_df["total_arrival_qtl"].idxmin()
        hi_row = daily_df.loc[hi_idx]
        lo_row = daily_df.loc[lo_idx]
        parts.append(
            f'<div class="insight-item"><span class="insight-label">Highest Arrival Day:</span> '
            f'{str(hi_row["date"])[:10]} — {hi_row["total_arrival_qtl"]:,.0f} Qtl</div>'
        )
        parts.append(
            f'<div class="insight-item"><span class="insight-label">Lowest Arrival Day:</span> '
            f'{str(lo_row["date"])[:10]} — {lo_row["total_arrival_qtl"]:,.0f} Qtl</div>'
        )

    corr = kpis.get("rain_arrival_corr", float("nan"))
    if not np.isnan(corr):
        direction = "positive" if corr > 0 else "negative"
        strength = "strong" if abs(corr) > 0.5 else ("moderate" if abs(corr) > 0.3 else "weak")
        parts.append(
            f'<div class="insight-item"><span class="insight-label">Rainfall–Arrival Correlation:</span> '
            f'{corr:.3f} ({strength} {direction} association). '
            f'This does not imply causation.</div>'
        )

    return "".join(parts) if parts else '<div class="insight-item">Insufficient data for summary.</div>'
