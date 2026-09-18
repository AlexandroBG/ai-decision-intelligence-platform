import pandas as pd
import pytest

from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)
from app.ml.errors import MLInputError
from app.ml.inference import score_revenue_anomalies
from app.ml.training import train_revenue_anomaly_model


def build_training_dataframe() -> pd.DataFrame:
    dates = pd.date_range(
        start="2025-07-01",
        periods=12,
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


def build_inference_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "O-IS-001",
                "O-IN-001",
                "O-IS-002",
                "O-IN-002",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-08-01",
                    "2025-08-01",
                    "2025-08-02",
                    "2025-08-02",
                ]
            ),
            "region": [
                "South",
                "North",
                "South",
                "North",
            ],
            "category": [
                "Computing",
                "Office",
                "Computing",
                "Office",
            ],
            "quantity": [
                1,
                3,
                1,
                3,
            ],
            "discount": [
                0.20,
                0.10,
                0.25,
                0.10,
            ],
            "net_revenue": [
                30.0,
                210.0,
                25.0,
                215.0,
            ],
        }
    )


def test_score_revenue_anomalies_returns_ml_result() -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
        contamination=0.08,
        random_state=42,
    )

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_inference_dataframe(),
    )

    assert isinstance(
        result,
        MLResult,
    )


def test_score_revenue_anomalies_returns_evidence() -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
    )

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_inference_dataframe(),
    )

    assert len(result.anomalies) > 0

    assert isinstance(
        result.anomalies[0],
        AnomalyEvidence,
    )


def test_score_revenue_anomalies_preserves_dimensions() -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
    )

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_inference_dataframe(),
    )

    dimensions = {anomaly.dimension for anomaly in result.anomalies}

    assert dimensions == {
        "region",
        "category",
    }


def test_score_revenue_anomalies_produces_boolean_anomaly_flag() -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
        ],
    )

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_inference_dataframe(),
    )

    assert all(
        isinstance(
            anomaly.is_anomaly,
            bool,
        )
        for anomaly in result.anomalies
    )


def test_score_revenue_anomalies_rejects_empty_input() -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=[
            "region",
        ],
    )

    empty_dataframe = build_inference_dataframe().iloc[0:0]

    with pytest.raises(
        MLInputError,
        match="Inference input dataframe must not be empty",
    ):
        score_revenue_anomalies(
            trained_model=trained_model,
            dataframe=empty_dataframe,
        )
