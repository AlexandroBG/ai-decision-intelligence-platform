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
            baseline_revenue=1773419.93,
            comparison_revenue=1275769.95,
            absolute_change=-497649.98,
            percentage_change=-0.2806,
        ),
        drivers=[
            DriverEvidence(
                dimension="category",
                value="Computing",
                baseline_revenue=1060508.0,
                comparison_revenue=608595.0,
                absolute_change=-451913.0,
                percentage_change=-0.4261,
                contribution_to_total_change=0.9081,
            ),
            DriverEvidence(
                dimension="region",
                value="South",
                baseline_revenue=491147.0,
                comparison_revenue=190156.0,
                absolute_change=-300991.0,
                percentage_change=-0.6128,
                contribution_to_total_change=0.6048,
            ),
        ],
    )


def build_ml_result() -> MLResult:
    return MLResult(
        anomalies=[
            AnomalyEvidence(
                date="2025-08-04",
                dimension="category",
                value="Computing",
                daily_revenue=2587.92,
                anomaly_score=0.068,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-15",
                dimension="region",
                value="South",
                daily_revenue=870.03,
                anomaly_score=0.071,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-03",
                dimension="sales_channel",
                value="Partner",
                daily_revenue=2623.33,
                anomaly_score=0.059,
                is_anomaly=True,
            ),
        ]
    )


def test_llm_pipeline_integration_returns_structured_interpretation() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined materially.",
        facts=[
            "Revenue declined by approximately 28%.",
            "Computing and South show large observed deterioration.",
        ],
        inferences=[
            "Computing and South are high-priority investigation areas.",
        ],
        unknowns=[
            "The supplied evidence does not establish causality.",
        ],
        recommended_investigations=[
            "Investigate Computing performance.",
            "Investigate South-region volume.",
        ],
    )

    result = interpret_decision_evidence(
        client=client,
        question=(
            "What is affecting revenue performance, "
            "and what should I investigate first?"
        ),
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    assert isinstance(
        result,
        LLMInterpretation,
    )

    assert result.summary == ("Revenue declined materially.")

    assert result.facts
    assert result.unknowns


def test_llm_pipeline_integration_builds_grounded_prompt() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined materially."
    )

    interpret_decision_evidence(
        client=client,
        question=(
            "What is affecting revenue performance, "
            "and what should I investigate first?"
        ),
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    prompt = client.generate_interpretation.call_args.kwargs["prompt"]

    assert "Computing" in prompt
    assert "South" in prompt
    assert "Partner" in prompt

    assert "-497649.98" in prompt
    assert "-0.2806" in prompt

    assert "Do not add contribution values across different dimensions." in prompt

    assert "An anomaly does NOT prove" in prompt


def test_llm_pipeline_integration_preserves_analytics_limit() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined materially."
    )

    interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=1,
        max_ml_anomalies=0,
    )

    prompt = client.generate_interpretation.call_args.kwargs["prompt"]

    assert '"value": "Computing"' in prompt
    assert '"value": "South"' not in prompt
    assert '"value": "Partner"' not in prompt
    assert '"ml_anomalies": []' in prompt


def test_llm_pipeline_integration_preserves_ml_limit() -> None:
    client = MagicMock()

    client.generate_interpretation.return_value = LLMInterpretation(
        summary="Revenue declined materially."
    )

    interpret_decision_evidence(
        client=client,
        question="Why did revenue decline?",
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
        max_analytics_drivers=0,
        max_ml_anomalies=1,
    )

    prompt = client.generate_interpretation.call_args.kwargs["prompt"]

    assert '"analytics_drivers": []' in prompt

    assert '"value": "South"' in prompt
    assert '"value": "Computing"' not in prompt
    assert '"value": "Partner"' not in prompt

    assert '"anomaly_score": 0.071' in prompt
