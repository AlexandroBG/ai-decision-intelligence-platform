from app.evaluation.error_report import (
    build_error_report,
    collect_suite_runs,
)


def build_successful_run() -> dict[
    str,
    object,
]:
    return {
        "run": 1,
        "case_id": "case_a",
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


def test_empty_report_has_no_errors() -> None:
    report = build_error_report(runs=[])

    assert report.total_runs_analyzed == 0

    assert report.total_errors == 0

    assert report.top_error_code is None


def test_successful_run_has_no_errors() -> None:
    report = build_error_report(runs=[build_successful_run()])

    assert report.total_runs_analyzed == 1

    assert report.runs_with_errors == 0

    assert report.total_errors == 0


def test_report_aggregates_errors() -> None:
    run = build_successful_run()

    run["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    run["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": True,
        "overlap_summing_risk": False,
        "failed_checks": [
            "no_causal_overclaim",
            "no_unsupported_certainty",
        ],
    }

    report = build_error_report(runs=[run])

    assert report.total_errors == 3

    assert report.high_severity_errors == 2

    assert report.medium_severity_errors == 1

    category_counts = {item.name: item.count for item in report.errors_by_category}

    assert category_counts["semantic"] == 2

    assert category_counts["tool_selection"] == 1


def test_report_tracks_top_error_code() -> None:
    run_one = build_successful_run()

    run_one["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    run_two = build_successful_run()

    run_two["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    report = build_error_report(
        runs=[
            run_one,
            run_two,
        ]
    )

    assert report.top_error_code == "causal_overclaim"

    assert report.errors_by_code[0].count == 2


def test_report_tracks_provider_error() -> None:
    run = {
        "run": 1,
        "case_id": "case_a",
        "run_type": ("provider_error"),
        "provider_error": {
            "kind": ("rate_or_quota_limit"),
        },
    }

    report = build_error_report(runs=[run])

    assert report.total_errors == 1

    assert report.medium_severity_errors == 1

    assert report.errors_by_category[0].name == "provider"


def test_collect_suite_runs_flattens_cases() -> None:
    run_one = build_successful_run()

    run_two = build_successful_run()

    case_results = [
        {
            "case_id": "case_a",
            "runs": [run_one],
        },
        {
            "case_id": "case_b",
            "runs": [run_two],
        },
    ]

    runs = collect_suite_runs(case_results=(case_results))

    assert len(runs) == 2
