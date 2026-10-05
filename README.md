# SpareFlow

SpareFlow is an inventory and spare parts analytics dashboard for analyzing demand, inventory levels, supplier lead time, reorder points, and stockout risk. The project demonstrates an end-to-end analytics workflow with Python, Pandas, PostgreSQL, SQL, Plotly, and Dash.

## Highlights

- Interactive analytics dashboard with global date, location, and spare part filters
- Demand trend, part-level demand, location demand, and demand distribution analysis
- Inventory trend, current stock monitoring, and low-stock classification
- Stockout frequency, stockout rate, and high-risk spare part analysis
- Safety stock and reorder point calculation
- PostgreSQL schema and reusable SQL analytics queries
- Cleaned dataset export for repeatable analysis

## Dataset

The project uses the Aviation Spare Parts Demand, Inventory, and Stockout dataset from Mendeley Data: <https://data.mendeley.com/datasets/htn863826t/1>.

The data is synthetic/simulated and is used for portfolio analytics, dashboarding, and inventory optimization demonstrations.

Expected local dataset path:

```text
data/raw/aviation_spare_parts.csv
```

Running the cleaning pipeline creates:

```text
data/processed/spare_parts_clean.csv
```

## Tech Stack

- Python
- Pandas and NumPy
- PostgreSQL
- SQLAlchemy
- Plotly
- Dash
- Dash Bootstrap Components

## Project Structure

```text
inventara/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── eda.ipynb
├── src/
│   ├── analysis.py
│   ├── data_cleaning.py
│   ├── database.py
│   └── metrics.py
├── sql/
│   ├── analytics_queries.sql
│   └── schema.sql
├── dashboard/
│   ├── callbacks.py
│   ├── components.py
│   └── layout.py
└── assets/
    └── style.css
```

## Getting Started

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Generate the cleaned dataset:

```bash
python -m src.data_cleaning
```

Run the dashboard:

```bash
python app.py
```

Open the local Dash URL shown in the terminal, usually:

```text
http://127.0.0.1:8050
```

## PostgreSQL Setup

Create a database, then copy `.env.example` to `.env` and update `DATABASE_URL`.

Create the analytics table:

```bash
psql -d spareflow -f sql/schema.sql
```

The cleaned dataframe can be loaded through `src.database.load_dataframe_to_postgres`.

## Inventory Metrics

SpareFlow calculates:

- Average demand
- Stockout events and stockout rate
- Average and current inventory
- Average and maximum supplier lead time
- Safety stock
- Reorder point
- Inventory status: `SAFE`, `REORDER`, `CRITICAL`, or `STOCKOUT`

## Portfolio Summary

SpareFlow turns spare part demand and inventory records into decision-ready insights for replenishment planning, stockout risk monitoring, and supplier lead time analysis.
