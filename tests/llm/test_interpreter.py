from unittest.mock import MagicMock

from app.analytics.contracts import (
    AnalyticsResult,
    DriverEvidence,
    RevenueComparison,
)
from app.llm.contracts import LLMInterpretation
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


def test_interpret_decision_evidence_returns_contract() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined.",
        facts=[
            "Revenue fell by 30%.",
        ],
        inferences=[
            "South is worth investigating.",
        ],
        unknowns=[
            "Causality is not established.",
        ],
        recommended_investigations=[
            "Review South order volume.",
        ],
    )

    result = interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert isinstance(
        result,
        LLMInterpretation,
    )

    assert result.summary == "Revenue declined."


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

    interpret_decision_evidence(
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
