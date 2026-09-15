"""
styles.py
---------
All custom CSS and Streamlit page configuration for MandiFlow dashboard.
"""

# ── Color palette ──────────────────────────────────────────────────────────────
GREEN_DARK    = "#1e4d2b"
GREEN_PRIMARY = "#2d6a4f"
GREEN_ACCENT  = "#52b788"
GREEN_LIGHT   = "#b7e4c7"
AMBER         = "#d4a017"
AMBER_LIGHT   = "#fde68a"
RED_SOFT      = "#c0392b"
RED_LIGHT     = "#fde8e8"
NEUTRAL_BG    = "#f7f9f5"
CARD_BG       = "#ffffff"
BORDER        = "#dde8d5"
TEXT_PRIMARY  = "#1a2e1a"
TEXT_MUTED    = "#6b7c5a"
TEXT_HEADING  = "#1e4d2b"

# ── Plotly chart template config ───────────────────────────────────────────────
CHART_COLORS = [
    "#2d6a4f", "#52b788", "#d4a017", "#74c69d", "#1e4d2b",
    "#95d5b2", "#c77dff", "#e07a5f", "#3d405b", "#81b29a",
]

PLOTLY_LAYOUT = dict(
    font_family="Inter, 'Segoe UI', sans-serif",
    font_color=TEXT_PRIMARY,
    paper_bgcolor=CARD_BG,
    plot_bgcolor=NEUTRAL_BG,
    margin=dict(l=40, r=30, t=48, b=40),
    title_font_size=14,
    title_font_color=TEXT_HEADING,
    legend=dict(
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor="#e8f0e4",
        linecolor=BORDER,
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor="#e8f0e4",
        linecolor=BORDER,
        tickfont=dict(size=11),
    ),
)

# ── CSS ───────────────────────────────────────────────────────────────────────
DASHBOARD_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global resets ────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

/* Remove default Streamlit top padding */
.main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 2rem;
    max-width: 1340px;
}

/* Hide default Streamlit header & footer */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Sidebar ──────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #1a2e1a !important;
    border-right: 1px solid #2d4a2d;
}
section[data-testid="stSidebar"] * {
    color: #d4e6c3 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stSlider label {
    color: #95b885 !important;
    font-size: 0.78rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
section[data-testid="stSidebar"] .stButton>button {
    background: #2d6a4f;
    color: #d4e6c3;
    border: 1px solid #52b788;
    border-radius: 6px;
    font-size: 0.82rem;
    padding: 0.35rem 0.8rem;
    width: 100%;
    transition: background 0.2s;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background: #52b788;
    color: #1a2e1a;
}
/* Sidebar radio buttons */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 0.3rem;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.88rem !important;
    padding: 0.45rem 0.7rem;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(82, 183, 136, 0.15);
}

/* Sidebar brand */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.2rem 0 1rem 0;
    border-bottom: 1px solid #2d4a2d;
    margin-bottom: 1rem;
}
.sb-brand-icon { font-size: 1.6rem; }
.sb-brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #95d5b2 !important;
    letter-spacing: -0.01em;
}
.sb-brand-sub {
    font-size: 0.72rem;
    color: #6b8c6b !important;
    font-weight: 400;
}
.sb-section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #4a6a4a !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.8rem 0 0.4rem 0;
}

/* ── Page header ──────────────────────────────────────── */
.page-header {
    margin-bottom: 1.2rem;
    padding-bottom: 0.9rem;
    border-bottom: 2px solid #e0ecd6;
}
.page-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: #1e4d2b;
    letter-spacing: -0.02em;
    margin: 0 0 0.2rem 0;
}
.page-subtitle {
    font-size: 0.88rem;
    color: #6b7c5a;
    margin: 0;
    font-weight: 400;
}

/* ── KPI Cards ────────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #dde8d5;
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(30, 77, 43, 0.06);
    transition: box-shadow 0.2s, transform 0.2s;
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    box-shadow: 0 4px 16px rgba(30, 77, 43, 0.12);
    transform: translateY(-1px);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: #2d6a4f;
    border-radius: 10px 0 0 10px;
}
.kpi-card.kpi-warn::before { background: #d4a017; }
.kpi-card.kpi-danger::before { background: #c0392b; }
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #6b7c5a;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: #1e4d2b;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.kpi-card.kpi-warn .kpi-value { color: #b5860f; }
.kpi-card.kpi-danger .kpi-value { color: #a93226; }
.kpi-delta {
    font-size: 0.75rem;
    color: #6b7c5a;
    margin-top: 0.3rem;
}

/* ── Section titles ──────────────────────────────────── */
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e4d2b;
    margin: 1.4rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #e0ecd6;
}

/* ── Chart containers ────────────────────────────────── */
.chart-card {
    background: #ffffff;
    border: 1px solid #dde8d5;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 1px 4px rgba(30, 77, 43, 0.05);
    margin-bottom: 1rem;
}

/* ── Insight / Key Facts card ────────────────────────── */
.insight-card {
    background: linear-gradient(135deg, #f0f7f0 0%, #e8f5e4 100%);
    border: 1px solid #c8ddb8;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 4px rgba(30, 77, 43, 0.07);
}
.insight-card h4 {
    font-size: 0.88rem;
    font-weight: 600;
    color: #1e4d2b;
    margin: 0 0 0.8rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.insight-row {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.55rem;
    font-size: 0.85rem;
    color: #2a4a2a;
}
.insight-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #2d6a4f;
    margin-top: 0.35rem;
    flex-shrink: 0;
}
.insight-dot.warn { background: #d4a017; }
.insight-dot.danger { background: #c0392b; }

/* ── Data table styling ──────────────────────────────── */
.stDataFrame {
    border: 1px solid #dde8d5 !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* ── Status pills ────────────────────────────────────── */
.status-good {
    display: inline-block;
    background: #d4edda;
    color: #155724;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-warn {
    display: inline-block;
    background: #fff3cd;
    color: #856404;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-critical {
    display: inline-block;
    background: #f8d7da;
    color: #721c24;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* ── Divider ─────────────────────────────────────────── */
.mf-divider {
    border: none;
    border-top: 1px solid #e0ecd6;
    margin: 1.4rem 0;
}

/* ── Methodology expander ────────────────────────────── */
.streamlit-expanderHeader {
    font-size: 0.85rem !important;
    color: #2d6a4f !important;
}

/* ── Download button ─────────────────────────────────── */
.stDownloadButton > button {
    background: #2d6a4f;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 0.82rem;
    padding: 0.4rem 1rem;
    transition: background 0.2s;
}
.stDownloadButton > button:hover {
    background: #1e4d2b;
}

/* ── Tooltip tweak ────────────────────────────────────── */
.js-plotly-plot .plotly .modebar {
    opacity: 0.35;
}
.js-plotly-plot .plotly .modebar:hover {
    opacity: 1;
}
</style>
"""


def apply_styles():
    """Inject the dashboard CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
