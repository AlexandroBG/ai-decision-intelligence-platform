import pandas as pd

from app.tools.contracts import ToolCall
from app.tools.drivers import DriverAnalysisTool


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "o1",
                "o2",
                "o3",
                "o4",
                "o5",
                "o6",
            ],
            "customer_id": [
                "c1",
                "c2",
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
                "p1",
                "p2",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-05",
                    "2025-07-10",
                    "2025-07-20",
                    "2025-08-05",
                    "2025-08-10",
                    "2025-08-20",
                ]
            ),
            "quantity": [
                5,
                4,
                3,
                1,
                2,
                1,
            ],
            "unit_price": [
                100.0,
                200.0,
                100.0,
                100.0,
                200.0,
                100.0,
            ],
            "discount": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "sales_channel": [
                "Partner",
                "Web",
                "Partner",
                "Partner",
                "Web",
                "Partner",
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


def build_tool() -> DriverAnalysisTool:
    return DriverAnalysisTool(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )


def build_valid_call() -> ToolCall:
    return ToolCall(
        tool_name="analyze_revenue_drivers",
        arguments={
            "baseline_start": "2025-07-01",
            "baseline_end": "2025-07-31",
            "comparison_start": "2025-08-01",
            "comparison_end": "2025-08-31",
            "max_drivers": 5,
        },
    )


def test_driver_tool_exposes_definition() -> None:
    tool = build_tool()

    assert tool.definition.name == "analyze_revenue_drivers"

    assert "not causal attribution" in tool.definition.description


def test_driver_tool_returns_ranked_drivers() -> None:
    tool = build_tool()

    result = tool.execute(call=build_valid_call())

    assert result.success is True

    assert isinstance(
        result.output,
        dict,
    )

    assert "drivers" in result.output

    assert "driver_count" in result.output

    drivers = result.output["drivers"]

    assert drivers

    first_driver = drivers[0]

    assert set(first_driver) == {
        "dimension",
        "value",
        "baseline_revenue",
        "comparison_revenue",
        "absolute_change",
        "percentage_change",
        "contribution_to_total_change",
    }


def test_driver_tool_preserves_analytics_ranking() -> None:
    tool = build_tool()

    result = tool.execute(call=build_valid_call())

    assert result.success is True

    drivers = result.output["drivers"]

    absolute_changes = [driver["absolute_change"] for driver in drivers]

    assert absolute_changes == sorted(absolute_changes)


def test_driver_tool_respects_max_drivers() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue_drivers",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "max_drivers": 1,
            },
        )
    )

    assert result.success is True

    assert result.output["driver_count"] == 1

    assert len(result.output["drivers"]) == 1


def test_driver_tool_allows_zero_max_drivers() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue_drivers",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "max_drivers": 0,
            },
        )
    )

    assert result.success is True

    assert result.output == {
        "drivers": [],
        "driver_count": 0,
    }


def test_driver_tool_rejects_negative_max_drivers() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue_drivers",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "max_drivers": -1,
            },
        )
    )

    assert result.success is False

    assert result.error == ("Invalid analyze_revenue_drivers arguments.")


def test_driver_tool_rejects_extra_arguments() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue_drivers",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "unexpected_argument": True,
            },
        )
    )

    assert result.success is False

    assert result.error == ("Invalid analyze_revenue_drivers arguments.")


def test_driver_tool_rejects_invalid_baseline_period() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue_drivers",
            arguments={
                "baseline_start": "2025-07-31",
                "baseline_end": "2025-07-01",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
            },
        )
    )

    assert result.success is False

    assert result.error == ("baseline_start must be before or equal to baseline_end.")


def test_driver_tool_rejects_invalid_comparison_period() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue_drivers",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-31",
                "comparison_end": "2025-08-01",
            },
        )
    )

    assert result.success is False

    assert result.error == (
        "comparison_start must be before or equal to comparison_end."
    )


def test_driver_tool_rejects_empty_orders() -> None:
    tool = DriverAnalysisTool(
        orders=pd.DataFrame(),
        customers=build_customers(),
        products=build_products(),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == "Orders data must not be empty."


def test_driver_tool_rejects_empty_customers() -> None:
    tool = DriverAnalysisTool(
        orders=build_orders(),
        customers=pd.DataFrame(),
        products=build_products(),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == "Customers data must not be empty."


def test_driver_tool_rejects_empty_products() -> None:
    tool = DriverAnalysisTool(
        orders=build_orders(),
        customers=build_customers(),
        products=pd.DataFrame(),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == "Products data must not be empty."


def test_driver_tool_rejects_wrong_tool_name() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="wrong_tool",
        )
    )

    assert result.success is False

    assert result.error is not None

    assert "does not match tool definition" in result.error
