import pytest

from app.llm.contracts import (
    EvidenceAnomaly,
    EvidenceContext,
    EvidenceDriver,
    EvidenceRevenue,
    GroundedClaim,
    LLMInterpretation,
)
from app.llm.grounding import (
    GroundingCoverageError,
    GroundingValidationError,
    calculate_grounding_coverage,
    collect_evidence_ids,
    enforce_grounding_coverage,
    validate_grounding,
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


def test_collect_evidence_ids_returns_all_ids() -> None:
    result = collect_evidence_ids(
        evidence=build_evidence_context(),
    )

    assert result == {
        "revenue_summary_1",
        "analytics_driver_1",
        "ml_anomaly_1",
    }


def test_validate_grounding_accepts_revenue_summary_id() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            )
        ],
    )

    validate_grounding(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )


def test_validate_grounding_accepts_known_ids() -> None:
    interpretation = LLMInterpretation(
        summary="South deserves investigation.",
        grounded_claims=[
            GroundedClaim(
                claim_type="inference",
                statement="South deserves investigation.",
                evidence_ids=[
                    "analytics_driver_1",
                    "ml_anomaly_1",
                ],
            )
        ],
    )

    validate_grounding(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )


def test_validate_grounding_accepts_unknown_without_evidence() -> None:
    interpretation = LLMInterpretation(
        summary="Cause unknown.",
        grounded_claims=[
            GroundedClaim(
                claim_type="unknown",
                statement="Root cause is unknown.",
                evidence_ids=[],
            )
        ],
    )

    validate_grounding(
        evidence=build_evidence_context(),
        interpretation=interpretation,
    )


def test_validate_grounding_rejects_fact_without_evidence() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[],
            )
        ],
    )

    with pytest.raises(
        GroundingValidationError,
        match="Fact claim must reference",
    ):
        validate_grounding(
            evidence=build_evidence_context(),
            interpretation=interpretation,
        )


def test_validate_grounding_rejects_inference_without_evidence() -> None:
    interpretation = LLMInterpretation(
        summary="South deserves investigation.",
        grounded_claims=[
            GroundedClaim(
                claim_type="inference",
                statement="South deserves investigation.",
                evidence_ids=[],
            )
        ],
    )

    with pytest.raises(
        GroundingValidationError,
        match="Inference claim must reference",
    ):
        validate_grounding(
            evidence=build_evidence_context(),
            interpretation=interpretation,
        )


def test_validate_grounding_rejects_unknown_id() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "analytics_driver_999",
                ],
            )
        ],
    )

    with pytest.raises(
        GroundingValidationError,
        match="analytics_driver_999",
    ):
        validate_grounding(
            evidence=build_evidence_context(),
            interpretation=interpretation,
        )


def test_validate_grounding_rejects_unknown_ml_id() -> None:
    interpretation = LLMInterpretation(
        summary="South is anomalous.",
        grounded_claims=[
            GroundedClaim(
                claim_type="inference",
                statement="South is anomalous.",
                evidence_ids=[
                    "ml_anomaly_999",
                ],
            )
        ],
    )

    with pytest.raises(
        GroundingValidationError,
        match="ml_anomaly_999",
    ):
        validate_grounding(
            evidence=build_evidence_context(),
            interpretation=interpretation,
        )


def test_grounding_coverage_is_full_when_all_claims_are_grounded() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South deserves investigation.",
                evidence_ids=[
                    "analytics_driver_1",
                ],
            ),
        ],
    )

    coverage = calculate_grounding_coverage(
        interpretation=interpretation,
    )

    assert coverage.expected_claims == 2
    assert coverage.grounded_claims == 2
    assert coverage.coverage_ratio == 1.0


def test_grounding_coverage_detects_partial_grounding() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South deserves investigation.",
                evidence_ids=[],
            ),
        ],
    )

    coverage = calculate_grounding_coverage(
        interpretation=interpretation,
    )

    assert coverage.expected_claims == 2
    assert coverage.grounded_claims == 1
    assert coverage.coverage_ratio == 0.5


def test_grounding_coverage_ignores_unknowns() -> None:
    interpretation = LLMInterpretation(
        summary="Cause unknown.",
        grounded_claims=[
            GroundedClaim(
                claim_type="unknown",
                statement="Root cause is unknown.",
                evidence_ids=[],
            )
        ],
    )

    coverage = calculate_grounding_coverage(
        interpretation=interpretation,
    )

    assert coverage.expected_claims == 0
    assert coverage.grounded_claims == 0
    assert coverage.coverage_ratio == 1.0


def test_grounding_coverage_does_not_depend_on_duplicate_text() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue decreased by 30%.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            )
        ],
    )

    coverage = calculate_grounding_coverage(
        interpretation=interpretation,
    )

    assert coverage.expected_claims == 1
    assert coverage.grounded_claims == 1
    assert coverage.coverage_ratio == 1.0


def test_enforce_grounding_coverage_accepts_full_coverage() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            )
        ],
    )

    coverage = enforce_grounding_coverage(
        interpretation=interpretation,
    )

    assert coverage.coverage_ratio == 1.0


def test_enforce_grounding_coverage_rejects_partial_coverage() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South deserves investigation.",
                evidence_ids=[],
            ),
        ],
    )

    with pytest.raises(
        GroundingCoverageError,
        match="Grounding coverage is below",
    ):
        enforce_grounding_coverage(
            interpretation=interpretation,
        )


def test_enforce_grounding_coverage_accepts_custom_threshold() -> None:
    interpretation = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South deserves investigation.",
                evidence_ids=[],
            ),
        ],
    )

    coverage = enforce_grounding_coverage(
        interpretation=interpretation,
        minimum_coverage=0.5,
    )

    assert coverage.coverage_ratio == 0.5


def test_enforce_grounding_coverage_rejects_invalid_threshold() -> None:
    interpretation = LLMInterpretation(summary="Revenue declined.")

    with pytest.raises(
        ValueError,
        match="minimum_coverage",
    ):
        enforce_grounding_coverage(
            interpretation=interpretation,
            minimum_coverage=1.5,
        )
