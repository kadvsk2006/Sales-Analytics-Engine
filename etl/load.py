import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("DB_NAME", "sales_analytics")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, pool_pre_ping=True)

def load_to_postgres(df: pd.DataFrame):
    engine = get_engine()

    customers = df[["customer_id"]].drop_duplicates().reset_index(drop=True)
    customers["customer_name"] = customers["customer_id"]

    products = df[
        ["product_id", "product_name", "category"]
    ].drop_duplicates("product_id")

    dates = df[["order_date"]].drop_duplicates().copy()
    dates["date_key"] = dates["order_date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["order_date"].dt.year
    dates["month"] = dates["order_date"].dt.month
    dates["month_name"] = dates["order_date"].dt.strftime("%B")
    dates["quarter"] = dates["order_date"].dt.quarter

    regions = df[["region", "city"]].drop_duplicates().reset_index(drop=True)
    regions["region_key"] = regions.index + 1

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE fact_sales, dim_customer, dim_product, dim_date, dim_region RESTART IDENTITY CASCADE"))

    customers.to_sql("dim_customer", engine, if_exists="append", index=False)
    products.to_sql("dim_product", engine, if_exists="append", index=False)
    dates[["date_key", "order_date", "year", "month", "month_name", "quarter"]].to_sql(
        "dim_date", engine, if_exists="append", index=False
    )
    regions[["region_key", "region", "city"]].to_sql(
        "dim_region", engine, if_exists="append", index=False
    )

    date_map = dict(zip(dates["order_date"], dates["date_key"]))
    region_map = dict(zip(
        zip(regions["region"], regions["city"]),
        regions["region_key"]
    ))

    fact = df.copy()
    fact["date_key"] = fact["order_date"].map(date_map)
    fact["region_key"] = [
        region_map[(r, c)] for r, c in zip(fact["region"], fact["city"])
    ]

    fact = fact[[
        "order_id", "date_key", "customer_id", "product_id",
        "region_key", "quantity", "unit_price", "discount", "revenue",
        "payment_method"
    ]]

    fact.to_sql("fact_sales", engine, if_exists="append", index=False)
