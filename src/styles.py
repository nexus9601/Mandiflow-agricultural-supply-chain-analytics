"""
MandiFlow Dashboard – Modern Design System & Theme
Elevated modern UI design with Google Fonts (Plus Jakarta Sans & Inter),
harmonious emerald-slate-amber palette, micro-interactions, and glassmorphic cards.
"""

# ── Elevated Color Palette ──────────────────────────────────────────────────
COLORS = {
    "primary":       "#059669",   # Vibrant Emerald Green
    "primary_dark":  "#064e3b",   # Deep Forest Green
    "primary_light": "#10b981",   # Bright Mint
    "primary_pale":  "#ecfdf5",   # Mint Glow tint
    "secondary":     "#475569",   # Slate Grey
    "accent":        "#f59e0b",   # Rich Amber
    "accent_pale":   "#fffbeb",   # Amber Tint
    "danger":        "#ef4444",   # Crimson Coral Red
    "danger_pale":   "#fef2f2",   # Soft Crimson Tint
    "info":          "#0ea5e9",   # Sky Blue
    "info_pale":     "#f0f9ff",   # Sky Tint
    "neutral":       "#64748b",   # Muted Slate
    "bg":            "#f8fafc",   # Crisp Slate White Background
    "card_bg":       "#ffffff",   # Pure White Card
    "border":        "#e2e8f0",   # Crisp Slate Border
    "text":          "#0f172a",   # Deep Charcoal Navy
    "text_muted":    "#64748b",   # Slate Grey
    "msp_color":     "#f59e0b",
    "modal_color":   "#059669",
    "positive":      "#10b981",
    "negative":      "#ef4444",
}

# ── Plotly Layout Theme Defaults ──────────────────────────────────────────────
CHART_THEME = dict(
    template="plotly_white",
    font=dict(family="'Inter', -apple-system, sans-serif", size=12, color=COLORS["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=55, t=48, b=16),  # r=55 prevents right-edge label cutoff!
    colorway=[
        "#059669",  # Emerald
        "#f59e0b",  # Amber
        "#0ea5e9",  # Sky
        "#8b5cf6",  # Violet
        "#ec4899",  # Rose
        "#14b8a6",  # Teal
        "#f97316",  # Orange
    ],
    hoverlabel=dict(
        bgcolor="#0f172a",
        font_size=12,
        font_family="'Inter', sans-serif",
        font_color="#f8fafc",
        bordercolor="#334155",
    ),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#f1f5f9",
    gridwidth=1,
    linecolor="#e2e8f0",
    tickfont=dict(size=11, color=COLORS["text_muted"], family="'Inter', sans-serif"),
    title_font=dict(size=12, color=COLORS["text"], family="'Plus Jakarta Sans', sans-serif"),
    zeroline=False,
)

# ── Custom CSS Injected via st.markdown ───────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Fonts Import ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

/* ── Global Styles ──────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
    letter-spacing: -0.01em;
}

/* Hide default Streamlit adornments */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar Redesign ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
}

.sidebar-brand-box {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 1.1rem;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 1.2rem;
}
.sidebar-logo-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
}
.sidebar-brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.2rem;
    color: #064e3b;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.sidebar-brand-subtitle {
    font-size: 0.7rem;
    color: #64748b;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.sidebar-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ecfdf5;
    color: #059669;
    padding: 3px 8px;
    border-radius: 9999px;
    font-size: 0.68rem;
    font-weight: 600;
    border: 1px solid #a7f3d0;
    margin-top: 4px;
}
.sidebar-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 6px #10b981;
}

/* Sidebar Section Headers */
.sidebar-section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.6rem 0;
}

/* Radio Navigation Buttons */
[data-testid="stSidebar"] .stRadio > div {
    gap: 3px !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 0.55rem 0.85rem !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #334155 !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    transform: translateX(2px);
}
[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #ecfdf5 !important;
    color: #064e3b !important;
    font-weight: 700 !important;
    border: 1px solid #a7f3d0 !important;
}

/* ── Modern Page Header Band ────────────────────────────────────── */
.mf-page-header-container {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 45%, #047857 100%);
    border-radius: 16px;
    padding: 1.35rem 1.75rem;
    margin-bottom: 1.5rem;
    color: #ffffff;
    box-shadow: 0 10px 25px -5px rgba(6, 78, 59, 0.2), 0 8px 10px -6px rgba(6, 78, 59, 0.1);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.12);
}
.mf-page-header-container::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, rgba(255, 255, 255, 0) 70%);
    pointer-events: none;
}
.mf-header-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 6px;
}
.mf-badge-group {
    display: flex;
    align-items: center;
    gap: 8px;
}
.mf-header-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 9999px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.mf-pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #34d399;
    box-shadow: 0 0 8px #34d399;
    animation: pulseGlow 2s infinite;
}
@keyframes pulseGlow {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}
.mf-header-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    margin: 0;
    line-height: 1.2;
    color: #ffffff;
}
.mf-header-subtitle {
    font-size: 0.88rem;
    color: rgba(255, 255, 255, 0.9);
    margin: 4px 0 0 0;
    max-width: 850px;
    line-height: 1.45;
}

/* ── Upgraded KPI Cards ─────────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    height: 100%;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    border-color: #cbd5e1;
}
.kpi-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.kpi-icon-badge {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    background: #f1f5f9;
    color: #334155;
}
.kpi-icon-badge.emerald { background: #ecfdf5; color: #059669; }
.kpi-icon-badge.amber   { background: #fffbeb; color: #d97706; }
.kpi-icon-badge.danger  { background: #fef2f2; color: #dc2626; }
.kpi-icon-badge.sky     { background: #f0f9ff; color: #0284c7; }
.kpi-icon-badge.violet  { background: #f5f3ff; color: #7c3aed; }

.kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.35rem;
}
.kpi-value.emerald { color: #059669; }
.kpi-value.amber   { color: #d97706; }
.kpi-value.danger  { color: #dc2626; }
.kpi-value.sky     { color: #0284c7; }

.kpi-delta {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.74rem;
    font-weight: 600;
    color: #64748b;
    background: #f8fafc;
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid #f1f5f9;
}
.kpi-delta.good {
    color: #059669;
    background: #ecfdf5;
    border-color: #d1fae5;
}
.kpi-delta.bad {
    color: #dc2626;
    background: #fef2f2;
    border-color: #fee2e2;
}

/* ── Modern Section Headers ─────────────────────────────────────── */
.section-header-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 1.6rem 0 0.9rem 0;
    padding-bottom: 0.45rem;
    border-bottom: 1.5px solid #e2e8f0;
}
.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 800;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 16px;
    background: linear-gradient(to bottom, #059669, #10b981);
    border-radius: 2px;
}
.section-badge {
    font-size: 0.72rem;
    font-weight: 600;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 9999px;
}

/* ── Modern Insight & Alert Cards ───────────────────────────────── */
.insight-card {
    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    border: 1px solid #bbf7d0;
    border-left: 4px solid #10b981;
    border-radius: 12px;
    padding: 1.15rem 1.35rem;
    margin-top: 1.2rem;
    box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.05);
}
.insight-card h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 800;
    color: #064e3b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 0.75rem;
}
.insight-item {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    font-size: 0.84rem;
    color: #0f172a;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}
.insight-label {
    font-weight: 700;
    color: #047857;
    white-space: nowrap;
}

/* ── AI Prompt Suggestion Pills ─────────────────────────────────── */
.prompt-chips-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0.85rem 0 1.2rem 0;
}
.prompt-chip {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 9999px;
    padding: 5px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #334155;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

/* ── Streamlit UI Element Overrides ─────────────────────────────── */
.stPlotlyChart {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 0.75rem !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03) !important;
    transition: box-shadow 0.2s ease !important;
}
.stPlotlyChart:hover {
    box-shadow: 0 6px 14px -2px rgba(0, 0, 0, 0.06) !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 0.85rem !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 8px !important;
    border-color: #cbd5e1 !important;
}

.stButton > button {
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25) !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 6px 15px rgba(16, 185, 129, 0.35) !important;
    transform: translateY(-1px) !important;
}

.stExpander {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
}
.stExpander header {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}
</style>
"""


def page_header(title: str, subtitle: str, badge: str = "TRACK 3 ANALYTICS") -> str:
    """Return HTML for the modern emerald gradient page header band with pulsing live indicator."""
    return f"""
<div class="mf-page-header-container">
  <div class="mf-header-top-row">
    <div class="mf-badge-group">
      <span class="mf-header-badge">
        <span class="mf-pulse-dot"></span>
        Live Analytics
      </span>
      <span class="mf-header-badge">{badge}</span>
    </div>
    <span class="mf-header-badge" style="background: rgba(0,0,0,0.25); border-color: rgba(255,255,255,0.15);">
      v2.2 Production
    </span>
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
    icon: str = "📊",
    trend: str = "",
) -> str:
    """Return HTML for an elevated modern KPI card with icon container, trend pill, and micro-elevation."""
    val_variant = "emerald"
    icon_variant = "emerald"
    delta_class = ""

    if variant == "danger":
        val_variant = "danger"
        icon_variant = "danger"
        delta_class = " bad"
    elif variant in ("amber", "warning"):
        val_variant = "amber"
        icon_variant = "amber"
        delta_class = " bad"
    elif variant == "sky":
        val_variant = "sky"
        icon_variant = "sky"
        delta_class = " good"
    elif variant == "violet":
        val_variant = "violet"
        icon_variant = "violet"
        delta_class = " good"

    if trend == "up":
        delta_class = " good"
    elif trend == "down":
        delta_class = " bad"

    delta_html = f'<div class="kpi-delta{delta_class}">{delta}</div>' if delta else ""

    return f"""
<div class="kpi-card">
  <div>
    <div class="kpi-header">
      <span class="kpi-label">{label}</span>
      <div class="kpi-icon-badge {icon_variant}">{icon}</div>
    </div>
    <div class="kpi-value {val_variant}">{value}</div>
  </div>
  <div>
    {delta_html}
  </div>
</div>
"""


def section_header(text: str, badge: str = "") -> str:
    """Return HTML for a modern section header with colored accent indicator."""
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    return f"""
<div class="section-header-box">
  <div class="section-title">{text}</div>
  {badge_html}
</div>
"""


def empty_state(message: str = "No data matches the selected filters.") -> str:
    """Modern empty state card."""
    return f"""
<div style="text-align: center; padding: 3rem 1.5rem; background: #ffffff; border: 1.5px dashed #cbd5e1; border-radius: 14px; margin: 1rem 0;">
  <div style="font-size: 2.4rem; margin-bottom: 0.6rem;">🌾</div>
  <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.3rem;">No Records Found</h3>
  <p style="font-size: 0.84rem; color: #64748b; max-width: 420px; margin: 0 auto;">{message}</p>
</div>
"""
