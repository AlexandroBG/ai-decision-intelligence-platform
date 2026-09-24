import pytest

from app.evaluation.cases import (
    ABSOLUTE_CHANGE,
    BASELINE_REVENUE,
    COMPARISON_REVENUE,
    PERCENTAGE_CHANGE,
    build_revenue_comparison_only_v1_case,
    build_revenue_decline_v1_case,
)


def test_build_revenue_decline_v1_case() -> None:
    case = build_revenue_decline_v1_case()

    assert case.case_id == "revenue_decline_v1"

    assert case.required_tools == [
        "analyze_revenue",
        "analyze_revenue_drivers",
    ]

    assert case.optional_tools == [
        "detect_revenue_anomalies",
    ]

    assert len(case.expected_outputs) == 1

    expected_output = case.expected_outputs[0]

    assert expected_output.tool_name == "analyze_revenue"

    metrics = {metric.field_path: metric for metric in expected_output.metrics}

    assert metrics["baseline_revenue"].expected_value == pytest.approx(BASELINE_REVENUE)

    assert metrics["comparison_revenue"].expected_value == pytest.approx(
        COMPARISON_REVENUE
    )

    assert metrics["absolute_change"].expected_value == pytest.approx(ABSOLUTE_CHANGE)

    assert metrics["percentage_change"].expected_value == pytest.approx(
        PERCENTAGE_CHANGE
    )


def test_build_revenue_comparison_only_v1_case() -> None:
    case = build_revenue_comparison_only_v1_case()

    assert case.case_id == "revenue_comparison_only_v1"

    assert case.required_tools == [
        "analyze_revenue",
    ]

    assert case.optional_tools == []

    assert len(case.expected_outputs) == 1

    assert case.expected_outputs[0].tool_name == "analyze_revenue"


def test_comparison_only_case_forbids_extra_tools_by_expectation() -> None:
    case = build_revenue_comparison_only_v1_case()

    allowed_tools = set(case.required_tools) | set(case.optional_tools)

    assert allowed_tools == {
        "analyze_revenue",
    }


def test_cases_share_same_numeric_ground_truth() -> None:
    decline_case = build_revenue_decline_v1_case()

    comparison_case = build_revenue_comparison_only_v1_case()

    decline_metrics = {
        metric.field_path: (metric.expected_value)
        for metric in decline_case.expected_outputs[0].metrics
    }

    comparison_metrics = {
        metric.field_path: (metric.expected_value)
        for metric in comparison_case.expected_outputs[0].metrics
    }

    assert decline_metrics == comparison_metrics
