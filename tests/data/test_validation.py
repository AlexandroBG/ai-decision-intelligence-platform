import pandas as pd
import pytest

from app.data.errors import DataValidationError
from app.data.validation import (
    build_validation_result,
    ensure_valid_datasets,
    validate_columns,
    validate_dtypes,
    validate_order_business_rules,
    validate_product_business_rules,
    validate_referential_integrity,
    validate_required_fields,
    validate_schema,
)


def test_build_validation_result_valid() -> None:
    result = build_validation_result([])

    assert result.is_valid is True
    assert result.errors == []


def test_build_validation_result_invalid() -> None:
    result = build_validation_result(["Example error"])

    assert result.is_valid is False
    assert result.errors == ["Example error"]


def test_product_business_rules_accept_valid_data() -> None:
    dataframe = pd.DataFrame(
        {
            "unit_cost": [10.0, 25.0, 100.0],
        }
    )

    errors = validate_product_business_rules(dataframe)

    assert errors == []


def test_product_business_rules_reject_negative_cost() -> None:
    dataframe = pd.DataFrame(
        {
            "unit_cost": [10.0, -5.0],
        }
    )

    errors = validate_product_business_rules(dataframe)

    assert errors == ["Column 'unit_cost' contains negative values"]


def test_order_business_rules_accept_valid_data() -> None:
    dataframe = pd.DataFrame(
        {
            "quantity": [1, 2],
            "unit_price": [100.0, 250.0],
            "discount": [0.0, 0.2],
        }
    )

    errors = validate_order_business_rules(dataframe)

    assert errors == []


def test_order_business_rules_reject_invalid_values() -> None:
    dataframe = pd.DataFrame(
        {
            "quantity": [0],
            "unit_price": [-10.0],
            "discount": [1.5],
        }
    )

    errors = validate_order_business_rules(dataframe)

    assert "Column 'quantity' must contain only positive values" in errors
    assert "Column 'unit_price' contains negative values" in errors
    assert "Column 'discount' must contain values between 0 and 1" in errors


def test_required_fields_reject_null_values() -> None:
    dataframe = pd.DataFrame(
        {
            "customer_id": ["C0001", None],
        }
    )

    errors = validate_required_fields(
        dataframe=dataframe,
        required_columns=["customer_id"],
    )

    assert errors == ["Column 'customer_id' contains null values"]


def test_validate_columns_accepts_expected_columns() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": ["P001"],
            "product_name": ["Product 01"],
        }
    )

    errors = validate_columns(
        dataframe=dataframe,
        expected_columns=["product_id", "product_name"],
    )

    assert errors == []


def test_validate_columns_detects_missing_column() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": ["P001"],
        }
    )

    errors = validate_columns(
        dataframe=dataframe,
        expected_columns=["product_id", "product_name"],
    )

    assert errors == ["Missing columns: ['product_name']"]


def test_validate_columns_detects_unexpected_column() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": ["P001"],
            "unexpected": ["value"],
        }
    )

    errors = validate_columns(
        dataframe=dataframe,
        expected_columns=["product_id"],
    )

    assert errors == ["Unexpected columns: ['unexpected']"]


def test_validate_dtypes_accepts_datetime() -> None:
    dataframe = pd.DataFrame(
        {
            "order_date": pd.to_datetime(["2025-07-01"]),
        }
    )

    errors = validate_dtypes(
        dataframe=dataframe,
        expected_dtypes={"order_date": "datetime64"},
    )

    assert errors == []


def test_validate_schema_detects_schema_error() -> None:
    dataframe = pd.DataFrame(
        {
            "product_id": ["P001"],
            "unit_cost": [10.0],
        }
    )

    errors = validate_schema(
        dataframe=dataframe,
        expected_columns=[
            "product_id",
            "product_name",
            "unit_cost",
        ],
        expected_dtypes={
            "product_id": "str",
            "product_name": "str",
            "unit_cost": "float64",
        },
    )

    assert "Missing columns: ['product_name']" in errors


def test_referential_integrity_accepts_valid_references() -> None:
    customers = pd.DataFrame(
        {
            "customer_id": ["C0001"],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": ["P001"],
        }
    )

    orders = pd.DataFrame(
        {
            "customer_id": ["C0001"],
            "product_id": ["P001"],
        }
    )

    errors = validate_referential_integrity(
        orders=orders,
        customers=customers,
        products=products,
    )

    assert errors == []


def test_referential_integrity_rejects_unknown_customer() -> None:
    customers = pd.DataFrame(
        {
            "customer_id": ["C0001"],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": ["P001"],
        }
    )

    orders = pd.DataFrame(
        {
            "customer_id": ["C9999"],
            "product_id": ["P001"],
        }
    )

    errors = validate_referential_integrity(
        orders=orders,
        customers=customers,
        products=products,
    )

    assert errors == ["Orders contain unknown customer IDs: ['C9999']"]


def test_ensure_valid_datasets_raises_for_invalid_orders() -> None:
    products = pd.DataFrame(
        {
            "product_id": ["P001"],
            "product_name": ["Product 01"],
            "category": ["Computing"],
            "unit_cost": [100.0],
        }
    )

    customers = pd.DataFrame(
        {
            "customer_id": ["C0001"],
            "signup_date": pd.to_datetime(["2025-01-01"]),
            "segment": ["SMB"],
            "region": ["North"],
            "acquisition_channel": ["Organic"],
        }
    )

    orders = pd.DataFrame(
        {
            "order_id": ["O00001"],
            "customer_id": ["C0001"],
            "product_id": ["P001"],
            "order_date": pd.to_datetime(["2025-07-01"]),
            "quantity": [0],
            "unit_price": [150.0],
            "discount": [0.1],
            "sales_channel": ["Web"],
        }
    )

    with pytest.raises(
        DataValidationError,
        match="quantity",
    ):
        ensure_valid_datasets(
            products=products,
            customers=customers,
            orders=orders,
        )
