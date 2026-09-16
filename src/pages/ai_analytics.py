"""MandiFlow – AI Analytics Page

Streamlit port of the original Dash AI chat feature.
Uses Groq's OpenAI-compatible API to generate Plotly charts from natural language.
Commands:
  /new  <query>        – generate a fresh chart (default)
  /followup <changes>  – modify the last chart
  /insight [question]  – get analytical insights on the last chart
"""

from __future__ import annotations

import re
import textwrap
import traceback
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import styles


# ── Groq / OpenAI client ──────────────────────────────────────────────────────

def _get_client():
    """Return an OpenAI-compatible client pointed at Groq, or None."""
    try:
        from openai import OpenAI
        import os
        key = (
            st.secrets.get("GROQ_API_KEY", "")
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
        import os
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

        Instructions:
        - Output ONLY valid, executable Python code.
        - NEVER include markdown fences (no ```python). No explanations.
        - You have access to: `df`, `pd`, `px`, `go`.
        - Assign the final generated Plotly figure to the variable `fig`.
        - Use template="plotly_white".
        - Give charts clean titles, color palettes, and axis labels.
        - Do NOT call `fig.show()`.
    """).strip()


def _followup_prompt(df: pd.DataFrame, prev_code: str, prev_query: str, followup: str) -> str:
    col_info = "\n".join(f"  - {c}: {dt}" for c, dt in df.dtypes.items())
    return textwrap.dedent(f"""
        You are an expert agricultural supply chain data analyst.
        The pandas DataFrame `df` has {df.shape[0]:,} rows.

        Available columns:
{col_info}

        The user previously asked: "{prev_query}"
        Here is the Python code that generated the current chart:
        --- EXISTING CODE START ---
        {prev_code}
        --- EXISTING CODE END ---

        The user now wants to MODIFY or FOLLOW UP:
        "{followup}"

        Instructions:
        - Apply the requested changes to the EXISTING code above.
        - Output ONLY valid, executable Python code (the complete modified script).
        - NEVER include markdown fences. No explanations.
        - Assign the final figure to `fig`. Use template="plotly_white".
        - Do NOT call `fig.show()`.
    """).strip()


def _insight_prompt(df: pd.DataFrame, prev_code: str, prev_query: str, question: str) -> str:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    stats = []
    for c in numeric_cols[:8]:
        s = df[c].dropna()
        if len(s) > 0:
            stats.append(f"  - {c}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}")
    extra = f'\nUser question: "{question}"' if question else ""
    return textwrap.dedent(f"""
        You are a senior agricultural economist specialising in Indian mandi markets.
        The DataFrame `df` was used to create the chart below, with {df.shape[0]:,} rows.

        Dataset numeric summary:
{chr(10).join(stats)}

        The chart was generated by: "{prev_query}"
        Code:
        --- CODE START ---
        {prev_code}
        --- CODE END ---
        {extra}

        Provide a structured, insightful analysis in MARKDOWN format using this structure:

        ## 📊 Chart Summary
        Brief 1-2 sentence description.

        ## 📈 Key Trends
        - 3-4 bullet points describing the most important patterns.

        ## ⚠️ Anomalies & Notable Observations
        - Flag price spikes, MSP-price gaps, or irregular patterns.

        ## 🚜 Supply Chain & Farmer Impact
        - 2-3 actionable interpretations.

        ## 💡 Recommendations
        - 1-3 data-driven recommendations.

        Rules:
        - Be concise and specific. Reference actual crops/mandis/districts where possible.
        - Do NOT generate any Python code.
        - Output ONLY the markdown insights.
    """).strip()


def _sanitize_code(raw: str) -> str:
    code = re.sub(r"^```(?:python)?\s*", "", raw, flags=re.MULTILINE)
    code = re.sub(r"```\s*$", "", code, flags=re.MULTILINE)
    return code.strip()


# ── Page renderer ─────────────────────────────────────────────────────────────

def render(df: pd.DataFrame) -> None:
    st.markdown(styles.page_header(
        "AI Analytics ✨",
        "Query arrivals, prices, MSP, weather and transport using natural language.",
    ), unsafe_allow_html=True)

    # Initialise session state
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    client, api_key = _get_client()

    # ── API key status ─────────────────────────────────────────────────────
    if not api_key:
        st.warning(
            "**Groq API key not configured.**  \n"
            "Add `GROQ_API_KEY = 'your-key'` to `.streamlit/secrets.toml` (locally) "
            "or as a Secret in Streamlit Community Cloud settings.",
            icon="🔑",
        )
    else:
        model = _resolve_model(client)
        st.success(f"Connected — model: **{model.split('/')[-1]}**", icon="✅")

    # ── Command hint pills ─────────────────────────────────────────────────
    st.markdown("""
<div style="display:flex;gap:8px;align-items:center;margin-bottom:0.75rem;flex-wrap:wrap;">
  <span style="font-size:0.75rem;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Supported Commands:</span>
  <code style="background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0;border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:600;">/new &lt;query&gt;</code>
  <code style="background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:600;">/followup &lt;changes&gt;</code>
  <code style="background:#fefce8;color:#a16207;border:1px solid #fef08a;border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:600;">/insight [question]</code>
</div>
""", unsafe_allow_html=True)

    # ── Quick Prompts ──────────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; margin-bottom: 0.35rem;'>Quick Sample Prompts (Click to execute):</div>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns(3)
    quick_query = None
    with p_col1:
        if st.button("📊 Top 5 Crops by Inflow", key="quick_p1", use_container_width=True):
            quick_query = "Plot the top 5 crops by total arrival quantity as a horizontal bar chart."
    with p_col2:
        if st.button("⚖️ Price vs MSP Gap by Crop", key="quick_p2", use_container_width=True):
            quick_query = "Create a bar chart showing the difference between modal price and MSP for each crop."
    with p_col3:
        if st.button("🌧️ Rainfall vs Arrival Trend", key="quick_p3", use_container_width=True):
            quick_query = "Show a scatter plot of total rainfall vs arrival quantity with a trendline."

    # ── Chat input ─────────────────────────────────────────────────────────
    with st.form("ai_chat_form", clear_on_submit=True):
        col_inp, col_btn, col_clr = st.columns([7, 1, 1])
        with col_inp:
            user_input = st.text_input(
                "Query",
                placeholder="Ask a question or use /new  /followup  /insight …",
                label_visibility="collapsed",
            )
        with col_btn:
            send = st.form_submit_button("Send ↵", use_container_width=True)
        with col_clr:
            clear = st.form_submit_button("Clear", use_container_width=True)

    if quick_query:
        _process_query(quick_query, df, client, api_key)

    # Handle clear
    if clear:
        st.session_state.ai_history = []
        st.rerun()

    # Handle send
    if send and user_input and user_input.strip():
        _process_query(user_input.strip(), df, client, api_key)

    # ── Render chat history ────────────────────────────────────────────────
    history = st.session_state.ai_history

    if not history:
        st.markdown("""
<div style="text-align:center;padding:3rem 2rem;color:#9ca3af;">
  <div style="font-size:2.5rem;margin-bottom:0.5rem;">✨</div>
  <h4 style="color:#374151;margin-bottom:0.5rem;">Ask MandiFlow AI</h4>
  <p style="font-size:0.9rem;">Inquire about modal prices, arrival volumes, weather impacts, or transit delays across mandis.</p>
  <p style="font-size:0.8rem;margin-top:1rem;">
    Try: <em>"Show monthly average modal price by crop"</em> or
    <em>"Which districts have the highest rainfall-to-arrival correlation?"</em>
  </p>
</div>
""", unsafe_allow_html=True)
        return

    # Render messages newest-last
    for i, msg in enumerate(history):
        role = msg.get("role", "")

        if role == "user":
            st.markdown(
                f'<div style="text-align:right;margin:0.75rem 0;">'
                f'<span style="background:#1a6b3c;color:#fff;padding:8px 14px;border-radius:18px 18px 4px 18px;'
                f'font-size:0.9rem;display:inline-block;max-width:80%;">{msg["text"]}</span></div>',
                unsafe_allow_html=True,
            )

        elif role == "assistant":
            fig_dict = msg.get("fig_dict")
            model_tag = msg.get("model", "").split("/")[-1]
            is_followup = msg.get("is_followup", False)
            tag = "↺ Follow-up" if is_followup else "✨ New chart"

            with st.container():
                st.markdown(
                    f'<div style="font-size:0.75rem;color:#6b7280;margin-bottom:0.3rem;">'
                    f'{tag} · {model_tag}</div>',
                    unsafe_allow_html=True,
                )
                if fig_dict:
                    import plotly.io as pio
                    fig = pio.from_json(go.Figure(fig_dict).to_json())
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

                # Quick-action buttons on each chart card
                b1, b2, b3, _ = st.columns([1, 1, 1, 4])
                with b1:
                    if st.button("📊 Insight", key=f"insight_btn_{i}"):
                        _trigger_insight(i, df, client, api_key)
                with b2:
                    if st.button("↺ Follow up", key=f"followup_btn_{i}"):
                        st.session_state["_prefill_followup"] = i
                with b3:
                    with st.expander("🔍 Code"):
                        st.code(msg.get("code", ""), language="python")

        elif role == "insight":
            with st.container():
                st.markdown(
                    f'<div style="background:#f0fdf4;border-left:3px solid #1a6b3c;'
                    f'padding:1rem 1.25rem;border-radius:0 8px 8px 0;margin:0.5rem 0;">',
                    unsafe_allow_html=True,
                )
                st.markdown(msg.get("markdown", ""))
                st.markdown("</div>", unsafe_allow_html=True)

        elif role == "error":
            with st.container():
                st.error(f"**{msg.get('title', 'Error')}:** {msg.get('text', '')}")
                if msg.get("code"):
                    with st.expander("Generated code"):
                        st.code(msg["code"], language="python")
                if msg.get("traceback"):
                    with st.expander("Traceback"):
                        st.text(msg["traceback"])

    # Handle pre-filled followup
    if "_prefill_followup" in st.session_state:
        st.info("💡 Type your `/followup <changes>` in the input above and click Send.")
        del st.session_state["_prefill_followup"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_last_visual() -> Optional[dict]:
    for msg in reversed(st.session_state.ai_history):
        if msg.get("role") == "assistant" and msg.get("fig_dict"):
            return msg
    return None


def _process_query(query: str, df: pd.DataFrame, client, api_key: str) -> None:
    """Parse the query and call the appropriate AI action."""
    history = st.session_state.ai_history
    history.append({"role": "user", "text": query})

    if not api_key:
        history.append({
            "role": "error",
            "title": "API Key Missing",
            "text": "GROQ_API_KEY is not configured. Add it to .streamlit/secrets.toml.",
        })
        st.session_state.ai_history = history
        st.rerun()
        return

    command, payload = _parse_command(query)
    model = _resolve_model(client)
    generated_code = ""

    try:
        if command == "insight":
            last_visual = _get_last_visual()
            if last_visual is None:
                history.append({
                    "role": "error",
                    "title": "No Visual Found",
                    "text": "Generate a chart first, then ask for /insight.",
                })
            else:
                prompt = _insight_prompt(df, last_visual.get("code", ""), last_visual.get("query", ""), payload)
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3, max_tokens=1800,
                )
                history.append({
                    "role": "insight",
                    "markdown": resp.choices[0].message.content.strip(),
                    "model": model,
                    "query": query,
                })

        elif command == "followup":
            last_visual = _get_last_visual()
            if last_visual is None:
                history.append({
                    "role": "error",
                    "title": "No Visual to Follow Up On",
                    "text": "Generate a chart first, then use /followup.",
                })
            else:
                prompt = _followup_prompt(df, last_visual.get("code", ""), last_visual.get("query", ""), payload)
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1, max_tokens=1400,
                )
                generated_code = _sanitize_code(resp.choices[0].message.content.strip())
                scope = {"df": df.copy(), "pd": pd, "px": px, "go": go}
                exec(generated_code, scope)  # noqa: S102
                fig = scope.get("fig")
                if fig is None:
                    history.append({"role": "error", "title": "No Chart Produced", "text": "Try rephrasing.", "code": generated_code})
                else:
                    history.append({"role": "assistant", "fig_dict": fig.to_dict(), "code": generated_code, "query": payload, "model": model, "is_followup": True})

        else:  # new
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
                history.append({"role": "error", "title": "No Chart Produced", "text": "Try rephrasing.", "code": generated_code})
            else:
                history.append({"role": "assistant", "fig_dict": fig.to_dict(), "code": generated_code, "query": payload, "model": model, "is_followup": False})

    except Exception as exc:
        history.append({
            "role": "error",
            "title": "Execution Error",
            "text": str(exc),
            "traceback": traceback.format_exc(),
            "code": generated_code,
        })

    st.session_state.ai_history = history
    st.rerun()


def _trigger_insight(visual_idx: int, df: pd.DataFrame, client, api_key: str) -> None:
    """Trigger an insight on a specific chart by index in history."""
    assistant_msgs = [m for m in st.session_state.ai_history if m.get("role") == "assistant"]
    if visual_idx >= len(assistant_msgs):
        return
    # Temporarily set the last visual and trigger insight
    target = assistant_msgs[visual_idx]
    history = st.session_state.ai_history
    history.append({"role": "user", "text": "/insight"})

    if not api_key:
        history.append({"role": "error", "title": "API Key Missing", "text": "GROQ_API_KEY not set."})
        st.session_state.ai_history = history
        st.rerun()
        return

    model = _resolve_model(client)
    prompt = _insight_prompt(df, target.get("code", ""), target.get("query", ""), "")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=1800,
        )
        history.append({"role": "insight", "markdown": resp.choices[0].message.content.strip(), "model": model, "query": "/insight"})
    except Exception as exc:
        history.append({"role": "error", "title": "Insight Error", "text": str(exc)})

    st.session_state.ai_history = history
    st.rerun()
