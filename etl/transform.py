import pandas as pd

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["customer_id"] = df["customer_id"].astype(str).str.strip()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    df["city"] = df["city"].astype(str).str.strip()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce")

    # Recalculate revenue rather than trusting raw derived values.
    df["revenue"] = (
        df["quantity"] * df["unit_price"] * (1 - df["discount"])
    ).round(2)

    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=[
        "order_id", "order_date", "customer_id", "product_id",
        "quantity", "unit_price", "discount"
    ])

    return df
