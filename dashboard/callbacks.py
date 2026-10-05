from __future__ import annotations

import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback_context, dash_table, html

from dashboard.layout import demand_page, overview_page, reorder_page, stockout_page
from src.analysis import apply_filters, build_analysis_context


STATUS_COLORS = {
    "SAFE": "#16a34a",
    "REORDER": "#d97706",
    "CRITICAL": "#dc2626",
    "STOCKOUT": "#991b1b",
}

FONT_FAMILY = '"Plus Jakarta Sans", Inter, "Segoe UI", Arial, sans-serif'
CHART_COLORS = ["#2563eb", "#14b8a6", "#22c55e", "#f59e0b", "#8b5cf6", "#ef4444", "#64748b"]


def _empty_figure(title: str):
    fig = px.scatter(title=title)
    fig.update_layout(annotations=[{"text": "No data", "showarrow": False, "font": {"color": "#667085"}}])
    return _format_fig(fig)


def _format_fig(fig):
    fig.update_layout(
        template="plotly_white",
        colorway=CHART_COLORS,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=18, t=18, b=28),
        font=dict(family=FONT_FAMILY, size=12, color="#162033"),
        legend_title_text="",
        hovermode="x unified",
        autosize=True,
    )
    fig.update_xaxes(showgrid=False, linecolor="#dbe6f3", zeroline=False, title_font_size=12)
    fig.update_yaxes(gridcolor="#eef3f8", zeroline=False, title_font_size=12)
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
        style_cell={
            "fontFamily": FONT_FAMILY,
            "fontSize": 12,
            "padding": "11px 10px",
            "border": "1px solid #e6edf5",
            "minWidth": "120px",
            "maxWidth": "220px",
            "whiteSpace": "normal",
        },
        style_header={
            "fontWeight": "800",
            "backgroundColor": "#f8fafc",
            "color": "#162033",
            "border": "1px solid #dbe6f3",
        },
        style_data={"backgroundColor": "#ffffff", "color": "#162033"},
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
            _format_fig(px.line(context["monthly"], x="month", y="inventory", markers=True, labels={"month": "", "inventory": "Inventory"})),
            _format_fig(px.line(context["monthly"], x="month", y="demand", markers=True, labels={"month": "", "demand": "Demand"})),
            _format_fig(px.bar(context["by_location"], x="location", y="inventory", color="location", labels={"location": "", "inventory": "Inventory"})),
            _format_fig(px.bar(top_parts, x="part_id", y="demand", color="demand", color_continuous_scale="Teal", labels={"part_id": "", "demand": "Demand"})),
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
            _format_fig(px.area(context["monthly"], x="month", y="demand", labels={"month": "", "demand": "Demand"})),
            _format_fig(px.bar(by_part, x="part_id", y="demand", color="demand", color_continuous_scale="Teal", labels={"part_id": "", "demand": "Demand"})),
            _format_fig(px.pie(context["by_location"], names="location", values="demand", hole=0.45)),
            _format_fig(px.histogram(filtered, x="demand", nbins=30, labels={"demand": "Demand"})),
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
            _format_fig(px.line(context["monthly"], x="month", y="stockout", markers=True, labels={"month": "", "stockout": "Stockout"})),
            _format_fig(px.bar(context["by_location"], x="location", y="stockout", color="location", labels={"location": "", "stockout": "Stockout"})),
            _format_fig(px.bar(stockout_parts, x="part_id", y="stockout_events", color="stockout_rate", color_continuous_scale="OrRd", labels={"part_id": "", "stockout_events": "Events", "stockout_rate": "Rate"})),
            _format_fig(px.scatter(filtered, x="demand", y="inventory", color="stockout", opacity=0.65, labels={"demand": "Demand", "inventory": "Inventory", "stockout": "Stockout"})),
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
            _format_fig(px.bar(long_metrics, x="part_id", y="value", color="metric", barmode="group", labels={"part_id": "", "value": "Units", "metric": ""})),
            _format_fig(px.bar(safety_metrics, x="part_id", y="value", color="metric", barmode="group", labels={"part_id": "", "value": "Units", "metric": ""})),
            _format_fig(px.pie(status_counts, names="status", values="count", color="status", color_discrete_map=STATUS_COLORS)),
            _metric_table(context["metrics"], "reorder-data-table"),
        )


def _empty_list(count: int):
    return [_empty_figure("No data") for _ in range(count)]
