"""
utils.py
--------
Shared helpers: KPI card renderer, section headers, download buttons, etc.
"""

import io
import pandas as pd
import streamlit as st


def kpi_card(label: str, value: str, card_class: str = "", delta_text: str = "") -> str:
    """Return HTML for a single KPI card."""
    delta_html = f'<div class="kpi-delta">{delta_text}</div>' if delta_text else ""
    return f"""
    <div class="kpi-card {card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def render_kpi_row(cards: list[dict]):
    """
    Render a row of KPI cards.
    Each dict has keys: label, value, card_class (optional), delta (optional).
    """
    n = len(cards)
    cols = st.columns(n)
    for col, card in zip(cols, cards):
        with col:
            st.markdown(
                kpi_card(
                    label=card["label"],
                    value=card["value"],
                    card_class=card.get("card_class", ""),
                    delta_text=card.get("delta", ""),
                ),
                unsafe_allow_html=True,
            )


def page_header(title: str, subtitle: str):
    """Render the standardized page header."""
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="mf-divider">', unsafe_allow_html=True)


def download_csv_button(df: pd.DataFrame, filename: str = "mandiflow_export.csv", label: str = "Download Filtered Data"):
    """Render a CSV download button for the given DataFrame."""
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv",
    )


def safe_num(val, default=0.0):
    """Return val if not NaN, else default."""
    import numpy as np
    return default if (val is None or (isinstance(val, float) and np.isnan(val))) else val


def chart_config():
    """Standard Plotly chart config dict for st.plotly_chart."""
    return {
        "displaylogo": False,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "responsive": True,
    }
