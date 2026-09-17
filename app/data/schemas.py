PRODUCT_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "unit_cost",
]

CUSTOMER_COLUMNS = [
    "customer_id",
    "signup_date",
    "segment",
    "region",
    "acquisition_channel",
]

ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
    "discount",
    "sales_channel",
]

PRODUCT_DTYPES = {
    "product_id": "str",
    "product_name": "str",
    "category": "str",
    "unit_cost": "float64",
}

CUSTOMER_DTYPES = {
    "customer_id": "str",
    "signup_date": "datetime64",
    "segment": "str",
    "region": "str",
    "acquisition_channel": "str",
}

ORDER_DTYPES = {
    "order_id": "str",
    "customer_id": "str",
    "product_id": "str",
    "order_date": "datetime64",
    "quantity": "int64",
    "unit_price": "float64",
    "discount": "float64",
    "sales_channel": "str",
}
