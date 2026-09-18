from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.analytics.contracts import (
    AnalyticsResult,
    DriverEvidence,
    RevenueComparison,
)
from app.llm.client import GeminiClient
from app.llm.config import load_llm_config
from app.llm.contracts import GroundedInterpretationResult
from app.llm.interpreter import interpret_decision_evidence
from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)

EVALUATION_NAME = "phase7_gemini_grounding_eval_v1"

OUTPUT_DIRECTORY = Path("artifacts/evals")

OUTPUT_FILE = OUTPUT_DIRECTORY / "phase7_gemini_grounding_eval.json"


def build_analytics_result() -> AnalyticsResult:
    return AnalyticsResult(
        revenue_comparison=RevenueComparison(
            baseline_revenue=1000.0,
            comparison_revenue=500.0,
            absolute_change=-500.0,
            percentage_change=-0.50,
        ),
        drivers=[
            DriverEvidence(
                dimension="region",
                value="South",
                baseline_revenue=600.0,
                comparison_revenue=300.0,
                absolute_change=-300.0,
                percentage_change=-0.50,
                contribution_to_total_change=0.60,
            ),
            DriverEvidence(
                dimension="category",
                value="Computing",
                baseline_revenue=400.0,
                comparison_revenue=250.0,
                absolute_change=-150.0,
                percentage_change=-0.375,
                contribution_to_total_change=0.30,
            ),
            DriverEvidence(
                dimension="sales_channel",
                value="Partner",
                baseline_revenue=200.0,
                comparison_revenue=150.0,
                absolute_change=-50.0,
                percentage_change=-0.25,
                contribution_to_total_change=0.10,
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
                daily_revenue=40.0,
                anomaly_score=0.24,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-12",
                dimension="category",
                value="Computing",
                daily_revenue=35.0,
                anomaly_score=0.19,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-15",
                dimension="sales_channel",
                value="Partner",
                daily_revenue=30.0,
                anomaly_score=0.14,
                is_anomaly=True,
            ),
            AnomalyEvidence(
                date="2025-08-18",
                dimension="region",
                value="North",
                daily_revenue=120.0,
                anomaly_score=-0.03,
                is_anomaly=False,
            ),
        ]
    )


def build_client() -> GeminiClient:
    config = load_llm_config()

    return GeminiClient(
        config=config,
    )


def evaluate_result(
    result: GroundedInterpretationResult,
) -> dict[str, bool]:
    fact_claims = [
        claim for claim in result.resolved_claims if claim.claim_type == "fact"
    ]

    inference_claims = [
        claim for claim in result.resolved_claims if claim.claim_type == "inference"
    ]

    facts_have_evidence = all(bool(claim.evidence) for claim in fact_claims)

    inferences_have_evidence = all(bool(claim.evidence) for claim in inference_claims)

    no_omitted_default_context = (
        result.context_selection.analytics_drivers_omitted == 0
        and result.context_selection.ml_anomalies_omitted == 0
    )

    no_context_pressure = (
        not result.context_selection.analytics_driver_context_pressure
        and not result.context_selection.ml_anomaly_context_pressure
    )

    return {
        "grounding_coverage_is_full": (result.grounding.coverage_ratio == 1.0),
        "facts_have_evidence": facts_have_evidence,
        "inferences_have_evidence": (inferences_have_evidence),
        "default_context_has_no_omissions": (no_omitted_default_context),
        "default_context_has_no_pressure": (no_context_pressure),
    }


def print_interpretation(
    result: GroundedInterpretationResult,
) -> None:
    interpretation = result.interpretation

    print()
    print("=" * 72)
    print("GEMINI INTERPRETATION")
    print("=" * 72)

    print()
    print("SUMMARY")
    print(interpretation.summary)

    print()
    print("FACTS")

    for fact in interpretation.facts:
        print(f"- {fact}")

    print()
    print("INFERENCES")

    for inference in interpretation.inferences:
        print(f"- {inference}")

    print()
    print("UNKNOWNS")

    for unknown in interpretation.unknowns:
        print(f"- {unknown}")

    print()
    print("RECOMMENDED INVESTIGATIONS")

    for investigation in interpretation.recommended_investigations:
        print(f"- {investigation}")

    print()
    print("RESOLVED GROUNDED CLAIMS")

    for claim in result.resolved_claims:
        evidence_ids = [evidence.evidence_id for evidence in claim.evidence]

        print(f"- [{claim.claim_type}] {claim.statement}")

        print(f"  evidence: {evidence_ids}")


def print_metrics(
    result: GroundedInterpretationResult,
    checks: dict[str, bool],
) -> None:
    selection = result.context_selection

    print()
    print("=" * 72)
    print("GROUNDING METRICS")
    print("=" * 72)

    print(
        "expected_claims:",
        result.grounding.expected_claims,
    )

    print(
        "grounded_claims:",
        result.grounding.grounded_claims,
    )

    print(
        "coverage_ratio:",
        result.grounding.coverage_ratio,
    )

    print()
    print("=" * 72)
    print("CONTEXT METRICS")
    print("=" * 72)

    print()
    print("ANALYTICS")

    print(
        "budget:",
        selection.analytics_driver_budget,
    )

    print(
        "available:",
        selection.analytics_drivers_available,
    )

    print(
        "selected:",
        selection.analytics_drivers_selected,
    )

    print(
        "omitted:",
        selection.analytics_drivers_omitted,
    )

    print(
        "retention:",
        selection.analytics_driver_retention_ratio,
    )

    print(
        "utilization:",
        selection.analytics_driver_budget_utilization,
    )

    print(
        "pressure:",
        selection.analytics_driver_context_pressure,
    )

    print()
    print("ML")

    print(
        "budget:",
        selection.ml_anomaly_budget,
    )

    print(
        "available:",
        selection.ml_anomalies_available,
    )

    print(
        "selected:",
        selection.ml_anomalies_selected,
    )

    print(
        "omitted:",
        selection.ml_anomalies_omitted,
    )

    print(
        "retention:",
        selection.ml_anomaly_retention_ratio,
    )

    print(
        "utilization:",
        selection.ml_anomaly_budget_utilization,
    )

    print(
        "pressure:",
        selection.ml_anomaly_context_pressure,
    )

    print()
    print("=" * 72)
    print("DETERMINISTIC EVALUATION")
    print("=" * 72)

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"

        print(f"{status}: {name}")


def build_report(
    result: GroundedInterpretationResult,
    checks: dict[str, bool],
) -> dict[str, object]:
    return {
        "evaluation_name": EVALUATION_NAME,
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "checks": checks,
        "all_deterministic_checks_passed": all(checks.values()),
        "result": result.model_dump(
            mode="json",
        ),
        "manual_review": {
            "facts_are_supported_by_evidence": None,
            "inferences_are_clearly_labeled": None,
            "unknowns_are_explicit": None,
            "no_causal_overclaiming": None,
            "no_cross_dimension_contribution_summing": None,
            "recommended_investigations_are_actionable": None,
            "notes": "",
        },
    }


def save_report(
    report: dict[str, object],
) -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:
    print(f"Running {EVALUATION_NAME}...")

    client = build_client()

    result = interpret_decision_evidence(
        client=client,
        question=(
            "What is affecting revenue performance, "
            "and what should I investigate first?"
        ),
        analytics_result=build_analytics_result(),
        ml_result=build_ml_result(),
    )

    checks = evaluate_result(
        result=result,
    )

    print_interpretation(
        result=result,
    )

    print_metrics(
        result=result,
        checks=checks,
    )

    report = build_report(
        result=result,
        checks=checks,
    )

    save_report(
        report=report,
    )

    print()
    print("=" * 72)
    print("EVALUATION RESULT")
    print("=" * 72)

    if all(checks.values()):
        print("PASS: all deterministic checks passed.")
    else:
        print("FAIL: one or more deterministic checks failed.")

    print()
    print("Manual review is still required for semantic quality and causal discipline.")

    print(f"Report written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
