import pandas as pd
import pytest
from etl.transform import transform_data
from etl.validate import validate_data

def sample_row():
    return {
        "order_id": "ORD1",
        "order_date": "2026-01-01",
        "customer_id": "CUST1",
        "product_id": "P001",
        "product_name": "Laptop",
        "category": "Electronics",
        "region": "West",
        "city": "Mumbai",
        "quantity": 2,
        "unit_price": 100,
        "discount": 0.10,
        "payment_method": "UPI",
        "revenue": 99999
    }

def test_revenue_is_recalculated():
    result = transform_data(pd.DataFrame([sample_row()]))
    assert result.iloc[0]["revenue"] == 180

def test_duplicate_orders_are_rejected():
    row = sample_row()
    df = pd.DataFrame([row, row])
    with pytest.raises(ValueError):
        validate_data(df)

def test_invalid_quantity_is_rejected():
    row = sample_row()
    row["quantity"] = 0
    with pytest.raises(ValueError):
        validate_data(pd.DataFrame([row]))
