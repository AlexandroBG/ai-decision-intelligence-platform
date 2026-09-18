import pytest

from app.analytics.contracts import (
    AnalyticsResult,
    DriverEvidence,
    RevenueComparison,
)
from app.llm.contracts import EvidenceContext
from app.llm.evidence import build_evidence_context
from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)


def build_analytics_result() -> AnalyticsResult:
    return AnalyticsResult(
        revenue_comparison=RevenueComparison(
            baseline_revenue=1000.0,
            comparison_revenue=700.0,
            absolute_change=-300.0,
            percentage_change=-0.30,
        ),
        drivers=[
            DriverEvidence(
                dimension="region",
                value="South",
                baseline_revenue=500.0,
                comparison_revenue=250.0,
                absolute_change=-250.0,
                percentage_change=-0.50,
                contribution_to_total_change=0.83,
            ),
            DriverEvidence(
                dimension="category",
                value="Computing",
                baseline_revenue=300.0,
                comparison_revenue=180.0,
                absolute_change=-120.0,
                percentage_change=-0.40,
                contribution_to_total_change=0.40,
            ),
            DriverEvidence(
                dimension="sales_channel",
                value="Partner",
                baseline_revenue=200.0,
                comparison_revenue=150.0,
                absolute_change=-50.0,
                percentage_change=-0.25,
                contribution_to_total_change=0.17,
            ),
        ],
    )


def build_ml_result() -> MLResult:
    return MLResult(
        anomalies=[
            AnomalyEvidence(
                date="2025-08-10",
                dimension="region",
                value="South",
                daily_revenue=50.0,
                anomaly_score=0.12,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-11",
                dimension="region",
                value="North",
                daily_revenue=120.0,
                anomaly_score=-0.02,
                is_anomaly=False,
            ),
            AnomalyEvidence(
                date="2025-08-12",
                dimension="category",
                value="Computing",
                daily_revenue=40.0,
                anomaly_score=0.20,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-13",
                dimension="sales_channel",
                value="Partner",
                daily_revenue=60.0,
                anomaly_score=0.15,
                is_anomaly=True,
            ),
        ]
    )


def test_build_evidence_context_returns_contract() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert isinstance(
        result,
        EvidenceContext,
    )


def test_build_evidence_context_maps_revenue() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert result.revenue.absolute_change == -300.0
    assert result.revenue.percentage_change == -0.30


def test_build_evidence_context_maps_drivers() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert len(result.analytics_drivers) == 3

    assert result.analytics_drivers[0].value == "South"


def test_build_evidence_context_limits_drivers() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=2,
    )

    assert len(result.analytics_drivers) == 2

    assert [driver.value for driver in result.analytics_drivers] == [
        "South",
        "Computing",
    ]


def test_build_evidence_context_allows_zero_drivers() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=0,
    )

    assert result.analytics_drivers == []


def test_build_evidence_context_rejects_negative_driver_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_analytics_drivers",
    ):
        build_evidence_context(
            question="Why did revenue decline?",
            analytics_result=build_analytics_result(),
            ml_result=build_ml_result(),
            max_analytics_drivers=-1,
        )


def test_build_evidence_context_keeps_only_anomalies() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert all(anomaly.value != "North" for anomaly in result.ml_anomalies)


def test_build_evidence_context_orders_anomalies_by_score() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert [anomaly.value for anomaly in result.ml_anomalies] == [
        "Computing",
        "Partner",
        "South",
    ]


def test_build_evidence_context_limits_ml_anomalies() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_ml_anomalies=2,
    )

    assert len(result.ml_anomalies) == 2

    assert [anomaly.value for anomaly in result.ml_anomalies] == [
        "Computing",
        "Partner",
    ]


def test_build_evidence_context_allows_zero_ml_anomalies() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_ml_anomalies=0,
    )

    assert result.ml_anomalies == []


def test_build_evidence_context_rejects_negative_ml_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_ml_anomalies",
    ):
        build_evidence_context(
            question="Why did revenue decline?",
            analytics_result=build_analytics_result(),
            ml_result=build_ml_result(),
            max_ml_anomalies=-1,
        )


def test_build_evidence_context_rejects_empty_question() -> None:
    with pytest.raises(
        ValueError,
        match="Question must not be empty",
    ):
        build_evidence_context(
            question="",
            analytics_result=build_analytics_result(),
            ml_result=build_ml_result(),
        )
