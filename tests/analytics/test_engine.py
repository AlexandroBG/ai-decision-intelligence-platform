import pandas as pd
import pytest

from app.analytics.contracts import AnalyticsResult
from app.analytics.engine import analyze_revenue_change
from app.analytics.errors import (
    EmptyAnalyticsInputError,
    EmptyPeriodError,
)


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "O001",
                "O002",
                "O003",
                "O004",
            ],
            "customer_id": [
                "C001",
                "C002",
                "C001",
                "C002",
            ],
            "product_id": [
                "P001",
                "P002",
                "P001",
                "P002",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-01",
                    "2025-07-02",
                    "2025-08-01",
                    "2025-08-02",
                ]
            ),
            "quantity": [
                1,
                1,
                1,
                1,
            ],
            "unit_price": [
                500.0,
                300.0,
                200.0,
                270.0,
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
                "C001",
                "C002",
            ],
            "segment": [
                "SMB",
                "Enterprise",
            ],
            "region": [
                "South",
                "North",
            ],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": [
                "P001",
                "P002",
            ],
            "category": [
                "Computing",
                "Office",
            ],
        }
    )


def test_analyze_revenue_change_returns_structured_result() -> None:
    result = analyze_revenue_change(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    assert isinstance(result, AnalyticsResult)

    assert result.revenue_comparison.baseline_revenue == 800.0
    assert result.revenue_comparison.comparison_revenue == 470.0
    assert result.revenue_comparison.absolute_change == -330.0

    assert len(result.drivers) > 0

    first_driver = result.drivers[0]

    assert first_driver.absolute_change < 0


def test_analyze_revenue_change_rejects_empty_orders() -> None:
    empty_orders = build_orders().iloc[0:0]

    with pytest.raises(
        EmptyAnalyticsInputError,
        match="Orders dataset must not be empty",
    ):
        analyze_revenue_change(
            orders=empty_orders,
            customers=build_customers(),
            products=build_products(),
            baseline_start="2025-07-01",
            baseline_end="2025-07-31",
            comparison_start="2025-08-01",
            comparison_end="2025-08-31",
        )


def test_analyze_revenue_change_rejects_empty_baseline_period() -> None:
    with pytest.raises(
        EmptyPeriodError,
        match="Baseline period contains no orders",
    ):
        analyze_revenue_change(
            orders=build_orders(),
            customers=build_customers(),
            products=build_products(),
            baseline_start="2025-06-01",
            baseline_end="2025-06-30",
            comparison_start="2025-08-01",
            comparison_end="2025-08-31",
        )


def test_analyze_revenue_change_rejects_empty_comparison_period() -> None:
    with pytest.raises(
        EmptyPeriodError,
        match="Comparison period contains no orders",
    ):
        analyze_revenue_change(
            orders=build_orders(),
            customers=build_customers(),
            products=build_products(),
            baseline_start="2025-07-01",
            baseline_end="2025-07-31",
            comparison_start="2025-09-01",
            comparison_end="2025-09-30",
        )
