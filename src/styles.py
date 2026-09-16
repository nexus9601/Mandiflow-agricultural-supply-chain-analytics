"""
MandiFlow Dashboard – Modern Executive Design System & Styling
Elevated agricultural fintech aesthetic: rich emeralds, crisp slates, warm amber for price signals,
layered depth, glassmorphic backdrops, smooth micro-interactions, and premium typography.
"""

# ── Tailored Color Palette ───────────────────────────────────────────────────
COLORS = {
    "primary":       "#059669",   # Rich Emerald
    "primary_dark":  "#064e3b",   # Deep Forest
    "primary_light": "#10b981",   # Vibrant Mint Emerald
    "primary_pale":  "#ecfdf5",   # Clean Emerald Tint
    "secondary":     "#334155",   # Slate Blue
    "accent":        "#f59e0b",   # Warm Amber / Gold
    "accent_dark":   "#d97706",   # Deep Amber
    "accent_pale":   "#fffbeb",   # Amber Tint
    "danger":        "#ef4444",   # Signal Red
    "danger_dark":   "#dc2626",   # Deep Red
    "danger_pale":   "#fef2f2",   # Red Tint
    "info":          "#0284c7",   # Sky Blue
    "info_light":    "#38bdf8",   # Soft Sky
    "info_pale":     "#f0f9ff",   # Sky Tint
    "neutral":       "#64748b",   # Muted Slate
    "neutral_light": "#94a3b8",   # Soft Slate
    "bg":            "#f8fafc",   # Crisp Slate Off-White Background
    "card_bg":       "#ffffff",   # Pure White Card
    "border":        "#e2e8f0",   # Clean Crisp Border
    "border_focus":  "#10b981",   # Focus Emerald Ring
    "text":          "#0f172a",   # Deep Slate Text
    "text_muted":    "#64748b",   # Slate Grey Subtext
    "msp_color":     "#f59e0b",   # MSP Gold/Amber
    "modal_color":   "#059669",   # Modal Price Emerald
    "positive":      "#059669",
    "negative":      "#ef4444",
}

# ── Plotly Layout Theme Defaults (Modern Executive) ──────────────────────────
CHART_THEME = dict(
    template="plotly_white",
    font=dict(family="'Inter', -apple-system, sans-serif", size=12, color=COLORS["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=40, t=48, b=24),
    colorway=[
        "#059669",  # Rich Emerald
        "#f59e0b",  # Amber Gold
        "#0284c7",  # Sky Blue
        "#8b5cf6",  # Modern Violet
        "#0d9488",  # Deep Teal
        "#f97316",  # Warm Orange
        "#ec4899",  # Rose
    ],
    hoverlabel=dict(
        bgcolor="#0f172a",
        font_size=12,
        font_family="'Inter', -apple-system, sans-serif",
        font_color="#ffffff",
        bordercolor="rgba(255,255,255,0.15)",
    ),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#f1f5f9",
    gridwidth=1,
    linecolor="#e2e8f0",
    tickfont=dict(size=11, color=COLORS["text_muted"], family="'Inter', -apple-system, sans-serif"),
    title_font=dict(size=12, color=COLORS["text"], family="'Plus Jakarta Sans', sans-serif"),
    zeroline=False,
)

# ── Custom CSS Injected via st.markdown ───────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Fonts Import ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

/* ── Global Canvas & Reset ──────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background: #f8fafc !important;
    background-image: 
        radial-gradient(at 10% 10%, rgba(5, 150, 105, 0.03) 0px, transparent 50%),
        radial-gradient(at 90% 90%, rgba(2, 132, 199, 0.03) 0px, transparent 50%) !important;
    color: #0f172a !important;
    -webkit-font-smoothing: antialiased;
}

/* Hide default Streamlit chrome while preserving sidebar expand/collapse controls */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { background: transparent !important; }

/* Ensure collapsed sidebar toggle control is always visible and easy to click */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"] [data-testid="collapsedControl"],
[data-testid="stHeader"] button,
button[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    z-index: 1000000 !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 9px !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08) !important;
    margin: 8px 0 0 10px !important;
    transition: all 0.2s ease !important;
    color: #059669 !important;
}

[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    border-color: #059669 !important;
    background: #ecfdf5 !important;
    transform: scale(1.05) !important;
}

/* ── Modern Sleek Sidebar ────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
    box-shadow: 2px 0 12px rgba(15, 23, 42, 0.02) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
    padding-left: 1.15rem !important;
    padding-right: 1.15rem !important;
}

.sidebar-brand-box {
    padding: 0.9rem 1.1rem;
    background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
    border-radius: 12px;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 16px -4px rgba(6, 78, 59, 0.25);
    color: #ffffff;
}
.sidebar-brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.22rem;
    color: #ffffff;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sidebar-brand-subtitle {
    font-size: 0.72rem;
    color: #a7f3d0;
    font-weight: 500;
    margin-top: 3px;
    letter-spacing: 0.02em;
}

/* Sidebar Section Headers */
.sidebar-section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.70rem;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 1.25rem 0 0.45rem 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sidebar-section-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #e2e8f0;
}

/* Sidebar Navigation Buttons */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.85rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #334155 !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    transform: translateX(2px) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25) !important;
    border: none !important;
    transform: none !important;
}

/* ── Top Navigation Hero Bar ─────────────────────────────────────── */
.mf-hero-bar {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 14px;
    padding: 0.85rem 1.4rem;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
}
.mf-hero-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.mf-hero-logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 6px;
}
.mf-live-pulse-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 20px;
    font-size: 0.70rem;
    font-weight: 700;
    color: #047857;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse-ring 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}
@keyframes pulse-ring {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 7px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}
.mf-current-module-badge {
    font-size: 0.76rem;
    color: #64748b;
    font-weight: 500;
}
.mf-current-module-badge strong {
    color: #059669;
    font-weight: 700;
}

/* ── Top Menu Navigation Buttons Bar ────────────────────────────── */
.top-menu-bar-container {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 12px;
    padding: 6px;
    margin-bottom: 1.25rem;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}
.top-menu-bar-container .stButton > button {
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.48rem 0.6rem !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #475569 !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.top-menu-bar-container .stButton > button:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    transform: translateY(-1px) !important;
}
.top-menu-bar-container .stButton > button[kind="primary"],
.top-menu-bar-container button[data-testid="baseButton-primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.28) !important;
    border: 1px solid #047857 !important;
}

button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #ffffff !important;
    border: 1px solid #047857 !important;
}
button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #047857 0%, #064e3b 100%) !important;
    color: #ffffff !important;
}

/* ── Executive Page Header Card ──────────────────────────────────── */
.mf-page-header-container {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 14px;
    padding: 1.35rem 1.8rem;
    margin-bottom: 1.35rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
}
.mf-page-header-container::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #059669 0%, #10b981 40%, #f59e0b 100%);
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
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.70rem;
    font-weight: 700;
    color: #059669;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 5px;
}
.mf-header-badge {
    font-size: 0.68rem;
    font-weight: 700;
    color: #475569;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 2px 8px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.mf-header-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    margin: 0.2rem 0 0 0;
    line-height: 1.2;
}
.mf-header-subtitle {
    font-size: 0.88rem;
    color: #64748b;
    margin: 0.35rem 0 0 0;
    line-height: 1.5;
}

/* ── Modern Premium KPI Cards ────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04), 0 2px 4px -1px rgba(15, 23, 42, 0.02);
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 24px -4px rgba(15, 23, 42, 0.08), 0 4px 8px -2px rgba(15, 23, 42, 0.03);
    border-color: #cbd5e1;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: #e2e8f0;
}
.kpi-card.variant-emerald::before { background: linear-gradient(90deg, #059669, #10b981); }
.kpi-card.variant-amber::before   { background: linear-gradient(90deg, #d97706, #f59e0b); }
.kpi-card.variant-danger::before  { background: linear-gradient(90deg, #dc2626, #ef4444); }
.kpi-card.variant-sky::before     { background: linear-gradient(90deg, #0284c7, #38bdf8); }

.kpi-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.55rem;
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
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    background: #f1f5f9;
}
.kpi-card.variant-emerald .kpi-icon-badge { background: #ecfdf5; color: #059669; }
.kpi-card.variant-amber .kpi-icon-badge   { background: #fffbeb; color: #d97706; }
.kpi-card.variant-danger .kpi-icon-badge  { background: #fef2f2; color: #dc2626; }
.kpi-card.variant-sky .kpi-icon-badge     { background: #f0f9ff; color: #0284c7; }

.kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.82rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 0.35rem;
}
.kpi-value.emerald { color: #059669; }
.kpi-value.amber   { color: #d97706; }
.kpi-value.danger  { color: #dc2626; }
.kpi-value.sky     { color: #0284c7; }

.kpi-delta-box {
    margin-top: 0.25rem;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.73rem;
    font-weight: 600;
    color: #64748b;
}
.kpi-delta-box.good { color: #059669; }
.kpi-delta-box.bad  { color: #dc2626; }

/* ── Section Headers ────────────────────────────────────────────── */
.section-header-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 1.6rem 0 0.95rem 0;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid #e2e8f0;
}
.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.92rem;
    font-weight: 800;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::before {
    content: "";
    display: inline-block;
    width: 4px;
    height: 14px;
    background: #059669;
    border-radius: 2px;
}
.section-badge {
    font-size: 0.70rem;
    font-weight: 700;
    color: #64748b;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    padding: 2px 8px;
    border-radius: 6px;
    letter-spacing: 0.04em;
}

/* ── Modern Chart Container Card ────────────────────────────────── */
.stPlotlyChart {
    background: #ffffff !important;
    border: 1px solid rgba(226, 232, 240, 0.9) !important;
    border-radius: 14px !important;
    padding: 0.75rem !important;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03) !important;
    transition: border-color 0.2s ease !important;
}
.stPlotlyChart:hover {
    border-color: #cbd5e1 !important;
}

/* ── Clean Insight Callout Box ──────────────────────────────────── */
.insight-card {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-left: 4px solid #059669;
    border-radius: 12px;
    padding: 1.25rem 1.45rem;
    margin-top: 1.35rem;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03);
}
.insight-card h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 800;
    color: #059669;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 0.85rem 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 0.85rem;
}
.insight-item {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem 0.95rem;
    font-size: 0.84rem;
    color: #0f172a;
    transition: all 0.2s ease;
}
.insight-item:hover {
    background: #ffffff;
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
}
.insight-label {
    font-size: 0.70rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 3px;
}

/* ── Streamlit Form & UI Controls Polish ────────────────────────── */
div[data-testid="stHorizontalBlock"] {
    gap: 0.85rem !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div {
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
    font-size: 0.85rem !important;
    background-color: #ffffff !important;
    transition: all 0.2s ease !important;
}
.stSelectbox > div > div:hover,
.stDateInput > div > div:hover {
    border-color: #94a3b8 !important;
}
.stSelectbox > div > div:focus-within,
.stDateInput > div > div:focus-within {
    border-color: #059669 !important;
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    padding: 0.55rem 1.25rem !important;
    box-shadow: 0 4px 14px rgba(5, 150, 105, 0.25) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(5, 150, 105, 0.35) !important;
}

.stExpander {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02) !important;
    overflow: hidden !important;
}
.stExpander header {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}

/* ── Modern Table Polish ────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03) !important;
}

/* ── Interactive Chat & Prompt Box Highlight ───────────────────── */
[data-testid="stForm"] {
    background: #ffffff !important;
    border: 2px solid #10b981 !important;
    border-radius: 14px !important;
    padding: 1.15rem 1.25rem !important;
    box-shadow: 0 6px 24px -4px rgba(5, 150, 105, 0.18), 0 2px 8px -1px rgba(15, 23, 42, 0.06) !important;
    transition: all 0.25s ease !important;
}

[data-testid="stForm"]:focus-within {
    border-color: #059669 !important;
    box-shadow: 0 8px 30px -4px rgba(5, 150, 105, 0.25), 0 0 0 3px rgba(16, 185, 129, 0.22) !important;
}

[data-testid="stForm"] [data-testid="stTextInput"] input {
    background: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    color: #0f172a !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stForm"] [data-testid="stTextInput"] input:focus {
    background: #ffffff !important;
    border-color: #059669 !important;
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15) !important;
}

[data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"],
[data-testid="stForm"] button[kind="primaryFormSubmit"],
[data-testid="stForm"] button[kind="primary"] {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #ffffff !important;
    border: 1px solid #047857 !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 3px 10px rgba(5, 150, 105, 0.3) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"]:hover,
[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
[data-testid="stForm"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #047857 0%, #064e3b 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 15px rgba(5, 150, 105, 0.4) !important;
}

[data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"],
[data-testid="stForm"] button[kind="secondaryFormSubmit"] {
    background: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 9px !important;
    color: #475569 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"]:hover,
[data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    border-color: #94a3b8 !important;
}

/* ── AI Analytics Sidebar Button – Special Emerald Glow ─────────────── */
[data-testid="stSidebar"] button[key="sb_AI Analytics ✨"],
[data-testid="stSidebar"] button[data-testid$="AI Analytics ✨"] {
    background: linear-gradient(135deg, #064e3b 0%, #059669 100%) !important;
    color: #ffffff !important;
    border: 1.5px solid #10b981 !important;
    box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35) !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] button[key="sb_AI Analytics ✨"]:hover,
[data-testid="stSidebar"] button[data-testid$="AI Analytics ✨"]:hover {
    background: linear-gradient(135deg, #047857 0%, #10b981 100%) !important;
    box-shadow: 0 6px 20px rgba(5, 150, 105, 0.45) !important;
    transform: translateX(2px) !important;
}

/* ── Global Filter Bar Expander ─────────────────────────────────────── */
[data-testid="stExpander"]:has(summary span:contains("Global Filters")) {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
}
</style>
"""


def page_header(title: str, subtitle: str, badge: str = "EXECUTIVE INTELLIGENCE") -> str:
    """Return HTML for a modern, sleek executive header card."""
    return f"""
<div class="mf-page-header-container">
  <div class="mf-header-top-row">
    <span class="mf-header-tag">🌾 Agricultural Supply Chain Intelligence</span>
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
    """Return HTML for an executive glass-accented KPI card with icon badge."""
    val_variant = "default"
    card_variant = "default"
    delta_class = ""

    if variant in ("emerald", "primary"):
        val_variant = "emerald"
        card_variant = "variant-emerald"
    elif variant == "danger":
        val_variant = "danger"
        card_variant = "variant-danger"
    elif variant in ("amber", "warning"):
        val_variant = "amber"
        card_variant = "variant-amber"
    elif variant == "sky":
        val_variant = "sky"
        card_variant = "variant-sky"

    if trend == "up":
        delta_class = " good"
    elif trend == "down":
        delta_class = " bad"

    # Default icons if none specified
    if not icon:
        if "arrival" in label.lower() or "volume" in label.lower() or "inflow" in label.lower():
            icon = "🌾"
        elif "modal" in label.lower() or "price" in label.lower():
            icon = "💰"
        elif "msp" in label.lower():
            icon = "🛡️"
        elif "crash" in label.lower() or "risk" in label.lower():
            icon = "⚠️"
        elif "transit" in label.lower() or "time" in label.lower() or "hour" in label.lower():
            icon = "⏱️"
        elif "mandi" in label.lower() or "center" in label.lower():
            icon = "🏛️"
        elif "district" in label.lower():
            icon = "📍"
        else:
            icon = "📊"

    delta_html = f'<div class="kpi-delta-box{delta_class}">{delta}</div>' if delta else ""

    return f"""
<div class="kpi-card {card_variant}">
  <div>
    <div class="kpi-top-row">
      <div class="kpi-label">{label}</div>
      <div class="kpi-icon-badge">{icon}</div>
    </div>
    <div class="kpi-value {val_variant}">{value}</div>
  </div>
  {delta_html}
</div>
"""


def section_header(text: str, badge: str = "") -> str:
    """Return HTML for an elegant section divider."""
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    return f"""
<div class="section-header-box">
  <div class="section-title">{text}</div>
  {badge_html}
</div>
"""


def empty_state(message: str = "No data matches the selected filters.") -> str:
    """Modern empty state card with visual icon."""
    return f"""
<div style="text-align: center; padding: 3rem 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; margin: 1rem 0; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03);">
  <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">🌾</div>
  <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0.35rem;">No Records Match Filters</h3>
  <p style="font-size: 0.85rem; color: #64748b; max-width: 440px; margin: 0 auto; line-height: 1.5;">{message}</p>
  <div style="margin-top: 1rem; font-size: 0.78rem; color: #059669; font-weight: 600;">Tip: Try broadening your date range or selecting 'All' in the filter dropdowns.</div>
</div>
"""
