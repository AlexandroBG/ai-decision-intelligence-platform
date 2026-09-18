import pandas as pd
import pytest

from app.ml.comparison import (
    DetectionComparison,
    compare_baseline_and_ml,
)
from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)


def build_baseline_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2025-08-01",
                    "2025-08-02",
                    "2025-08-03",
                    "2025-08-04",
                ]
            ),
            "dimension": [
                "region",
                "region",
                "region",
                "region",
            ],
            "value": [
                "South",
                "South",
                "North",
                "North",
            ],
            "daily_revenue": [
                100.0,
                50.0,
                200.0,
                80.0,
            ],
            "is_anomaly": [
                False,
                True,
                False,
                True,
            ],
        }
    )


def build_ml_result() -> MLResult:
    return MLResult(
        anomalies=[
            AnomalyEvidence(
                date="2025-08-01",
                dimension="region",
                value="South",
                daily_revenue=100.0,
                anomaly_score=0.05,
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
                anomaly_score=0.10,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-04",
                dimension="region",
                value="North",
                daily_revenue=80.0,
                anomaly_score=0.35,
                is_anomaly=True,
            ),
        ]
    )


def test_compare_baseline_and_ml_returns_contract() -> None:
    result = compare_baseline_and_ml(
        baseline_results=build_baseline_results(),
        ml_result=build_ml_result(),
    )

    assert isinstance(
        result,
        DetectionComparison,
    )


def test_compare_baseline_and_ml_counts_observations() -> None:
    result = compare_baseline_and_ml(
        baseline_results=build_baseline_results(),
        ml_result=build_ml_result(),
    )

    assert result.total_observations == 4


def test_compare_baseline_and_ml_counts_anomalies() -> None:
    result = compare_baseline_and_ml(
        baseline_results=build_baseline_results(),
        ml_result=build_ml_result(),
    )

    assert result.baseline_anomaly_count == 2
    assert result.ml_anomaly_count == 3


def test_compare_baseline_and_ml_calculates_agreement() -> None:
    result = compare_baseline_and_ml(
        baseline_results=build_baseline_results(),
        ml_result=build_ml_result(),
    )

    assert result.agreement_count == 3
    assert result.disagreement_count == 1
    assert result.agreement_rate == 0.75


def test_compare_baseline_and_ml_rejects_empty_baseline() -> None:
    baseline = build_baseline_results().iloc[0:0]

    with pytest.raises(
        ValueError,
        match="Baseline results must not be empty",
    ):
        compare_baseline_and_ml(
            baseline_results=baseline,
            ml_result=build_ml_result(),
        )


def test_compare_baseline_and_ml_rejects_empty_ml_result() -> None:
    with pytest.raises(
        ValueError,
        match="MLResult must contain anomaly observations",
    ):
        compare_baseline_and_ml(
            baseline_results=build_baseline_results(),
            ml_result=MLResult(
                anomalies=[],
            ),
        )
