from dash import html, dcc


def layout():
    return html.Div([
        html.Div([
            html.H2("✨ AI Agent Analytics Dashboard", className="page-title"),
            html.P(
                "Ask questions in natural language. The agent synthesizes and renders custom Plotly visualizations.",
                className="page-desc"
            )
        ], className="page-header"),

        # Query Input Card
        html.Div([
            html.Div([
                html.Div([
                    dcc.Input(
                        id="ai-query-input",
                        type="text",
                        placeholder="e.g. Compare modal price across top 10 districts for Wheat as a bar chart",
                        className="mandi-input"
                    )
                ], style={"flex": "5"}),
                html.Div([
                    html.Button("Generate Visualization", id="ai-run-btn", n_clicks=0, className="mandi-btn", style={"width": "100%"})
                ], style={"flex": "1.5"}),
            ], style={"display": "flex", "gap": "1rem", "alignItems": "center"}),
        ], className="mandi-card"),

        # Dynamic Results Section
        dcc.Loading(
            id="ai-loading",
            type="dot",
            color="#689f38",
            children=[
                html.Div(id="ai-output-container")
            ]
        )
    ])
