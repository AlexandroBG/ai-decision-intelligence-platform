from app.evaluation.analysis_report import (
    build_evaluation_analysis_report,
)


def build_successful_run() -> dict[
    str,
    object,
]:
    return {
        "run": 1,
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


def test_successful_runs_produce_clean_analysis() -> None:
    report = build_evaluation_analysis_report(runs=[build_successful_run()])

    assert report.total_runs_analyzed == 1

    assert report.total_errors == 0

    assert report.top_priority_code is None

    assert "No machine-detected" in report.recommended_action


def test_analysis_identifies_top_priority() -> None:
    run = build_successful_run()

    run["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    report = build_evaluation_analysis_report(runs=[run])

    assert report.total_errors == 1

    assert report.high_severity_errors == 1

    assert report.top_priority_code == "causal_overclaim"

    assert "causal_overclaim" in report.recommended_action


def test_analysis_combines_frequency_and_severity() -> None:
    semantic_run = build_successful_run()

    semantic_run["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    tool_run_one = build_successful_run()

    tool_run_one["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    tool_run_two = build_successful_run()

    tool_run_two["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    report = build_evaluation_analysis_report(
        runs=[
            semantic_run,
            tool_run_one,
            tool_run_two,
        ]
    )

    assert report.total_errors == 3

    assert report.top_priority_code == "unexpected_tool"

    assert report.priorities[0].priority_score == 4


def test_analysis_handles_provider_failure() -> None:
    run = {
        "run": 1,
        "case_id": ("revenue_decline_v1"),
        "run_type": ("provider_error"),
        "provider_error": {
            "kind": ("rate_or_quota_limit"),
        },
    }

    report = build_evaluation_analysis_report(runs=[run])

    assert report.total_errors == 1

    assert report.medium_severity_errors == 1

    assert report.top_priority_code == "rate_or_quota_limit"
