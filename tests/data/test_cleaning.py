import pandas as pd

from app.data.cleaning import (
    normalize_customers,
    normalize_orders,
    normalize_products,
    normalize_string_columns,
)


def test_normalize_string_columns_strips_whitespace() -> None:
    dataframe = pd.DataFrame(
        {
            "region": [" South ", "North "],
        }
    )

    normalized = normalize_string_columns(
        dataframe=dataframe,
        columns=["region"],
    )

    assert normalized["region"].tolist() == ["South", "North"]


def test_normalize_string_columns_does_not_modify_original() -> None:
    dataframe = pd.DataFrame(
        {
            "region": [" South "],
        }
    )

    normalize_string_columns(
        dataframe=dataframe,
        columns=["region"],
    )

    assert dataframe["region"].tolist() == [" South "]


def test_normalize_products_preserves_shape() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": [" P001 "],
            "product_name": [" Product 01 "],
            "category": [" Computing "],
            "unit_cost": [100.0],
        }
    )

    normalized = normalize_products(dataframe)

    assert normalized.shape == dataframe.shape


def test_normalize_customers_preserves_shape() -> None:
    dataframe = pd.DataFrame(
        {
            "customer_id": [" C0001 "],
            "signup_date": pd.to_datetime(["2025-01-01"]),
            "segment": [" SMB "],
            "region": [" North "],
            "acquisition_channel": [" Organic "],
        }
    )

    normalized = normalize_customers(dataframe)

    assert normalized.shape == dataframe.shape


def test_normalize_orders_preserves_shape() -> None:
    dataframe = pd.DataFrame(
        {
            "order_id": [" O00001 "],
            "customer_id": [" C0001 "],
            "product_id": [" P001 "],
            "order_date": pd.to_datetime(["2025-07-01"]),
            "quantity": [1],
            "unit_price": [150.0],
            "discount": [0.1],
            "sales_channel": [" Web "],
        }
    )

    normalized = normalize_orders(dataframe)

    assert normalized.shape == dataframe.shape
