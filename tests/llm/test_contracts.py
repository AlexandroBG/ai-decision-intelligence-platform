import pytest
from pydantic import ValidationError

from app.llm.contracts import (
    ContextSelectionMetadata,
    GroundedClaim,
    GroundedInterpretationResult,
    GroundingMetadata,
    LLMInterpretation,
)


def test_llm_interpretation_accepts_valid_data():
    result = LLMInterpretation(
        summary="Revenue declined.",
        recommended_investigations=["Review South order volume."],
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue fell by 28%.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement=("South may deserve investigation."),
                evidence_ids=[
                    "analytics_driver_1",
                ],
            ),
            GroundedClaim(
                claim_type="unknown",
                statement=("Causality is not established."),
                evidence_ids=[],
            ),
        ],
    )

    assert result.summary == "Revenue declined."


def test_llm_interpretation_uses_empty_lists_by_default():
    result = LLMInterpretation(summary="Revenue declined.")

    assert result.facts == []
    assert result.inferences == []
    assert result.unknowns == []
    assert result.recommended_investigations == []
    assert result.grounded_claims == []


def test_llm_interpretation_derives_facts_from_grounded_claims():
    result = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue fell.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South deserves review.",
                evidence_ids=[
                    "analytics_driver_1",
                ],
            ),
        ],
    )

    assert result.facts == ["Revenue fell."]


def test_llm_interpretation_derives_inferences_from_grounded_claims():
    result = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue fell.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South deserves review.",
                evidence_ids=[
                    "analytics_driver_1",
                ],
            ),
        ],
    )

    assert result.inferences == ["South deserves review."]


def test_llm_interpretation_derives_unknowns_from_grounded_claims():
    result = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="unknown",
                statement="The root cause is unknown.",
                evidence_ids=[],
            )
        ],
    )

    assert result.unknowns == ["The root cause is unknown."]


def test_llm_interpretation_rejects_empty_summary():
    with pytest.raises(ValidationError):
        LLMInterpretation(summary="")


def test_llm_interpretation_rejects_whitespace_summary():
    with pytest.raises(ValidationError):
        LLMInterpretation(summary="   ")


def test_llm_interpretation_strips_summary_whitespace():
    result = LLMInterpretation(summary="  Revenue declined.  ")

    assert result.summary == "Revenue declined."


def test_llm_interpretation_removes_empty_investigations():
    result = LLMInterpretation(
        summary="Revenue declined.",
        recommended_investigations=[
            "Review South.",
            "",
            "   ",
        ],
    )

    assert result.recommended_investigations == ["Review South."]


def test_llm_interpretation_strips_investigation_whitespace():
    result = LLMInterpretation(
        summary="Revenue declined.",
        recommended_investigations=[
            "  Review South.  ",
        ],
    )

    assert result.recommended_investigations == ["Review South."]


def test_llm_interpretation_removes_duplicate_investigations():
    result = LLMInterpretation(
        summary="Revenue declined.",
        recommended_investigations=[
            "Review South.",
            "Review South.",
        ],
    )

    assert result.recommended_investigations == ["Review South."]


def test_grounded_claim_accepts_evidence_ids():
    claim = GroundedClaim(
        claim_type="fact",
        statement="South shows deterioration.",
        evidence_ids=[
            "analytics_driver_1",
            "ml_anomaly_2",
        ],
    )

    assert claim.evidence_ids == [
        "analytics_driver_1",
        "ml_anomaly_2",
    ]


def test_grounded_claim_rejects_empty_statement():
    with pytest.raises(ValidationError):
        GroundedClaim(
            claim_type="fact",
            statement="   ",
            evidence_ids=[
                "analytics_driver_1",
            ],
        )


def test_grounded_claim_normalizes_evidence_ids():
    claim = GroundedClaim(
        claim_type="fact",
        statement="South shows deterioration.",
        evidence_ids=[
            " analytics_driver_1 ",
            "",
            "analytics_driver_1",
        ],
    )

    assert claim.evidence_ids == [
        "analytics_driver_1",
    ]


def test_grounded_claim_rejects_invalid_claim_type():
    with pytest.raises(ValidationError):
        GroundedClaim(
            claim_type="unsupported",
            statement="Invalid claim type.",
            evidence_ids=[],
        )


def test_grounded_interpretation_result_accepts_metadata():
    interpretation = LLMInterpretation(summary="Revenue declined.")

    result = GroundedInterpretationResult(
        interpretation=interpretation,
        grounding=GroundingMetadata(
            expected_claims=2,
            grounded_claims=2,
            coverage_ratio=1.0,
        ),
        context_selection=ContextSelectionMetadata(
            analytics_driver_budget=5,
            analytics_drivers_available=3,
            analytics_drivers_selected=2,
            analytics_drivers_omitted=1,
            analytics_driver_retention_ratio=2 / 3,
            analytics_driver_budget_utilization=0.4,
            analytics_driver_context_pressure=False,
            ml_anomaly_budget=10,
            ml_anomalies_available=4,
            ml_anomalies_selected=2,
            ml_anomalies_omitted=2,
            ml_anomaly_retention_ratio=0.5,
            ml_anomaly_budget_utilization=0.2,
            ml_anomaly_context_pressure=False,
        ),
    )

    assert result.interpretation.summary == ("Revenue declined.")

    assert result.grounding.coverage_ratio == 1.0

    assert result.context_selection.analytics_driver_budget == 5

    assert result.context_selection.analytics_drivers_omitted == 1

    assert result.context_selection.ml_anomaly_budget == 10

    assert result.context_selection.ml_anomalies_omitted == 2

    assert result.resolved_claims == []
