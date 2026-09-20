import pandas as pd

from app.tools.anomalies import AnomalyDetectionTool
from app.tools.drivers import DriverAnalysisTool
from app.tools.factory import build_default_tool_registry
from app.tools.revenue import RevenueAnalysisTool


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "o1",
            ],
            "customer_id": [
                "c1",
            ],
            "product_id": [
                "p1",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-01",
                ]
            ),
            "quantity": [
                1,
            ],
            "unit_price": [
                100.0,
            ],
            "discount": [
                0.0,
            ],
            "sales_channel": [
                "Web",
            ],
        }
    )


def build_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [
                "c1",
            ],
            "signup_date": pd.to_datetime(
                [
                    "2024-01-01",
                ]
            ),
            "segment": [
                "SMB",
            ],
            "region": [
                "South",
            ],
            "acquisition_channel": [
                "Organic",
            ],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": [
                "p1",
            ],
            "product_name": [
                "Laptop",
            ],
            "category": [
                "Computing",
            ],
            "unit_cost": [
                60.0,
            ],
        }
    )


def test_default_registry_contains_all_tools() -> None:
    registry = build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    assert registry.names() == [
        "analyze_revenue",
        "analyze_revenue_drivers",
        "detect_revenue_anomalies",
    ]


def test_default_registry_contains_revenue_tool() -> None:
    registry = build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    tool = registry.get("analyze_revenue")

    assert isinstance(
        tool,
        RevenueAnalysisTool,
    )


def test_default_registry_contains_driver_tool() -> None:
    registry = build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    tool = registry.get("analyze_revenue_drivers")

    assert isinstance(
        tool,
        DriverAnalysisTool,
    )


def test_default_registry_contains_anomaly_tool() -> None:
    registry = build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    tool = registry.get("detect_revenue_anomalies")

    assert isinstance(
        tool,
        AnomalyDetectionTool,
    )


def test_default_registry_exposes_all_definitions() -> None:
    registry = build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    definitions = registry.definitions()

    assert [definition.name for definition in definitions] == [
        "analyze_revenue",
        "analyze_revenue_drivers",
        "detect_revenue_anomalies",
    ]
