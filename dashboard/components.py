from __future__ import annotations

from dash import dcc, html


def kpi_card(title: str, value_id: str, accent: str) -> html.Div:
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        html.Div(className=f"kpi-dot dot-{accent}"),
                        html.Div("Live", className="kpi-pill"),
                    ],
                    className="kpi-topline",
                ),
                html.Div(
                    [
                        html.Div(title, className="kpi-title"),
                        html.Div(id=value_id, className="kpi-value"),
                    ],
                    className="kpi-copy",
                ),
            ],
            className="kpi-body",
        ),
        className=f"kpi-card kpi-{accent} rounded-lg bg-white",
    )


def chart_card(title: str, graph_id: str, class_name: str = "") -> html.Div:
    return html.Div(
        [
            html.Div(html.Div(title, className="chart-title"), className="chart-header"),
            html.Div(
                dcc.Graph(
                    id=graph_id,
                    config={"displayModeBar": False, "responsive": True},
                    className="chart-graph",
                    style={"height": "320px", "width": "100%"},
                ),
                className="chart-body",
            ),
        ],
        className=f"chart-card {class_name} rounded-lg bg-white".strip(),
    )


def sidebar() -> html.Aside:
    return html.Aside(
        [
            html.Div(
                [
                    html.Div("IV", className="brand-mark"),
                    html.Div(
                        [
                            html.Div("Inventara", className="brand-name"),
                            html.Div("Aviation Inventory", className="brand-tagline"),
                        ],
                    ),
                ],
                className="brand",
            ),
            html.Nav(
                [
                    html.Button("Overview", id="nav-overview", n_clicks=0, className="nav-link active"),
                    html.Button("Demand Analytics", id="nav-demand", n_clicks=0, className="nav-link"),
                    html.Button("Stockout & Risk", id="nav-stockout", n_clicks=0, className="nav-link"),
                    html.Button("Reorder Analysis", id="nav-reorder", n_clicks=0, className="nav-link"),
                ],
                className="nav-list",
            ),
        ],
        className="sidebar",
    )
