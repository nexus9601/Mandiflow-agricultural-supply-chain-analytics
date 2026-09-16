"""
MandiFlow Dashboard – Clean, Professional Design System & Theme
Clean, neat, solid palette (no gradients, no AI-glow effects).
Built for high readability, institutional credibility, and enterprise analytics.
"""

# ── Clean, Solid Color Palette ──────────────────────────────────────────────
COLORS = {
    "primary":       "#166534",   # Solid Forest Green
    "primary_dark":  "#14532d",   # Deep Forest
    "primary_light": "#15803d",   # Mid Forest Green
    "primary_pale":  "#f0fdf4",   # Clean light green tint
    "secondary":     "#475569",   # Solid Slate Grey
    "accent":        "#d97706",   # Solid Warm Amber
    "accent_pale":   "#fffbeb",   # Warm Amber Tint
    "danger":        "#dc2626",   # Solid Red
    "danger_pale":   "#fef2f2",   # Clean Red Tint
    "info":          "#2563eb",   # Solid Navy/Blue
    "info_pale":     "#eff6ff",   # Clean Blue Tint
    "neutral":       "#64748b",   # Muted Slate
    "bg":            "#f8fafc",   # Crisp Slate Off-White Background
    "card_bg":       "#ffffff",   # Pure White Card
    "border":        "#e2e8f0",   # Clean Crisp Border
    "text":          "#0f172a",   # Deep Slate Text
    "text_muted":    "#64748b",   # Slate Grey Subtext
    "msp_color":     "#d97706",
    "modal_color":   "#166534",
    "positive":      "#166534",
    "negative":      "#dc2626",
}

# ── Plotly Layout Theme Defaults (Clean, Solid) ──────────────────────────────
CHART_THEME = dict(
    template="plotly_white",
    font=dict(family="'Inter', -apple-system, sans-serif", size=12, color=COLORS["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=60, t=44, b=16),  # ample room to prevent text clipping
    colorway=[
        "#166534",  # Forest Green
        "#d97706",  # Amber
        "#475569",  # Slate
        "#2563eb",  # Blue
        "#7c3aed",  # Purple
        "#0d9488",  # Teal
        "#ea580c",  # Orange
    ],
    hoverlabel=dict(
        bgcolor="#ffffff",
        font_size=12,
        font_family="'Inter', sans-serif",
        font_color="#0f172a",
        bordercolor="#cbd5e1",
    ),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#f1f5f9",
    gridwidth=1,
    linecolor="#cbd5e1",
    tickfont=dict(size=11, color=COLORS["text_muted"], family="'Inter', sans-serif"),
    title_font=dict(size=12, color=COLORS["text"], family="'Plus Jakarta Sans', sans-serif"),
    zeroline=False,
)

# ── Custom CSS Injected via st.markdown ───────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Fonts Import ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap');

/* ── Global Styles ──────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

/* Hide default Streamlit adornments */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Clean Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
}

.sidebar-brand-box {
    padding-bottom: 0.9rem;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 1.1rem;
}
.sidebar-brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 1.18rem;
    color: #166534;
    letter-spacing: -0.01em;
    line-height: 1.2;
}
.sidebar-brand-subtitle {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 500;
    margin-top: 2px;
}

/* Sidebar Section Headers */
.sidebar-section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.5rem 0;
}

/* Radio Navigation Buttons */
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 0.45rem 0.75rem !important;
    border-radius: 6px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #334155 !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: background 0.15s ease !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
}
[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #f0fdf4 !important;
    color: #166534 !important;
    font-weight: 600 !important;
    border: 1px solid #bbf7d0 !important;
}

/* ── Clean Page Header (Solid, Enterprise) ───────────────────────── */
.mf-page-header-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top: 3px solid #166534;
    border-radius: 8px;
    padding: 1.25rem 1.6rem;
    margin-bottom: 1.35rem;
    color: #0f172a;
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
    font-size: 0.72rem;
    font-weight: 700;
    color: #166534;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.mf-header-badge {
    font-size: 0.7rem;
    font-weight: 600;
    color: #475569;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2px 7px;
}
.mf-header-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0.2rem 0 0 0;
    line-height: 1.25;
}
.mf-header-subtitle {
    font-size: 0.85rem;
    color: #475569;
    margin: 0.25rem 0 0 0;
    line-height: 1.45;
}

/* ── Clean KPI Cards ────────────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem 1.15rem;
    transition: border-color 0.15s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-card:hover {
    border-color: #cbd5e1;
}
.kpi-label {
    font-size: 0.74rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 0.35rem;
}
.kpi-value.emerald { color: #166534; }
.kpi-value.amber   { color: #b45309; }
.kpi-value.danger  { color: #b91c1c; }
.kpi-value.sky     { color: #0369a1; }

.kpi-delta {
    font-size: 0.74rem;
    font-weight: 500;
    color: #64748b;
}
.kpi-delta.good { color: #15803d; font-weight: 600; }
.kpi-delta.bad  { color: #b91c1c; font-weight: 600; }

/* ── Section Headers ────────────────────────────────────────────── */
.section-header-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 1.5rem 0 0.85rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #e2e8f0;
}
.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.section-badge {
    font-size: 0.7rem;
    font-weight: 600;
    color: #64748b;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    padding: 2px 7px;
    border-radius: 4px;
}

/* ── Clean Insight Box (Solid) ──────────────────────────────────── */
.insight-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #166534;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    margin-top: 1.25rem;
}
.insight-card h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: #166534;
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
    border-radius: 6px;
    padding: 0.65rem 0.85rem;
    font-size: 0.82rem;
    color: #0f172a;
}
.insight-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 2px;
}

/* ── Streamlit UI Element Clean Overrides ────────────────────────── */
.stPlotlyChart {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 0.6rem !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 0.75rem !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 6px !important;
    border-color: #cbd5e1 !important;
}

.stButton > button {
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #334155 !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

.stDownloadButton > button {
    background: #166534 !important;
    color: #ffffff !important;
    border: 1px solid #166534 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 1rem !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: #14532d !important;
    border-color: #14532d !important;
}

.stExpander {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}
.stExpander header {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
}
</style>
"""


def page_header(title: str, subtitle: str, badge: str = "INSTITUTIONAL DASHBOARD") -> str:
    """Return HTML for clean solid white header card with forest green top border."""
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
<div style="text-align: center; padding: 2.5rem 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 1rem 0;">
  <div style="font-size: 1.8rem; margin-bottom: 0.4rem;">🌾</div>
  <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 0.25rem;">No Records Found</h3>
  <p style="font-size: 0.82rem; color: #64748b; max-width: 420px; margin: 0 auto;">{message}</p>
</div>
"""
