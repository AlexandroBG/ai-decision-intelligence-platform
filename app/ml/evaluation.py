from dataclasses import dataclass

from app.ml.contracts import MLResult


@dataclass(frozen=True)
class ModelEvaluation:
    total_observations: int
    anomaly_count: int
    anomaly_rate: float
    mean_anomaly_score: float
    max_anomaly_score: float


def evaluate_ml_result(
    result: MLResult,
) -> ModelEvaluation:
    if not result.anomalies:
        raise ValueError("MLResult must contain at least one anomaly observation.")

    total_observations = len(result.anomalies)

    anomaly_count = sum(anomaly.is_anomaly for anomaly in result.anomalies)

    anomaly_rate = anomaly_count / total_observations

    anomaly_scores = [anomaly.anomaly_score for anomaly in result.anomalies]

    mean_anomaly_score = sum(anomaly_scores) / total_observations

    max_anomaly_score = max(anomaly_scores)

    return ModelEvaluation(
        total_observations=total_observations,
        anomaly_count=anomaly_count,
        anomaly_rate=anomaly_rate,
        mean_anomaly_score=mean_anomaly_score,
        max_anomaly_score=max_anomaly_score,
    )
