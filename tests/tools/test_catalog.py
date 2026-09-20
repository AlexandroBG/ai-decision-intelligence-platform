import pandas as pd

from app.tools.catalog import build_tool_catalog
from app.tools.factory import build_default_tool_registry


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1"],
            "customer_id": ["c1"],
            "product_id": ["p1"],
            "order_date": pd.to_datetime(["2025-07-01"]),
            "quantity": [1],
            "unit_price": [100.0],
            "discount": [0.0],
            "sales_channel": ["Web"],
        }
    )


def build_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["c1"],
            "signup_date": pd.to_datetime(["2024-01-01"]),
            "segment": ["SMB"],
            "region": ["South"],
            "acquisition_channel": ["Organic"],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": ["p1"],
            "product_name": ["Laptop"],
            "category": ["Computing"],
            "unit_cost": [60.0],
        }
    )


def build_registry():
    return build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )


def test_catalog_contains_all_registered_tools() -> None:
    registry = build_registry()

    catalog = build_tool_catalog(registry=registry)

    assert [tool["name"] for tool in catalog] == [
        "analyze_revenue",
        "analyze_revenue_drivers",
        "detect_revenue_anomalies",
    ]


def test_catalog_exposes_public_fields_only() -> None:
    registry = build_registry()

    catalog = build_tool_catalog(registry=registry)

    for tool in catalog:
        assert set(tool) == {
            "name",
            "description",
            "input_schema",
        }


def test_catalog_exposes_descriptions() -> None:
    registry = build_registry()

    catalog = build_tool_catalog(registry=registry)

    for tool in catalog:
        assert isinstance(
            tool["description"],
            str,
        )

        assert tool["description"]


def test_catalog_exposes_input_schemas() -> None:
    registry = build_registry()

    catalog = build_tool_catalog(registry=registry)

    for tool in catalog:
        schema = tool["input_schema"]

        assert isinstance(
            schema,
            dict,
        )

        assert schema["type"] == "object"

        assert "properties" in schema


def test_catalog_does_not_expose_tool_instances() -> None:
    registry = build_registry()

    catalog = build_tool_catalog(registry=registry)

    for tool in catalog:
        assert "execute" not in tool
        assert "_run" not in tool
        assert "definition" not in tool
