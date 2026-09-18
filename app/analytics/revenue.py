import pandas as pd

from app.analytics.contracts import RevenueComparison


def add_net_revenue(dataframe: pd.DataFrame) -> pd.DataFrame:
    enriched = dataframe.copy()

    enriched["net_revenue"] = (
        enriched["quantity"] * enriched["unit_price"] * (1 - enriched["discount"])
    )

    return enriched


def calculate_total_revenue(dataframe: pd.DataFrame) -> float:
    return float(dataframe["net_revenue"].sum())


def compare_revenue_periods(
    baseline: pd.DataFrame,
    comparison: pd.DataFrame,
) -> RevenueComparison:
    baseline_revenue = calculate_total_revenue(baseline)
    comparison_revenue = calculate_total_revenue(comparison)

    absolute_change = comparison_revenue - baseline_revenue

    if baseline_revenue == 0:
        percentage_change = 0.0
    else:
        percentage_change = absolute_change / baseline_revenue

    return RevenueComparison(
        baseline_revenue=baseline_revenue,
        comparison_revenue=comparison_revenue,
        absolute_change=absolute_change,
        percentage_change=percentage_change,
    )


def filter_period(
    dataframe: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    mask = (dataframe["order_date"] >= pd.Timestamp(start_date)) & (
        dataframe["order_date"] <= pd.Timestamp(end_date)
    )

    return dataframe.loc[mask].copy()
