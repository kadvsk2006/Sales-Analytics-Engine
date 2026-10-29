import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    errors = []

    null_counts = df.isnull().sum()
    null_columns = null_counts[null_counts > 0]
    if not null_columns.empty:
        errors.append(f"Null values found: {null_columns.to_dict()}")

    duplicates = int(df["order_id"].duplicated().sum())
    if duplicates:
        errors.append(f"Duplicate order IDs: {duplicates}")

    if (df["quantity"] <= 0).any():
        errors.append("Non-positive quantity detected")

    if (df["unit_price"] < 0).any():
        errors.append("Negative unit price detected")

    if ((df["discount"] < 0) | (df["discount"] > 1)).any():
        errors.append("Invalid discount values detected")

    if errors:
        for error in errors:
            logger.error(error)
        raise ValueError("Data validation failed. Check ETL log for details.")

    logger.info("Data-quality validation passed.")
    return df
