import os
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR = Path(
    os.getenv(
        "DECISIONAI_DATA_DIR",
        str(DEFAULT_DATA_DIR),
    )
).resolve()


def load_products() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "products.csv",
    )


def load_customers() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "customers.csv",
        parse_dates=[
            "signup_date",
        ],
    )


def load_orders() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=[
            "order_date",
        ],
    )
