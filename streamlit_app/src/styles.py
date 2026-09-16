"""
MandiFlow Dashboard - Design System and Theme
Dark-green sidebar with high-contrast navigation, enterprise KPI cards.
"""

# Color Palette
COLORS = {
    "primary":       "#166534",
    "primary_dark":  "#14532d",
    "primary_light": "#15803d",
    "primary_pale":  "#f0fdf4",
    "secondary":     "#475569",
    "accent":        "#d97706",
    "accent_pale":   "#fffbeb",
    "danger":        "#dc2626",
    "danger_pale":   "#fef2f2",
    "info":          "#2563eb",
    "info_pale":     "#eff6ff",
    "neutral":       "#64748b",
    "bg":            "#f1f5f9",
    "card_bg":       "#ffffff",
    "border":        "#e2e8f0",
    "text":          "#0f172a",
    "text_muted":    "#64748b",
    "msp_color":     "#d97706",
    "modal_color":   "#166534",
    "positive":      "#166534",
    "negative":      "#dc2626",
}

CHART_THEME = dict(
    template="plotly_white",
    font=dict(family="'Inter', -apple-system, sans-serif", size=12, color=COLORS["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=60, t=44, b=16),
    colorway=["#166534","#d97706","#475569","#2563eb","#7c3aed","#0d9488","#ea580c"],
    hoverlabel=dict(
        bgcolor="#ffffff",font_size=12,
        font_family="'Inter', sans-serif",
        font_color="#0f172a",bordercolor="#cbd5e1",
    ),
)

AXIS_STYLE = dict(
    showgrid=True,gridcolor="#f1f5f9",gridwidth=1,linecolor="#cbd5e1",
    tickfont=dict(size=11,color=COLORS["text_muted"],family="'Inter', sans-serif"),
    title_font=dict(size=12,color=COLORS["text"],family="'Plus Jakarta Sans', sans-serif"),
    zeroline=False,
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

[data-testid="stSidebar"] {
    background: #0d1f14 !important;
    border-right: 1px solid #1c3829 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding: 1rem 1rem !important;
}

.sidebar-brand-box {
    padding: 0.9rem 0 1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.9rem;
}
.sidebar-brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.2rem;
    color: #ffffff;
    letter-spacing: -0.01em;
    line-height: 1.2;
}
.sidebar-brand-subtitle {
    font-size: 0.69rem;
    color: #86efac;
    font-weight: 500;
    margin-top: 3px;
    opacity: 0.9;
}

.sidebar-section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.63rem;
    font-weight: 700;
    color: #6ee7b7;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1rem 0 0.4rem 0;
    opacity: 0.8;
}

[data-testid="stSidebar"] .stRadio > div,
[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 2px !important;
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 0.48rem 0.8rem !important;
    border-radius: 7px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #cbd5e1 !important;
    cursor: pointer !important;
    width: 100% !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] .stRadio label *,
[data-testid="stSidebar"] .stRadio label p,
[data-testid="stSidebar"] .stRadio label span,
[data-testid="stSidebar"] .stRadio label div {
    color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
}

[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] > p {
    margin: 0 !important;
    line-height: 1.4 !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stRadio label[aria-checked="true"],
[data-testid="stSidebar"] .stRadio [data-checked="true"] > label,
[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
[data-testid="stSidebar"] .stRadio label:has(input[type="radio"]:checked) {
    background: rgba(22,101,52,0.50) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-color: rgba(74,222,128,0.35) !important;
}

[data-testid="stSidebar"] .stSelectbox label p,
[data-testid="stSidebar"] .stDateInput label p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #94a3b8 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stDateInput > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: 7px !important;
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div:hover,
[data-testid="stSidebar"] .stDateInput > div > div:hover {
    border-color: rgba(74,222,128,0.45) !important;
}
[data-testid="stSidebar"] .stSelectbox svg,
[data-testid="stSidebar"] .stDateInput svg {
    fill: #94a3b8 !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 0.75rem 0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 7px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 0.45rem 0.75rem !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border-color: rgba(74,222,128,0.35) !important;
}

[data-testid="stMainBlockContainer"],
[data-testid="block-container"] {
    padding: 1.5rem 2rem 2.5rem 2rem !important;
    max-width: 1440px !important;
}

.mf-page-header-container {
    background: linear-gradient(135deg, #0f2318 0%, #166534 100%);
    border: 1px solid #15803d;
    border-radius: 10px;
    padding: 1.4rem 1.75rem;
    margin-bottom: 1.5rem;
    color: #ffffff;
    box-shadow: 0 4px 20px rgba(22,101,52,0.2);
}
.mf-header-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 4px;
}
.mf-header-tag {
    font-size: 0.68rem;
    font-weight: 700;
    color: #86efac;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}
.mf-header-badge {
    font-size: 0.67rem;
    font-weight: 600;
    color: #86efac;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(134,239,172,0.3);
    border-radius: 4px;
    padding: 2px 8px;
}
.mf-header-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin: 0.2rem 0 0 0;
    line-height: 1.25;
}
.mf-header-subtitle {
    font-size: 0.84rem;
    color: #bbf7d0;
    margin: 0.3rem 0 0 0;
    line-height: 1.5;
    opacity: 0.9;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(15,23,42,0.05);
}
.kpi-card:hover {
    border-color: #94a3b8;
    box-shadow: 0 4px 14px rgba(15,23,42,0.1);
    transform: translateY(-1px);
}
.kpi-label {
    font-size: 0.71rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 0.35rem;
}
.kpi-value.emerald { color: #166534; }
.kpi-value.amber   { color: #b45309; }
.kpi-value.danger  { color: #b91c1c; }
.kpi-value.sky     { color: #0369a1; }

.kpi-delta { font-size: 0.74rem; font-weight: 500; color: #64748b; }
.kpi-delta.good { color: #15803d; font-weight: 600; }
.kpi-delta.bad  { color: #b91c1c; font-weight: 600; }

.section-header-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 1.6rem 0 0.9rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}
.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.84rem;
    font-weight: 700;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.section-badge {
    font-size: 0.68rem;
    font-weight: 600;
    color: #64748b;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    padding: 2px 8px;
    border-radius: 4px;
}

.insight-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #166534;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-top: 1.25rem;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04);
}
.insight-card h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.79rem;
    font-weight: 700;
    color: #166534;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 0 0 0.75rem 0;
}
.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 0.75rem;
}
.insight-item {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    padding: 0.65rem 0.85rem;
    font-size: 0.82rem;
    color: #0f172a;
}
.insight-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
}

.stPlotlyChart {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04) !important;
}

div[data-testid="stHorizontalBlock"] { gap: 0.9rem !important; }

.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 7px !important;
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #166534 !important;
    box-shadow: 0 0 0 2px rgba(22,101,52,0.12) !important;
}

.stButton > button {
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #334155 !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06) !important;
    transition: all 0.15s ease !important;
    padding: 0.45rem 1rem !important;
}
.stButton > button:hover {
    background: #f0fdf4 !important;
    border-color: #166534 !important;
    color: #166534 !important;
    box-shadow: 0 2px 8px rgba(22,101,52,0.14) !important;
}

.stDownloadButton > button {
    background: #166534 !important;
    color: #ffffff !important;
    border: 1px solid #166534 !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 1rem !important;
    box-shadow: 0 2px 8px rgba(22,101,52,0.2) !important;
    transition: all 0.15s ease !important;
}
.stDownloadButton > button:hover {
    background: #14532d !important;
    border-color: #14532d !important;
    box-shadow: 0 4px 12px rgba(22,101,52,0.3) !important;
}

.stExpander {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04) !important;
}
.stExpander header {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.9rem 1.1rem !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04);
}
[data-testid="stMetricLabel"] p {
    font-size: 0.71rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}
[data-testid="stMetricDelta"] { font-size: 0.74rem !important; font-weight: 600 !important; }

.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
    border-bottom: 2px solid #e2e8f0 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px 7px 0 0 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    background: transparent !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    transition: color 0.15s ease, background 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #166534 !important; background: #f0fdf4 !important; }
.stTabs [aria-selected="true"] {
    color: #166534 !important;
    background: #f0fdf4 !important;
    border-bottom: 2px solid #166534 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.methodology-box { font-size: 0.83rem; color: #475569; line-height: 1.75; }
.methodology-box strong { color: #0f172a; }
</style>
"""


def page_header(title: str, subtitle: str, badge: str = "INSTITUTIONAL DASHBOARD") -> str:
    """Return HTML for dark green gradient header card."""
    return f"""
<div class="mf-page-header-container">
  <div class="mf-header-top-row">
    <span class="mf-header-tag">Agricultural Supply Chain Intelligence</span>
    <span class="mf-header-badge">{badge}</span>
  </div>
  <h1 class="mf-header-title">{title}</h1>
  <p class="mf-header-subtitle">{subtitle}</p>
</div>
"""


def kpi_card(
    label: str,
    value: str,
    variant: str = "default",
    delta: str = "",
    icon: str = "",
    trend: str = "",
) -> str:
    """Return HTML for a clean, solid, professional KPI card."""
    val_variant = "default"
    delta_class = ""

    if variant in ("emerald", "primary"):
        val_variant = "emerald"
    elif variant == "danger":
        val_variant = "danger"
    elif variant in ("amber", "warning"):
        val_variant = "amber"
    elif variant == "sky":
        val_variant = "sky"

    if trend == "up":
        delta_class = " good"
    elif trend == "down":
        delta_class = " bad"

    delta_html = f'<div class="kpi-delta{delta_class}">{delta}</div>' if delta else ""

    return f"""
<div class="kpi-card">
  <div>
    <div class="kpi-label">{label}</div>
    <div class="kpi-value {val_variant}">{value}</div>
  </div>
  {delta_html}
</div>
"""


def section_header(text: str, badge: str = "") -> str:
    """Return HTML for a clean, solid section divider."""
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    return f"""
<div class="section-header-box">
  <div class="section-title">{text}</div>
  {badge_html}
</div>
"""


def empty_state(message: str = "No data matches the selected filters.") -> str:
    """Clean empty state card."""
    return f"""
<div style="text-align: center; padding: 2.5rem 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin: 1rem 0; box-shadow: 0 1px 4px rgba(15,23,42,0.05);">
  <div style="font-size: 1.8rem; margin-bottom: 0.4rem;">&#x1F33E;</div>
  <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">No Records Found</h3>
  <p style="font-size: 0.82rem; color: #64748b; max-width: 420px; margin: 0 auto;">{message}</p>
</div>
"""
