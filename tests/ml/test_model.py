import pandas as pd
import pytest
from sklearn.ensemble import IsolationForest

from app.ml.errors import MLInputError
from app.ml.features import FEATURE_COLUMNS
from app.ml.model import (
    score_isolation_forest,
    train_isolation_forest,
)


def build_training_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "daily_revenue": [
                100.0,
                102.0,
                98.0,
                101.0,
                99.0,
                103.0,
                97.0,
                100.0,
                101.0,
                99.0,
                300.0,
            ],
            "order_count": [
                10,
                10,
                9,
                10,
                10,
                11,
                9,
                10,
                10,
                10,
                3,
            ],
            "units_sold": [
                20,
                21,
                19,
                20,
                20,
                22,
                18,
                20,
                21,
                20,
                5,
            ],
            "average_order_value": [
                10.0,
                10.2,
                10.89,
                10.1,
                9.9,
                9.36,
                10.78,
                10.0,
                10.1,
                9.9,
                100.0,
            ],
            "average_discount": [
                0.05,
                0.05,
                0.06,
                0.05,
                0.04,
                0.05,
                0.06,
                0.05,
                0.05,
                0.04,
                0.30,
            ],
        }
    )


def test_training_dataframe_contains_model_features() -> None:
    dataframe = build_training_dataframe()

    assert all(column in dataframe.columns for column in FEATURE_COLUMNS)


def test_train_isolation_forest_returns_model() -> None:
    model = train_isolation_forest(
        dataframe=build_training_dataframe(),
        contamination=0.08,
        random_state=42,
    )

    assert isinstance(
        model,
        IsolationForest,
    )


def test_score_isolation_forest_adds_expected_columns() -> None:
    dataframe = build_training_dataframe()

    model = train_isolation_forest(
        dataframe=dataframe,
        contamination=0.08,
        random_state=42,
    )

    result = score_isolation_forest(
        model=model,
        dataframe=dataframe,
    )

    assert "anomaly_score" in result.columns
    assert "is_anomaly" in result.columns


def test_score_isolation_forest_marks_at_least_one_anomaly() -> None:
    dataframe = build_training_dataframe()

    model = train_isolation_forest(
        dataframe=dataframe,
        contamination=0.08,
        random_state=42,
    )

    result = score_isolation_forest(
        model=model,
        dataframe=dataframe,
    )

    assert result["is_anomaly"].any()


def test_obvious_outlier_has_high_anomaly_score() -> None:
    dataframe = build_training_dataframe()

    model = train_isolation_forest(
        dataframe=dataframe,
        contamination=0.08,
        random_state=42,
    )

    result = score_isolation_forest(
        model=model,
        dataframe=dataframe,
    )

    outlier_score = result.iloc[-1]["anomaly_score"]

    typical_score = result.iloc[0]["anomaly_score"]

    assert outlier_score > typical_score


def test_train_rejects_empty_dataframe() -> None:
    dataframe = pd.DataFrame(columns=FEATURE_COLUMNS)

    with pytest.raises(
        MLInputError,
        match="Training dataframe must not be empty",
    ):
        train_isolation_forest(dataframe=dataframe)


def test_train_rejects_invalid_contamination() -> None:
    with pytest.raises(
        MLInputError,
        match="contamination must be greater than 0",
    ):
        train_isolation_forest(
            dataframe=build_training_dataframe(),
            contamination=0.0,
        )
