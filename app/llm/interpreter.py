from app.analytics.contracts import AnalyticsResult
from app.llm.client import GeminiClient
from app.llm.contracts import (
    ContextSelectionMetadata,
    GroundedInterpretationResult,
    GroundingMetadata,
)
from app.llm.evidence import build_evidence_context
from app.llm.grounding import (
    DEFAULT_MIN_GROUNDING_COVERAGE,
    enforce_grounding_coverage,
    validate_grounding,
)
from app.llm.prompts import build_evidence_prompt
from app.llm.resolution import resolve_grounded_claims
from app.ml.contracts import MLResult


def interpret_decision_evidence(
    client: GeminiClient,
    question: str,
    analytics_result: AnalyticsResult,
    ml_result: MLResult,
    max_analytics_drivers: int = 5,
    max_ml_anomalies: int = 10,
    minimum_grounding_coverage: float = (DEFAULT_MIN_GROUNDING_COVERAGE),
) -> GroundedInterpretationResult:
    evidence_build = build_evidence_context(
        question=question,
        analytics_result=analytics_result,
        ml_result=ml_result,
        max_analytics_drivers=max_analytics_drivers,
        max_ml_anomalies=max_ml_anomalies,
    )

    evidence = evidence_build.evidence

    prompt = build_evidence_prompt(
        evidence=evidence,
    )

    interpretation = client.generate_interpretation(
        prompt=prompt,
    )

    validate_grounding(
        evidence=evidence,
        interpretation=interpretation,
    )

    coverage = enforce_grounding_coverage(
        interpretation=interpretation,
        minimum_coverage=minimum_grounding_coverage,
    )

    resolved_claims = resolve_grounded_claims(
        evidence=evidence,
        interpretation=interpretation,
    )

    selection = evidence_build.selection_metadata

    return GroundedInterpretationResult(
        interpretation=interpretation,
        grounding=GroundingMetadata(
            expected_claims=coverage.expected_claims,
            grounded_claims=coverage.grounded_claims,
            coverage_ratio=coverage.coverage_ratio,
        ),
        context_selection=ContextSelectionMetadata(
            analytics_driver_budget=(selection.analytics_driver_budget),
            analytics_drivers_available=(selection.analytics_drivers_available),
            analytics_drivers_selected=(selection.analytics_drivers_selected),
            analytics_drivers_omitted=(selection.analytics_drivers_omitted),
            analytics_driver_retention_ratio=(
                selection.analytics_driver_retention_ratio
            ),
            analytics_driver_budget_utilization=(
                selection.analytics_driver_budget_utilization
            ),
            analytics_driver_context_pressure=(
                selection.analytics_driver_context_pressure
            ),
            ml_anomaly_budget=(selection.ml_anomaly_budget),
            ml_anomalies_available=(selection.ml_anomalies_available),
            ml_anomalies_selected=(selection.ml_anomalies_selected),
            ml_anomalies_omitted=(selection.ml_anomalies_omitted),
            ml_anomaly_retention_ratio=(selection.ml_anomaly_retention_ratio),
            ml_anomaly_budget_utilization=(selection.ml_anomaly_budget_utilization),
            ml_anomaly_context_pressure=(selection.ml_anomaly_context_pressure),
        ),
        resolved_claims=resolved_claims,
    )
