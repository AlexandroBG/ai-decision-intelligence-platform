from pathlib import Path

import joblib

from app.ml.errors import MLModelArtifactError
from app.ml.training import TrainedAnomalyModel


def save_trained_model(
    trained_model: TrainedAnomalyModel,
    path: str | Path,
) -> Path:
    model_path = Path(path)

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        trained_model,
        model_path,
    )

    return model_path


def load_trained_model(
    path: str | Path,
) -> TrainedAnomalyModel:
    model_path = Path(path)

    if not model_path.exists():
        raise MLModelArtifactError(f"Model artifact does not exist: {model_path}")

    trained_model = joblib.load(model_path)

    if not isinstance(
        trained_model,
        TrainedAnomalyModel,
    ):
        raise MLModelArtifactError("Loaded artifact is not a TrainedAnomalyModel.")

    return trained_model
