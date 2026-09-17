"""MandiFlow – AI Analytics Page

Natural Language Supply Chain Intelligence powered by LLMs (Groq / Llama 3)
with Built-in Instant Query Analytics and Interactive API Configuration.
Commands:
  /new  <query>        – generate a fresh chart (default)
  /followup <changes>  – modify the last chart
  /insight [question]  – get analytical insights on the last chart
"""

from __future__ import annotations

import os
import re
import textwrap
import time
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src import styles
from src.styles import COLORS, CHART_THEME, AXIS_STYLE


# ── Groq / OpenAI client ──────────────────────────────────────────────────────

def _get_client():
    """Return an OpenAI-compatible client pointed at Groq, or None."""
    try:
        from openai import OpenAI

        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        key = (
            st.session_state.get("user_groq_key", "")
            or st.secrets.get("GROQ_API_KEY", "")
            or os.environ.get("GROQ_API_KEY", "")
        )

        if not key:
            for candidate in [".env", os.path.join(os.path.dirname(__file__), "..", "..", ".env")]:
                if os.path.exists(candidate):
                    try:
                        with open(candidate, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line.startswith("GROQ_API_KEY="):
                                    key = line.split("=", 1)[1].strip().strip("'\"")
                                    if key:
                                        os.environ["GROQ_API_KEY"] = key
                                        break
                    except Exception:
                        pass
                if key:
                    break

        if not key:
            return None, ""
        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        return client, key
    except ImportError:
        return None, ""


CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]


def _resolve_model(client) -> str:
    """Pick the best available Groq model."""
    configured = ""
    try:
        configured = st.secrets.get("GROQ_MODEL", "") or os.environ.get("GROQ_MODEL", "")
    except Exception:
        pass
    if configured:
        return configured
    try:
        available = {m.id for m in client.models.list().data}
        for m in CANDIDATE_MODELS:
            if m in available:
                return m
        chat_models = [m for m in available if "guard" not in m and "whisper" not in m]
        if chat_models:
            return chat_models[0]
    except Exception:
        pass
    return CANDIDATE_MODELS[0]


# ── Command parser ────────────────────────────────────────────────────────────

def _parse_command(text: str) -> tuple[str, str]:
    t = text.strip()
    m = re.match(r"^/(insights?)\s*(.*)", t, re.IGNORECASE | re.DOTALL)
    if m:
        return "insight", m.group(2).strip()
    m = re.match(r"^/(followup|edit)\s+(.*)", t, re.IGNORECASE | re.DOTALL)
    if m:
        return "followup", m.group(2).strip()
    m = re.match(r"^/new\s+(.*)", t, re.IGNORECASE | re.DOTALL)
    if m:
        return "new", m.group(1).strip()
    return "new", t


# ── System prompts ────────────────────────────────────────────────────────────

def _system_prompt(df: pd.DataFrame) -> str:
    col_info = "\n".join(f"  - {c}: {dt}" for c, dt in df.dtypes.items())
    return textwrap.dedent(f"""
        You are an expert agricultural supply chain data analyst.
        The pandas DataFrame `df` is already loaded with {df.shape[0]:,} rows and {df.shape[1]} columns.

        IMPORTANT Column Mappings:
        - Crop name: `crop_name`
        - Price: `modal_price` (wholesale market price in ₹/quintal)
        - Minimum Support Price: `msp`
        - Arrival volume: `arrival_quantity_qtl`
        - Geography: `district`, `mandi_name`, `mandi_type`
        - Date: `date` (already datetime)
        - Weather: `avg_temperature_c`, `total_rainfall_mm`, `avg_humidity_percent`
        - Transport: `avg_distance_km`, `avg_transit_hours`, `transit_delay_rate`

        Available columns:
        {col_info}

        Generate ONLY valid Python code using plotly.express (`px`) or plotly.graph_objects (`go`).
        The final chart MUST be assigned to variable `fig`.
        Follow modern theme: use '#059669' (emerald), '#f59e0b' (amber/gold), '#0284c7' (sky) colorway.
        Do NOT call fig.show(). Do NOT import pandas or plotly (they are already in scope).
        Wrap your code in ```python ``` blocks.
    """)


def _sanitize_code(code_str: str) -> str:
    """Extract code from markdown fences and remove unsafe calls."""
    m = re.search(r"```(?:python)?\s*(.*?)\s*```", code_str, re.DOTALL)
    code = m.group(1) if m else code_str
    lines = [
        line for line in code.splitlines()
        if not re.match(r"^\s*(?:import\s|from\s|fig\.show\(\))", line)
    ]
    return "\n".join(lines).strip()


# ── Built-in Demo Engine (Works without API key) ──────────────────────────────

def _run_demo_query(query: str, df: pd.DataFrame) -> tuple[go.Figure, str, str]:
    """Execute pre-computed smart queries for instant interactive demonstrations."""
    q_lower = query.lower()
    
    if "inflow" in q_lower or "top 5" in q_lower or ("crop" in q_lower and "arrival" in q_lower):
        grp = df.groupby("crop_name")["arrival_quantity_qtl"].sum().sort_values(ascending=False).head(5).reset_index()
        grp.columns = ["Crop", "Arrivals"]
        fig = px.bar(
            grp, x="Crop", y="Arrivals",
            text="Arrivals",
            color="Arrivals",
            color_continuous_scale=["#a7f3d0", "#059669"],
            labels={"Arrivals": "Total Arrivals (Qtl)"},
        )
        fig.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside",
            marker=dict(cornerradius=6),
            hovertemplate="<b>%{x}</b><br>Inflow: <b>%{y:,.0f} Qtl</b><extra></extra>",
        )
        fig.update_layout(
            **CHART_THEME,
            height=370,
            title=dict(text="<b>Top 5 Crops by Inflow Volume</b>", font=dict(family="'Plus Jakarta Sans', sans-serif", size=13)),
            xaxis=dict(**AXIS_STYLE, title="Crop"),
            yaxis=dict(**AXIS_STYLE, title="Total Arrivals (Qtl)"),
            coloraxis_showscale=False,
        )
        code = textwrap.dedent("""
            grp = df.groupby('crop_name')['arrival_quantity_qtl'].sum().sort_values(ascending=False).head(5).reset_index()
            fig = px.bar(grp, x='crop_name', y='arrival_quantity_qtl', text='arrival_quantity_qtl', color='arrival_quantity_qtl', color_continuous_scale=['#a7f3d0', '#059669'])
            fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside', marker=dict(cornerradius=6))
        """).strip()
        insight = textwrap.dedent(f"""
            ### 📊 Top Crop Inflow Takeaways
            - **{grp.iloc[0]['Crop']}** leads overall arrivals with **{grp.iloc[0]['Arrivals']:,.0f} Quintals**, representing high market liquidity.
            - The top 5 commodities together account for over **{grp['Arrivals'].sum():,.0f} Quintals** of total mandi turnover.
            - Highly concentrated inflows suggest focused logistics infrastructure should be positioned around these primary commodities.
        """).strip()
        return fig, code, insight

    elif "msp" in q_lower or "gap" in q_lower or "support" in q_lower:
        grp = df.dropna(subset=["modal_price", "msp"]).groupby("crop_name")[["modal_price", "msp"]].mean().reset_index()
        grp["gap"] = grp["modal_price"] - grp["msp"]
        grp = grp.sort_values("gap")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Modal Price", x=grp["crop_name"], y=grp["modal_price"],
            marker=dict(color="#059669", cornerradius=6),
            hovertemplate="<b>%{x}</b><br>Modal Price: <b>₹%{y:,.0f}</b><extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name="MSP Floor", x=grp["crop_name"], y=grp["msp"],
            marker=dict(color="#f59e0b", cornerradius=6),
            hovertemplate="<b>%{x}</b><br>MSP Floor: <b>₹%{y:,.0f}</b><extra></extra>",
        ))
        fig.update_layout(
            **CHART_THEME,
            barmode="group",
            height=370,
            title=dict(text="<b>Wholesale Modal Price vs Guaranteed MSP Floor</b>", font=dict(family="'Plus Jakarta Sans', sans-serif", size=13)),
            xaxis=dict(**AXIS_STYLE, title="Crop"),
            yaxis=dict(**AXIS_STYLE, title="Price (₹/Qtl)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        code = textwrap.dedent("""
            grp = df.dropna(subset=['modal_price', 'msp']).groupby('crop_name')[['modal_price', 'msp']].mean().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Modal Price', x=grp['crop_name'], y=grp['modal_price'], marker=dict(color='#059669', cornerradius=6)))
            fig.add_trace(go.Bar(name='MSP Floor', x=grp['crop_name'], y=grp['msp'], marker=dict(color='#f59e0b', cornerradius=6)))
            fig.update_layout(barmode='group')
        """).strip()
        worst = grp.iloc[0]
        insight = textwrap.dedent(f"""
            ### 🛡️ MSP Compliance Assessment
            - **{worst['crop_name']}** exhibits the most severe downside deficit, trading at **₹{worst['modal_price']:,.0f}** vs the support floor of **₹{worst['msp']:,.0f}** (Deficit of **₹{abs(worst['gap']):,.0f}**).
            - Crops trading below MSP indicate urgent need for targeted procurement intervention or price deficiency payments to safeguard farmer realizations.
        """).strip()
        return fig, code, insight

    else:
        # Default: Rainfall vs Arrival Trend
        daily = df.groupby("date").agg({"total_rainfall_mm": "mean", "arrival_quantity_qtl": "sum"}).dropna().reset_index()
        corr = daily["total_rainfall_mm"].corr(daily["arrival_quantity_qtl"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["total_rainfall_mm"], y=daily["arrival_quantity_qtl"],
            mode="markers",
            marker=dict(color="#059669", size=8, opacity=0.75, line=dict(color="#ffffff", width=1)),
            hovertemplate="Rainfall: <b>%{x:.1f} mm</b><br>Arrivals: <b>%{y:,.0f} Qtl</b><extra></extra>",
            name="Daily Reading",
        ))
        x = daily["total_rainfall_mm"].to_numpy(dtype=float)
        y = daily["arrival_quantity_qtl"].to_numpy(dtype=float)
        m, b = np.polyfit(x, y, 1)
        xr = np.linspace(x.min(), x.max(), 100)
        fig.add_trace(go.Scatter(
            x=xr, y=m * xr + b,
            mode="lines",
            line=dict(color="#f59e0b", width=2.5, dash="dash"),
            name="Trendline",
        ))
        fig.update_layout(
            **CHART_THEME,
            height=370,
            title=dict(text=f"<b>Rainfall vs Arrival Correlation (r = {corr:.3f})</b>", font=dict(family="'Plus Jakarta Sans', sans-serif", size=13)),
            xaxis=dict(**AXIS_STYLE, title="Precipitation (mm)"),
            yaxis=dict(**AXIS_STYLE, title="Daily Inflows (Qtl)"),
        )
        code = textwrap.dedent("""
            daily = df.groupby('date').agg({'total_rainfall_mm': 'mean', 'arrival_quantity_qtl': 'sum'}).dropna().reset_index()
            fig = px.scatter(daily, x='total_rainfall_mm', y='arrival_quantity_qtl', trendline='ols')
        """).strip()
        insight = textwrap.dedent(f"""
            ### 🌦️ Climatic Influence Findings
            - Pearson correlation between precipitation and arrival volume measures **{corr:.3f}**.
            - Heavy rainfall episodes correspond with temporary disruptions in transport hauls, leading to delayed arrivals followed by compensatory volume surges.
        """).strip()
        return fig, code, insight


# ── Insight Prompts & Summarization ───────────────────────────────────────────

INSIGHT_SYSTEM_PROMPT = """You are MandiFlow Intelligence, an executive agricultural supply chain economist and commodities market analyst.
You are provided with the exact chart query and the real-world aggregated numbers, market volumes, prices, and distributions plotted on the user's dashboard.

STRICT OPERATIONAL RULES:
1. NEVER discuss Python code, pandas, scripts, programming environments, or tell the user to "run code" or "inspect df". The user is an executive viewing a dashboard.
2. NEVER say "without seeing the actual data" or "I cannot see the DataFrame". You have the exact plotted data points and numbers right in front of you.
3. Treat the data as live, verified wholesale market intelligence from Indian agricultural mandis.
4. Provide structured, executive-ready analytical commentary with the following 3 sections using clear markdown:
   - **Executive Headline**: A direct, 1-2 sentence market takeaway summarizing the primary pattern or dominant leader.
   - **Key Quantified Observations**: 3 bullet points citing the specific numbers, percentage spreads, volumes, or price variations from the plotted data.
   - **Strategic Supply Chain Implications**: 1-2 actionable insights for procurement logistics, storage planning, MSP floor defense, or transit management.
"""


def _summarize_visual_data(visual: dict) -> str:
    """Extract human-readable data points, categories, and metrics from Plotly fig_dict."""
    if not visual:
        return "No visual data available."
    fig_dict = visual.get("fig_dict", {})
    traces = fig_dict.get("data", [])
    layout = fig_dict.get("layout", {})

    lines = []
    t_obj = layout.get("title", "")
    t_text = t_obj.get("text", "") if isinstance(t_obj, dict) else str(t_obj or "")
    if t_text:
        clean_title = re.sub(r"<[^>]+>", "", t_text).strip()
        lines.append(f"Chart Title: {clean_title}")

    x_axis = layout.get("xaxis", {}).get("title", {}).get("text", "")
    y_axis = layout.get("yaxis", {}).get("title", {}).get("text", "")
    if x_axis or y_axis:
        lines.append(f"Axes: X={x_axis or 'Dimension'}, Y={y_axis or 'Metric'}")

    for idx, trace in enumerate(traces):
        name = trace.get("name") or f"Series {idx + 1}"
        x = trace.get("x")
        y = trace.get("y")
        labels = trace.get("labels")
        values = trace.get("values")

        if labels is not None and values is not None:
            pairs = [
                f"{str(l)}: {v:,.2f}" if isinstance(v, float) else f"{str(l)}: {v:,}" if isinstance(v, int) else f"{str(l)}: {v}"
                for l, v in zip(list(labels)[:15], list(values)[:15])
            ]
            lines.append(f"Plotted Data ({name}): " + "; ".join(pairs))
        elif x is not None and y is not None:
            pairs = []
            for xi, yi in zip(list(x)[:15], list(y)[:15]):
                y_str = f"{yi:,.2f}" if isinstance(yi, float) else f"{yi:,}" if isinstance(yi, int) else str(yi)
                x_str = f"{xi:,.2f}" if isinstance(xi, float) else f"{xi:,}" if isinstance(xi, int) else str(xi)
                pairs.append(f"{x_str}: {y_str}")
            lines.append(f"Plotted Values ({name}): " + "; ".join(pairs))

    return "\n".join(lines) if lines else "Plotted Data: Values extracted from visual."


def _build_insight_messages(last_visual: dict, user_question: str = "") -> list:
    data_summary = _summarize_visual_data(last_visual)
    query_context = last_visual.get("query", "Market Analysis")
    user_prompt = f"Chart Subject / Query: {query_context}\n{data_summary}\n"
    if user_question and user_question.strip().lower() not in ("/insight", "/insights", "insight"):
        user_prompt += f"\nUser Question: {user_question.strip()}\n"
    user_prompt += "\nAnalyze the exact figures above and provide executive market intelligence and strategic supply chain implications."
    return [
        {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def _get_last_visual() -> Optional[dict]:
    for msg in reversed(st.session_state.ai_history):
        if msg.get("role") == "assistant" and msg.get("fig_dict"):
            return msg
    return None


# ── Auto-scroll Helper ────────────────────────────────────────────────────────

def _inject_auto_scroll():
    """Inject JavaScript to smoothly scroll the page down to the latest generated content."""
    components.html(
        """
        <script>
        function scrollToLatest() {
            try {
                const doc = window.parent.document;
                const anchor = doc.getElementById('latest-output-anchor');
                if (anchor) {
                    anchor.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    return;
                }
                const main = doc.querySelector('section[data-testid="stMain"]') || doc.querySelector('.main');
                if (main) {
                    main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' });
                } else {
                    window.parent.scrollTo({ top: doc.body.scrollHeight, behavior: 'smooth' });
                }
            } catch (e) {}
        }
        setTimeout(scrollToLatest, 80);
        setTimeout(scrollToLatest, 300);
        setTimeout(scrollToLatest, 700);
        setTimeout(scrollToLatest, 1200);
        </script>
        """,
        height=0,
    )


# ── Custom CSS for Floating Chat & Aesthetic ──────────────────────────────────

_AI_CHAT_CSS = """
<style>
/* Modern floating chat bar pinned at bottom of viewport */
[data-testid="stBottom"] {
    background: linear-gradient(180deg, rgba(248, 250, 252, 0) 0%, rgba(248, 250, 252, 0.94) 20%, #f8fafc 100%) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    padding-bottom: 14px !important;
}

[data-testid="stChatInput"] {
    border-radius: 18px !important;
    border: 1.5px solid #cbd5e1 !important;
    background: #ffffff !important;
    box-shadow: 0 4px 24px -2px rgba(15, 23, 42, 0.09) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #059669 !important;
    box-shadow: 0 0 0 3.5px rgba(5, 150, 105, 0.16) !important;
}

[data-testid="stChatInputSubmitButton"] {
    color: #059669 !important;
}

/* Insight card design */
.mandi-insight-container {
    margin: 0.8rem 0;
    padding: 1.1rem 1.3rem;
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border: 1px solid #a7f3d0;
    border-radius: 14px;
    box-shadow: 0 3px 12px -2px rgba(5, 150, 105, 0.08);
}
</style>
"""


# ── Render Page ───────────────────────────────────────────────────────────────

def render(df: pd.DataFrame) -> None:
    st.markdown(_AI_CHAT_CSS, unsafe_allow_html=True)

    st.markdown(styles.page_header(
        "MandiFlow AI Assistant",
        "Interact with agricultural data in natural language. Query arrivals, price realization, weather impacts, and logistics corridors.",
        badge="NATURAL LANGUAGE AI",
    ), unsafe_allow_html=True)

    client, api_key = _get_client()

    # Session state initialization
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []
    if "_scroll_needed" not in st.session_state:
        st.session_state._scroll_needed = False

    # ── Quick Prompts & Controls ──────────────────────────────────────────────
    st.markdown("""
<div style="font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin: 0.8rem 0 0.4rem 0;">
  ⚡ Quick Sample Analytics (Click to Run Immediately)
</div>
""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2.5, 2.5, 2.5, 1.2])
    quick_query = ""
    with col1:
        if st.button("📊 Top 5 Crops by Inflow", key="quick_p1", use_container_width=True):
            quick_query = "Top 5 Crops by Inflow"
    with col2:
        if st.button("🛡️ Price vs MSP Parity", key="quick_p2", use_container_width=True):
            quick_query = "Price vs MSP Gap by Crop"
    with col3:
        if st.button("🌦️ Rainfall vs Arrivals", key="quick_p3", use_container_width=True):
            quick_query = "Rainfall vs Arrival Trend"
    with col4:
        if st.button("🗑️ Clear", key="clear_chat_top", use_container_width=True):
            st.session_state.ai_history = []
            if "stream_insight_for_idx" in st.session_state:
                del st.session_state["stream_insight_for_idx"]
            st.rerun()

    # ── Command Helper Guide ───────────────────────────────────────────────────
    st.markdown("""
<div style="margin-top: 0.5rem; margin-bottom: 1.2rem; padding: 0.65rem 1rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.03);">
  <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 0.80rem;">
    <span style="font-weight: 700; color: #059669; font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 4px;">
      <span>⚡</span> Commands:
    </span>
    <span style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 2px 7px; border-radius: 6px; font-family: 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 0.78rem; font-weight: 700; color: #065f46;">/new &lt;query&gt;</span>
    <span style="color: #64748b; font-size: 0.75rem;">New visual</span>
    <span style="color: #cbd5e1;">•</span>
    <span style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 2px 7px; border-radius: 6px; font-family: 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 0.78rem; font-weight: 700; color: #166534;">/followup &lt;changes&gt;</span>
    <span style="color: #64748b; font-size: 0.75rem;">Modify visual</span>
    <span style="color: #cbd5e1;">•</span>
    <span style="background: #fffbeb; border: 1px solid #fde68a; padding: 2px 7px; border-radius: 6px; font-family: 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 0.78rem; font-weight: 700; color: #92400e;">/insight [prompt]</span>
    <span style="color: #64748b; font-size: 0.75rem;">Strategic insight</span>
  </div>
  <div style="font-size: 0.73rem; color: #64748b; font-weight: 500;">
    Type below in the floating chat bar
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Handle quick queries ──────────────────────────────────────────────────
    if quick_query:
        st.session_state._scroll_needed = True
        _handle_query(quick_query, df, client, api_key)
        return

    # ── Render chat history ───────────────────────────────────────────────────
    history = st.session_state.ai_history

    if not history and "stream_insight_for_idx" not in st.session_state:
        st.markdown("""
<div style="text-align:center; padding: 3.5rem 2rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; margin-top: 0.5rem; margin-bottom: 2rem; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03);">
  <div style="font-size:2.8rem; margin-bottom:0.6rem;">✨</div>
  <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color:#0f172a; margin-bottom:0.4rem;">Natural Language Market Query Engine</h3>
  <p style="font-size:0.88rem; color:#64748b; max-width: 500px; margin: 0 auto; line-height: 1.5;">
    Query wholesale prices, inflow volumes, weather correlations, or corridor transit bottlenecks in plain English.
    Type your prompt in the floating chat bar at the bottom ↓
  </p>
</div>
""", unsafe_allow_html=True)
    else:
        for i, msg in enumerate(history):
            role = msg.get("role", "")

            if role == "user":
                st.markdown(
                    f'<div style="text-align:right; margin: 1rem 0;">'
                    f'<span style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color:#ffffff; padding: 10px 18px; border-radius: 18px 18px 4px 18px;'
                    f'font-size:0.9rem; font-weight: 500; display:inline-block; max-width:80%; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);">'
                    f'💬 {msg["text"]}</span></div>',
                    unsafe_allow_html=True,
                )

            elif role == "assistant":
                fig_dict = msg.get("fig_dict")
                model_tag = msg.get("model", "Built-in Analytics Engine")
                is_followup = msg.get("is_followup", False)
                tag = "↺ Follow-up" if is_followup else "✨ AI Generated Chart"

                with st.container():
                    st.markdown(
                        f'<div style="font-size:0.75rem; font-weight: 700; color:#059669; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom:0.4rem;">'
                        f'{tag} · <span style="color:#64748b; font-weight: 500;">{model_tag}</span></div>',
                        unsafe_allow_html=True,
                    )
                    if fig_dict:
                        import plotly.io as pio
                        fig = pio.from_json(go.Figure(fig_dict).to_json())
                        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

                    b1, b2 = st.columns([2, 5])
                    with b1:
                        if st.button("📊 Generate Insight", key=f"insight_btn_{i}"):
                            st.session_state["stream_insight_for_idx"] = i
                            st.session_state._scroll_needed = True
                            st.rerun()
                    with b2:
                        if msg.get("code"):
                            with st.expander("🔍 View Python Code"):
                                st.code(msg.get("code", ""), language="python")

            elif role == "insight":
                with st.container():
                    st.markdown("""
<div style="margin: 0.8rem 0; padding: 1.1rem 1.3rem; background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); border: 1.5px solid #a7f3d0; border-radius: 14px;">
  <div style="font-size: 0.72rem; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">💡 Analytical Intelligence</div>
""", unsafe_allow_html=True)
                    st.markdown(msg.get("markdown", ""))
                    st.markdown("</div>", unsafe_allow_html=True)

            elif role == "error":
                with st.container():
                    st.error(f"**{msg.get('title', 'Notice')}:** {msg.get('text', '')}")
                    if msg.get("code"):
                        with st.expander("Generated code"):
                            st.code(msg["code"], language="python")

    # ── Handle Streaming Insight if triggered ─────────────────────────────────
    if "stream_insight_for_idx" in st.session_state:
        target_idx = st.session_state["stream_insight_for_idx"]
        target_visual = None
        if 0 <= target_idx < len(history) and history[target_idx].get("fig_dict"):
            target_visual = history[target_idx]
        else:
            target_visual = _get_last_visual()

        if target_visual:
            st.markdown("""
<div style="margin: 0.8rem 0; padding: 1.1rem 1.3rem; background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); border: 1.5px solid #a7f3d0; border-radius: 14px;">
  <div style="font-size: 0.72rem; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">
    💡 Analytical Intelligence &nbsp;<span style="font-weight: 500; color: #047857; text-transform: none; font-size: 0.72rem;">· streaming insights…</span>
  </div>
""", unsafe_allow_html=True)

            model_name = "MandiFlow Instant Analytics"
            if not api_key:
                _, _, demo_text = _run_demo_query(target_visual.get("query", ""), df)
                def _demo_token_stream():
                    for token in re.split(r'(\s+)', demo_text):
                        yield token
                        time.sleep(0.012)
                full_text = st.write_stream(_demo_token_stream())
            else:
                model_name = _resolve_model(client)
                messages = _build_insight_messages(target_visual)
                stream_resp = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=900,
                    stream=True,
                )
                def _groq_token_stream():
                    for chunk in stream_resp:
                        delta = chunk.choices[0].delta
                        token = getattr(delta, "content", None)
                        if token:
                            yield token
                full_text = st.write_stream(_groq_token_stream())

            st.markdown("</div>", unsafe_allow_html=True)

            # Persist the streamed insight into history
            st.session_state.ai_history.append({
                "role": "insight",
                "markdown": full_text if isinstance(full_text, str) else "",
                "model": model_name,
                "query": "/insight",
            })
            del st.session_state["stream_insight_for_idx"]
            st.session_state._scroll_needed = True
            st.rerun()

    # Anchor at the end of generated content
    st.markdown('<div id="latest-output-anchor" style="height: 1px; margin-bottom: 80px;"></div>', unsafe_allow_html=True)

    # ── Auto-scroll injection if needed ───────────────────────────────────────
    if st.session_state.get("_scroll_needed"):
        _inject_auto_scroll()
        st.session_state._scroll_needed = False

    # ── Floating Chat Input at Bottom (Native Streamlit Sticky Bottom) ─────────
    chat_prompt = st.chat_input(
        "💬  Ask about crop prices, arrivals, weather, transport corridors... or /new, /followup, /insight"
    )
    if chat_prompt and chat_prompt.strip():
        st.session_state._scroll_needed = True
        _handle_query(chat_prompt.strip(), df, client, api_key)


# ── Query Handler ─────────────────────────────────────────────────────────────

def _handle_query(query: str, df: pd.DataFrame, client, api_key: str) -> None:
    """Intelligently route query to live Groq LLM or Built-in Analytics Engine."""
    history = st.session_state.ai_history
    history.append({"role": "user", "text": query})

    command, payload = _parse_command(query)

    # If it's an insight command, trigger streaming insight directly
    if command == "insight" or "insight" in query.lower():
        last_vis = _get_last_visual()
        if not last_vis:
            history.append({
                "role": "error",
                "title": "No Chart Found",
                "text": "Generate a chart first, then ask for /insight.",
            })
            st.session_state.ai_history = history
            st.session_state._scroll_needed = True
            st.rerun()
            return
        # Find target index
        for idx in range(len(history) - 1, -1, -1):
            if history[idx].get("fig_dict"):
                st.session_state["stream_insight_for_idx"] = idx
                st.session_state._scroll_needed = True
                st.session_state.ai_history = history
                st.rerun()
                return

    # If no API key is provided, handle with built-in instant demo engine
    if not api_key:
        fig, code, insight = _run_demo_query(payload or query, df)
        history.append({
            "role": "assistant",
            "fig_dict": fig.to_dict(),
            "code": code,
            "query": payload or query,
            "model": "MandiFlow Instant Analytics Engine",
            "is_followup": False,
        })
        st.session_state.ai_history = history
        st.session_state._scroll_needed = True
        st.rerun()
        return

    # Live Groq API Execution
    model = _resolve_model(client)
    generated_code = ""

    try:
        prev_context = ""
        if command == "followup":
            last_visual = _get_last_visual()
            if last_visual:
                prev_context = f"\nPrevious chart query: '{last_visual.get('query')}'.\nPrevious code:\n```python\n{last_visual.get('code')}\n```\n"

        user_msg = f"{prev_context}Generate chart code for: {payload}" if prev_context else payload
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _system_prompt(df)},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1, max_tokens=1200,
        )
        generated_code = _sanitize_code(resp.choices[0].message.content.strip())
        scope = {"df": df.copy(), "pd": pd, "px": px, "go": go, "np": np}
        exec(generated_code, scope)  # noqa: S102
        fig = scope.get("fig")
        if fig is None:
            history.append({
                "role": "error",
                "title": "No Chart Produced",
                "text": "Model did not output a 'fig' object. Try rephrasing.",
                "code": generated_code,
            })
        else:
            history.append({
                "role": "assistant",
                "fig_dict": fig.to_dict(),
                "code": generated_code,
                "query": payload or query,
                "model": model,
                "is_followup": (command == "followup"),
            })

    except Exception as exc:
        history.append({
            "role": "error",
            "title": "Query Error",
            "text": str(exc),
            "code": generated_code,
        })

    st.session_state.ai_history = history
    st.session_state._scroll_needed = True
    st.rerun()
