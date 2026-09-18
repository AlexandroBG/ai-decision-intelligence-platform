from unittest.mock import MagicMock

import pytest

from app.analytics.contracts import (
    AnalyticsResult,
    DriverEvidence,
    RevenueComparison,
)
from app.llm.contracts import (
    GroundedClaim,
    GroundedInterpretationResult,
    LLMInterpretation,
)
from app.llm.grounding import (
    GroundingValidationError,
)
from app.llm.interpreter import interpret_decision_evidence
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
            )
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
            )
        ]
    )


def build_grounded_interpretation() -> LLMInterpretation:
    return LLMInterpretation(
        summary="Revenue declined.",
        recommended_investigations=[
            "Review South order volume.",
        ],
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue fell by 30%.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South may deserve investigation.",
                evidence_ids=[
                    "analytics_driver_1",
                    "ml_anomaly_1",
                ],
            ),
            GroundedClaim(
                claim_type="unknown",
                statement="Causality is not established.",
                evidence_ids=[],
            ),
        ],
    )


def test_interpret_decision_evidence_returns_grounded_result() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = build_grounded_interpretation()

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert isinstance(
        result,
        GroundedInterpretationResult,
    )

    assert result.interpretation.summary == "Revenue declined."


def test_interpret_decision_evidence_derives_claim_views() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = build_grounded_interpretation()

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert result.interpretation.facts == ["Revenue fell by 30%."]

    assert result.interpretation.inferences == ["South may deserve investigation."]

    assert result.interpretation.unknowns == ["Causality is not established."]


def test_interpret_decision_evidence_returns_grounding_metadata() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = build_grounded_interpretation()

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert result.grounding.expected_claims == 2
    assert result.grounding.grounded_claims == 2
    assert result.grounding.coverage_ratio == 1.0


def test_interpret_decision_evidence_returns_context_selection_metadata() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = build_grounded_interpretation()

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert result.context_selection.analytics_driver_budget == 5

    assert result.context_selection.analytics_drivers_available == 1

    assert result.context_selection.analytics_drivers_selected == 1

    assert result.context_selection.analytics_drivers_omitted == 0

    assert result.context_selection.analytics_driver_retention_ratio == 1.0

    assert result.context_selection.analytics_driver_budget_utilization == 0.2

    assert result.context_selection.analytics_driver_context_pressure is False

    assert result.context_selection.ml_anomaly_budget == 10

    assert result.context_selection.ml_anomalies_available == 1

    assert result.context_selection.ml_anomalies_selected == 1

    assert result.context_selection.ml_anomalies_omitted == 0

    assert result.context_selection.ml_anomaly_retention_ratio == 1.0

    assert result.context_selection.ml_anomaly_budget_utilization == 0.1

    assert result.context_selection.ml_anomaly_context_pressure is False


def test_interpret_decision_evidence_returns_resolved_claims() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = build_grounded_interpretation()

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert len(result.resolved_claims) == 3

    assert result.resolved_claims[0].evidence[0].evidence_id == "revenue_summary_1"

    assert [item.evidence_id for item in result.resolved_claims[1].evidence] == [
        "analytics_driver_1",
        "ml_anomaly_1",
    ]

    assert result.resolved_claims[2].claim_type == "unknown"

    assert result.resolved_claims[2].evidence == []


def test_interpret_decision_evidence_calls_client_once() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined."
    )

    interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    client.generate_interpretation.assert_called_once()


def test_interpret_decision_evidence_prompt_contains_evidence() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined."
    )

    interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    prompt = client.generate_interpretation.call_args.kwargs["prompt"]

    assert "South" in prompt
    assert '"absolute_change": -300.0' in prompt
    assert "Why did revenue decline?" in prompt


def test_interpret_decision_evidence_respects_limits() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined."
    )

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=0,
        max_ml_anomalies=0,
    )

    prompt = client.generate_interpretation.call_args.kwargs["prompt"]

    assert '"analytics_drivers": []' in prompt
    assert '"ml_anomalies": []' in prompt

    assert result.context_selection.analytics_drivers_omitted == 1

    assert result.context_selection.analytics_driver_context_pressure is True

    assert result.context_selection.ml_anomalies_omitted == 1

    assert result.context_selection.ml_anomaly_context_pressure is True


def test_interpret_decision_evidence_rejects_unknown_grounding() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Unknown evidence claim.",
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
        interpret_decision_evidence(
            client=client,
            question="Why did revenue decline?",
            analytics_result=build_analytics_result(),
            ml_result=build_ml_result(),
        )


def test_interpret_decision_evidence_rejects_low_coverage() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined.",
        grounded_claims=[
            GroundedClaim(
                claim_type="fact",
                statement="Revenue declined by 30%.",
                evidence_ids=[
                    "revenue_summary_1",
                ],
            ),
            GroundedClaim(
                claim_type="inference",
                statement="South is worth investigating.",
                evidence_ids=[],
            ),
        ],
    )

    with pytest.raises(
        GroundingValidationError,
        match="Inference claim must reference",
    ):
        interpret_decision_evidence(
            client=client,
            question="Why did revenue decline?",
            analytics_result=build_analytics_result(),
            ml_result=build_ml_result(),
        )
