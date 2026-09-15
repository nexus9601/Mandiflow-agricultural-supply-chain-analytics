from dash import html, dcc, dash_table
from utils.data_store import get_data


def layout():
    df = get_data()

    crop_options = [{"label": "All Crops", "value": "ALL"}] + [
        {"label": str(c), "value": str(c)} for c in sorted(df["crop_name"].dropna().unique())
    ]
    district_options = [{"label": "All Districts", "value": "ALL"}] + [
        {"label": str(d), "value": str(d)} for d in sorted(df["district"].dropna().unique())
    ]
    type_options = [{"label": "All Types", "value": "ALL"}] + [
        {"label": str(t), "value": str(t)} for t in sorted(df["mandi_type"].dropna().unique())
    ]

    # Core table columns for clean preview
    preview_cols = [
        "arrival_id", "date", "crop_name", "variety", "mandi_name",
        "district", "mandi_type", "arrival_quantity_qtl", "modal_price", "msp"
    ]
    display_cols = [c for c in preview_cols if c in df.columns]

    return html.Div([
        html.Div([
            html.H2("📋 Mandi Dataset Explorer", className="page-title"),
            html.P("Structured view of unified agricultural arrivals, pricing, and spatial data.", className="page-desc")
        ], className="page-header"),

        # Top summary metrics
        html.Div([
            html.Div([
                html.Div(f"{len(df):,}", className="metric-value"),
                html.Div("Total Records", className="metric-label")
            ], className="metric-card"),
            html.Div([
                html.Div(str(df["crop_name"].nunique()), className="metric-value"),
                html.Div("Unique Crops", className="metric-label")
            ], className="metric-card"),
            html.Div([
                html.Div(str(df["mandi_id"].nunique()), className="metric-value"),
                html.Div("Active Mandis", className="metric-label")
            ], className="metric-card"),
            html.Div([
                html.Div(str(df["district"].nunique()), className="metric-value"),
                html.Div("Districts", className="metric-label")
            ], className="metric-card"),
            html.Div([
                html.Div(f"₹{df['modal_price'].median():,.0f}", className="metric-value"),
                html.Div("Median Price", className="metric-label")
            ], className="metric-card"),
        ], className="metrics-grid"),

        # Filters
        html.Div([
            html.Div([
                html.Label("Filter Crop", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "4px"}),
                dcc.Dropdown(id="dataset-crop-filter", options=crop_options, value="ALL", clearable=False)
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Filter District", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "4px"}),
                dcc.Dropdown(id="dataset-district-filter", options=district_options, value="ALL", clearable=False)
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Filter Mandi Type", style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "4px"}),
                dcc.Dropdown(id="dataset-type-filter", options=type_options, value="ALL", clearable=False)
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "1rem", "marginBottom": "1.2rem"}),

        # Table container
        html.Div([
            dash_table.DataTable(
                id="dataset-table",
                columns=[{"name": col.replace("_", " ").title(), "id": col} for col in display_cols],
                data=df[display_cols].head(100).to_dict("records"),
                page_size=15,
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#151d0e",
                    "color": "#788c60",
                    "fontWeight": "600",
                    "border": "1px solid #2a381c",
                    "fontSize": "0.8rem"
                },
                style_cell={
                    "backgroundColor": "#1b2413",
                    "color": "#dde8c8",
                    "border": "1px solid #2a381c",
                    "fontSize": "0.85rem",
                    "padding": "8px 12px",
                    "textAlign": "left"
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#172010"
                    }
                ]
            )
        ], className="mandi-card")
    ])
