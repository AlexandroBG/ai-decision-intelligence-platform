import pytest

from app.evaluation.summary import (
    build_multi_run_summary,
)


def build_quality_run(
    *,
    passed: bool = True,
    completed: bool = True,
    tool_selection_passed: bool = True,
    ground_truth_passed: bool = True,
    semantic_passed: bool = True,
    steps_used: int = 3,
    tool_calls: int = 2,
    successful_tool_calls: int = 2,
    tool_failures: int = 0,
    duplicate_tool_calls: int = 0,
    duration_ms: float = 1000.0,
) -> dict[str, object]:
    return {
        "run_type": "quality_result",
        "overall_passed": passed,
        "duration_ms": duration_ms,
        "agent_metrics": {
            "completed": completed,
            "steps_used": steps_used,
            "tool_calls": tool_calls,
            "successful_tool_calls": successful_tool_calls,
            "tool_failures": tool_failures,
            "duplicate_tool_calls": duplicate_tool_calls,
        },
        "tool_selection": {
            "passed": tool_selection_passed,
        },
        "ground_truth": {
            "passed": ground_truth_passed,
        },
        "semantic_evaluation": {
            "passed": semantic_passed,
        },
    }


def build_provider_error_run() -> dict[
    str,
    object,
]:
    return {
        "run_type": "provider_error",
        "overall_passed": None,
        "provider_error": {
            "kind": "rate_or_quota_limit",
        },
    }


def test_summary_for_successful_runs() -> None:
    runs = [
        build_quality_run(),
        build_quality_run(),
        build_quality_run(),
    ]

    summary = build_multi_run_summary(
        requested_runs=3,
        runs=runs,
    )

    assert summary.requested_runs == 3
    assert summary.attempted_runs == 3
    assert summary.evaluated_runs == 3
    assert summary.provider_errors == 0
    assert summary.passed_runs == 3

    assert summary.quality_pass_rate == 1.0
    assert summary.completion_rate == 1.0
    assert summary.tool_selection_pass_rate == 1.0
    assert summary.ground_truth_pass_rate == 1.0
    assert summary.semantic_pass_rate == 1.0

    assert summary.tool_success_rate == 1.0
    assert summary.duplicate_tool_call_rate == 0.0

    assert summary.average_steps == 3.0
    assert summary.average_tool_calls == 2.0
    assert summary.average_tool_failures == 0.0
    assert summary.average_latency_ms == 1000.0

    assert summary.requested_run_evaluation_rate == 1.0


def test_summary_separates_provider_error() -> None:
    runs = [
        build_quality_run(),
        build_provider_error_run(),
    ]

    summary = build_multi_run_summary(
        requested_runs=3,
        runs=runs,
    )

    assert summary.attempted_runs == 2
    assert summary.evaluated_runs == 1
    assert summary.provider_errors == 1

    assert summary.quality_pass_rate == 1.0
    assert summary.average_tool_failures == 0.0
    assert summary.average_latency_ms == 1000.0

    assert summary.requested_run_evaluation_rate == pytest.approx(1 / 3)


def test_summary_uses_none_when_no_quality_runs() -> None:
    runs = [
        build_provider_error_run(),
    ]

    summary = build_multi_run_summary(
        requested_runs=3,
        runs=runs,
    )

    assert summary.evaluated_runs == 0
    assert summary.provider_errors == 1

    assert summary.quality_pass_rate is None
    assert summary.completion_rate is None
    assert summary.tool_selection_pass_rate is None
    assert summary.ground_truth_pass_rate is None
    assert summary.semantic_pass_rate is None

    assert summary.tool_success_rate is None
    assert summary.duplicate_tool_call_rate is None

    assert summary.average_steps is None
    assert summary.average_tool_calls is None
    assert summary.average_tool_failures is None
    assert summary.average_latency_ms is None


def test_summary_uses_none_when_quality_runs_have_no_tool_calls() -> None:
    runs = [
        build_quality_run(
            steps_used=1,
            tool_calls=0,
            successful_tool_calls=0,
            tool_failures=0,
        )
    ]

    summary = build_multi_run_summary(
        requested_runs=1,
        runs=runs,
    )

    assert summary.tool_success_rate is None
    assert summary.duplicate_tool_call_rate is None

    assert summary.average_tool_calls == 0.0
    assert summary.average_tool_failures == 0.0


def test_summary_tracks_partial_quality_failures() -> None:
    runs = [
        build_quality_run(),
        build_quality_run(
            passed=False,
            semantic_passed=False,
        ),
    ]

    summary = build_multi_run_summary(
        requested_runs=2,
        runs=runs,
    )

    assert summary.quality_pass_rate == 0.5
    assert summary.semantic_pass_rate == 0.5
    assert summary.ground_truth_pass_rate == 1.0


def test_summary_calculates_average_tool_failures() -> None:
    runs = [
        build_quality_run(
            tool_calls=2,
            successful_tool_calls=2,
            tool_failures=0,
        ),
        build_quality_run(
            tool_calls=4,
            successful_tool_calls=2,
            tool_failures=2,
        ),
    ]

    summary = build_multi_run_summary(
        requested_runs=2,
        runs=runs,
    )

    assert summary.average_tool_failures == 1.0

    assert summary.tool_success_rate == pytest.approx(4 / 6)


def test_summary_calculates_average_latency() -> None:
    runs = [
        build_quality_run(
            duration_ms=800.0,
        ),
        build_quality_run(
            duration_ms=1200.0,
        ),
        build_quality_run(
            duration_ms=1600.0,
        ),
    ]

    summary = build_multi_run_summary(
        requested_runs=3,
        runs=runs,
    )

    assert summary.average_latency_ms == 1200.0


def test_summary_rejects_invalid_requested_runs() -> None:
    with pytest.raises(
        ValueError,
        match="requested_runs must be greater than zero",
    ):
        build_multi_run_summary(
            requested_runs=0,
            runs=[],
        )
