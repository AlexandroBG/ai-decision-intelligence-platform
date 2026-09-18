from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import IsolationForest

from app.ml.errors import (
    MLInputError,
    MLTrainingError,
)
from app.ml.features import build_daily_revenue_features_for_dimensions
from app.ml.model import train_isolation_forest

ModelKey = tuple[str, str]


@dataclass(frozen=True)
class TrainedAnomalyModel:
    models: dict[ModelKey, IsolationForest]
    features: pd.DataFrame
    dimensions: list[str]
    contamination: float
    random_state: int


def train_revenue_anomaly_model(
    dataframe: pd.DataFrame,
    dimensions: list[str],
    contamination: float = 0.08,
    random_state: int = 42,
) -> TrainedAnomalyModel:
    if dataframe.empty:
        raise MLInputError("Training input dataframe must not be empty.")

    if not dimensions:
        raise MLInputError("At least one dimension is required for training.")

    features = build_daily_revenue_features_for_dimensions(
        dataframe=dataframe,
        dimensions=dimensions,
    )

    if features.empty:
        raise MLTrainingError("Feature generation produced an empty dataframe.")

    models: dict[ModelKey, IsolationForest] = {}

    grouped = features.groupby(
        [
            "dimension",
            "value",
        ],
        sort=True,
    )

    for (dimension, value), group in grouped:
        if len(group) < 2:
            continue

        model = train_isolation_forest(
            dataframe=group,
            contamination=contamination,
            random_state=random_state,
        )

        key = (
            str(dimension),
            str(value),
        )

        models[key] = model

    if not models:
        raise MLTrainingError(
            "No anomaly models could be trained from the generated features."
        )

    return TrainedAnomalyModel(
        models=models,
        features=features,
        dimensions=dimensions.copy(),
        contamination=contamination,
        random_state=random_state,
    )
