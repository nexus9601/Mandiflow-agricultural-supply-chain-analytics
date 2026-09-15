"""
MandiFlow Dashboard – Styles & Theme
Centralised CSS injection and Plotly chart theme constants.
"""

# ── Colour palette ────────────────────────────────────────────────────────────
COLORS = {
    "primary":       "#1a6b3c",   # dark green (primary accent)
    "primary_light": "#2d9657",   # mid green
    "primary_pale":  "#e8f5ee",   # very light green background tint
    "secondary":     "#5a7d6a",   # muted sage green
    "accent":        "#e8a020",   # warm amber (highlights / warnings)
    "danger":        "#c0392b",   # red for price crashes
    "danger_pale":   "#fdecea",
    "neutral":       "#6b7280",   # grey text
    "bg":            "#f8faf9",   # page background
    "card_bg":       "#ffffff",
    "border":        "#e2e8e4",
    "text":          "#1c2b22",
    "text_muted":    "#4a5e52",
    "msp_color":     "#e8a020",
    "modal_color":   "#1a6b3c",
    "positive":      "#1a6b3c",
    "negative":      "#c0392b",
}

# ── Plotly layout defaults ────────────────────────────────────────────────────
CHART_THEME = dict(
    template="plotly_white",
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color=COLORS["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=16, t=48, b=16),
    colorway=[
        COLORS["primary"],
        COLORS["accent"],
        COLORS["secondary"],
        "#3d7ab5",
        "#9c6b2e",
        "#5c4a8a",
    ],
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#eef1ef",
    gridwidth=1,
    linecolor=COLORS["border"],
    tickfont=dict(size=11, color=COLORS["text_muted"]),
    title_font=dict(size=12, color=COLORS["text"]),
    zeroline=False,
)

# ── Custom CSS injected via st.markdown ───────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Import Google Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Root & Body ────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background-color: #f8faf9 !important;
    color: #1c2b22 !important;
}

/* Hide default Streamlit decorations */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8e4 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    font-size: 0.8rem !important;
    color: #4a5e52 !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin: 1.2rem 0 0.4rem 0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label {
    font-size: 0.78rem !important;
    color: #4a5e52 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    font-size: 0.78rem !important;
}

/* ── Page header band ───────────────────────────────────────────── */
.mf-page-header {
    background: linear-gradient(135deg, #1a6b3c 0%, #2d9657 100%);
    border-radius: 10px;
    padding: 1.1rem 1.5rem;
    margin-bottom: 1.5rem;
    color: #ffffff;
}
.mf-page-header .brand-name {
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.2;
}
.mf-page-header .brand-sub {
    font-size: 0.78rem;
    opacity: 0.75;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0;
}
.mf-page-header .page-subtitle {
    font-size: 0.88rem;
    opacity: 0.88;
    margin-top: 0.3rem;
    line-height: 1.4;
}

/* ── KPI Cards ──────────────────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8e4;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease;
    height: 100%;
}
.kpi-card:hover { box-shadow: 0 3px 12px rgba(26,107,60,0.12); }
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #4a5e52;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #1a6b3c;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.kpi-value.danger { color: #c0392b; }
.kpi-value.amber  { color: #c07010; }
.kpi-delta {
    font-size: 0.75rem;
    color: #6b7280;
}

/* ── Section headers ────────────────────────────────────────────── */
.section-header {
    font-size: 0.85rem;
    font-weight: 700;
    color: #1a6b3c;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    border-bottom: 2px solid #e8f5ee;
    padding-bottom: 0.4rem;
    margin: 1.4rem 0 0.9rem 0;
}

/* ── Chart containers ───────────────────────────────────────────── */
.chart-card {
    background: #ffffff;
    border: 1px solid #e2e8e4;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

/* ── Insight card ───────────────────────────────────────────────── */
.insight-card {
    background: linear-gradient(135deg, #e8f5ee 0%, #f0f8f3 100%);
    border: 1px solid #c8e6d4;
    border-left: 4px solid #1a6b3c;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
}
.insight-card h4 {
    font-size: 0.82rem;
    font-weight: 700;
    color: #1a6b3c;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 0 0 0.6rem 0;
}
.insight-item {
    font-size: 0.84rem;
    color: #1c2b22;
    padding: 0.25rem 0;
    border-bottom: 1px solid rgba(26,107,60,0.1);
}
.insight-item:last-child { border-bottom: none; }
.insight-label {
    font-weight: 600;
    color: #2d9657;
}

/* ── Quality status indicators ──────────────────────────────────── */
.status-good     { color: #1a6b3c; font-weight: 600; }
.status-warning  { color: #c07010; font-weight: 600; }
.status-critical { color: #c0392b; font-weight: 600; }

/* ── Empty state ────────────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 2.5rem 1rem;
    color: #6b7280;
    border: 1px dashed #d1d5db;
    border-radius: 10px;
    background: #fafafa;
}
.empty-state .icon { font-size: 2rem; margin-bottom: 0.5rem; }
.empty-state p { font-size: 0.88rem; margin: 0; }

/* ── Methodology expander ───────────────────────────────────────── */
.methodology-box {
    background: #f8faf9;
    border: 1px solid #e2e8e4;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-size: 0.82rem;
    color: #4a5e52;
    line-height: 1.65;
}

/* ── Streamlit overrides ────────────────────────────────────────── */
.stPlotlyChart { border-radius: 8px; overflow: hidden; }
div[data-testid="stHorizontalBlock"] { gap: 0.75rem; }
.stExpander > div { border: 1px solid #e2e8e4 !important; border-radius: 8px !important; }
.stExpander header { font-size: 0.82rem !important; font-weight: 600 !important; color: #1a6b3c !important; }

/* Dataframe / table styling */
.stDataFrame { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid #e2e8e4 !important; }

/* Sidebar brand block */
.sidebar-brand {
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #e2e8e4;
    margin-bottom: 0.5rem;
}
.sidebar-brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a6b3c;
    letter-spacing: -0.01em;
}
.sidebar-brand-sub {
    font-size: 0.72rem;
    color: #4a5e52;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* nav pills */
.nav-pill {
    display: block;
    padding: 0.45rem 0.75rem;
    border-radius: 6px;
    margin-bottom: 0.2rem;
    font-size: 0.84rem;
    font-weight: 500;
    color: #1c2b22;
    cursor: pointer;
    transition: background 0.15s;
}
.nav-pill.active {
    background: #e8f5ee;
    color: #1a6b3c;
    font-weight: 600;
}
.nav-pill:hover { background: #f0f4f1; }

/* Radio button nav style */
[data-testid="stSidebar"] .stRadio > div {
    gap: 0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 0.45rem 0.75rem !important;
    border-radius: 6px !important;
    margin-bottom: 0.15rem !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #f0f4f1 !important;
}

/* ── Download buttons ───────────────────────────────────────────── */
.stDownloadButton > button {
    font-size: 0.78rem !important;
    padding: 0.35rem 0.8rem !important;
    background: #1a6b3c !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover {
    background: #2d9657 !important;
}

/* ── Divider ────────────────────────────────────────────────────── */
.mf-divider {
    border: none;
    border-top: 1px solid #e2e8e4;
    margin: 1.25rem 0;
}
</style>
"""


def page_header(title: str, subtitle: str) -> str:
    """Return HTML for the green page header band."""
    return f"""
<div class="mf-page-header">
  <p class="brand-name">MandiFlow</p>
  <p class="brand-sub">Agricultural Supply Chain Analytics</p>
  <p class="page-subtitle">{subtitle}</p>
</div>
"""


def kpi_card(label: str, value: str, variant: str = "default", delta: str = "") -> str:
    """Return HTML for a single KPI card."""
    val_class = ""
    if variant == "danger":
        val_class = " danger"
    elif variant == "amber":
        val_class = " amber"
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    return f"""
<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value{val_class}">{value}</div>
  {delta_html}
</div>
"""


def section_header(text: str) -> str:
    return f'<div class="section-header">{text}</div>'


def empty_state(message: str = "No data matches the selected filters.") -> str:
    return f"""
<div class="empty-state">
  <div class="icon">🌾</div>
  <p>{message}</p>
</div>
"""
