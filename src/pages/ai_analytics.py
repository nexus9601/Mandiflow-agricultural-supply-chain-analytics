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
import traceback
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import styles
from src.styles import COLORS, CHART_THEME, AXIS_STYLE


# ── Groq / OpenAI client ──────────────────────────────────────────────────────

def _get_client():
    """Return an OpenAI-compatible client pointed at Groq, or None."""
    try:
        from openai import OpenAI
        key = (
            st.session_state.get("user_groq_key", "")
            or st.secrets.get("GROQ_API_KEY", "")
            or os.environ.get("GROQ_API_KEY", "")
        )
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
    
    if "inflow" in q_lower or "top 5" in q_lower or "crop" in q_lower and "arrival" in q_lower:
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


# ── Render Page ───────────────────────────────────────────────────────────────

def render(df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "MandiFlow AI Assistant",
        "Interact with agricultural data in natural language. Query arrivals, price realization, weather impacts, and logistics corridors.",
        badge="NATURAL LANGUAGE AI",
    ), unsafe_allow_html=True)

    client, api_key = _get_client()

    # Session state initialization
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    # ── API Key Configuration Bar ─────────────────────────────────────────────
    with st.expander("🔑 AI Engine Configuration & Model Settings", expanded=not bool(api_key)):
        c_k1, c_k2 = st.columns([3, 1])
        with c_k1:
            entered_key = st.text_input(
                "Groq API Key (Optional for demo, required for freeform LLM generation)",
                value=st.session_state.get("user_groq_key", ""),
                type="password",
                placeholder="gsk_...",
                help="Get a free ultra-fast Groq API key at console.groq.com",
            )
            if entered_key != st.session_state.get("user_groq_key", ""):
                st.session_state["user_groq_key"] = entered_key
                st.rerun()
        with c_k2:
            st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
            if api_key:
                st.markdown('<span style="color:#059669; font-weight:700; font-size:0.85rem;">● Groq Connected</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#d97706; font-weight:600; font-size:0.85rem;">● Instant Demo Mode Active</span>', unsafe_allow_html=True)

    # ── Quick Prompts ─────────────────────────────────────────────────────────
    st.markdown("""
<div style="font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin: 0.8rem 0 0.4rem 0;">
  ⚡ Quick Sample Analytics (Click to Run Immediately)
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    quick_query = ""
    with col1:
        if st.button("📊 Top 5 Crops by Inflow Volume", key="quick_p1", use_container_width=True):
            quick_query = "Top 5 Crops by Inflow"
    with col2:
        if st.button("🛡️ Price vs MSP Floor Parity", key="quick_p2", use_container_width=True):
            quick_query = "Price vs MSP Gap by Crop"
    with col3:
        if st.button("🌦️ Rainfall vs Arrival Dynamics", key="quick_p3", use_container_width=True):
            quick_query = "Rainfall vs Arrival Trend"

    # ── Chat input ────────────────────────────────────────────────────────────
    with st.form("ai_chat_form", clear_on_submit=True):
        col_inp, col_btn, col_clr = st.columns([7, 1.2, 1])
        with col_inp:
            user_input = st.text_input(
                "Query",
                placeholder="Ask any question or use /new, /followup, /insight ...",
                label_visibility="collapsed",
            )
        with col_btn:
            send = st.form_submit_button("Send ↵", use_container_width=True)
        with col_clr:
            clear = st.form_submit_button("Clear", use_container_width=True)

    if quick_query:
        _handle_query(quick_query, df, client, api_key)

    if clear:
        st.session_state.ai_history = []
        st.rerun()

    if send and user_input and user_input.strip():
        _handle_query(user_input.strip(), df, client, api_key)

    # ── Render chat history ───────────────────────────────────────────────────
    history = st.session_state.ai_history

    if not history:
        st.markdown("""
<div style="text-align:center; padding: 3.5rem 2rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; margin-top: 1rem; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03);">
  <div style="font-size:2.8rem; margin-bottom:0.6rem;">✨</div>
  <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color:#0f172a; margin-bottom:0.4rem;">Natural Language Market Query Engine</h3>
  <p style="font-size:0.88rem; color:#64748b; max-width: 500px; margin: 0 auto; line-height: 1.5;">
    Query wholesale prices, inflow volumes, weather correlations, or corridor transit bottlenecks in plain English.
  </p>
  <div style="margin-top: 1.2rem; display: inline-flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
    <span style="background:#f1f5f9; padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; font-weight: 600; color: #475569;">/new &lt;query&gt;</span>
    <span style="background:#f1f5f9; padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; font-weight: 600; color: #475569;">/followup &lt;changes&gt;</span>
    <span style="background:#f1f5f9; padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; font-weight: 600; color: #475569;">/insight [question]</span>
  </div>
</div>
""", unsafe_allow_html=True)
        return

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
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                b1, b2, b3 = st.columns([1.2, 1.2, 4])
                with b1:
                    if st.button("📊 Generate Insight", key=f"insight_btn_{i}"):
                        _trigger_insight(i, df, client, api_key)
                with b2:
                    if st.button("↺ Refine Query", key=f"followup_btn_{i}"):
                        st.session_state["_prefill_followup"] = i
                with b3:
                    if msg.get("code"):
                        with st.expander("🔍 View Python Code"):
                            st.code(msg.get("code", ""), language="python")

        elif role == "insight":
            st.markdown(
                f"""
<div class="insight-card" style="margin: 0.8rem 0;">
  <h4>💡 Analytical Intelligence</h4>
  <div style="font-size: 0.88rem; line-height: 1.6; color: #1e293b;">
    {msg.get("markdown", "")}
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

        elif role == "error":
            with st.container():
                st.error(f"**{msg.get('title', 'Notice')}:** {msg.get('text', '')}")
                if msg.get("code"):
                    with st.expander("Generated code"):
                        st.code(msg["code"], language="python")


def _get_last_visual() -> Optional[dict]:
    for msg in reversed(st.session_state.ai_history):
        if msg.get("role") == "assistant" and msg.get("fig_dict"):
            return msg
    return None


def _handle_query(query: str, df: pd.DataFrame, client, api_key: str) -> None:
    """Intelligently route query to live Groq LLM or Built-in Analytics Engine."""
    history = st.session_state.ai_history
    history.append({"role": "user", "text": query})

    command, payload = _parse_command(query)

    # If no API key is provided, handle with built-in instant demo engine
    if not api_key:
        fig, code, insight = _run_demo_query(payload or query, df)
        history.append({
            "role": "assistant",
            "fig_dict": fig.to_dict(),
            "code": code,
            "query": payload,
            "model": "MandiFlow Instant Analytics Engine",
            "is_followup": False,
        })
        if command == "insight" or "insight" in query.lower():
            history.append({
                "role": "insight",
                "markdown": insight,
                "model": "MandiFlow Intelligence",
                "query": query,
            })
        st.session_state.ai_history = history
        st.rerun()
        return

    # Live Groq API Execution
    model = _resolve_model(client)
    generated_code = ""

    try:
        if command == "insight":
            last_visual = _get_last_visual()
            if last_visual is None:
                history.append({
                    "role": "error",
                    "title": "No Chart Found",
                    "text": "Generate a chart first, then ask for /insight.",
                })
            else:
                prompt = f"Analyze this agricultural chart code and query:\nQuery: {last_visual.get('query')}\nCode: {last_visual.get('code')}\nProvide 3 succinct takeaways."
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3, max_tokens=1200,
                )
                history.append({
                    "role": "insight",
                    "markdown": resp.choices[0].message.content.strip(),
                    "model": model,
                    "query": query,
                })
        else:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _system_prompt(df)},
                    {"role": "user", "content": payload},
                ],
                temperature=0.1, max_tokens=1200,
            )
            generated_code = _sanitize_code(resp.choices[0].message.content.strip())
            scope = {"df": df.copy(), "pd": pd, "px": px, "go": go}
            exec(generated_code, scope)  # noqa: S102
            fig = scope.get("fig")
            if fig is None:
                history.append({"role": "error", "title": "No Chart Produced", "text": "Model did not output a 'fig' object. Try rephrasing.", "code": generated_code})
            else:
                history.append({"role": "assistant", "fig_dict": fig.to_dict(), "code": generated_code, "query": payload, "model": model, "is_followup": (command == "followup")})

    except Exception as exc:
        history.append({
            "role": "error",
            "title": "Query Error",
            "text": str(exc),
            "code": generated_code,
        })

    st.session_state.ai_history = history
    st.rerun()


def _trigger_insight(visual_idx: int, df: pd.DataFrame, client, api_key: str) -> None:
    history = st.session_state.ai_history
    last_visual = _get_last_visual()
    if not last_visual:
        return
    
    if not api_key:
        _, _, insight = _run_demo_query(last_visual.get("query", ""), df)
        history.append({
            "role": "insight",
            "markdown": insight,
            "model": "MandiFlow Instant Analytics",
            "query": "/insight",
        })
        st.session_state.ai_history = history
        st.rerun()
        return

    model = _resolve_model(client)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"Analyze this chart:\nCode: {last_visual.get('code')}\nQuery: {last_visual.get('query')}"}],
            temperature=0.3, max_tokens=1200,
        )
        history.append({"role": "insight", "markdown": resp.choices[0].message.content.strip(), "model": model, "query": "/insight"})
    except Exception as exc:
        history.append({"role": "error", "title": "Insight Error", "text": str(exc)})

    st.session_state.ai_history = history
    st.rerun()
