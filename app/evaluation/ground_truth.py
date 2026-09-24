from collections.abc import Mapping
from typing import Any

from app.agent.contracts import (
    AgentObservation,
    AgentRunResult,
)
from app.evaluation.contracts import (
    EvaluationCase,
    ExpectedNumericMetric,
    GroundTruthEvaluation,
    GroundTruthMetricResult,
)


def evaluate_ground_truth(
    case: EvaluationCase,
    result: AgentRunResult,
) -> GroundTruthEvaluation:
    metric_results: list[GroundTruthMetricResult] = []

    for expected_output in case.expected_outputs:
        observation = _find_successful_observation(
            result=result,
            tool_name=(expected_output.tool_name),
        )

        for metric in expected_output.metrics:
            metric_results.append(
                _evaluate_metric(
                    observation=observation,
                    tool_name=(expected_output.tool_name),
                    metric=metric,
                )
            )

    total_checks = len(metric_results)

    passed_checks = sum(1 for metric_result in metric_results if metric_result.passed)

    if total_checks == 0:
        score = 1.0
    else:
        score = passed_checks / total_checks

    return GroundTruthEvaluation(
        total_checks=(total_checks),
        passed_checks=(passed_checks),
        score=score,
        passed=(passed_checks == total_checks),
        results=(metric_results),
    )


def _find_successful_observation(
    result: AgentRunResult,
    tool_name: str,
) -> AgentObservation | None:
    for observation in result.history.observations:
        if observation.call.tool_name != tool_name:
            continue

        if not observation.result.success:
            continue

        return observation

    return None


def _evaluate_metric(
    observation: AgentObservation | None,
    tool_name: str,
    metric: ExpectedNumericMetric,
) -> GroundTruthMetricResult:
    if observation is None:
        return GroundTruthMetricResult(
            tool_name=tool_name,
            field_path=(metric.field_path),
            expected_value=(metric.expected_value),
            tolerance=(metric.absolute_tolerance),
            passed=False,
            error=("Successful tool observation not found."),
        )

    output = observation.result.output

    found, raw_value = _extract_field(
        value=output,
        field_path=(metric.field_path),
    )

    if not found:
        return GroundTruthMetricResult(
            tool_name=tool_name,
            field_path=(metric.field_path),
            expected_value=(metric.expected_value),
            tolerance=(metric.absolute_tolerance),
            passed=False,
            error=("Expected output field was not found."),
        )

    if isinstance(
        raw_value,
        bool,
    ) or not isinstance(
        raw_value,
        int | float,
    ):
        return GroundTruthMetricResult(
            tool_name=tool_name,
            field_path=(metric.field_path),
            expected_value=(metric.expected_value),
            tolerance=(metric.absolute_tolerance),
            passed=False,
            error=("Expected output field is not numeric."),
        )

    actual_value = float(raw_value)

    absolute_error = abs(actual_value - metric.expected_value)

    passed = absolute_error <= metric.absolute_tolerance

    return GroundTruthMetricResult(
        tool_name=tool_name,
        field_path=(metric.field_path),
        expected_value=(metric.expected_value),
        actual_value=(actual_value),
        absolute_error=(absolute_error),
        tolerance=(metric.absolute_tolerance),
        passed=passed,
    )


def _extract_field(
    value: Any,
    field_path: str,
) -> tuple[
    bool,
    Any,
]:
    current = value

    for part in field_path.split("."):
        if not isinstance(
            current,
            Mapping,
        ):
            return (
                False,
                None,
            )

        if part not in current:
            return (
                False,
                None,
            )

        current = current[part]

    return (
        True,
        current,
    )
