from app.llm.contracts import (
    EvidenceAnomaly,
    EvidenceContext,
    EvidenceDriver,
    EvidenceRevenue,
    GroundedClaim,
    LLMInterpretation,
)
from app.llm.resolution import resolve_grounded_claims


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
            )
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
            )
        ],
    )


def test_resolve_grounded_claims_resolves_revenue_evidence() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined by 30%.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            )
        ],
    )

    result = resolve_grounded_claims(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )

    assert len(result) == 1

    assert result[0].statement == ("Revenue declined by 30%.")

    assert len(result[0].evidence) == 1

    assert result[0].evidence[0].evidence_id == "revenue_summary_1"


def test_resolve_grounded_claims_resolves_multiple_evidence_items() -> None:
    interpretation = LLMInterpretation(
        summary="South deserves investigation.",
        grounded_claims=[
            GroundedClaim(
                claim_type="inference",
                statement="South is worth investigating.",
                evidence_ids=[
                    "analytics_driver_1",
                    "ml_anomaly_1",
                ],
            )
        ],
    )

    result = resolve_grounded_claims(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )

    assert len(result) == 1

    assert [item.evidence_id for item in result[0].evidence] == [
        "analytics_driver_1",
        "ml_anomaly_1",
    ]


def test_resolve_grounded_claims_preserves_claim_type() -> None:
    interpretation = LLMInterpretation(
        summary="South deserves investigation.",
        grounded_claims=[
            GroundedClaim(
                claim_type="inference",
                statement="South is worth investigating.",
                evidence_ids=[
                    "analytics_driver_1",
                ],
            )
        ],
    )

    result = resolve_grounded_claims(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )

    assert result[0].claim_type == "inference"


def test_resolve_grounded_claims_allows_unknown_without_evidence() -> None:
    interpretation = LLMInterpretation(
        summary="Cause unknown.",
        grounded_claims=[
            GroundedClaim(
                claim_type="unknown",
                statement="The root cause is not established.",
                evidence_ids=[],
            )
        ],
    )

    result = resolve_grounded_claims(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )

    assert len(result) == 1
    assert result[0].claim_type == "unknown"
    assert result[0].evidence == []


def test_resolve_grounded_claims_preserves_evidence_provenance() -> None:
    interpretation = LLMInterpretation(
        summary="South deserves investigation.",
        grounded_claims=[
            GroundedClaim(
                claim_type="inference",
                statement="South is worth investigating.",
                evidence_ids=[
                    "analytics_driver_1",
                    "ml_anomaly_1",
                ],
            )
        ],
    )

    result = resolve_grounded_claims(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )

    assert result[0].evidence[0].source == "analytics"

    assert result[0].evidence[0].evidence_type == "driver"

    assert result[0].evidence[1].source == "ml"

    assert result[0].evidence[1].evidence_type == "anomaly"
