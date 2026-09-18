from app.analytics.engine import analyze_revenue_change
from app.data.loaders import (
    load_customers,
    load_orders,
    load_products,
)


def test_revenue_decline_scenario_matches_expected_direction() -> None:
    result = analyze_revenue_change(
        orders=load_orders(),
        customers=load_customers(),
        products=load_products(),
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    comparison = result.revenue_comparison

    assert comparison.comparison_revenue < comparison.baseline_revenue
    assert comparison.absolute_change < 0
    assert comparison.percentage_change < 0


def test_south_is_strongest_regional_deterioration() -> None:
    result = analyze_revenue_change(
        orders=load_orders(),
        customers=load_customers(),
        products=load_products(),
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    regional_drivers = [
        driver for driver in result.drivers if driver.dimension == "region"
    ]

    assert regional_drivers

    strongest_regional_driver = regional_drivers[0]

    assert strongest_regional_driver.value == "South"
    assert strongest_regional_driver.absolute_change < 0


def test_computing_is_strongest_category_deterioration() -> None:
    result = analyze_revenue_change(
        orders=load_orders(),
        customers=load_customers(),
        products=load_products(),
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    category_drivers = [
        driver for driver in result.drivers if driver.dimension == "category"
    ]

    assert category_drivers

    strongest_category_driver = category_drivers[0]

    assert strongest_category_driver.value == "Computing"
    assert strongest_category_driver.absolute_change < 0


def test_partner_channel_is_present_as_negative_signal() -> None:
    result = analyze_revenue_change(
        orders=load_orders(),
        customers=load_customers(),
        products=load_products(),
        baseline_start="2025-07-01",
        baseline_end="2025-07-31",
        comparison_start="2025-08-01",
        comparison_end="2025-08-31",
    )

    partner_drivers = [
        driver
        for driver in result.drivers
        if driver.dimension == "sales_channel" and driver.value == "Partner"
    ]

    assert len(partner_drivers) == 1
    assert partner_drivers[0].absolute_change < 0
