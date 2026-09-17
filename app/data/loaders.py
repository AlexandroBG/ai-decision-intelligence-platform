from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")


def load_products() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "products.csv")


def load_customers() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )


def load_orders() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_date"],
    )