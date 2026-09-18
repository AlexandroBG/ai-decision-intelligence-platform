import pytest

from app.llm.contracts import (
    EvidenceAnomaly,
    EvidenceContext,
    EvidenceDriver,
    EvidenceRevenue,
)
from app.llm.registry import (
    EvidenceRegistryError,
    build_evidence_registry,
    resolve_evidence,
)


def build_evidence_context() -> EvidenceContext:
    return EvidenceContext(
        question="Why did revenue decline?",
        revenue=EvidenceRevenue(
            evidence_id="revenue_summary_1",
            source="analytics",
            evidence_type="revenue_summary",
            baseline_revenue=1000.0,
            comparison_revenue=700.0,
            absolute_change=-300.0,
            percentage_change=-0.30,
        ),
        analytics_drivers=[
            EvidenceDriver(
                evidence_id="analytics_driver_1",
                source="analytics",
                evidence_type="driver",
                dimension="region",
                value="South",
                absolute_change=-250.0,
                percentage_change=-0.50,
                contribution_to_total_change=0.83,
            ),
        ],
        ml_anomalies=[
            EvidenceAnomaly(
                evidence_id="ml_anomaly_1",
                source="ml",
                evidence_type="anomaly",
                date="2025-08-10",
                dimension="region",
                value="South",
                daily_revenue=50.0,
                anomaly_score=0.12,
            ),
        ],
    )


def test_build_evidence_registry_contains_all_evidence() -> None:
    evidence = build_evidence_context()

    registry = build_evidence_registry(
        evidence=evidence,
    )

    assert set(registry.keys()) == {
        "revenue_summary_1",
        "analytics_driver_1",
        "ml_anomaly_1",
    }


def test_build_evidence_registry_preserves_revenue_evidence() -> None:
    evidence = build_evidence_context()

    registry = build_evidence_registry(
        evidence=evidence,
    )

    revenue = registry["revenue_summary_1"]

    assert revenue.source == "analytics"
    assert revenue.evidence_type == "revenue_summary"


def test_resolve_evidence_returns_driver() -> None:
    evidence = build_evidence_context()

    registry = build_evidence_registry(
        evidence=evidence,
    )

    result = resolve_evidence(
        registry=registry,
        evidence_id="analytics_driver_1",
    )

    assert isinstance(
        result,
        EvidenceDriver,
    )

    assert result.dimension == "region"
    assert result.value == "South"


def test_resolve_evidence_returns_anomaly() -> None:
    evidence = build_evidence_context()

    registry = build_evidence_registry(
        evidence=evidence,
    )

    result = resolve_evidence(
        registry=registry,
        evidence_id="ml_anomaly_1",
    )

    assert isinstance(
        result,
        EvidenceAnomaly,
    )

    assert result.source == "ml"
    assert result.value == "South"


def test_resolve_evidence_rejects_unknown_id() -> None:
    evidence = build_evidence_context()

    registry = build_evidence_registry(
        evidence=evidence,
    )

    with pytest.raises(
        EvidenceRegistryError,
        match="Unknown evidence_id",
    ):
        resolve_evidence(
            registry=registry,
            evidence_id="analytics_driver_999",
        )


def test_build_evidence_registry_rejects_duplicate_ids() -> None:
    evidence = EvidenceContext(
        question="Why did revenue decline?",
        revenue=EvidenceRevenue(
            evidence_id="duplicate_id",
            source="analytics",
            evidence_type="revenue_summary",
            baseline_revenue=1000.0,
            comparison_revenue=700.0,
            absolute_change=-300.0,
            percentage_change=-0.30,
        ),
        analytics_drivers=[
            EvidenceDriver(
                evidence_id="duplicate_id",
                source="analytics",
                evidence_type="driver",
                dimension="region",
                value="South",
                absolute_change=-250.0,
                percentage_change=-0.50,
                contribution_to_total_change=0.83,
            ),
        ],
    )

    with pytest.raises(
        EvidenceRegistryError,
        match="Duplicate evidence_id",
    ):
        build_evidence_registry(
            evidence=evidence,
        )
