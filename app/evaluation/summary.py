from typing import Any

from app.evaluation.summary_contracts import (
    MultiRunEvaluationSummary,
)


def build_multi_run_summary(
    requested_runs: int,
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> MultiRunEvaluationSummary:
    if requested_runs <= 0:
        raise ValueError("requested_runs must be greater than zero.")

    quality_runs = [run for run in runs if run.get("run_type") == "quality_result"]

    provider_error_runs = [
        run for run in runs if run.get("run_type") == "provider_error"
    ]

    attempted_runs = len(runs)
    evaluated_runs = len(quality_runs)
    provider_errors = len(provider_error_runs)

    passed_runs = sum(1 for run in quality_runs if run.get("overall_passed") is True)

    if evaluated_runs == 0:
        return MultiRunEvaluationSummary(
            requested_runs=requested_runs,
            attempted_runs=attempted_runs,
            evaluated_runs=0,
            provider_errors=provider_errors,
            passed_runs=0,
            quality_pass_rate=None,
            completion_rate=None,
            tool_selection_pass_rate=None,
            ground_truth_pass_rate=None,
            semantic_pass_rate=None,
            tool_success_rate=None,
            duplicate_tool_call_rate=None,
            average_steps=None,
            average_tool_calls=None,
            average_tool_failures=None,
            average_latency_ms=None,
            requested_run_evaluation_rate=0.0,
        )

    completed_runs = sum(1 for run in quality_runs if run["agent_metrics"]["completed"])

    tool_selection_passes = sum(
        1 for run in quality_runs if run["tool_selection"]["passed"]
    )

    ground_truth_passes = sum(
        1 for run in quality_runs if run["ground_truth"]["passed"]
    )

    semantic_passes = sum(
        1 for run in quality_runs if run["semantic_evaluation"]["passed"]
    )

    total_steps = sum(run["agent_metrics"]["steps_used"] for run in quality_runs)

    total_tool_calls = sum(run["agent_metrics"]["tool_calls"] for run in quality_runs)

    successful_tool_calls = sum(
        run["agent_metrics"]["successful_tool_calls"] for run in quality_runs
    )

    total_tool_failures = sum(
        run["agent_metrics"]["tool_failures"] for run in quality_runs
    )

    duplicate_tool_calls = sum(
        run["agent_metrics"]["duplicate_tool_calls"] for run in quality_runs
    )

    total_latency_ms = sum(run["duration_ms"] for run in quality_runs)

    if total_tool_calls == 0:
        tool_success_rate = None
        duplicate_tool_call_rate = None
    else:
        tool_success_rate = successful_tool_calls / total_tool_calls

        duplicate_tool_call_rate = duplicate_tool_calls / total_tool_calls

    return MultiRunEvaluationSummary(
        requested_runs=requested_runs,
        attempted_runs=attempted_runs,
        evaluated_runs=evaluated_runs,
        provider_errors=provider_errors,
        passed_runs=passed_runs,
        quality_pass_rate=(passed_runs / evaluated_runs),
        completion_rate=(completed_runs / evaluated_runs),
        tool_selection_pass_rate=(tool_selection_passes / evaluated_runs),
        ground_truth_pass_rate=(ground_truth_passes / evaluated_runs),
        semantic_pass_rate=(semantic_passes / evaluated_runs),
        tool_success_rate=tool_success_rate,
        duplicate_tool_call_rate=(duplicate_tool_call_rate),
        average_steps=(total_steps / evaluated_runs),
        average_tool_calls=(total_tool_calls / evaluated_runs),
        average_tool_failures=(total_tool_failures / evaluated_runs),
        average_latency_ms=(total_latency_ms / evaluated_runs),
        requested_run_evaluation_rate=(evaluated_runs / requested_runs),
    )
