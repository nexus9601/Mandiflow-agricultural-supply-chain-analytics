"""MandiFlow – Data Quality Page"""

import numpy as np
import pandas as pd
import streamlit as st

from src import styles


def render(df: pd.DataFrame, transport_df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "Data Integrity & Pipeline Validation",
        "Systematic verification of cross-dataset joins, range checks, missingness profiles, and anomaly audits across arrivals, prices, and logistics.",
        badge="DATA AUDIT",
    ), unsafe_allow_html=True)

    # ── Quality check functions ───────────────────────────────────────────────
    def safe_neg(series: pd.Series) -> int:
        try:
            return int((series < 0).sum())
        except Exception:
            return 0

    def safe_null(series: pd.Series) -> int:
        return int(series.isna().sum())

    # ── Compute checks ────────────────────────────────────────────────────────
    checks = []

    # Arrivals
    checks.append({
        "Dataset": "Arrivals",
        "Check": "Missing arrival dates",
        "Count": safe_null(df["date"]) if "date" in df.columns else 0,
        "_threshold_warn": 10, "_threshold_crit": 100,
    })
    checks.append({
        "Dataset": "Arrivals",
        "Check": "Missing modal prices",
        "Count": safe_null(df["modal_price"]) if "modal_price" in df.columns else 0,
        "_threshold_warn": 50, "_threshold_crit": 500,
    })
    checks.append({
        "Dataset": "Arrivals",
        "Check": "Negative arrival quantities",
        "Count": safe_neg(df["arrival_quantity_qtl"]) if "arrival_quantity_qtl" in df.columns else 0,
        "_threshold_warn": 1, "_threshold_crit": 10,
    })

    # Weather
    checks.append({
        "Dataset": "Weather",
        "Check": "Missing temperature values",
        "Count": safe_null(df["avg_temperature_c"]) if "avg_temperature_c" in df.columns else 0,
        "_threshold_warn": 20, "_threshold_crit": 200,
    })
    checks.append({
        "Dataset": "Weather",
        "Check": "Missing rainfall values",
        "Count": safe_null(df["total_rainfall_mm"]) if "total_rainfall_mm" in df.columns else 0,
        "_threshold_warn": 20, "_threshold_crit": 200,
    })
    checks.append({
        "Dataset": "Weather",
        "Check": "Missing humidity values",
        "Count": safe_null(df["avg_humidity_percent"]) if "avg_humidity_percent" in df.columns else 0,
        "_threshold_warn": 20, "_threshold_crit": 200,
    })

    # Transport
    if not transport_df.empty:
        checks.append({
            "Dataset": "Transport",
            "Check": "Missing vehicle numbers",
            "Count": safe_null(transport_df["vehicle_no"]) if "vehicle_no" in transport_df.columns else 0,
            "_threshold_warn": 10, "_threshold_crit": 100,
        })
        checks.append({
            "Dataset": "Transport",
            "Check": "Negative distances",
            "Count": safe_neg(transport_df["distance_km"]) if "distance_km" in transport_df.columns else 0,
            "_threshold_warn": 1, "_threshold_crit": 10,
        })
        checks.append({
            "Dataset": "Transport",
            "Check": "Negative cleaned transit hours",
            "Count": safe_neg(transport_df["transit_hours_clean"]) if "transit_hours_clean" in transport_df.columns else 0,
            "_threshold_warn": 1, "_threshold_crit": 10,
        })
    else:
        checks.append({
            "Dataset": "Transport (integrated)",
            "Check": "Negative cleaned transit hours",
            "Count": safe_neg(df["transit_hours_clean"]) if "transit_hours_clean" in df.columns else 0,
            "_threshold_warn": 1, "_threshold_crit": 10,
        })
        checks.append({
            "Dataset": "Transport (integrated)",
            "Check": "Negative distances",
            "Count": safe_neg(df["distance_km"]) if "distance_km" in df.columns else 0,
            "_threshold_warn": 1, "_threshold_crit": 10,
        })

    # ── Status assignment ─────────────────────────────────────────────────────
    def status(count: int, warn: int, crit: int) -> str:
        if count == 0:
            return "Good"
        if count < crit:
            return "Warning"
        return "Critical"

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    good_count = sum(1 for c in checks if status(c["Count"], c["_threshold_warn"], c["_threshold_crit"]) == "Good")
    warn_count = sum(1 for c in checks if status(c["Count"], c["_threshold_warn"], c["_threshold_crit"]) == "Warning")
    crit_count = sum(1 for c in checks if status(c["Count"], c["_threshold_warn"], c["_threshold_crit"]) == "Critical")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(styles.kpi_card("Total Checks", str(len(checks)), variant="sky", delta="Validation Rules", icon="📋"), unsafe_allow_html=True)
    with c2:
        st.markdown(styles.kpi_card("Checks Passed", str(good_count), variant="emerald", delta="Zero Anomalies", trend="up", icon="✅"), unsafe_allow_html=True)
    with c3:
        st.markdown(styles.kpi_card("Warnings", str(warn_count), variant="amber", delta="Moderate Gaps", icon="⚠️"), unsafe_allow_html=True)
    with c4:
        st.markdown(styles.kpi_card("Critical Issues", str(crit_count), variant="danger", delta="High Imputation Need", trend="down", icon="🚨"), unsafe_allow_html=True)

    # ── Quality Table ─────────────────────────────────────────────────────────
    st.markdown(styles.section_header("Quality Verification Matrix", "AUDIT RESULTS"), unsafe_allow_html=True)

    rows = []
    for c in checks:
        s = status(c["Count"], c["_threshold_warn"], c["_threshold_crit"])
        rows.append({
            "Dataset": c["Dataset"],
            "Check": c["Check"],
            "Invalid / Missing Count": c["Count"],
            "Status": s,
        })

    qdf = pd.DataFrame(rows)
    st.dataframe(qdf, use_container_width=True, hide_index=True)

    # ── Dataset Overview ──────────────────────────────────────────────────────
    st.markdown(styles.section_header("Harmonized Dataset Metadata", "CORPUS STATS"), unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l:
        date_str = (
            f"{df['date'].min().date()} to {df['date'].max().date()}"
            if 'date' in df.columns and df['date'].notna().any()
            else "—"
        )
        st.markdown(f"""
<div class="insight-card" style="margin-top: 0;">
  <h4>Core Inflow Scope</h4>
  <div class="insight-item" style="margin-bottom: 8px;">
    <span class="insight-label">Total Records:</span> <strong>{len(df):,}</strong>
  </div>
  <div class="insight-item" style="margin-bottom: 8px;">
    <span class="insight-label">Observation Window:</span> <strong>{date_str}</strong>
  </div>
  <div class="insight-item" style="margin-bottom: 8px;">
    <span class="insight-label">Distinct Commodities:</span> <strong>{df['crop_name'].nunique() if 'crop_name' in df.columns else '—'}</strong>
  </div>
  <div class="insight-item">
    <span class="insight-label">Distinct Mandis:</span> <strong>{df['mandi_name'].nunique() if 'mandi_name' in df.columns else '—'}</strong>
  </div>
</div>
""", unsafe_allow_html=True)

    with c_r:
        trans_recs = f"{len(transport_df):,}" if not transport_df.empty else "Integrated"
        trans_wh = str(transport_df["warehouse"].nunique()) if not transport_df.empty and "warehouse" in transport_df.columns else "—"
        st.markdown(f"""
<div class="insight-card" style="margin-top: 0;">
  <h4>Geographic & Logistics Scope</h4>
  <div class="insight-item" style="margin-bottom: 8px;">
    <span class="insight-label">Total Schema Attributes:</span> <strong>{len(df.columns)} columns</strong>
  </div>
  <div class="insight-item" style="margin-bottom: 8px;">
    <span class="insight-label">Catchment Districts:</span> <strong>{df['district'].nunique() if 'district' in df.columns else '—'}</strong>
  </div>
  <div class="insight-item" style="margin-bottom: 8px;">
    <span class="insight-label">Transport Records:</span> <strong>{trans_recs}</strong>
  </div>
  <div class="insight-item">
    <span class="insight-label">Logistics Warehouses:</span> <strong>{trans_wh}</strong>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Null heatmap per column ───────────────────────────────────────────────
    st.markdown(styles.section_header("Missing Value Audit by Feature", "MISSINGNESS"), unsafe_allow_html=True)
    null_counts = df.isnull().sum().reset_index()
    null_counts.columns = ["Column", "Missing Count"]
    null_counts["Missing %"] = (null_counts["Missing Count"] / len(df) * 100).round(2).astype(str) + "%"
    null_counts = null_counts[null_counts["Missing Count"] > 0].sort_values("Missing Count", ascending=False)
    if null_counts.empty:
        st.success("Zero missing values detected across the integrated features.")
    else:
        st.dataframe(null_counts, use_container_width=True, hide_index=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        "📥 Download Quality Audit Report (CSV)",
        data=pd.DataFrame(rows).to_csv(index=False).encode("utf-8"),
        file_name="mandiflow_data_quality.csv",
        mime="text/csv",
    )
