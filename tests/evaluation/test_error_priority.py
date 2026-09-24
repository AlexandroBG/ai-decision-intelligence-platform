from app.evaluation.error_priority import (
    build_error_priority_report,
)


def build_successful_run(
    run_number: int = 1,
) -> dict[
    str,
    object,
]:
    return {
        "run": run_number,
        "case_id": ("revenue_decline_v1"),
        "run_type": ("quality_result"),
        "agent_metrics": {
            "completed": True,
            "duplicate_tool_calls": 0,
        },
        "tool_selection": {
            "missing_required_tools": [],
            "unexpected_tools": [],
        },
        "ground_truth": {
            "passed": True,
        },
        "semantic_evaluation": {
            "causal_overclaim": False,
            "unsupported_certainty": False,
            "overlap_summing_risk": False,
            "failed_checks": [],
        },
    }


def test_empty_priority_report() -> None:
    report = build_error_priority_report(runs=[])

    assert report.total_prioritized_errors == 0

    assert report.priorities == []

    assert report.top_priority_code is None


def test_successful_runs_have_no_priorities() -> None:
    runs = [
        build_successful_run(),
        build_successful_run(run_number=2),
    ]

    report = build_error_priority_report(runs=runs)

    assert report.total_prioritized_errors == 0


def test_high_severity_error_gets_weight_three() -> None:
    run = build_successful_run()

    run["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    report = build_error_priority_report(runs=[run])

    priority = report.priorities[0]

    assert priority.code == "causal_overclaim"

    assert priority.severity == "high"

    assert priority.severity_weight == 3

    assert priority.priority_score == 3


def test_medium_severity_error_gets_weight_two() -> None:
    run = build_successful_run()

    run["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    report = build_error_priority_report(runs=[run])

    priority = report.priorities[0]

    assert priority.code == "unexpected_tool"

    assert priority.severity == "medium"

    assert priority.priority_score == 2


def test_frequency_increases_priority_score() -> None:
    runs = []

    for run_number in range(
        1,
        4,
    ):
        run = build_successful_run(run_number=(run_number))

        run["semantic_evaluation"] = {
            "causal_overclaim": True,
            "unsupported_certainty": False,
            "overlap_summing_risk": False,
            "failed_checks": ["no_causal_overclaim"],
        }

        runs.append(run)

    report = build_error_priority_report(runs=runs)

    priority = report.priorities[0]

    assert priority.occurrences == 3

    assert priority.priority_score == 9


def test_report_orders_by_priority_score() -> None:
    causal_run = build_successful_run(run_number=1)

    causal_run["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    tool_run_one = build_successful_run(run_number=2)

    tool_run_one["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    tool_run_two = build_successful_run(run_number=3)

    tool_run_two["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    report = build_error_priority_report(
        runs=[
            causal_run,
            tool_run_one,
            tool_run_two,
        ]
    )

    assert report.priorities[0].code == "unexpected_tool"

    assert report.priorities[0].priority_score == 4

    assert report.priorities[1].code == "causal_overclaim"

    assert report.priorities[1].priority_score == 3


def test_severity_breaks_equal_score_tie() -> None:
    causal_runs = []

    for run_number in (
        1,
        2,
    ):
        run = build_successful_run(run_number=(run_number))

        run["semantic_evaluation"] = {
            "causal_overclaim": True,
            "unsupported_certainty": False,
            "overlap_summing_risk": False,
            "failed_checks": ["no_causal_overclaim"],
        }

        causal_runs.append(run)

    tool_runs = []

    for run_number in (
        3,
        4,
        5,
    ):
        run = build_successful_run(run_number=(run_number))

        run["tool_selection"] = {
            "missing_required_tools": [],
            "unexpected_tools": ["detect_revenue_anomalies"],
        }

        tool_runs.append(run)

    report = build_error_priority_report(runs=(causal_runs + tool_runs))

    assert report.priorities[0].priority_score == 6

    assert report.priorities[1].priority_score == 6

    assert report.priorities[0].code == "causal_overclaim"

    assert report.top_priority_code == "causal_overclaim"


def test_provider_error_is_prioritized() -> None:
    run = {
        "run": 1,
        "case_id": ("revenue_decline_v1"),
        "run_type": ("provider_error"),
        "provider_error": {
            "kind": ("rate_or_quota_limit"),
        },
    }

    report = build_error_priority_report(runs=[run])

    priority = report.priorities[0]

    assert priority.category == "provider"

    assert priority.severity == "medium"

    assert priority.priority_score == 2
