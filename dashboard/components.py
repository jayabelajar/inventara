from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def kpi_card(title: str, value_id: str, accent: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(title, className="kpi-title"),
                html.Div(id=value_id, className="kpi-value"),
            ]
        ),
        className=f"kpi-card kpi-{accent}",
    )


def chart_card(title: str, graph_id: str, class_name: str = "") -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardHeader(title),
            dbc.CardBody(dcc.Graph(id=graph_id, config={"displayModeBar": False})),
        ],
        className=f"chart-card {class_name}".strip(),
    )


def sidebar() -> html.Aside:
    return html.Aside(
        [
            html.Div("SpareFlow", className="brand"),
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
