from app.analytics.contracts import AnalyticsResult
from app.analytics.engine import analyze_revenue_change
from app.data.loaders import (
    load_customers,
    load_orders,
    load_products,
)


def test_real_dataset_analytics_pipeline() -> None:
    orders = load_orders()
    customers = load_customers()
    products = load_products()

    result = analyze_revenue_change(
        orders=orders,
        customers=customers,
        products=products,
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    assert isinstance(result, AnalyticsResult)

    comparison = result.revenue_comparison

    assert comparison.baseline_revenue > 0
    assert comparison.comparison_revenue > 0

    assert comparison.comparison_revenue < comparison.baseline_revenue
    assert comparison.absolute_change < 0
    assert comparison.percentage_change < 0

    assert len(result.drivers) > 0

    dimensions = {driver.dimension for driver in result.drivers}

    assert "region" in dimensions
    assert "segment" in dimensions
    assert "category" in dimensions
    assert "sales_channel" in dimensions


def test_real_dataset_contains_expected_major_driver_signals() -> None:
    result = analyze_revenue_change(
        orders=load_orders(),
        customers=load_customers(),
        products=load_products(),
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    driver_pairs = {
        (
            driver.dimension,
            driver.value,
        )
        for driver in result.drivers
    }

    assert ("region", "South") in driver_pairs
    assert ("category", "Computing") in driver_pairs
    assert ("sales_channel", "Partner") in driver_pairs
