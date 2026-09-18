import pandas as pd

from app.analytics.contracts import DriverEvidence
from app.analytics.drivers import (
    build_driver_candidates,
    rank_observed_drivers,
)


def test_build_driver_candidates() -> None:
    dataframe = pd.DataFrame(
        {
            "region": ["South"],
            "baseline_revenue": [500.0],
            "comparison_revenue": [200.0],
            "absolute_change": [-300.0],
            "percentage_change": [-0.6],
            "contribution_to_total_change": [0.75],
        }
    )

    result = build_driver_candidates(
        dataframe=dataframe,
        dimension="region",
    )

    assert result.loc[0, "dimension"] == "region"
    assert result.loc[0, "value"] == "South"
    assert result.loc[0, "baseline_revenue"] == 500.0
    assert result.loc[0, "comparison_revenue"] == 200.0
    assert result.loc[0, "absolute_change"] == -300.0
    assert result.loc[0, "percentage_change"] == -0.6
    assert result.loc[0, "contribution_to_total_change"] == 0.75


def test_rank_observed_drivers_orders_largest_decline_first() -> None:
    region = pd.DataFrame(
        {
            "dimension": ["region"],
            "value": ["South"],
            "baseline_revenue": [500.0],
            "comparison_revenue": [200.0],
            "absolute_change": [-300.0],
            "percentage_change": [-0.6],
            "contribution_to_total_change": [0.75],
        }
    )

    category = pd.DataFrame(
        {
            "dimension": ["category"],
            "value": ["Computing"],
            "baseline_revenue": [700.0],
            "comparison_revenue": [250.0],
            "absolute_change": [-450.0],
            "percentage_change": [-0.642857],
            "contribution_to_total_change": [1.125],
        }
    )

    result = rank_observed_drivers(
        [
            region,
            category,
        ]
    )

    assert len(result) == 2

    assert isinstance(result[0], DriverEvidence)
    assert isinstance(result[1], DriverEvidence)

    assert result[0].dimension == "category"
    assert result[0].value == "Computing"
    assert result[0].absolute_change == -450.0

    assert result[1].dimension == "region"
    assert result[1].value == "South"
    assert result[1].absolute_change == -300.0


def test_rank_observed_drivers_excludes_positive_changes() -> None:
    dataframe = pd.DataFrame(
        {
            "dimension": ["region", "region"],
            "value": ["South", "North"],
            "baseline_revenue": [500.0, 200.0],
            "comparison_revenue": [200.0, 250.0],
            "absolute_change": [-300.0, 50.0],
            "percentage_change": [-0.6, 0.25],
            "contribution_to_total_change": [0.75, -0.125],
        }
    )

    result = rank_observed_drivers([dataframe])

    assert len(result) == 1
    assert result[0].value == "South"
    assert result[0].absolute_change == -300.0
