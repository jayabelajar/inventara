from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback_context, dash_table, html

from dashboard.layout import demand_page, overview_page, reorder_page, stockout_page
from src.analysis import apply_filters, build_analysis_context


STATUS_COLORS = {
    "SAFE": "#2f9e44",
    "REORDER": "#f08c00",
    "CRITICAL": "#d6336c",
    "STOCKOUT": "#c92a2a",
}


def _empty_figure(title: str):
    fig = px.scatter(title=title)
    fig.update_layout(template="plotly_white", annotations=[{"text": "No data", "showarrow": False}])
    return fig


def _format_fig(fig):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=28, b=20),
        font=dict(family="Inter, Segoe UI, sans-serif", size=12),
        legend_title_text="",
    )
    return fig


def _context(df, start_date, end_date, locations, parts):
    filtered = apply_filters(df, start_date, end_date, locations, parts)
    if filtered.empty:
        return filtered, None
    return filtered, build_analysis_context(filtered)


def _metric_table(metrics: pd.DataFrame, table_id: str) -> dash_table.DataTable:
    columns = [
        "part_id",
        "location",
        "current_stock",
        "average_demand",
        "average_lead_time",
        "safety_stock",
        "reorder_point",
        "stockout_rate",
        "status",
    ]
    table_data = metrics[columns].copy()
    table_data["average_demand"] = table_data["average_demand"].round(2)
    table_data["average_lead_time"] = table_data["average_lead_time"].round(2)
    table_data["stockout_rate"] = (table_data["stockout_rate"] * 100).round(2)
    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": col.replace("_", " ").title(), "id": col} for col in columns],
        data=table_data.sort_values(["status", "stockout_rate"], ascending=[True, False]).to_dict("records"),
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"fontFamily": "Inter, Segoe UI, sans-serif", "fontSize": 12, "padding": "10px"},
        style_header={"fontWeight": "700", "backgroundColor": "#f1f5f9"},
        style_data_conditional=[
            {
                "if": {"filter_query": f'{{status}} = "{status}"', "column_id": "status"},
                "backgroundColor": color,
                "color": "white",
                "fontWeight": "700",
            }
            for status, color in STATUS_COLORS.items()
        ],
    )


def register_callbacks(app, df: pd.DataFrame) -> None:
    @app.callback(
        Output("active-page", "data"),
        Output("nav-overview", "className"),
        Output("nav-demand", "className"),
        Output("nav-stockout", "className"),
        Output("nav-reorder", "className"),
        Input("nav-overview", "n_clicks"),
        Input("nav-demand", "n_clicks"),
        Input("nav-stockout", "n_clicks"),
        Input("nav-reorder", "n_clicks"),
        prevent_initial_call=True,
    )
    def switch_page(*_):
        triggered = callback_context.triggered_id or "nav-overview"
        page_map = {
            "nav-overview": "overview",
            "nav-demand": "demand",
            "nav-stockout": "stockout",
            "nav-reorder": "reorder",
        }
        page = page_map[triggered]
        classes = {key: "nav-link active" if value == page else "nav-link" for key, value in page_map.items()}
        return page, classes["nav-overview"], classes["nav-demand"], classes["nav-stockout"], classes["nav-reorder"]

    @app.callback(Output("page-content", "children"), Input("active-page", "data"))
    def render_page(page):
        if page == "demand":
            return demand_page()
        if page == "stockout":
            return stockout_page()
        if page == "reorder":
            return reorder_page()
        return overview_page()

    @app.callback(
        Output("kpi-total-parts", "children"),
        Output("kpi-total-inventory", "children"),
        Output("kpi-average-demand", "children"),
        Output("kpi-stockout-rate", "children"),
        Output("kpi-critical-parts", "children"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("location-filter", "value"),
        Input("part-filter", "value"),
    )
    def update_kpis(start_date, end_date, locations, parts):
        filtered, context = _context(df, start_date, end_date, locations, parts)
        if filtered.empty:
            return "0", "0", "0", "0%", "0"
        kpis = context["kpis"]
        return (
            f"{kpis['total_parts']:,}",
            f"{kpis['total_inventory']:,}",
            f"{kpis['average_demand']:,.2f}",
            f"{kpis['stockout_rate']:,.2f}%",
            f"{kpis['critical_parts']:,}",
        )

    @app.callback(
        Output("inventory-trend", "figure"),
        Output("demand-trend", "figure"),
        Output("inventory-location", "figure"),
        Output("top-demand-parts", "figure"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("location-filter", "value"),
        Input("part-filter", "value"),
    )
    def update_overview(start_date, end_date, locations, parts):
        filtered, context = _context(df, start_date, end_date, locations, parts)
        if filtered.empty:
            return [_empty_figure("No data")] * 4
        top_parts = context["by_part"].nlargest(10, "demand")
        return (
            _format_fig(px.line(context["monthly"], x="month", y="inventory", markers=True)),
            _format_fig(px.line(context["monthly"], x="month", y="demand", markers=True)),
            _format_fig(px.bar(context["by_location"], x="location", y="inventory", color="location")),
            _format_fig(px.bar(top_parts, x="part_id", y="demand", color="demand", color_continuous_scale="Blues")),
        )

    @app.callback(
        Output("monthly-demand", "figure"),
        Output("demand-by-part", "figure"),
        Output("demand-by-location", "figure"),
        Output("demand-distribution", "figure"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("location-filter", "value"),
        Input("part-filter", "value"),
    )
    def update_demand(start_date, end_date, locations, parts):
        filtered, context = _context(df, start_date, end_date, locations, parts)
        if filtered.empty:
            return [_empty_figure("No data")] * 4
        by_part = context["by_part"].nlargest(15, "demand")
        return (
            _format_fig(px.area(context["monthly"], x="month", y="demand")),
            _format_fig(px.bar(by_part, x="part_id", y="demand", color="demand", color_continuous_scale="Teal")),
            _format_fig(px.pie(context["by_location"], names="location", values="demand", hole=0.45)),
            _format_fig(px.histogram(filtered, x="demand", nbins=30)),
        )

    @app.callback(
        Output("stockout-trend", "figure"),
        Output("stockout-location", "figure"),
        Output("stockout-parts", "figure"),
        Output("demand-inventory", "figure"),
        Output("risk-table", "children"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("location-filter", "value"),
        Input("part-filter", "value"),
    )
    def update_stockout(start_date, end_date, locations, parts):
        filtered, context = _context(df, start_date, end_date, locations, parts)
        if filtered.empty:
            return *_empty_list(4), html.Div("No data", className="empty-state")
        metrics = context["metrics"]
        stockout_parts = metrics.nlargest(15, "stockout_events")
        return (
            _format_fig(px.line(context["monthly"], x="month", y="stockout", markers=True)),
            _format_fig(px.bar(context["by_location"], x="location", y="stockout", color="location")),
            _format_fig(px.bar(stockout_parts, x="part_id", y="stockout_events", color="stockout_rate")),
            _format_fig(px.scatter(filtered, x="demand", y="inventory", color="stockout", opacity=0.65)),
            _metric_table(metrics, "risk-data-table"),
        )

    @app.callback(
        Output("stock-vs-rop", "figure"),
        Output("safety-vs-inventory", "figure"),
        Output("status-distribution", "figure"),
        Output("reorder-table", "children"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("location-filter", "value"),
        Input("part-filter", "value"),
    )
    def update_reorder(start_date, end_date, locations, parts):
        filtered, context = _context(df, start_date, end_date, locations, parts)
        if filtered.empty:
            return *_empty_list(3), html.Div("No data", className="empty-state")
        metrics = context["metrics"].sort_values("reorder_point", ascending=False).head(25)
        long_metrics = metrics.melt(
            id_vars=["part_id", "location", "status"],
            value_vars=["current_stock", "reorder_point"],
            var_name="metric",
            value_name="value",
        )
        safety_metrics = metrics.melt(
            id_vars=["part_id", "location", "status"],
            value_vars=["current_stock", "safety_stock"],
            var_name="metric",
            value_name="value",
        )
        status_counts = context["metrics"]["status"].value_counts().rename_axis("status").reset_index(name="count")
        return (
            _format_fig(px.bar(long_metrics, x="part_id", y="value", color="metric", barmode="group")),
            _format_fig(px.bar(safety_metrics, x="part_id", y="value", color="metric", barmode="group")),
            _format_fig(px.pie(status_counts, names="status", values="count", color="status", color_discrete_map=STATUS_COLORS)),
            _metric_table(context["metrics"], "reorder-data-table"),
        )


def _empty_list(count: int):
    return [_empty_figure("No data") for _ in range(count)]
