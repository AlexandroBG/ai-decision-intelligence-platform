import pandas as pd

from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)
from app.ml.errors import (
    MLInferenceError,
    MLInputError,
)
from app.ml.features import (
    build_daily_revenue_features_for_dimensions,
)
from app.ml.model import score_isolation_forest
from app.ml.training import TrainedAnomalyModel


def score_revenue_anomalies(
    trained_model: TrainedAnomalyModel,
    dataframe: pd.DataFrame,
) -> MLResult:
    if dataframe.empty:
        raise MLInputError("Inference input dataframe must not be empty.")

    features = build_daily_revenue_features_for_dimensions(
        dataframe=dataframe,
        dimensions=trained_model.dimensions,
    )

    if features.empty:
        raise MLInferenceError(
            "Feature generation produced an empty dataframe during inference."
        )

    evidence: list[AnomalyEvidence] = []

    grouped = features.groupby(
        [
            "dimension",
            "value",
        ],
        sort=True,
    )

    for (dimension, value), group in grouped:
        key = (
            str(dimension),
            str(value),
        )

        model = trained_model.models.get(key)

        if model is None:
            continue

        scored = score_isolation_forest(
            model=model,
            dataframe=group,
        )

        evidence.extend(
            AnomalyEvidence(
                date=row.date.strftime("%Y-%m-%d"),
                dimension=str(row.dimension),
                value=str(row.value),
                daily_revenue=float(row.daily_revenue),
                anomaly_score=float(row.anomaly_score),
                is_anomaly=bool(row.is_anomaly),
            )
            for row in scored.itertuples(index=False)
        )

    if not evidence:
        raise MLInferenceError(
            "No inference observations matched trained anomaly models."
        )

    return MLResult(
        anomalies=evidence,
    )
