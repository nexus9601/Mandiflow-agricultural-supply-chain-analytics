"""MandiFlow – Weather Impact Page"""

import numpy as np
import pandas as pd
import streamlit as st

from src import charts, metrics, styles


def render(df: pd.DataFrame, daily_df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "Agro-Climatic & Environmental Dynamics",
        "Investigate precipitation, thermal patterns, and ambient moisture correlations against agricultural arrivals and market supply flows.",
        badge="CLIMATE ANALYTICS",
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
        (c1, "Avg Temperature",          f"{kpis['avg_temp']:.1f} °C" if not np.isnan(kpis['avg_temp']) else "—", "amber",   "Daily Mean", "🌡️"),
        (c2, "Total Rainfall",           f"{kpis['total_rainfall']:.0f} mm" if not np.isnan(kpis['total_rainfall']) else "—", "sky",     "Precipitation", "🌧️"),
        (c3, "Avg Humidity",             f"{kpis['avg_humidity']:.1f}%" if not np.isnan(kpis['avg_humidity']) else "—", "sky",     "Relative Moisture", "💧"),
        (c4, "Rain–Arrival Correlation",  corr_str, "emerald", "Pearson r Coefficient", "📈"),
    ]
    for col, label, val, variant, delta, icon in kpi_data:
        with col:
            st.markdown(styles.kpi_card(label, val, variant=variant, delta=delta, icon=icon), unsafe_allow_html=True)

    # ── Chart Row 1 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Precipitation & Daily Inflow Overlay", "DUAL AXIS"), unsafe_allow_html=True)
    st.plotly_chart(charts.create_rainfall_arrival_dual(daily_df),
                    use_container_width=True, config={"displayModeBar": False})

    # ── Chart Row 2 ───────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Climatic Distribution & Correlation Analysis", "ENVIRONMENTAL TRENDS"), unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l:
        st.plotly_chart(charts.create_rainfall_scatter(daily_df),
                        use_container_width=True, config={"displayModeBar": False})
    with c_r:
        st.plotly_chart(charts.create_temperature_trend(daily_df),
                        use_container_width=True, config={"displayModeBar": False})

    # ── Humidity ──────────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Ambient Moisture Trajectory", "HUMIDITY"), unsafe_allow_html=True)
    st.plotly_chart(charts.create_humidity_trend(daily_df),
                    use_container_width=True, config={"displayModeBar": False})

    # ── Weather Impact Summary ────────────────────────────────────────────────
    _render_weather_summary(daily_df, kpis)


def _render_weather_summary(daily_df: pd.DataFrame, kpis: dict) -> None:
    parts = []

    if "total_rainfall_mm" in daily_df.columns and daily_df["total_rainfall_mm"].notna().any():
        rainiest_row = daily_df.loc[daily_df["total_rainfall_mm"].idxmax()]
        parts.append(
            f'<div class="insight-item">'
            f'<div class="insight-label">Peak Precipitation Event</div>'
            f'<div style="font-weight: 700; color: #0284c7; margin-top: 2px;">{str(rainiest_row["date"])[:10]}</div>'
            f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{rainiest_row["total_rainfall_mm"]:.1f} mm recorded</div>'
            f'</div>'
        )

    if "total_arrival_qtl" in daily_df.columns and daily_df["total_arrival_qtl"].notna().any():
        hi_idx = daily_df["total_arrival_qtl"].idxmax()
        lo_idx = daily_df["total_arrival_qtl"].idxmin()
        hi_row = daily_df.loc[hi_idx]
        lo_row = daily_df.loc[lo_idx]
        parts.append(
            f'<div class="insight-item">'
            f'<div class="insight-label">Max Daily Inflow Day</div>'
            f'<div style="font-weight: 700; color: #059669; margin-top: 2px;">{str(hi_row["date"])[:10]}</div>'
            f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{hi_row["total_arrival_qtl"]:,.0f} Quintals arrived</div>'
            f'</div>'
        )
        parts.append(
            f'<div class="insight-item">'
            f'<div class="insight-label">Min Daily Inflow Day</div>'
            f'<div style="font-weight: 700; color: #dc2626; margin-top: 2px;">{str(lo_row["date"])[:10]}</div>'
            f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{lo_row["total_arrival_qtl"]:,.0f} Quintals arrived</div>'
            f'</div>'
        )

    corr = kpis.get("rain_arrival_corr", float("nan"))
    if not np.isnan(corr):
        direction = "positive" if corr > 0 else "negative"
        strength = "strong" if abs(corr) > 0.5 else ("moderate" if abs(corr) > 0.3 else "weak")
        parts.append(
            f'<div class="insight-item">'
            f'<div class="insight-label">Rainfall–Inflow Association</div>'
            f'<div style="font-weight: 700; color: #0f172a; margin-top: 2px;">{corr:.3f} ({strength} {direction})</div>'
            f'<div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">Denotes linear statistical correlation</div>'
            f'</div>'
        )

    if parts:
        st.markdown(
            f"""
<div class="insight-card">
  <h4>🌦️ Agro-Climatic Key Takeaways</h4>
  <div class="insight-grid">
    {''.join(parts)}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
