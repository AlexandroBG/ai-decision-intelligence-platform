from app.data.loaders import (
    load_customers,
    load_orders,
    load_products,
)


def test_load_products() -> None:
    dataframe = load_products()

    assert dataframe.shape == (20, 4)
    assert dataframe["product_id"].nunique() == 20


def test_load_customers() -> None:
    dataframe = load_customers()

    assert dataframe.shape == (300, 5)
    assert dataframe["customer_id"].nunique() == 300
    assert str(dataframe["signup_date"].dtype).startswith("datetime64")


def test_load_orders() -> None:
    dataframe = load_orders()

    assert dataframe.shape == (2250, 8)
    assert dataframe["order_id"].nunique() == 2250
    assert str(dataframe["order_date"].dtype).startswith("datetime64")
