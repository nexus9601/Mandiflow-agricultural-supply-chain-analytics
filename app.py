import os
import re
import textwrap
import traceback

import dash
from dash import html, dcc, Input, Output, State
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

from utils.data_store import get_data
from dash_pages import dataset_view, manual_dashboard_view, ai_dashboard_view

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Dash app init ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title="MandiFlow · Agricultural Analytics",
    suppress_callback_exceptions=True,
)
server = app.server


# ── Navbar ────────────────────────────────────────────────────
def navbar(pathname):
    links = [
        ("/dataset",          "📋 Dataset"),
        ("/manual-dashboard", "📊 Manual Dashboard"),
        ("/ai-dashboard",     "✨ AI Analytics"),
    ]
    nav_items = []
    for href, label in links:
        is_active = pathname in (["/", href] if href == "/dataset" else [href])
        nav_items.append(
            dcc.Link(label, href=href,
                     className="nav-tab-link active" if is_active else "nav-tab-link")
        )
    return html.Header([
        html.A([
            html.Span("🌾"),
            html.Span("MandiFlow"),
            html.Span("Agricultural Analytics", className="subtitle"),
        ], href="/", className="navbar-brand"),
        html.Nav(nav_items, className="nav-menu"),
    ], className="mandi-navbar")


# ── Root layout ───────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="navbar-container"),
    html.Main(id="page-content", className="main-container"),
])


# ── Router ────────────────────────────────────────────────────
@app.callback(
    [Output("navbar-container", "children"),
     Output("page-content", "children")],
    Input("url", "pathname"),
)
def route(pathname):
    routes = {
        "/":                  dataset_view.layout,
        "/dataset":           dataset_view.layout,
        "/manual-dashboard":  manual_dashboard_view.layout,
        "/ai-dashboard":      ai_dashboard_view.layout,
    }
    page_fn = routes.get(pathname, dataset_view.layout)
    return navbar(pathname), page_fn()


# ── Dataset filter callback ───────────────────────────────────
@app.callback(
    Output("dataset-table", "data"),
    [Input("dataset-crop-filter", "value"),
     Input("dataset-district-filter", "value"),
     Input("dataset-type-filter", "value")],
)
def filter_table(crop, district, mtype):
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
        "arrival_quantity_qtl", "modal_price", "msp"
    ] if c in df.columns]
    return df[cols].head(100).to_dict("records")


# ── AI agent callback ─────────────────────────────────────────
def _system_prompt(df):
    lines = [f"  - {c}: {d}" for c, d in df.dtypes.items()]
    return textwrap.dedent(f"""
        You are an agricultural supply chain analyst.
        DataFrame `df` is already loaded ({df.shape[0]:,} rows, {df.shape[1]} cols).

        Columns:
{chr(10).join(lines)}

        Rules — return ONLY executable Python code, no prose, no fences:
        - Use `df`, `pd`, `px`, `go` (all in scope).
        - Assign the final figure to `fig`. Use template="plotly_dark".
        - Do NOT call fig.show().
    """).strip()


@app.callback(
    Output("ai-output-container", "children"),
    Input("ai-run-btn", "n_clicks"),
    State("ai-query-input", "value"),
    prevent_initial_call=True,
)
def run_agent(n_clicks, query):
    if not query or not query.strip():
        return html.Div("Please enter a question above.", className="callout-error")
    if not GROQ_API_KEY:
        return html.Div("GROQ_API_KEY not found in .env file.", className="callout-error")

    df = get_data()
    clean_code = ""
    try:
        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        raw = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": _system_prompt(df)},
                {"role": "user",   "content": query.strip()},
            ],
            temperature=0.1,
            max_tokens=1024,
        ).choices[0].message.content.strip()

        clean_code = re.sub(r"^```(?:python)?\s*", "", raw, flags=re.MULTILINE)
        clean_code = re.sub(r"```\s*$", "", clean_code, flags=re.MULTILINE).strip()

        ns = {"df": df.copy(), "pd": pd, "px": px, "go": go}
        exec(clean_code, ns)  # noqa: S102
        fig = ns.get("fig")

        if fig is None:
            return _no_fig_error(clean_code)

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0)",
            font_color   ="#dde8c8",
            font_family  ="Inter, sans-serif",
            margin       =dict(l=30, r=30, t=50, b=30),
        )
        return html.Div([
            html.Div(dcc.Graph(figure=fig, config={"responsive": True}), className="mandi-card"),
            _code_expander("View Generated Code", clean_code),
        ])

    except Exception:
        return html.Div([
            html.Div([html.Strong("Execution Error"), html.Pre(traceback.format_exc(), style={"fontSize": "0.8rem"})],
                     className="callout-error"),
            _code_expander("View Generated Code (failed)", clean_code or ""),
        ])


def _no_fig_error(code):
    return html.Div([
        html.Div("No `fig` object was generated. Try rephrasing your query.", className="callout-error"),
        _code_expander("View Generated Code", code),
    ])


def _code_expander(title, code):
    return html.Details([
        html.Summary(title, style={"cursor": "pointer", "color": "var(--text-muted)", "fontSize": "0.85rem", "marginTop": "0.5rem"}),
        html.Pre(code, className="code-container"),
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
