import pandas as pd


def normalize_string_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    normalized = dataframe.copy()

    for column in columns:
        if column not in normalized.columns:
            continue

        normalized[column] = normalized[column].str.strip()

    return normalized


def normalize_products(dataframe: pd.DataFrame) -> pd.DataFrame:
    return normalize_string_columns(
        dataframe,
        [
            "product_id",
            "product_name",
            "category",
        ],
    )


def normalize_customers(dataframe: pd.DataFrame) -> pd.DataFrame:
    return normalize_string_columns(
        dataframe,
        [
            "customer_id",
            "segment",
            "region",
            "acquisition_channel",
        ],
    )


def normalize_orders(dataframe: pd.DataFrame) -> pd.DataFrame:
    return normalize_string_columns(
        dataframe,
        [
            "order_id",
            "customer_id",
            "product_id",
            "sales_channel",
        ],
    )
