import json
from collections.abc import Sequence

from app.agent.contracts import (
    AgentObservation,
    AgentRunResult,
)
from app.evaluation.contracts import (
    EvaluationSummary,
    RunEvaluationMetrics,
)


def evaluate_run(
    result: AgentRunResult,
) -> RunEvaluationMetrics:
    duplicate_tool_calls = _count_duplicate_tool_calls(
        observations=(result.history.observations)
    )

    successful_tool_calls = sum(
        1 for observation in result.history.observations if observation.result.success
    )

    tool_success_rate = _safe_success_rate(
        successful=successful_tool_calls,
        total=result.tool_calls,
    )

    duplicate_tool_call_rate = _safe_failure_rate(
        failures=duplicate_tool_calls,
        total=result.tool_calls,
    )

    return RunEvaluationMetrics(
        status=result.status,
        completed=(result.status == "completed"),
        steps_used=result.steps_used,
        tool_calls=result.tool_calls,
        successful_tool_calls=(successful_tool_calls),
        tool_failures=result.tool_failures,
        duplicate_tool_calls=(duplicate_tool_calls),
        tool_success_rate=tool_success_rate,
        duplicate_tool_call_rate=(duplicate_tool_call_rate),
        invalid_final_evidence=(result.status == "invalid_final_evidence"),
        invalid_final_grounding=(result.status == "invalid_final_grounding"),
    )


def build_evaluation_summary(
    results: Sequence[AgentRunResult],
) -> EvaluationSummary:
    if not results:
        raise ValueError("Evaluation requires at least one agent run.")

    run_metrics = [evaluate_run(result=result) for result in results]

    total_runs = len(run_metrics)

    completed_runs = sum(1 for metrics in run_metrics if metrics.completed)

    total_steps = sum(metrics.steps_used for metrics in run_metrics)

    total_tool_calls = sum(metrics.tool_calls for metrics in run_metrics)

    successful_tool_calls = sum(
        metrics.successful_tool_calls for metrics in run_metrics
    )

    total_tool_failures = sum(metrics.tool_failures for metrics in run_metrics)

    duplicate_tool_calls = sum(metrics.duplicate_tool_calls for metrics in run_metrics)

    invalid_final_evidence_runs = sum(
        1 for metrics in run_metrics if metrics.invalid_final_evidence
    )

    invalid_final_grounding_runs = sum(
        1 for metrics in run_metrics if metrics.invalid_final_grounding
    )

    return EvaluationSummary(
        total_runs=total_runs,
        completed_runs=completed_runs,
        completion_rate=(completed_runs / total_runs),
        total_steps=total_steps,
        average_steps=(total_steps / total_runs),
        total_tool_calls=total_tool_calls,
        average_tool_calls=(total_tool_calls / total_runs),
        successful_tool_calls=(successful_tool_calls),
        total_tool_failures=(total_tool_failures),
        average_tool_failures=(total_tool_failures / total_runs),
        tool_success_rate=(
            _safe_success_rate(
                successful=(successful_tool_calls),
                total=total_tool_calls,
            )
        ),
        duplicate_tool_calls=(duplicate_tool_calls),
        duplicate_tool_call_rate=(
            _safe_failure_rate(
                failures=(duplicate_tool_calls),
                total=total_tool_calls,
            )
        ),
        invalid_final_evidence_runs=(invalid_final_evidence_runs),
        invalid_final_evidence_rate=(invalid_final_evidence_runs / total_runs),
        invalid_final_grounding_runs=(invalid_final_grounding_runs),
        invalid_final_grounding_rate=(invalid_final_grounding_runs / total_runs),
    )


def _count_duplicate_tool_calls(
    observations: Sequence[AgentObservation],
) -> int:
    signatures: set[str] = set()

    duplicate_count = 0

    for observation in observations:
        signature = _build_tool_call_signature(observation=observation)

        if signature in signatures:
            duplicate_count += 1

            continue

        signatures.add(signature)

    return duplicate_count


def _build_tool_call_signature(
    observation: AgentObservation,
) -> str:
    payload = {
        "tool_name": (observation.call.tool_name),
        "arguments": (observation.call.arguments),
    }

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )


def _safe_success_rate(
    successful: int,
    total: int,
) -> float:
    if total == 0:
        return 1.0

    return successful / total


def _safe_failure_rate(
    failures: int,
    total: int,
) -> float:
    if total == 0:
        return 0.0

    return failures / total
