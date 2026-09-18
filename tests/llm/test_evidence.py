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
        result.evidence,
        EvidenceContext,
    )


def test_build_evidence_context_maps_revenue() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert evidence.revenue.absolute_change == -300.0
    assert evidence.revenue.percentage_change == -0.30


def test_build_evidence_context_assigns_revenue_provenance() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert evidence.revenue.evidence_id == ("revenue_summary_1")

    assert evidence.revenue.source == "analytics"

    assert evidence.revenue.evidence_type == "revenue_summary"


def test_build_evidence_context_maps_drivers() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert len(evidence.analytics_drivers) == 3

    assert evidence.analytics_drivers[0].value == "South"


def test_build_evidence_context_assigns_driver_ids() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert [driver.evidence_id for driver in evidence.analytics_drivers] == [
        "analytics_driver_1",
        "analytics_driver_2",
        "analytics_driver_3",
    ]


def test_build_evidence_context_assigns_driver_provenance() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert all(driver.source == "analytics" for driver in evidence.analytics_drivers)

    assert all(
        driver.evidence_type == "driver" for driver in evidence.analytics_drivers
    )


def test_build_evidence_context_excludes_positive_drivers() -> None:
    analytics_result = build_analytics_result()

    analytics_result = AnalyticsResult(
        revenue_comparison=analytics_result.revenue_comparison,
        drivers=[
            *analytics_result.drivers,
            DriverEvidence(
                dimension="region",
                value="North",
                baseline_revenue=100.0,
                comparison_revenue=150.0,
                absolute_change=50.0,
                percentage_change=0.50,
                contribution_to_total_change=-0.17,
            ),
        ],
    )

    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=analytics_result,
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert all(driver.value != "North" for driver in evidence.analytics_drivers)


def test_build_evidence_context_limits_drivers() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=2,
    )

    evidence = result.evidence

    assert len(evidence.analytics_drivers) == 2

    assert [driver.value for driver in evidence.analytics_drivers] == [
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

    evidence = result.evidence

    assert evidence.analytics_drivers == []


def test_build_evidence_context_rejects_negative_driver_limit() -> None:
    with pytest.raises(
        ValueError,
        match="analytics_driver_items",
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

    evidence = result.evidence

    assert all(anomaly.value != "North" for anomaly in evidence.ml_anomalies)


def test_build_evidence_context_orders_anomalies_by_score() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert [anomaly.value for anomaly in evidence.ml_anomalies] == [
        "Computing",
        "Partner",
        "South",
    ]


def test_build_evidence_context_assigns_anomaly_ids() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert [anomaly.evidence_id for anomaly in evidence.ml_anomalies] == [
        "ml_anomaly_1",
        "ml_anomaly_2",
        "ml_anomaly_3",
    ]


def test_build_evidence_context_assigns_anomaly_provenance() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    evidence = result.evidence

    assert all(anomaly.source == "ml" for anomaly in evidence.ml_anomalies)

    assert all(anomaly.evidence_type == "anomaly" for anomaly in evidence.ml_anomalies)


def test_build_evidence_context_limits_ml_anomalies() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_ml_anomalies=2,
    )

    evidence = result.evidence

    assert len(evidence.ml_anomalies) == 2

    assert [anomaly.value for anomaly in evidence.ml_anomalies] == [
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

    evidence = result.evidence

    assert evidence.ml_anomalies == []


def test_build_evidence_context_rejects_negative_ml_limit() -> None:
    with pytest.raises(
        ValueError,
        match="ml_anomaly_items",
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


def test_build_evidence_context_returns_selection_metadata() -> None:
    result = build_evidence_context(
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=2,
        max_ml_anomalies=2,
    )

    assert result.selection_metadata.analytics_drivers_available == 3

    assert result.selection_metadata.analytics_drivers_selected == 2

    assert result.selection_metadata.ml_anomalies_available == 3

    assert result.selection_metadata.ml_anomalies_selected == 2
