# Inventara

Inventara is an aviation spare parts inventory analytics dashboard built with Python, Pandas, Plotly, Dash, SQLAlchemy, and PostgreSQL. It transforms demand, inventory, stockout, and supplier lead time records into an interactive decision-support dashboard for monitoring operational performance and replenishment risk.

## Preview

![Inventara overview dashboard](screenshots/overview-dashboard.png)

Additional dashboard views:

- [Demand Analytics](screenshots/demand-analytics.png)
- [Stockout Risk](screenshots/stockout-risk.png)
- [Reorder Analysis](screenshots/reorder-analysis.png)

## Key Features

- Responsive Dash dashboard with global period, location, and spare part filters.
- KPI cards for spare part count, total inventory, average demand, stockout rate, and critical parts.
- Overview charts for inventory trends, demand trends, inventory by location, and top demand parts.
- Demand analytics by month, spare part, location, and demand distribution.
- Stockout monitoring with trend, location, frequency, risk, and table views.
- Reorder analysis using safety stock, reorder point, current inventory, and inventory status.
- PostgreSQL schema and reusable SQL analytics queries for database-backed analysis.
- Reproducible data cleaning pipeline from raw CSV to processed analytics dataset.

## Dataset

This project uses the Aviation Spare Parts Demand, Inventory, and Stockout dataset from Mendeley Data:

<https://data.mendeley.com/datasets/htn863826t/1>

The dataset is synthetic/simulated and is used for analytics, dashboarding, and inventory optimization workflows.

Expected raw data path:

```text
data/raw/aviation_spare_parts.csv
```

Processed output path:

```text
data/processed/spare_parts_clean.csv
```

## Tech Stack

- Python
- Pandas and NumPy
- Dash
- Plotly
- PostgreSQL
- SQLAlchemy
- python-dotenv

## Project Structure

```text
inventara/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .env.example
|-- assets/
|   `-- style.css
|-- dashboard/
|   |-- callbacks.py
|   |-- components.py
|   `-- layout.py
|-- data/
|   |-- raw/
|   `-- processed/
|-- docs/
|   |-- dataset/
|   `-- PRD.MD
|-- notebooks/
|   `-- eda.ipynb
|-- screenshots/
|   |-- demand-analytics.png
|   |-- overview-dashboard.png
|   |-- reorder-analysis.png
|   `-- stockout-risk.png
|-- sql/
|   |-- analytics_queries.sql
|   `-- schema.sql
`-- src/
    |-- analysis.py
    |-- data_cleaning.py
    |-- database.py
    `-- metrics.py
```

## Getting Started

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the processed dataset:

```bash
python -m src.data_cleaning
```

Run the dashboard:

```bash
python app.py
```

Open the local Dash URL shown in the terminal. The default is usually:

```text
http://127.0.0.1:8050
```

## Environment Variables

Copy `.env.example` to `.env` when using PostgreSQL integration:

```text
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/inventara
RAW_DATA_PATH=data/raw/aviation_spare_parts.csv
PROCESSED_DATA_PATH=data/processed/spare_parts_clean.csv
```

## PostgreSQL Setup

Create the database, then run the schema:

```bash
psql -d inventara -f sql/schema.sql
```

Reusable analytics queries are available in:

```text
sql/analytics_queries.sql
```

The cleaned dataframe can be loaded through `src.database.load_dataframe_to_postgres`.

## Inventory Metrics

Inventara calculates:

- Average demand
- Stockout events
- Stockout rate
- Average inventory
- Current inventory
- Average and maximum supplier lead time
- Safety stock
- Reorder point
- Inventory status: `SAFE`, `REORDER`, `CRITICAL`, or `STOCKOUT`

## License

This repository is provided for educational and demonstration purposes.
