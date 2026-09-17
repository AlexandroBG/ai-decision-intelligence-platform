from app.data.cleaning import (
    normalize_customers,
    normalize_orders,
    normalize_products,
)
from app.data.loaders import (
    load_customers,
    load_orders,
    load_products,
)
from app.data.validation import (
    ensure_valid_datasets,
    validate_datasets,
)


def test_data_pipeline_end_to_end() -> None:
    products = normalize_products(load_products())
    customers = normalize_customers(load_customers())
    orders = normalize_orders(load_orders())

    result = validate_datasets(
        products=products,
        customers=customers,
        orders=orders,
    )

    assert result.is_valid is True
    assert result.errors == []

    ensure_valid_datasets(
        products=products,
        customers=customers,
        orders=orders,
    )

    assert products.shape == (20, 4)
    assert customers.shape == (300, 5)
    assert orders.shape == (2250, 8)
