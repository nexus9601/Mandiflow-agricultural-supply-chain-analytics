from dash import html, dcc
from utils.data_store import get_data


def layout():
    df = get_data()

    crop_options = [
        {"label": str(c), "value": str(c)} for c in sorted(df["crop_name"].dropna().unique())
    ]
    mandi_types = [
        {"label": str(t), "value": str(t)} for t in sorted(df["mandi_type"].dropna().unique())
    ]

    return html.Div([
        html.Div([
            html.H2("📊 Manual Analytics Dashboard", className="page-title"),
            html.P("Modular workspace with parameter toggles and control hub for manual supply chain analytics.", className="page-desc")
        ], className="page-header"),

        # Controls & Toggle Hub
        html.Div([
            html.H4("🎛️ Control Panel & Filter Hub", style={"fontSize": "0.95rem", "color": "var(--text-primary)", "marginTop": "0"}),
            html.Div([
                html.Div([
                    html.Label("Select Crop(s)", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "4px"}),
                    dcc.Dropdown(
                        id="manual-crop-select",
                        options=crop_options,
                        value=[crop_options[0]["value"]] if crop_options else None,
                        multi=True
                    )
                ], style={"flex": "1"}),
                html.Div([
                    html.Label("Mandi Types", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "4px"}),
                    dcc.Dropdown(
                        id="manual-mandi-types",
                        options=mandi_types,
                        value=[m["value"] for m in mandi_types],
                        multi=True
                    )
                ], style={"flex": "1"}),
                html.Div([
                    html.Label("Primary Metric", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "4px"}),
                    dcc.Dropdown(
                        id="manual-metric-select",
                        options=[
                            {"label": "Modal Price (₹)", "value": "modal_price"},
                            {"label": "Arrival Quantity (Qtl)", "value": "arrival_quantity_qtl"},
                            {"label": "Transit Delay Rate", "value": "transit_delay_rate"},
                            {"label": "Average Distance (km)", "value": "avg_distance_km"},
                        ],
                        value="modal_price",
                        clearable=False
                    )
                ], style={"flex": "1"}),
            ], style={"display": "flex", "gap": "1rem", "marginBottom": "1.2rem"}),

            # Toggle Buttons Row
            html.Div([
                html.Label("Analysis Flags & Toggles:", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginRight": "1.5rem"}),
                dcc.Checklist(
                    id="manual-toggles",
                    options=[
                        {"label": "  Apply Log Scale", "value": "LOG"},
                        {"label": "  Show Moving Average", "value": "MA"},
                        {"label": "  Filter Outliers", "value": "OUTLIER"},
                        {"label": "  Overlay MSP Benchmark", "value": "MSP"},
                    ],
                    value=["MA", "MSP"],
                    inline=True,
                    style={"color": "var(--text-primary)", "fontSize": "0.88rem", "display": "flex", "gap": "1.5rem"}
                )
            ], style={"display": "flex", "alignItems": "center", "padding": "0.5rem 0"})
        ], className="mandi-card"),

        # Reserved Integration Slot / Door
        html.Div([
            html.Div([
                html.Div("📈", style={"fontSize": "2.2rem", "marginBottom": "0.5rem"}),
                html.H3("Manual Dashboard Workspace", style={"color": "var(--text-primary)", "margin": "0 0 0.5rem 0", "fontSize": "1.15rem"}),
                html.P(
                    "This section is isolated and reserved for custom manual dashboard components, KPIs, and graphs designed by your team.",
                    style={"color": "var(--text-muted)", "fontSize": "0.85rem", "maxWidth": "520px", "margin": "0 auto 1.2rem"}
                ),
                html.Div(
                    "Door open: Plug in your custom Plotly charts & layout callbacks here",
                    style={
                        "backgroundColor": "rgba(104, 159, 56, 0.12)",
                        "border": "1px solid var(--green-accent)",
                        "padding": "0.45rem 1.2rem",
                        "borderRadius": "6px",
                        "fontSize": "0.82rem",
                        "color": "var(--text-primary)"
                    }
                )
            ], style={
                "minHeight": "380px",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "center",
                "textAlign": "center",
                "border": "1px dashed #3a4d22",
                "borderRadius": "var(--radius)",
                "padding": "2rem"
            })
        ], className="mandi-card")
    ])
