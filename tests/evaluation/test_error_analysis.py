from app.evaluation.error_analysis import (
    analyze_evaluation_run,
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


def test_successful_run_has_no_errors() -> None:
    run = build_successful_run()

    result = analyze_evaluation_run(run=run)

    assert result.total_errors == 0

    assert result.errors == []

    assert result.categories == []

    assert result.has_high_severity_error is False


def test_detects_missing_required_tool() -> None:
    run = build_successful_run()

    run["tool_selection"] = {
        "missing_required_tools": ["analyze_revenue"],
        "unexpected_tools": [],
    }

    result = analyze_evaluation_run(run=run)

    assert result.total_errors == 1

    assert result.errors[0].category == "tool_selection"

    assert result.errors[0].code == "missing_required_tool"

    assert result.errors[0].severity == "high"


def test_detects_unexpected_tool() -> None:
    run = build_successful_run()

    run["tool_selection"] = {
        "missing_required_tools": [],
        "unexpected_tools": ["detect_revenue_anomalies"],
    }

    result = analyze_evaluation_run(run=run)

    assert result.errors[0].code == "unexpected_tool"

    assert result.errors[0].severity == "medium"


def test_detects_ground_truth_failure() -> None:
    run = build_successful_run()

    run["ground_truth"] = {
        "passed": False,
    }

    result = analyze_evaluation_run(run=run)

    assert result.errors[0].code == "ground_truth_mismatch"

    assert result.has_high_severity_error is True


def test_detects_causal_overclaim() -> None:
    run = build_successful_run()

    run["semantic_evaluation"] = {
        "causal_overclaim": True,
        "unsupported_certainty": False,
        "overlap_summing_risk": False,
        "failed_checks": ["no_causal_overclaim"],
    }

    result = analyze_evaluation_run(run=run)

    assert result.errors[0].category == "semantic"

    assert result.errors[0].code == "causal_overclaim"

    assert result.has_high_severity_error is True


def test_detects_multiple_errors() -> None:
    run = build_successful_run()

    run["agent_metrics"] = {
        "completed": False,
        "duplicate_tool_calls": 1,
    }

    run["ground_truth"] = {
        "passed": False,
    }

    result = analyze_evaluation_run(run=run)

    assert result.total_errors == 3

    assert set(result.categories) == {
        "execution",
        "ground_truth",
    }


def test_provider_error_is_separate_category() -> None:
    run = {
        "run": 1,
        "case_id": ("revenue_decline_v1"),
        "run_type": ("provider_error"),
        "provider_error": {
            "kind": ("rate_or_quota_limit"),
        },
    }

    result = analyze_evaluation_run(run=run)

    assert result.total_errors == 1

    assert result.errors[0].category == "provider"

    assert result.errors[0].code == "rate_or_quota_limit"

    assert result.has_high_severity_error is False
