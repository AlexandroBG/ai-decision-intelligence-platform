import pandas as pd

from app.analytics.contracts import AnalyticsResult
from app.analytics.dimensions import (
    add_change_contribution,
    add_customer_dimensions,
    add_product_dimensions,
    compare_revenue_by_dimension,
)
from app.analytics.drivers import (
    build_driver_candidates,
    rank_observed_drivers,
)
from app.analytics.errors import (
    EmptyAnalyticsInputError,
    EmptyPeriodError,
)
from app.analytics.revenue import (
    add_net_revenue,
    compare_revenue_periods,
    filter_period,
)


def analyze_revenue_change(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    baseline_start: str,
    baseline_end: str,
    comparison_start: str,
    comparison_end: str,
) -> AnalyticsResult:
    if orders.empty:
        raise EmptyAnalyticsInputError("Orders dataset must not be empty.")

    enriched = add_net_revenue(orders)

    enriched = add_customer_dimensions(
        orders=enriched,
        customers=customers,
    )

    enriched = add_product_dimensions(
        orders=enriched,
        products=products,
    )

    baseline = filter_period(
        dataframe=enriched,
        start_date=baseline_start,
        end_date=baseline_end,
    )

    comparison = filter_period(
        dataframe=enriched,
        start_date=comparison_start,
        end_date=comparison_end,
    )

    if baseline.empty:
        raise EmptyPeriodError("Baseline period contains no orders.")

    if comparison.empty:
        raise EmptyPeriodError("Comparison period contains no orders.")

    revenue_comparison = compare_revenue_periods(
        baseline=baseline,
        comparison=comparison,
    )

    dimensions = [
        "region",
        "segment",
        "category",
        "sales_channel",
    ]

    candidates: list[pd.DataFrame] = []

    for dimension in dimensions:
        dimension_comparison = compare_revenue_by_dimension(
            baseline=baseline,
            comparison=comparison,
            dimension=dimension,
        )

        dimension_with_contribution = add_change_contribution(
            dataframe=dimension_comparison,
            total_change=revenue_comparison.absolute_change,
        )

        dimension_candidates = build_driver_candidates(
            dataframe=dimension_with_contribution,
            dimension=dimension,
        )

        candidates.append(dimension_candidates)

    drivers = rank_observed_drivers(candidates)

    return AnalyticsResult(
        revenue_comparison=revenue_comparison,
        drivers=drivers,
    )
