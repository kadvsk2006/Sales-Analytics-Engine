import pandas as pd
from pathlib import Path

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "product_id",
    "product_name", "category", "region", "city", "quantity",
    "unit_price", "discount", "payment_method", "revenue"
]

def extract_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Schema mismatch. Missing columns: {sorted(missing)}")
    return df
