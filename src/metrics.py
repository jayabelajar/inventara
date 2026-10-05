from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_inventory_metrics(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["part_id", "location"]
    metrics = (
        df.groupby(group_cols)
        .agg(
            average_demand=("demand", "mean"),
            demand_std=("demand", "std"),
            total_demand=("demand", "sum"),
            current_stock=("inventory", "last"),
            average_inventory=("inventory", "mean"),
            stockout_events=("stockout", "sum"),
            observations=("stockout", "count"),
            average_lead_time=("lead_time", "mean"),
            max_lead_time=("lead_time", "max"),
        )
        .reset_index()
    )
    metrics["demand_std"] = metrics["demand_std"].fillna(0)
    metrics["stockout_rate"] = metrics["stockout_events"] / metrics["observations"]
    safety_lead_time = np.maximum(metrics["max_lead_time"] - metrics["average_lead_time"], 1)
    metrics["safety_stock"] = np.ceil(metrics["average_demand"] * safety_lead_time / 30).astype(int)
    metrics["reorder_point"] = np.ceil(
        (metrics["average_demand"] * metrics["average_lead_time"] / 30) + metrics["safety_stock"]
    ).astype(int)

    metrics["status"] = np.select(
        [
            metrics["current_stock"] <= 0,
            metrics["current_stock"] <= metrics["safety_stock"],
            metrics["current_stock"] <= metrics["reorder_point"],
        ],
        ["STOCKOUT", "CRITICAL", "REORDER"],
        default="SAFE",
    )
    return metrics


def summarize_kpis(df: pd.DataFrame, metrics: pd.DataFrame) -> dict[str, float | int]:
    return {
        "total_parts": int(df["part_id"].nunique()),
        "total_inventory": int(df.sort_values("date").groupby(["part_id", "location"])["inventory"].last().sum()),
        "average_demand": round(float(df["demand"].mean()), 2),
        "stockout_rate": round(float(df["stockout"].mean() * 100), 2),
        "critical_parts": int(metrics["status"].isin(["CRITICAL", "STOCKOUT"]).sum()),
        "parts_below_rop": int(metrics["status"].isin(["REORDER", "CRITICAL", "STOCKOUT"]).sum()),
        "average_lead_time": round(float(df["lead_time"].mean()), 2),
    }
