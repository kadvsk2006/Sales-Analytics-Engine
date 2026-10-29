# Sales Data ETL Pipeline & Analytics Dashboard

A portfolio project in data engineering and analytics. It processes raw retail sales data, stores it in a PostgreSQL star schema, and presents business insights through SQL and Streamlit.

## Architecture

**CSV → Python/Pandas ETL → Data Quality Checks → PostgreSQL Star Schema → SQL Analytics → Streamlit Dashboard**

The [docs/architecture.md](docs/architecture.md) file contains diagrams of the data flow and star schema.

> **Sample data note:** The included dataset contains 15,000 synthetic rows. Its metrics illustrate how the pipeline works; they are not actual business results. Refer to [the analytics review](docs/data_quality_and_metric_notes.md) for validation results and important notes on interpreting the data.

## Key features

- Reads raw retail sales records from a CSV file.
- Checks the data schema, missing values, duplicate records, data types, and business rules.
- Uses Pandas to transform and standardize sales fields.
- Loads the dimensional data model into PostgreSQL.
- Analyzes data with SQL joins, CTEs, and window functions.
- Reports monthly and cumulative revenue, product rankings, average order value (AOV), and the repeat-customer rate.
- Offers an interactive Streamlit dashboard with date, category, and region filters, concise KPI values, and easy-to-read horizontal charts for categories and regions.
- Runs checks across the warehouse for missing measures, invalid quantities, prices or discounts, revenue calculation mismatches, and invalid links to dimension records.
- Provides pipeline tests and logging.

## Data warehouse

| Table | Type | Purpose |
|---|---|---|
| `fact_sales` | Fact | Measures recorded for each transaction |
| `dim_date` | Dimension | Calendar date, month, quarter, and year details |
| `dim_customer` | Dimension | Details about each customer |
| `dim_product` | Dimension | Product and category details |
| `dim_region` | Dimension | Region and city details |

## Tech stack

- Python
- Pandas / NumPy
- PostgreSQL
- SQLAlchemy / psycopg2
- SQL
- Streamlit
- Plotly
- Pytest

## Project structure

```text
sales-data-etl-pipeline/
├── data/raw/sales.csv
├── data/processed/
├── etl/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── pipeline.py
├── sql/
│   ├── schema.sql
│   ├── analytics.sql
│   └── create_database.sql
├── dashboard/app.py
├── docs/
│   ├── architecture.md
│   └── interview_questions.md
├── tests/test_etl.py
├── requirements.txt
├── .env.example
└── README.md
```

## Set up locally

### 1. Create and enable the virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install the required packages

```powershell
python -m pip install -r requirements.txt
```

### 3. Create a PostgreSQL database

In PostgreSQL or pgAdmin, create a database named `sales_analytics`.

Apply `sql/schema.sql` to the new database.

### 4. Set up database credentials

Copy `.env.example` to `.env`, then enter your PostgreSQL password:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_analytics
DB_USER=postgres
DB_PASSWORD=your_password
```

### 5. Execute the ETL pipeline

```powershell
python etl\pipeline.py
```

### 6. Launch the dashboard

```powershell
streamlit run dashboard\app.py
```

Use the local Streamlit address printed in the terminal. It is usually `http://localhost:8501`.

## Analytics included

- Monthly revenue and order patterns
- Revenue grouped by category
- Revenue grouped by region
- The 10 highest-revenue products
- Product rankings within each category
- Average order value
- Repeat-customer rate
- Highest-value customers
- Checks on warehouse and pipeline health
