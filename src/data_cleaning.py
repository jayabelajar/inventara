from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RAW_DATA_PATH = Path("data/raw/aviation_spare_parts.csv")
PROCESSED_DATA_PATH = Path("data/processed/spare_parts_clean.csv")


COLUMN_RENAME_MAP = {
    "location_id": "location",
    "period_start_date": "date",
    "demand_quantity": "demand",
    "issues_quantity": "issues",
    "opening_inventory": "opening_inventory",
    "closing_inventory": "inventory",
    "stockout_indicator": "stockout",
    "lead_time_days": "lead_time",
    "flight_cycles": "flight_cycle",
}


def load_raw_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_inventory_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.rename(columns=COLUMN_RENAME_MAP).copy()

    cleaned["date"] = pd.to_datetime(cleaned["date"], format="%d-%m-%Y", errors="coerce")
    cleaned = cleaned.dropna(subset=["date", "part_id", "location"])
    cleaned = cleaned.drop_duplicates(subset=["part_id", "location", "date"])

    numeric_columns = [
        "demand",
        "issues",
        "opening_inventory",
        "inventory",
        "stockout",
        "flight_cycle",
        "lead_time",
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned[numeric_columns] = cleaned[numeric_columns].fillna(0)
    cleaned["demand"] = cleaned["demand"].clip(lower=0)
    cleaned["issues"] = cleaned["issues"].clip(lower=0)
    cleaned["opening_inventory"] = cleaned["opening_inventory"].clip(lower=0)
    cleaned["inventory"] = cleaned["inventory"].clip(lower=0)
    cleaned["stockout"] = np.where(
        (cleaned["stockout"] > 0) | (cleaned["inventory"] <= 0),
        1,
        0,
    )

    cleaned["part_id"] = cleaned["part_id"].astype(str).str.upper().str.strip()
    cleaned["location"] = cleaned["location"].astype(str).str.upper().str.strip()
    cleaned["month"] = cleaned["date"].dt.to_period("M").dt.to_timestamp()
    cleaned["year"] = cleaned["date"].dt.year

    ordered_columns = [
        "date",
        "month",
        "year",
        "part_id",
        "part_class",
        "ata_chapter",
        "aircraft_type",
        "location",
        "demand",
        "issues",
        "opening_inventory",
        "inventory",
        "stockout",
        "flight_cycle",
        "lead_time",
    ]
    return cleaned[ordered_columns].sort_values(["date", "part_id", "location"]).reset_index(drop=True)


def save_processed_data(
    raw_path: str | Path = RAW_DATA_PATH,
    output_path: str | Path = PROCESSED_DATA_PATH,
) -> pd.DataFrame:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned = clean_inventory_data(load_raw_data(raw_path))
    cleaned.to_csv(output_path, index=False)
    return cleaned


if __name__ == "__main__":
    data = save_processed_data()
    print(f"Saved {len(data):,} clean records to {PROCESSED_DATA_PATH}")
