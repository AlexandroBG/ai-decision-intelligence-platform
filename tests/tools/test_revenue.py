import pandas as pd

from app.tools.contracts import ToolCall
from app.tools.revenue import RevenueAnalysisTool


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "o1",
                "o2",
                "o3",
                "o4",
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
        }
    )


def build_valid_call() -> ToolCall:
    return ToolCall(
        tool_name="analyze_revenue",
        arguments={
            "baseline_start": "2025-07-01",
            "baseline_end": "2025-07-31",
            "comparison_start": "2025-08-01",
            "comparison_end": "2025-08-31",
        },
    )


def test_revenue_tool_exposes_definition() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    assert tool.definition.name == "analyze_revenue"


def test_revenue_tool_returns_revenue_comparison() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(call=build_valid_call())

    assert result.success is True

    assert result.output == {
        "baseline_revenue": 400.0,
        "comparison_revenue": 200.0,
        "absolute_change": -200.0,
        "percentage_change": -0.5,
    }


def test_revenue_tool_does_not_modify_original_orders() -> None:
    orders = build_orders()

    original_columns = list(orders.columns)

    tool = RevenueAnalysisTool(orders=orders)

    tool.execute(call=build_valid_call())

    assert list(orders.columns) == original_columns

    assert "net_revenue" not in orders.columns


def test_revenue_tool_rejects_invalid_arguments() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue",
            arguments={
                "baseline_start": "invalid-date",
            },
        )
    )

    assert result.success is False

    assert result.error == "Invalid analyze_revenue arguments."


def test_revenue_tool_rejects_extra_arguments() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue",
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

    assert result.error == "Invalid analyze_revenue arguments."


def test_revenue_tool_rejects_invalid_baseline_period() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue",
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


def test_revenue_tool_rejects_invalid_comparison_period() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue",
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


def test_revenue_tool_rejects_empty_baseline_period() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue",
            arguments={
                "baseline_start": "2024-01-01",
                "baseline_end": "2024-01-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
            },
        )
    )

    assert result.success is False

    assert result.error == "Baseline period contains no orders."


def test_revenue_tool_rejects_empty_comparison_period() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="analyze_revenue",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2024-01-01",
                "comparison_end": "2024-01-31",
            },
        )
    )

    assert result.success is False

    assert result.error == "Comparison period contains no orders."


def test_revenue_tool_rejects_missing_required_columns() -> None:
    orders = build_orders().drop(
        columns=[
            "discount",
            "quantity",
        ]
    )

    tool = RevenueAnalysisTool(orders=orders)

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == (
        "Orders data is missing required columns: discount, quantity."
    )


def test_revenue_tool_rejects_wrong_tool_name() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    result = tool.execute(
        call=ToolCall(
            tool_name="wrong_tool",
            arguments={},
        )
    )

    assert result.success is False

    assert result.error is not None

    assert "does not match tool definition" in result.error
