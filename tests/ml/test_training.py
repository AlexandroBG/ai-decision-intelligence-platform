import pandas as pd
import pytest
from sklearn.ensemble import IsolationForest

from app.ml.errors import MLInputError
from app.ml.features import FEATURE_COLUMNS
from app.ml.training import (
    TrainedAnomalyModel,
    train_revenue_anomaly_model,
)


def build_training_dataframe() -> pd.DataFrame:
    dates = pd.date_range(
        start="2025-07-01",
        periods=10,
        freq="D",
    )

    rows = []

    for index, date in enumerate(dates):
        rows.append(
            {
                "order_id": f"O-S-{index}",
                "order_date": date,
                "region": "South",
                "category": "Computing",
                "quantity": 2,
                "discount": 0.05,
                "net_revenue": 100.0 + index,
            }
        )

        rows.append(
            {
                "order_id": f"O-N-{index}",
                "order_date": date,
                "region": "North",
                "category": "Office",
                "quantity": 3,
                "discount": 0.10,
                "net_revenue": 200.0 + index,
            }
        )

    return pd.DataFrame(rows)


def test_train_revenue_anomaly_model_returns_contract() -> None:
    result = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
        contamination=0.08,
        random_state=42,
    )

    assert isinstance(
        result,
        TrainedAnomalyModel,
    )

    assert result.models


def test_train_revenue_anomaly_model_trains_models_per_series() -> None:
    result = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
    )

    expected_keys = {
        ("region", "South"),
        ("region", "North"),
        ("category", "Computing"),
        ("category", "Office"),
    }

    assert set(result.models) == expected_keys

    assert all(isinstance(model, IsolationForest) for model in result.models.values())


def test_train_revenue_anomaly_model_builds_features() -> None:
    result = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
    )

    assert not result.features.empty

    assert result.features.columns.tolist() == [
        "date",
        "dimension",
        "value",
        *FEATURE_COLUMNS,
    ]


def test_train_revenue_anomaly_model_preserves_dimensions() -> None:
    dimensions = [
        "region",
        "category",
    ]

    result = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=dimensions,
    )

    assert result.dimensions == dimensions


def test_train_revenue_anomaly_model_copies_dimensions() -> None:
    dimensions = [
        "region",
    ]

    result = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=dimensions,
    )

    dimensions.append("category")

    assert result.dimensions == [
        "region",
    ]


def test_train_revenue_anomaly_model_rejects_empty_input() -> None:
    dataframe = build_training_dataframe().iloc[0:0]

    with pytest.raises(
        MLInputError,
        match="Training input dataframe must not be empty",
    ):
        train_revenue_anomaly_model(
            dataframe=dataframe,
            dimensions=["region"],
        )


def test_train_revenue_anomaly_model_rejects_empty_dimensions() -> None:
    with pytest.raises(
        MLInputError,
        match="At least one dimension is required",
    ):
        train_revenue_anomaly_model(
            dataframe=build_training_dataframe(),
            dimensions=[],
        )
