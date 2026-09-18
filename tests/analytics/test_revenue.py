import pandas as pd

from app.analytics.revenue import (
    add_net_revenue,
    calculate_total_revenue,
    compare_revenue_periods,
    filter_period,
)


def test_add_net_revenue_calculates_expected_value() -> None:
    dataframe = pd.DataFrame(
        {
            "quantity": [2],
            "unit_price": [100.0],
            "discount": [0.10],
        }
    )

    result = add_net_revenue(dataframe)

    assert result.loc[0, "net_revenue"] == 180.0


def test_add_net_revenue_does_not_modify_original() -> None:
    dataframe = pd.DataFrame(
        {
            "quantity": [2],
            "unit_price": [100.0],
            "discount": [0.10],
        }
    )

    add_net_revenue(dataframe)

    assert "net_revenue" not in dataframe.columns


def test_calculate_total_revenue_sums_net_revenue() -> None:
    dataframe = pd.DataFrame(
        {
            "net_revenue": [180.0, 50.0, 70.0],
        }
    )

    result = calculate_total_revenue(dataframe)

    assert result == 300.0


def test_compare_revenue_periods_calculates_change() -> None:
    baseline = pd.DataFrame(
        {
            "net_revenue": [600.0, 400.0],
        }
    )

    comparison = pd.DataFrame(
        {
            "net_revenue": [500.0, 300.0],
        }
    )

    result = compare_revenue_periods(
        baseline=baseline,
        comparison=comparison,
    )

    assert result.baseline_revenue == 1000.0
    assert result.comparison_revenue == 800.0
    assert result.absolute_change == -200.0
    assert result.percentage_change == -0.2


def test_compare_revenue_periods_handles_zero_baseline() -> None:
    baseline = pd.DataFrame(
        {
            "net_revenue": [0.0],
        }
    )

    comparison = pd.DataFrame(
        {
            "net_revenue": [100.0],
        }
    )

    result = compare_revenue_periods(
        baseline=baseline,
        comparison=comparison,
    )

    assert result.baseline_revenue == 0.0
    assert result.comparison_revenue == 100.0
    assert result.absolute_change == 100.0
    assert result.percentage_change == 0.0


def test_filter_period_returns_expected_rows() -> None:
    dataframe = pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                [
                    "2025-07-01",
                    "2025-07-15",
                    "2025-08-01",
                ]
            ),
            "net_revenue": [100.0, 200.0, 300.0],
        }
    )

    result = filter_period(
        dataframe=dataframe,
        start_date="2025-07-01",
        end_date="2025-07-31",
    )

    assert len(result) == 2
    assert result["net_revenue"].sum() == 300.0
