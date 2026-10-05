from __future__ import annotations

from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, dcc, html

from dashboard.callbacks import register_callbacks
from dashboard.layout import create_layout
from src.data_cleaning import PROCESSED_DATA_PATH, RAW_DATA_PATH, save_processed_data


def load_dataset() -> pd.DataFrame:
    processed_path = Path(PROCESSED_DATA_PATH)
    if not processed_path.exists():
        save_processed_data(RAW_DATA_PATH, processed_path)
    df = pd.read_csv(processed_path, parse_dates=["date", "month"])
    return df.sort_values(["date", "part_id", "location"]).reset_index(drop=True)


df = load_dataset()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="SpareFlow",
)
server = app.server
app.layout = create_layout(df)
register_callbacks(app, df)


if __name__ == "__main__":
    app.run(debug=True)
