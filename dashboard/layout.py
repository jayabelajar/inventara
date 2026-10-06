from __future__ import annotations

import pandas as pd
from dash import dcc, html

from dashboard.components import chart_card, kpi_card, sidebar


def create_layout(df: pd.DataFrame) -> html.Div:
    min_date = df["date"].min()
    max_date = df["date"].max()
    part_options = [{"label": part, "value": part} for part in sorted(df["part_id"].unique())]
    location_options = [{"label": loc, "value": loc} for loc in sorted(df["location"].unique())]
    record_count = f"{len(df):,}"
    part_count = f"{df['part_id'].nunique():,}"

    return html.Div(
        [
            dcc.Store(id="active-page", data="overview"),
            sidebar(),
            html.Main(
                [
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.H1("Dashboard"),
                                    html.P("Operational command view for demand, stock health, stockout risk, and reorder planning."),
                                    html.Div(
                                        [
                                            html.Span(f"{record_count} records", className="summary-chip"),
                                            html.Span(f"{part_count} spare parts", className="summary-chip"),
                                        ],
                                        className="summary-row",
                                    ),
                                ],
                                className="page-heading",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label("Period", className="filter-label"),
                                            dcc.DatePickerRange(
                                                id="date-filter",
                                                min_date_allowed=min_date,
                                                max_date_allowed=max_date,
                                                start_date=min_date,
                                                end_date=max_date,
                                                display_format="MMM YYYY",
                                            ),
                                        ],
                                        className="filter-group",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Location", className="filter-label"),
                                            dcc.Dropdown(
                                                id="location-filter",
                                                options=location_options,
                                                multi=True,
                                                placeholder="All locations",
                                                className="filter",
                                            ),
                                        ],
                                        className="filter-group",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Spare Part", className="filter-label"),
                                            dcc.Dropdown(
                                                id="part-filter",
                                                options=part_options,
                                                multi=True,
                                                placeholder="All spare parts",
                                                className="filter",
                                            ),
                                        ],
                                        className="filter-group",
                                    ),
                                ],
                                className="filters",
                            ),
                        ],
                        className="topbar",
                    ),
                    html.Section(
                        [
                            kpi_card("Total Spare Parts", "kpi-total-parts", "blue"),
                            kpi_card("Total Inventory", "kpi-total-inventory", "green"),
                            kpi_card("Average Demand", "kpi-average-demand", "amber"),
                            kpi_card("Stockout Rate", "kpi-stockout-rate", "red"),
                            kpi_card("Critical Parts", "kpi-critical-parts", "violet"),
                        ],
                        className="kpi-grid",
                    ),
                    html.Section(id="page-content", className="content-grid"),
                ],
                className="main",
            ),
        ],
        className="app-shell",
    )


def overview_page() -> list:
    return [
        chart_card("Inventory Trend", "inventory-trend"),
        chart_card("Demand Trend", "demand-trend"),
        chart_card("Inventory by Location", "inventory-location"),
        chart_card("Top Demand Parts", "top-demand-parts"),
    ]


def demand_page() -> list:
    return [
        chart_card("Monthly Demand Trend", "monthly-demand"),
        chart_card("Demand by Spare Part", "demand-by-part"),
        chart_card("Demand by Location", "demand-by-location"),
        chart_card("Demand Distribution", "demand-distribution"),
    ]


def stockout_page() -> list:
    return [
        chart_card("Stockout Trend", "stockout-trend"),
        chart_card("Stockout by Location", "stockout-location"),
        chart_card("Highest Stockout Frequency", "stockout-parts"),
        chart_card("Demand vs Inventory", "demand-inventory"),
        html.Div(id="risk-table", className="table-wrap wide"),
    ]


def reorder_page() -> list:
    return [
        chart_card("Current Stock vs ROP", "stock-vs-rop", "wide"),
        chart_card("Safety Stock vs Inventory", "safety-vs-inventory"),
        chart_card("Reorder Status Distribution", "status-distribution"),
        html.Div(id="reorder-table", className="table-wrap wide"),
    ]
