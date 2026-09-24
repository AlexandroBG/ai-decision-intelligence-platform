from typing import Any

from app.evaluation.error_analysis_contracts import (
    ErrorAnalysisResult,
    EvaluationError,
)


def analyze_evaluation_run(
    run: dict[
        str,
        Any,
    ],
) -> ErrorAnalysisResult:
    case_id = str(
        run.get(
            "case_id",
            "unknown_case",
        )
    )

    run_number = int(
        run.get(
            "run",
            1,
        )
    )

    errors: list[EvaluationError] = []

    if run.get("run_type") == "provider_error":
        errors.append(
            _build_provider_error(
                run=run,
                case_id=case_id,
                run_number=run_number,
            )
        )

        return _build_result(errors=errors)

    _collect_execution_errors(
        run=run,
        errors=errors,
        case_id=case_id,
        run_number=run_number,
    )

    _collect_tool_selection_errors(
        run=run,
        errors=errors,
        case_id=case_id,
        run_number=run_number,
    )

    _collect_ground_truth_errors(
        run=run,
        errors=errors,
        case_id=case_id,
        run_number=run_number,
    )

    _collect_semantic_errors(
        run=run,
        errors=errors,
        case_id=case_id,
        run_number=run_number,
    )

    return _build_result(errors=errors)


def _collect_execution_errors(
    *,
    run: dict[
        str,
        Any,
    ],
    errors: list[EvaluationError],
    case_id: str,
    run_number: int,
) -> None:
    metrics = run.get(
        "agent_metrics",
        {},
    )

    if not metrics.get(
        "completed",
        False,
    ):
        errors.append(
            EvaluationError(
                category="execution",
                severity="high",
                code="agent_not_completed",
                message=("The agent did not complete the task."),
                case_id=case_id,
                run_number=run_number,
            )
        )

    if (
        metrics.get(
            "duplicate_tool_calls",
            0,
        )
        > 0
    ):
        errors.append(
            EvaluationError(
                category="execution",
                severity="medium",
                code="duplicate_tool_call",
                message=("The agent made one or more duplicate tool calls."),
                case_id=case_id,
                run_number=run_number,
            )
        )


def _collect_tool_selection_errors(
    *,
    run: dict[
        str,
        Any,
    ],
    errors: list[EvaluationError],
    case_id: str,
    run_number: int,
) -> None:
    selection = run.get(
        "tool_selection",
        {},
    )

    missing_tools = selection.get(
        "missing_required_tools",
        [],
    )

    unexpected_tools = selection.get(
        "unexpected_tools",
        [],
    )

    if missing_tools:
        errors.append(
            EvaluationError(
                category="tool_selection",
                severity="high",
                code="missing_required_tool",
                message=(f"Missing required tools: {missing_tools}"),
                case_id=case_id,
                run_number=run_number,
            )
        )

    if unexpected_tools:
        errors.append(
            EvaluationError(
                category="tool_selection",
                severity="medium",
                code="unexpected_tool",
                message=(f"Unexpected tools used: {unexpected_tools}"),
                case_id=case_id,
                run_number=run_number,
            )
        )


def _collect_ground_truth_errors(
    *,
    run: dict[
        str,
        Any,
    ],
    errors: list[EvaluationError],
    case_id: str,
    run_number: int,
) -> None:
    ground_truth = run.get(
        "ground_truth",
        {},
    )

    if ground_truth.get("passed") is False:
        errors.append(
            EvaluationError(
                category="ground_truth",
                severity="high",
                code="ground_truth_mismatch",
                message=("One or more deterministic ground-truth checks failed."),
                case_id=case_id,
                run_number=run_number,
            )
        )


def _collect_semantic_errors(
    *,
    run: dict[
        str,
        Any,
    ],
    errors: list[EvaluationError],
    case_id: str,
    run_number: int,
) -> None:
    semantic = run.get(
        "semantic_evaluation",
        {},
    )

    if semantic.get(
        "causal_overclaim",
        False,
    ):
        errors.append(
            EvaluationError(
                category="semantic",
                severity="high",
                code="causal_overclaim",
                message=("The answer contains a causal overclaim."),
                case_id=case_id,
                run_number=run_number,
            )
        )

    if semantic.get(
        "causal_language_risk",
        False,
    ):
        errors.append(
            EvaluationError(
                category="semantic",
                severity="medium",
                code="causal_language_risk",
                message=(
                    "The answer contains "
                    "ambiguous causal language "
                    "that is stronger than the "
                    "observational evidence."
                ),
                case_id=case_id,
                run_number=run_number,
            )
        )

    if semantic.get(
        "unsupported_certainty",
        False,
    ):
        errors.append(
            EvaluationError(
                category="semantic",
                severity="high",
                code="unsupported_certainty",
                message=("The answer contains unsupported certainty."),
                case_id=case_id,
                run_number=run_number,
            )
        )

    if semantic.get(
        "overlap_summing_risk",
        False,
    ):
        errors.append(
            EvaluationError(
                category="semantic",
                severity="high",
                code="overlap_summing_risk",
                message=(
                    "The answer may incorrectly "
                    "combine overlapping driver "
                    "contributions."
                ),
                case_id=case_id,
                run_number=run_number,
            )
        )

    failed_checks = semantic.get(
        "failed_checks",
        [],
    )

    if "recommendation_present" in failed_checks:
        errors.append(
            EvaluationError(
                category="semantic",
                severity="medium",
                code="missing_recommendation",
                message=("The case required a recommendation but none was detected."),
                case_id=case_id,
                run_number=run_number,
            )
        )


def _build_provider_error(
    *,
    run: dict[
        str,
        Any,
    ],
    case_id: str,
    run_number: int,
) -> EvaluationError:
    provider = run.get(
        "provider_error",
        {},
    )

    kind = provider.get(
        "kind",
        "provider_error",
    )

    return EvaluationError(
        category="provider",
        severity="medium",
        code=str(kind),
        message=("The provider prevented the evaluation run."),
        case_id=case_id,
        run_number=run_number,
    )


def _build_result(
    *,
    errors: list[EvaluationError],
) -> ErrorAnalysisResult:
    categories = list(dict.fromkeys(error.category for error in errors))

    return ErrorAnalysisResult(
        total_errors=len(errors),
        errors=errors,
        has_high_severity_error=any(error.severity == "high" for error in errors),
        categories=categories,
    )
