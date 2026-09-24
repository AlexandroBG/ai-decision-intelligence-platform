from app.evaluation.contracts import (
    EvaluationCase,
    ExpectedNumericMetric,
    ExpectedToolOutput,
)

BASELINE_REVENUE = 1773419.9302160002
COMPARISON_REVENUE = 1275769.9454039999
ABSOLUTE_CHANGE = -497649.9848120003
PERCENTAGE_CHANGE = -0.28061598741105115


def build_revenue_decline_v1_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="revenue_decline_v1",
        question=(
            "Compare revenue from 2025-07-01 to "
            "2025-07-31 with revenue from 2025-08-01 "
            "to 2025-08-31. What is affecting revenue "
            "performance, and what should I investigate first?"
        ),
        required_tools=[
            "analyze_revenue",
            "analyze_revenue_drivers",
        ],
        optional_tools=[
            "detect_revenue_anomalies",
        ],
        expected_outputs=[
            _build_revenue_ground_truth(),
        ],
    )


def build_revenue_comparison_only_v1_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="revenue_comparison_only_v1",
        question=(
            "Compare total revenue from 2025-07-01 to "
            "2025-07-31 with total revenue from 2025-08-01 "
            "to 2025-08-31. Report the revenue change only. "
            "Do not analyze drivers, segments, categories, "
            "regions, channels, or anomalies."
        ),
        required_tools=[
            "analyze_revenue",
        ],
        optional_tools=[],
        expected_outputs=[
            _build_revenue_ground_truth(),
        ],
    )


def _build_revenue_ground_truth() -> ExpectedToolOutput:
    return ExpectedToolOutput(
        tool_name="analyze_revenue",
        metrics=[
            ExpectedNumericMetric(
                field_path="baseline_revenue",
                expected_value=BASELINE_REVENUE,
                absolute_tolerance=0.01,
            ),
            ExpectedNumericMetric(
                field_path="comparison_revenue",
                expected_value=COMPARISON_REVENUE,
                absolute_tolerance=0.01,
            ),
            ExpectedNumericMetric(
                field_path="absolute_change",
                expected_value=ABSOLUTE_CHANGE,
                absolute_tolerance=0.01,
            ),
            ExpectedNumericMetric(
                field_path="percentage_change",
                expected_value=PERCENTAGE_CHANGE,
                absolute_tolerance=0.000001,
            ),
        ],
    )
