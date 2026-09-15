import os
import re
import textwrap
import traceback
import json

import dash
from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

from utils.data_store import get_data
from dash_pages import dataset_view, manual_dashboard_view, ai_dashboard_view

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CONFIGURED_MODEL = os.getenv("GROQ_MODEL", "")

# Candidate models in priority order
CANDIDATE_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "openai/gpt-oss-20b",
    "groq/compound",
]

_ACTIVE_MODEL = CONFIGURED_MODEL or "openai/gpt-oss-120b"


def resolve_model(client: OpenAI) -> str:
    """Dynamically determine the best accessible model on the user's Groq account."""
    global _ACTIVE_MODEL
    if CONFIGURED_MODEL:
        _ACTIVE_MODEL = CONFIGURED_MODEL
        return _ACTIVE_MODEL

    try:
        available = {m.id for m in client.models.list().data}
        for candidate in CANDIDATE_MODELS:
            if candidate in available:
                _ACTIVE_MODEL = candidate
                return _ACTIVE_MODEL
        chat_models = [m for m in available if "guard" not in m and "whisper" not in m]
        if chat_models:
            _ACTIVE_MODEL = chat_models[0]
            return _ACTIVE_MODEL
    except Exception:
        pass

    _ACTIVE_MODEL = "openai/gpt-oss-120b"
    return _ACTIVE_MODEL


# Initialize model at startup if API key present
if GROQ_API_KEY:
    try:
        _init_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        _ACTIVE_MODEL = resolve_model(_init_client)
    except Exception:
        pass


app = dash.Dash(
    __name__,
    title="MandiFlow · Agricultural Analytics",
    suppress_callback_exceptions=True,
)
server = app.server

# ── App Shell Layout ──────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="chat-store", data=[]),
    # Store for pending quick-action (insight/followup triggered from button clicks)
    dcc.Store(id="quick-action-store", data=None),
    html.Div([
        html.Aside(id="sidebar-container", className="left-sidebar"),
        html.Main(id="page-content", className="page-content"),
    ], className="app-shell"),
])


# ── Navigation Sidebar Generator ──────────────────────────────
def build_sidebar(pathname):
    links = [
        ("/dataset", "📋", "Dataset Explorer", "Records & schema"),
        ("/manual-dashboard", "📊", "Manual Dashboard", "Interactive filters"),
        ("/ai-dashboard", "✨", "AI Analytics", "Conversational charts"),
    ]
    nav_items = []
    for href, icon, title, desc in links:
        is_active = (pathname == href) or (href == "/dataset" and pathname in ("/", ""))
        nav_items.append(
            dcc.Link([
                html.Span(icon, className="nav-link-icon"),
                html.Div([
                    html.Span(title, className="nav-link-title"),
                    html.Span(desc, className="nav-link-desc"),
                ], className="nav-link-text"),
            ], href=href, className="sidebar-nav-link active" if is_active else "sidebar-nav-link")
        )

    model_display = _ACTIVE_MODEL.split("/")[-1] if _ACTIVE_MODEL else "Groq AI"

    return [
        html.A([
            html.Span("🌾", className="brand-icon"),
            html.Div([
                html.Span("MandiFlow", className="brand-name"),
                html.Span("Agri Supply Chain", className="brand-sub"),
            ], className="brand-title-wrap"),
        ], href="/dataset", className="sidebar-brand"),

        html.Nav(nav_items, className="sidebar-nav"),

        html.Div([
            html.Div([
                html.Span("●", className="status-dot-green"),
                html.Span("Engine Connected", className="status-label"),
            ], className="system-status"),
            html.Div(model_display, className="model-tag"),
        ], className="sidebar-footer"),
    ]


# ── Routing Callback ──────────────────────────────────────────
ROUTES = {
    "/":                  dataset_view.layout,
    "/dataset":           dataset_view.layout,
    "/manual-dashboard":  manual_dashboard_view.layout,
    "/ai-dashboard":      ai_dashboard_view.layout,
}


@app.callback(
    [Output("sidebar-container", "children"),
     Output("page-content", "children")],
    Input("url", "pathname"),
)
def route(pathname):
    page_fn = ROUTES.get(pathname, dataset_view.layout)
    return build_sidebar(pathname), page_fn()


# ── Dataset Explorer Table Filter ─────────────────────────────
@app.callback(
    Output("dataset-table", "data"),
    [Input("dataset-crop-filter", "value"),
     Input("dataset-district-filter", "value"),
     Input("dataset-type-filter", "value")],
    prevent_initial_call=True,
)
def filter_dataset_table(crop, district, mtype):
    df = get_data()
    if crop and crop != "ALL":
        df = df[df["crop_name"] == crop]
    if district and district != "ALL":
        df = df[df["district"] == district]
    if mtype and mtype != "ALL":
        df = df[df["mandi_type"] == mtype]

    cols = [c for c in [
        "arrival_id", "date", "crop_name", "variety",
        "mandi_name", "district", "mandi_type",
        "arrival_quantity_qtl", "modal_price", "msp",
    ] if c in df.columns]
    return df[cols].head(100).to_dict("records")


# ── Command Parsing ───────────────────────────────────────────
def parse_command(text: str):
    """
    Returns (command, payload) where command is one of:
      'new'       - generate a fresh chart
      'followup'  - modify the most recent chart
      'insight'   - generate analytical insights on the most recent chart
    """
    t = text.strip()
    # /insight or /insights
    m = re.match(r"^/(insights?)\s*(.*)", t, re.IGNORECASE | re.DOTALL)
    if m:
        return "insight", m.group(2).strip()

    # /followup or /edit
    m = re.match(r"^/(followup|edit)\s+(.*)", t, re.IGNORECASE | re.DOTALL)
    if m:
        return "followup", m.group(2).strip()

    # /new
    m = re.match(r"^/new\s+(.*)", t, re.IGNORECASE | re.DOTALL)
    if m:
        return "new", m.group(1).strip()

    # Default: new chart
    return "new", t


def _get_last_visual(history):
    """Return the most recent assistant visual message from chat history."""
    for msg in reversed(history or []):
        if msg.get("role") == "assistant" and msg.get("fig_dict"):
            return msg
    return None


# ── System Prompts ────────────────────────────────────────────
def _generate_system_prompt(df):
    col_info = [f"  - {col}: {dtype}" for col, dtype in df.dtypes.items()]
    return textwrap.dedent(f"""
        You are an expert agricultural supply chain data analyst.
        The pandas DataFrame `df` is already loaded with {df.shape[0]:,} rows and {df.shape[1]} columns.

        IMPORTANT Column Mappings:
        - Crop name: `crop_name` (Do NOT use `crop`)
        - Price: `modal_price` (wholesale market price in ₹/quintal)
        - Minimum Support Price: `msp`
        - Arrival volume: `arrival_quantity_qtl`
        - Geography: `district`, `mandi_name`, `mandi_type`
        - Date: `date` (already datetime)
        - Weather: `avg_temperature_c`, `total_rainfall_mm`, `avg_humidity_percent`
        - Transport: `avg_distance_km`, `avg_transit_hours`, `transit_delay_rate`

        Available columns:
{chr(10).join(col_info)}

        Instructions:
        - Output ONLY valid, executable Python code.
        - NEVER include markdown fences (no ```python or ```). No explanations or comments before/after.
        - You have access to: `df`, `pd`, `px`, `go`.
        - Assign the final generated Plotly figure to the variable `fig`.
        - Use template="plotly_dark".
        - Give charts clean titles, color palettes, and axis labels.
        - Do NOT call `fig.show()`.
    """).strip()


def _generate_followup_prompt(df, previous_code: str, previous_query: str, followup_prompt: str):
    col_info = [f"  - {col}: {dtype}" for col, dtype in df.dtypes.items()]
    return textwrap.dedent(f"""
        You are an expert agricultural supply chain data analyst.
        The pandas DataFrame `df` is already loaded with {df.shape[0]:,} rows and {df.shape[1]} columns.

        IMPORTANT Column Mappings:
        - Crop name: `crop_name` (Do NOT use `crop`)
        - Price: `modal_price` (wholesale market price in ₹/quintal)
        - Minimum Support Price: `msp`
        - Arrival volume: `arrival_quantity_qtl`
        - Geography: `district`, `mandi_name`, `mandi_type`
        - Date: `date` (already datetime)
        - Weather: `avg_temperature_c`, `total_rainfall_mm`, `avg_humidity_percent`
        - Transport: `avg_distance_km`, `avg_transit_hours`, `transit_delay_rate`

        Available columns:
{chr(10).join(col_info)}

        The user previously asked: "{previous_query}"

        Here is the Python code that generated the current chart:
        --- EXISTING CODE START ---
        {previous_code}
        --- EXISTING CODE END ---

        The user now wants to MODIFY or FOLLOW UP on this chart:
        "{followup_prompt}"

        Instructions:
        - Apply the requested changes to the EXISTING code above.
        - Output ONLY valid, executable Python code (the complete modified script).
        - NEVER include markdown fences (no ```python or ```). No explanations.
        - You have access to: `df`, `pd`, `px`, `go`.
        - Assign the final figure to the variable `fig`.
        - Use template="plotly_dark".
        - Do NOT call `fig.show()`.
    """).strip()


def _generate_insight_prompt(df, previous_code: str, previous_query: str, insight_prompt: str):
    # Compute quick dataset stats for context
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    stats_lines = []
    for c in numeric_cols[:8]:
        s = df[c].dropna()
        if len(s) > 0:
            stats_lines.append(f"  - {c}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}, std={s.std():.2f}")

    extra_question = f'\nThe user has a specific question about this visual: "{insight_prompt}"' if insight_prompt else ""

    return textwrap.dedent(f"""
        You are a senior agricultural economist and supply chain analyst specialising in Indian mandi markets.
        The pandas DataFrame `df` was used to create the chart below, with {df.shape[0]:,} rows.

        Dataset numeric summary:
{chr(10).join(stats_lines)}

        The chart was generated by the user query: "{previous_query}"

        The Python code that generated it:
        --- CODE START ---
        {previous_code}
        --- CODE END ---
        {extra_question}

        Your task: Provide a structured, insightful analysis of the visual in MARKDOWN format.
        Use this exact structure:

        ## 📊 Chart Summary
        Brief 1-2 sentence description of what the chart shows.

        ## 📈 Key Trends
        - 3-4 bullet points describing the most important patterns or trends.

        ## ⚠️ Anomalies & Notable Observations
        - Flag any price spikes, unusual drops, MSP-price gaps, or irregular patterns.

        ## 🚜 Supply Chain & Farmer Impact
        - 2-3 actionable interpretations for market participants (farmers, mandis, traders).

        ## 💡 Recommendations
        - 1-3 data-driven recommendations or next steps for deeper analysis.

        Rules:
        - Be concise and specific. Do not pad with generic statements.
        - Reference actual crop names, mandi names, or districts from the code context where relevant.
        - Do NOT generate any Python code.
        - Output ONLY the markdown insights, nothing else.
    """).strip()


def _sanitize_code(raw_text):
    code = re.sub(r"^```(?:python)?\s*", "", raw_text, flags=re.MULTILINE)
    code = re.sub(r"```\s*$", "", code, flags=re.MULTILINE)
    return code.strip()


def _apply_dark_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5edd6",
        font_family="Inter, sans-serif",
        margin=dict(l=35, r=35, t=50, b=35),
    )
    return fig


# ── AI Agent Logic & History ──────────────────────────────────
@app.callback(
    [Output("chat-store", "data"),
     Output("ai-query-input", "value"),
     Output("quick-action-store", "data")],
    [Input("ai-run-btn", "n_clicks"),
     Input("ai-query-input", "n_submit"),
     Input("ai-clear-btn", "n_clicks"),
     Input("quick-action-store", "data")],
    [State("ai-query-input", "value"),
     State("chat-store", "data")],
    prevent_initial_call=True,
)
def manage_chat(run_click, enter_submit, clear_click, quick_action, query_text, history):
    ctx = callback_context
    if not ctx.triggered:
        return history, query_text, None

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Clear button
    if trigger_id == "ai-clear-btn":
        return [], "", None

    history = history or []

    # Determine the actual query text: from quick-action store or text input
    if trigger_id == "quick-action-store" and quick_action:
        clean_query = quick_action.get("text", "").strip()
        command_override = quick_action.get("command", None)
        payload_override = quick_action.get("payload", "")
    else:
        if not query_text or not query_text.strip():
            return history, "", None
        clean_query = query_text.strip()
        command_override = None
        payload_override = None

    if not clean_query:
        return history, "", None

    # Parse command
    if command_override:
        command = command_override
        payload = payload_override
    else:
        command, payload = parse_command(clean_query)

    # Append user message bubble
    history.append({"role": "user", "text": clean_query})

    if not GROQ_API_KEY:
        history.append({
            "role": "error",
            "title": "API Key Missing",
            "text": "GROQ_API_KEY is not configured in your .env file. Add your Groq key to get started.",
        })
        return history, "", None

    df = get_data()
    generated_code = ""

    try:
        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        model_name = resolve_model(client)

        # ── INSIGHT command ────────────────────────────────────
        if command == "insight":
            last_visual = _get_last_visual(history[:-1])  # exclude user bubble just added
            if last_visual is None:
                history.append({
                    "role": "error",
                    "title": "No Visual Found",
                    "text": "There's no chart to analyze yet. Generate a visual first, then ask for insights.",
                })
                return history, "", None

            prev_code = last_visual.get("code", "")
            prev_query = last_visual.get("query", "")
            system_msg = _generate_insight_prompt(df, prev_code, prev_query, payload)

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": system_msg}],
                temperature=0.3,
                max_tokens=1800,
            )
            insight_markdown = response.choices[0].message.content.strip()
            history.append({
                "role": "insight",
                "markdown": insight_markdown,
                "model": model_name,
                "query": clean_query,
            })

        # ── FOLLOWUP / EDIT command ────────────────────────────
        elif command == "followup":
            last_visual = _get_last_visual(history[:-1])
            if last_visual is None:
                history.append({
                    "role": "error",
                    "title": "No Visual to Follow Up On",
                    "text": "There's no previous chart to modify. Generate a visual first, then use /followup.",
                })
                return history, "", None

            prev_code = last_visual.get("code", "")
            prev_query = last_visual.get("query", "")
            system_msg = _generate_followup_prompt(df, prev_code, prev_query, payload)

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": system_msg}],
                temperature=0.1,
                max_tokens=1400,
            )
            raw_output = response.choices[0].message.content.strip()
            generated_code = _sanitize_code(raw_output)

            execution_scope = {"df": df.copy(), "pd": pd, "px": px, "go": go}
            exec(generated_code, execution_scope)  # noqa: S102
            fig = execution_scope.get("fig")

            if fig is None:
                history.append({
                    "role": "error",
                    "title": "No Chart Object Produced",
                    "text": "The agent modified the code but didn't assign a figure to `fig`. Try rephrasing.",
                    "code": generated_code,
                })
                return history, "", None

            fig = _apply_dark_theme(fig)
            history.append({
                "role": "assistant",
                "fig_dict": fig.to_dict(),
                "code": generated_code,
                "query": payload,
                "model": model_name,
                "is_followup": True,
            })

        # ── NEW chart command (default) ────────────────────────
        else:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": _generate_system_prompt(df)},
                    {"role": "user", "content": payload},
                ],
                temperature=0.1,
                max_tokens=1200,
            )
            raw_output = response.choices[0].message.content.strip()
            generated_code = _sanitize_code(raw_output)

            execution_scope = {"df": df.copy(), "pd": pd, "px": px, "go": go}
            exec(generated_code, execution_scope)  # noqa: S102
            fig = execution_scope.get("fig")

            if fig is None:
                history.append({
                    "role": "error",
                    "title": "No Chart Object Produced",
                    "text": "The agent generated code but didn't assign a figure to `fig`. Try rephrasing your question.",
                    "code": generated_code,
                })
                return history, "", None

            fig = _apply_dark_theme(fig)
            history.append({
                "role": "assistant",
                "fig_dict": fig.to_dict(),
                "code": generated_code,
                "query": payload,
                "model": model_name,
                "is_followup": False,
            })

    except Exception as exc:
        history.append({
            "role": "error",
            "title": "Execution Error",
            "text": str(exc),
            "traceback": traceback.format_exc(),
            "code": generated_code,
        })

    return history, "", None


# ── Quick Action Buttons (insight & followup from card buttons) ──
@app.callback(
    Output("quick-action-store", "data", allow_duplicate=True),
    Input({"type": "card-insight-btn", "index": ALL}, "n_clicks"),
    State("chat-store", "data"),
    prevent_initial_call=True,
)
def trigger_insight_from_button(n_clicks_list, history):
    ctx = callback_context
    if not ctx.triggered or not any(n for n in n_clicks_list if n):
        return None
    # Find which button was clicked — get its index (visual index in history)
    triggered_prop = ctx.triggered[0]["prop_id"]
    idx_match = re.search(r'"index":(\d+)', triggered_prop)
    if not idx_match:
        return None
    visual_idx = int(idx_match.group(1))
    # Find the visual at that position among assistant messages
    assistant_msgs = [m for m in (history or []) if m.get("role") == "assistant"]
    if visual_idx >= len(assistant_msgs):
        return None
    target = assistant_msgs[visual_idx]
    return {
        "command": "insight",
        "payload": "",
        "text": "/insight",
        "target_code": target.get("code", ""),
        "target_query": target.get("query", ""),
    }


@app.callback(
    [Output("quick-action-store", "data", allow_duplicate=True),
     Output("ai-query-input", "value", allow_duplicate=True)],
    Input({"type": "card-followup-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def trigger_followup_from_button(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered or not any(n for n in n_clicks_list if n):
        return None, dash.no_update
    # Pre-fill the input with /followup
    return None, "/followup "


# ── Render Chat Stream ─────────────────────────────────────────
@app.callback(
    Output("chat-history-display", "children"),
    Input("chat-store", "data"),
)
def render_chat_stream(history):
    if not history:
        return html.Div([
            html.Div("✨", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
            html.H4("Ask MandiFlow AI", style={"color": "var(--cream)", "marginBottom": "0.4rem"}),
            html.P(
                "Inquire about modal prices, arrival volumes, weather impacts, or transit delays across mandis.",
                style={"color": "var(--text-muted)", "fontSize": "0.88rem", "maxWidth": "520px", "margin": "0 auto"},
            ),
            html.Div([
                html.Span("Commands:", className="command-hint-label"),
                html.Span("/new <query>", className="command-pill"),
                html.Span("/followup <changes>", className="command-pill command-pill--followup"),
                html.Span("/insight [question]", className="command-pill command-pill--insight"),
            ], className="command-hint-bar"),
        ], style={
            "textAlign": "center",
            "padding": "4rem 2rem",
            "background": "var(--card-bg)",
            "border": "1px dashed var(--border-color)",
            "borderRadius": "var(--radius-lg)",
        })

    elements = []
    visual_index = 0  # tracks index among assistant-visual messages for button IDs

    for msg in history:
        role = msg.get("role")

        # ── User bubble ─────────────────────────────────────
        if role == "user":
            elements.append(
                html.Div([
                    html.Div([
                        html.Div("You", className="chat-user-meta"),
                        html.Div(msg["text"]),
                    ], className="chat-user-bubble"),
                ], className="chat-user-row")
            )

        # ── Assistant visual card ───────────────────────────
        elif role == "assistant":
            fig_dict = msg.get("fig_dict")
            code_text = msg.get("code", "")
            model_used = msg.get("model", "AI Agent")
            is_followup = msg.get("is_followup", False)
            current_idx = visual_index
            visual_index += 1

            header_label = "✏️ Modified Visual" if is_followup else "🌾 MandiFlow Agent Analysis"

            elements.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span([
                                html.Span(header_label),
                            ], className="chat-ai-title"),
                            html.Span(model_used.split("/")[-1], className="chat-ai-badge"),
                        ], className="chat-ai-card-header"),

                        html.Div(
                            dcc.Graph(
                                figure=fig_dict,
                                config={"responsive": True, "displayModeBar": "hover"},
                            ),
                            className="chat-graph-container",
                        ),

                        # ── Action Buttons ──
                        html.Div([
                            html.Button([
                                html.Span("💡", className="action-btn-icon"),
                                "Get Market Insights",
                            ], id={"type": "card-insight-btn", "index": current_idx},
                                n_clicks=0, className="action-btn action-btn--insight"),
                            html.Button([
                                html.Span("✏️", className="action-btn-icon"),
                                "Follow-up / Edit",
                            ], id={"type": "card-followup-btn", "index": current_idx},
                                n_clicks=0, className="action-btn action-btn--followup"),
                        ], className="chat-action-bar"),

                        html.Details([
                            html.Summary("View Generated Python Code"),
                            html.Pre(code_text, className="code-box"),
                        ], className="code-accordion") if code_text else None,
                    ], className="chat-ai-card"),
                ], className="chat-ai-row")
            )

        # ── Insight card ────────────────────────────────────
        elif role == "insight":
            markdown_text = msg.get("markdown", "")
            model_used = msg.get("model", "AI Agent")
            # Convert markdown to structured Dash elements
            elements.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("💡 AI Market Insights", className="chat-ai-title"),
                            html.Span(model_used.split("/")[-1], className="chat-ai-badge"),
                        ], className="chat-ai-card-header"),
                        html.Div(
                            _render_markdown_insight(markdown_text),
                            className="insight-body",
                        ),
                    ], className="chat-insight-card"),
                ], className="chat-ai-row")
            )

        # ── Error card ──────────────────────────────────────
        elif role == "error":
            elements.append(
                html.Div([
                    html.Div([
                        html.Strong(msg.get("title", "Error")),
                        html.P(msg.get("text", "")),
                        html.Details([
                            html.Summary("View Error Details & Code"),
                            html.Pre(msg.get("traceback", msg.get("code", "")), className="code-box"),
                        ], className="code-accordion") if (msg.get("code") or msg.get("traceback")) else None,
                    ], className="callout-error"),
                ], className="chat-ai-row")
            )

    return elements


def _render_markdown_insight(text: str):
    """Convert markdown insight text into structured Dash HTML elements."""
    elements = []
    lines = text.split("\n")
    current_section = []

    def flush_section(items):
        if items:
            elements.append(html.Div(items, className="insight-section"))

    i = 0
    while i < len(lines):
        line = lines[i]

        # H2 headings (## )
        if line.startswith("## "):
            flush_section(current_section)
            current_section = [html.H5(line[3:].strip(), className="insight-heading")]
            i += 1
            continue

        # H3 headings (### )
        if line.startswith("### "):
            flush_section(current_section)
            current_section = [html.H6(line[4:].strip(), className="insight-subheading")]
            i += 1
            continue

        # Bullet points
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            bullet_text = line.strip()[2:]
            # Handle **bold** in bullets
            bullet_content = _parse_inline(bullet_text)
            current_section.append(
                html.Div([
                    html.Span("›", className="insight-bullet-dot"),
                    html.Span(bullet_content, className="insight-bullet-text"),
                ], className="insight-bullet")
            )
            i += 1
            continue

        # Non-empty non-special lines → paragraph
        if line.strip():
            current_section.append(
                html.P(_parse_inline(line.strip()), className="insight-para")
            )

        i += 1

    flush_section(current_section)
    return elements


def _parse_inline(text: str):
    """Parse **bold** markdown and return a list of Dash children."""
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    children = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            children.append(html.Strong(part[2:-2]))
        elif part:
            children.append(part)
    return children if len(children) > 1 else text



# ── Command Pill Click → Pre-fill Input ───────────────────────
@app.callback(
    Output("ai-query-input", "value", allow_duplicate=True),
    [Input("pill-new", "n_clicks"),
     Input("pill-followup", "n_clicks"),
     Input("pill-insight", "n_clicks")],
    prevent_initial_call=True,
)
def pill_prefill(new_clicks, followup_clicks, insight_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    mapping = {
        "pill-new": "/new ",
        "pill-followup": "/followup ",
        "pill-insight": "/insight ",
    }
    return mapping.get(trigger_id, dash.no_update)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)

