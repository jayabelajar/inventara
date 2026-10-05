from __future__ import annotations

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()


def get_engine(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not configured.")
    return create_engine(url)


def load_dataframe_to_postgres(
    df: pd.DataFrame,
    table_name: str = "fact_inventory",
    if_exists: str = "replace",
) -> None:
    engine = get_engine()
    with engine.begin() as connection:
        df.to_sql(table_name, connection, if_exists=if_exists, index=False)


def run_query(query: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.begin() as connection:
        return pd.read_sql(text(query), connection)
