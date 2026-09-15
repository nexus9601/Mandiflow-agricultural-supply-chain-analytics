import os
import re
import textwrap
import traceback

import dash
from dash import html, dcc, Input, Output, State, callback_context
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


# ── AI Agent Logic & History ──────────────────────────────────
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


def _sanitize_code(raw_text):
    code = re.sub(r"^```(?:python)?\s*", "", raw_text, flags=re.MULTILINE)
    code = re.sub(r"```\s*$", "", code, flags=re.MULTILINE)
    return code.strip()


@app.callback(
    [Output("chat-store", "data"),
     Output("ai-query-input", "value")],
    [Input("ai-run-btn", "n_clicks"),
     Input("ai-query-input", "n_submit"),
     Input("ai-clear-btn", "n_clicks")],
    [State("ai-query-input", "value"),
     State("chat-store", "data")],
    prevent_initial_call=True,
)
def manage_chat(run_click, enter_submit, clear_click, query_text, history):
    ctx = callback_context
    if not ctx.triggered:
        return history, query_text

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Clear button
    if trigger_id == "ai-clear-btn":
        return [], ""

    # Empty query check
    if not query_text or not query_text.strip():
        return history or [], ""

    clean_query = query_text.strip()
    history = history or []
    history.append({"role": "user", "text": clean_query})

    if not GROQ_API_KEY:
        history.append({
            "role": "error",
            "title": "API Key Missing",
            "text": "GROQ_API_KEY is not configured in your .env file. Add your Groq key to get started.",
        })
        return history, ""

    df = get_data()
    generated_code = ""
    try:
        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        model_name = resolve_model(client)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": _generate_system_prompt(df)},
                {"role": "user", "content": clean_query},
            ],
            temperature=0.1,
            max_tokens=1200,
        )
        raw_output = response.choices[0].message.content.strip()
        generated_code = _sanitize_code(raw_output)

        execution_scope = {
            "df": df.copy(),
            "pd": pd,
            "px": px,
            "go": go,
        }
        exec(generated_code, execution_scope)  # noqa: S102
        fig = execution_scope.get("fig")

        if fig is None:
            history.append({
                "role": "error",
                "title": "No Chart Object Produced",
                "text": "The agent generated code but didn't assign a figure to `fig`. Try rephrasing your question.",
                "code": generated_code,
            })
            return history, ""

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e5edd6",
            font_family="Inter, sans-serif",
            margin=dict(l=35, r=35, t=50, b=35),
        )
        history.append({
            "role": "assistant",
            "fig_dict": fig.to_dict(),
            "code": generated_code,
            "model": model_name,
        })

    except Exception as exc:
        history.append({
            "role": "error",
            "title": "Execution Error",
            "text": str(exc),
            "traceback": traceback.format_exc(),
            "code": generated_code,
        })

    return history, ""


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
        ], style={
            "textAlign": "center",
            "padding": "4rem 2rem",
            "background": "var(--card-bg)",
            "border": "1px dashed var(--border-color)",
            "borderRadius": "var(--radius-lg)",
        })

    elements = []
    for msg in history:
        role = msg.get("role")

        if role == "user":
            elements.append(
                html.Div([
                    html.Div([
                        html.Div("You", className="chat-user-meta"),
                        html.Div(msg["text"]),
                    ], className="chat-user-bubble"),
                ], className="chat-user-row")
            )

        elif role == "assistant":
            fig_dict = msg.get("fig_dict")
            code_text = msg.get("code", "")
            model_used = msg.get("model", "AI Agent")
            elements.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span([
                                html.Span("🌾", style={"marginRight": "6px"}),
                                html.Span("MandiFlow Agent Analysis"),
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

                        html.Details([
                            html.Summary("View Generated Python Code"),
                            html.Pre(code_text, className="code-box"),
                        ], className="code-accordion") if code_text else None,
                    ], className="chat-ai-card"),
                ], className="chat-ai-row")
            )

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
