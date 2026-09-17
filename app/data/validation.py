import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from app.data.contracts import ValidationResult
from app.data.errors import DataValidationError
from app.data.schemas import (
    CUSTOMER_COLUMNS,
    CUSTOMER_DTYPES,
    ORDER_COLUMNS,
    ORDER_DTYPES,
    PRODUCT_COLUMNS,
    PRODUCT_DTYPES,
)


def validate_columns(
    dataframe: pd.DataFrame,
    expected_columns: list[str],
) -> list[str]:
    errors = []

    actual_columns = list(dataframe.columns)

    missing_columns = [
        column for column in expected_columns if column not in actual_columns
    ]

    unexpected_columns = [
        column for column in actual_columns if column not in expected_columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

    if unexpected_columns:
        errors.append(f"Unexpected columns: {unexpected_columns}")

    return errors


def validate_dtypes(
    dataframe: pd.DataFrame,
    expected_dtypes: dict[str, str],
) -> list[str]:
    errors = []

    for column, expected_dtype in expected_dtypes.items():
        if column not in dataframe.columns:
            continue

        actual_dtype = dataframe[column].dtype

        if expected_dtype == "datetime64":
            if not is_datetime64_any_dtype(actual_dtype):
                errors.append(
                    f"Column '{column}' has dtype '{actual_dtype}', "
                    "expected a datetime dtype"
                )
            continue

        if str(actual_dtype) != expected_dtype:
            errors.append(
                f"Column '{column}' has dtype '{actual_dtype}', "
                f"expected '{expected_dtype}'"
            )

    return errors


def validate_schema(
    dataframe: pd.DataFrame,
    expected_columns: list[str],
    expected_dtypes: dict[str, str],
) -> list[str]:
    errors = []

    errors.extend(
        validate_columns(
            dataframe=dataframe,
            expected_columns=expected_columns,
        )
    )

    errors.extend(
        validate_dtypes(
            dataframe=dataframe,
            expected_dtypes=expected_dtypes,
        )
    )

    return errors


def validate_product_business_rules(
    dataframe: pd.DataFrame,
) -> list[str]:
    errors = []

    if (dataframe["unit_cost"] < 0).any():
        errors.append("Column 'unit_cost' contains negative values")

    return errors


def validate_order_business_rules(
    dataframe: pd.DataFrame,
) -> list[str]:
    errors = []

    if (dataframe["quantity"] <= 0).any():
        errors.append("Column 'quantity' must contain only positive values")

    if (dataframe["unit_price"] < 0).any():
        errors.append("Column 'unit_price' contains negative values")

    if ((dataframe["discount"] < 0) | (dataframe["discount"] > 1)).any():
        errors.append("Column 'discount' must contain values between 0 and 1")

    return errors


def validate_required_fields(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> list[str]:
    errors = []

    for column in required_columns:
        if column not in dataframe.columns:
            continue

        if dataframe[column].isna().any():
            errors.append(f"Column '{column}' contains null values")

    return errors


def validate_referential_integrity(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> list[str]:
    errors = []

    valid_customer_ids = set(customers["customer_id"])
    valid_product_ids = set(products["product_id"])

    invalid_customer_ids = set(orders["customer_id"]) - valid_customer_ids
    invalid_product_ids = set(orders["product_id"]) - valid_product_ids

    if invalid_customer_ids:
        errors.append(
            f"Orders contain unknown customer IDs: {sorted(invalid_customer_ids)}"
        )

    if invalid_product_ids:
        errors.append(
            f"Orders contain unknown product IDs: {sorted(invalid_product_ids)}"
        )

    return errors


def build_validation_result(
    errors: list[str],
) -> ValidationResult:
    return ValidationResult(
        is_valid=not errors,
        errors=errors,
    )


def validate_datasets(
    products: pd.DataFrame,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> ValidationResult:
    errors = []

    product_schema_errors = validate_schema(
        dataframe=products,
        expected_columns=PRODUCT_COLUMNS,
        expected_dtypes=PRODUCT_DTYPES,
    )

    customer_schema_errors = validate_schema(
        dataframe=customers,
        expected_columns=CUSTOMER_COLUMNS,
        expected_dtypes=CUSTOMER_DTYPES,
    )

    order_schema_errors = validate_schema(
        dataframe=orders,
        expected_columns=ORDER_COLUMNS,
        expected_dtypes=ORDER_DTYPES,
    )

    errors.extend(product_schema_errors)
    errors.extend(customer_schema_errors)
    errors.extend(order_schema_errors)

    if product_schema_errors or customer_schema_errors or order_schema_errors:
        return build_validation_result(errors)

    errors.extend(
        validate_required_fields(
            dataframe=products,
            required_columns=PRODUCT_COLUMNS,
        )
    )

    errors.extend(
        validate_required_fields(
            dataframe=customers,
            required_columns=CUSTOMER_COLUMNS,
        )
    )

    errors.extend(
        validate_required_fields(
            dataframe=orders,
            required_columns=ORDER_COLUMNS,
        )
    )

    errors.extend(validate_product_business_rules(products))
    errors.extend(validate_order_business_rules(orders))

    errors.extend(
        validate_referential_integrity(
            orders=orders,
            customers=customers,
            products=products,
        )
    )

    return build_validation_result(errors)


def ensure_valid_datasets(
    products: pd.DataFrame,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    result = validate_datasets(
        products=products,
        customers=customers,
        orders=orders,
    )

    if not result.is_valid:
        error_message = "; ".join(result.errors)
        raise DataValidationError(error_message)
