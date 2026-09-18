from app.analytics.contracts import AnalyticsResult
from app.llm.client import GeminiClient
from app.llm.contracts import LLMInterpretation
from app.llm.evidence import build_evidence_context
from app.llm.prompts import build_evidence_prompt
from app.ml.contracts import MLResult


def interpret_decision_evidence(
    client: GeminiClient,
    question: str,
    analytics_result: AnalyticsResult,
    ml_result: MLResult,
    max_analytics_drivers: int = 5,
    max_ml_anomalies: int = 10,
) -> LLMInterpretation:
    evidence = build_evidence_context(
        question=question,
        analytics_result=analytics_result,
        ml_result=ml_result,
        max_analytics_drivers=max_analytics_drivers,
        max_ml_anomalies=max_ml_anomalies,
    )

    prompt = build_evidence_prompt(
        evidence=evidence,
    )

    return client.generate_interpretation(
        prompt=prompt,
    )
