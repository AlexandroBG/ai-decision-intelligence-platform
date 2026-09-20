import pandas as pd

from app.tools.catalog import build_tool_catalog
from app.tools.executor import ToolExecutor
from app.tools.factory import build_default_tool_registry


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "o1",
                "o2",
                "o3",
                "o4",
            ],
            "customer_id": [
                "c1",
                "c2",
                "c1",
                "c2",
            ],
            "product_id": [
                "p1",
                "p2",
                "p1",
                "p2",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-10",
                    "2025-07-20",
                    "2025-08-10",
                    "2025-08-20",
                ]
            ),
            "quantity": [
                2,
                1,
                1,
                1,
            ],
            "unit_price": [
                100.0,
                200.0,
                100.0,
                100.0,
            ],
            "discount": [
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "sales_channel": [
                "Partner",
                "Web",
                "Partner",
                "Web",
            ],
        }
    )


def build_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [
                "c1",
                "c2",
            ],
            "signup_date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-02-01",
                ]
            ),
            "segment": [
                "Enterprise",
                "SMB",
            ],
            "region": [
                "South",
                "North",
            ],
            "acquisition_channel": [
                "Organic",
                "Paid",
            ],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": [
                "p1",
                "p2",
            ],
            "product_name": [
                "Laptop",
                "Router",
            ],
            "category": [
                "Computing",
                "Networking",
            ],
            "unit_cost": [
                60.0,
                120.0,
            ],
        }
    )


def build_system():
    registry = build_default_tool_registry(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    executor = ToolExecutor(registry=registry)

    catalog = build_tool_catalog(registry=registry)

    return registry, executor, catalog


def test_full_tool_system_exposes_expected_catalog() -> None:
    registry, _, catalog = build_system()

    assert len(registry) == 3

    assert [tool["name"] for tool in catalog] == [
        "analyze_revenue",
        "analyze_revenue_drivers",
        "detect_revenue_anomalies",
    ]


def test_full_tool_system_executes_revenue_tool() -> None:
    _, executor, _ = build_system()

    result = executor.execute_payload(
        {
            "tool_name": "analyze_revenue",
            "arguments": {
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
            },
        }
    )

    assert result.success is True

    assert result.tool_name == ("analyze_revenue")

    assert result.output == {
        "baseline_revenue": 400.0,
        "comparison_revenue": 200.0,
        "absolute_change": -200.0,
        "percentage_change": -0.5,
    }


def test_full_tool_system_rejects_unknown_tool() -> None:
    _, executor, _ = build_system()

    result = executor.execute_payload(
        {
            "tool_name": "unknown_tool",
            "arguments": {},
        }
    )

    assert result.success is False

    assert result.tool_name == ("unknown_tool")

    assert result.error == ("Unknown tool: unknown_tool")


def test_full_tool_system_rejects_invalid_payload() -> None:
    _, executor, _ = build_system()

    result = executor.execute_payload(
        {
            "tool_name": "",
            "arguments": {},
        }
    )

    assert result.success is False

    assert result.error == "Invalid tool call payload."


def test_catalog_and_executor_use_same_tool_names() -> None:
    registry, _, catalog = build_system()

    catalog_names = [tool["name"] for tool in catalog]

    assert catalog_names == (registry.names())
