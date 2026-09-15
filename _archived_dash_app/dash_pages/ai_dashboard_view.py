from dash import html, dcc


def layout():
    return html.Div([
        html.Div([
            html.H2("✨ AI Analytics", className="page-title"),
            html.P(
                "Query arrivals, modal prices, MSP, weather, and transport data using natural language.",
                className="page-desc",
            ),
        ], className="page-header"),

        html.Div([
            # Command helper pills bar
            html.Div([
                html.Span("Commands:", className="command-hint-label"),
                html.Button("/new <query>", className="command-pill",
                            id="pill-new", n_clicks=0),
                html.Button("/followup <changes>", className="command-pill command-pill--followup",
                            id="pill-followup", n_clicks=0),
                html.Button("/insight [question]", className="command-pill command-pill--insight",
                            id="pill-insight", n_clicks=0),
            ], className="command-hint-bar"),

            # Sleek Chat Input Card
            html.Div([
                html.Span("💬", className="chat-input-icon"),
                dcc.Input(
                    id="ai-query-input",
                    type="text",
                    placeholder="Ask a question, or use /new  /followup  /insight  commands...",
                    debounce=False,
                    className="chat-query-input",
                    n_submit=0,
                ),
                html.Div([
                    html.Button("Send ↵", id="ai-run-btn", n_clicks=0, className="chat-send-btn"),
                    html.Button("Clear", id="ai-clear-btn", n_clicks=0, className="chat-reset-btn"),
                ], className="chat-actions"),
            ], className="chat-input-card"),

            # Chat History Feed with loading indicator
            dcc.Loading(
                id="ai-loading",
                type="circle",
                color="#8bc34a",
                children=html.Div(id="chat-history-display", className="chat-history-feed"),
            ),
        ], className="ai-chat-wrapper"),
    ])
