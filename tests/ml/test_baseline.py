import pandas as pd
import pytest

from app.ml.baseline import add_statistical_anomaly_scores


def build_stable_series() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range(
                start="2025-07-01",
                periods=8,
                freq="D",
            ),
            "dimension": ["region"] * 8,
            "value": ["South"] * 8,
            "daily_revenue": [
                100.0,
                102.0,
                98.0,
                101.0,
                99.0,
                100.0,
                103.0,
                50.0,
            ],
        }
    )


def test_statistical_baseline_adds_expected_columns() -> None:
    result = add_statistical_anomaly_scores(
        dataframe=build_stable_series(),
        window=5,
        min_periods=3,
        threshold=2.0,
    )

    assert "expected_revenue" in result.columns
    assert "historical_std" in result.columns
    assert "z_score" in result.columns
    assert "is_anomaly" in result.columns


def test_statistical_baseline_detects_large_revenue_drop() -> None:
    result = add_statistical_anomaly_scores(
        dataframe=build_stable_series(),
        window=5,
        min_periods=3,
        threshold=2.0,
    )

    last_row = result.iloc[-1]

    assert last_row["daily_revenue"] == 50.0
    assert last_row["z_score"] < -2.0
    assert bool(last_row["is_anomaly"]) is True


def test_statistical_baseline_does_not_use_current_value_in_history() -> None:
    dataframe = pd.DataFrame(
        {
            "date": pd.date_range(
                start="2025-07-01",
                periods=4,
                freq="D",
            ),
            "dimension": ["region"] * 4,
            "value": ["South"] * 4,
            "daily_revenue": [
                100.0,
                100.0,
                100.0,
                1000.0,
            ],
        }
    )

    result = add_statistical_anomaly_scores(
        dataframe=dataframe,
        window=3,
        min_periods=3,
        threshold=2.0,
    )

    last_row = result.iloc[-1]

    assert last_row["expected_revenue"] == 100.0


def test_statistical_baseline_preserves_independent_groups() -> None:
    dataframe = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2025-07-01",
                    "2025-07-02",
                    "2025-07-03",
                    "2025-07-04",
                    "2025-07-01",
                    "2025-07-02",
                    "2025-07-03",
                    "2025-07-04",
                ]
            ),
            "dimension": ["region"] * 8,
            "value": [
                "South",
                "South",
                "South",
                "South",
                "North",
                "North",
                "North",
                "North",
            ],
            "daily_revenue": [
                100.0,
                100.0,
                100.0,
                50.0,
                500.0,
                500.0,
                500.0,
                500.0,
            ],
        }
    )

    result = add_statistical_anomaly_scores(
        dataframe=dataframe,
        window=3,
        min_periods=3,
        threshold=2.0,
    )

    south_last = result[result["value"] == "South"].iloc[-1]

    north_last = result[result["value"] == "North"].iloc[-1]

    assert south_last["expected_revenue"] == 100.0
    assert north_last["expected_revenue"] == 500.0


def test_statistical_baseline_rejects_invalid_window() -> None:
    with pytest.raises(
        ValueError,
        match="Window must be greater than zero",
    ):
        add_statistical_anomaly_scores(
            dataframe=build_stable_series(),
            window=0,
        )


def test_statistical_baseline_rejects_min_periods_greater_than_window() -> None:
    with pytest.raises(
        ValueError,
        match="min_periods must be less than or equal to window",
    ):
        add_statistical_anomaly_scores(
            dataframe=build_stable_series(),
            window=3,
            min_periods=5,
        )


def test_statistical_baseline_rejects_invalid_threshold() -> None:
    with pytest.raises(
        ValueError,
        match="Threshold must be greater than zero",
    ):
        add_statistical_anomaly_scores(
            dataframe=build_stable_series(),
            threshold=0.0,
        )
