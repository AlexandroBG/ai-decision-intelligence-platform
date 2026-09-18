import pytest

from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)
from app.ml.evaluation import (
    ModelEvaluation,
    evaluate_ml_result,
)


def build_ml_result() -> MLResult:
    return MLResult(
        anomalies=[
            AnomalyEvidence(
                date="2025-08-01",
                dimension="region",
                value="South",
                daily_revenue=100.0,
                anomaly_score=0.10,
                is_anomaly=False,
            ),
            AnomalyEvidence(
                date="2025-08-02",
                dimension="region",
                value="South",
                daily_revenue=50.0,
                anomaly_score=0.40,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-03",
                dimension="region",
                value="North",
                daily_revenue=200.0,
                anomaly_score=0.05,
                is_anomaly=False,
            ),
            AnomalyEvidence(
                date="2025-08-04",
                dimension="region",
                value="North",
                daily_revenue=80.0,
                anomaly_score=0.30,
                is_anomaly=True,
            ),
        ]
    )


def test_evaluate_ml_result_returns_contract() -> None:
    evaluation = evaluate_ml_result(
        result=build_ml_result(),
    )

    assert isinstance(
        evaluation,
        ModelEvaluation,
    )


def test_evaluate_ml_result_counts_observations() -> None:
    evaluation = evaluate_ml_result(
        result=build_ml_result(),
    )

    assert evaluation.total_observations == 4


def test_evaluate_ml_result_counts_anomalies() -> None:
    evaluation = evaluate_ml_result(
        result=build_ml_result(),
    )

    assert evaluation.anomaly_count == 2


def test_evaluate_ml_result_calculates_anomaly_rate() -> None:
    evaluation = evaluate_ml_result(
        result=build_ml_result(),
    )

    assert evaluation.anomaly_rate == 0.5


def test_evaluate_ml_result_calculates_mean_score() -> None:
    evaluation = evaluate_ml_result(
        result=build_ml_result(),
    )

    assert evaluation.mean_anomaly_score == pytest.approx(0.2125)


def test_evaluate_ml_result_calculates_max_score() -> None:
    evaluation = evaluate_ml_result(
        result=build_ml_result(),
    )

    assert evaluation.max_anomaly_score == 0.40


def test_evaluate_ml_result_rejects_empty_result() -> None:
    result = MLResult(
        anomalies=[],
    )

    with pytest.raises(
        ValueError,
        match="MLResult must contain at least one anomaly observation",
    ):
        evaluate_ml_result(
            result=result,
        )
