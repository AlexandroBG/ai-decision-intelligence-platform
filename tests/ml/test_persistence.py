import pandas as pd
import pytest

from app.ml.errors import MLModelArtifactError
from app.ml.persistence import (
    load_trained_model,
    save_trained_model,
)
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
                "quantity": 3,
                "discount": 0.10,
                "net_revenue": 200.0 + index,
            }
        )

    return pd.DataFrame(rows)


def test_save_and_load_trained_model(
    tmp_path,
) -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=["region"],
        contamination=0.08,
        random_state=42,
    )

    model_path = tmp_path / "anomaly_model.joblib"

    saved_path = save_trained_model(
        trained_model=trained_model,
        path=model_path,
    )

    loaded_model = load_trained_model(
        path=saved_path,
    )

    assert isinstance(
        loaded_model,
        TrainedAnomalyModel,
    )

    assert loaded_model.dimensions == [
        "region",
    ]

    assert loaded_model.contamination == 0.08
    assert loaded_model.random_state == 42

    assert set(loaded_model.models) == set(trained_model.models)


def test_save_trained_model_creates_parent_directory(
    tmp_path,
) -> None:
    trained_model = train_revenue_anomaly_model(
        dataframe=build_training_dataframe(),
        dimensions=["region"],
    )

    model_path = tmp_path / "models" / "anomaly_model.joblib"

    saved_path = save_trained_model(
        trained_model=trained_model,
        path=model_path,
    )

    assert saved_path.exists()


def test_load_trained_model_rejects_missing_file(
    tmp_path,
) -> None:
    model_path = tmp_path / "missing.joblib"

    with pytest.raises(
        MLModelArtifactError,
        match="Model artifact does not exist",
    ):
        load_trained_model(
            path=model_path,
        )
