from __future__ import annotations

import pandas as pd

from src.metrics import calculate_inventory_metrics, summarize_kpis


def apply_filters(
    df: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
    locations: list[str] | None = None,
    parts: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if start_date:
        filtered = filtered[filtered["date"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["date"] <= pd.to_datetime(end_date)]
    if locations:
        filtered = filtered[filtered["location"].isin(locations)]
    if parts:
        filtered = filtered[filtered["part_id"].isin(parts)]
    return filtered


def build_analysis_context(df: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    metrics = calculate_inventory_metrics(df)
    return {
        "kpis": summarize_kpis(df, metrics),
        "metrics": metrics,
        "monthly": df.groupby("month", as_index=False).agg(
            demand=("demand", "sum"),
            inventory=("inventory", "mean"),
            stockout=("stockout", "sum"),
            lead_time=("lead_time", "mean"),
        ),
        "by_location": df.groupby("location", as_index=False).agg(
            demand=("demand", "sum"),
            inventory=("inventory", "mean"),
            stockout=("stockout", "sum"),
            lead_time=("lead_time", "mean"),
        ),
        "by_part": df.groupby("part_id", as_index=False).agg(
            demand=("demand", "sum"),
            inventory=("inventory", "mean"),
            stockout=("stockout", "sum"),
            lead_time=("lead_time", "mean"),
        ),
    }
