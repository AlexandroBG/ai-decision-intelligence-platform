from app.evaluation.contracts import (
    EvaluationCase,
    ExpectedNumericMetric,
    ExpectedToolOutput,
)


def build_revenue_decline_v1_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="revenue_decline_v1",
        question=(
            "Compare revenue from 2025-07-01 to 2025-07-31 "
            "with 2025-08-01 to 2025-08-31. "
            "What is affecting revenue performance, "
            "and what should I investigate first?"
        ),
        required_tools=[
            "analyze_revenue",
            "analyze_revenue_drivers",
        ],
        optional_tools=[
            "detect_revenue_anomalies",
        ],
        expected_outputs=[
            ExpectedToolOutput(
                tool_name="analyze_revenue",
                metrics=[
                    ExpectedNumericMetric(
                        field_path="baseline_revenue",
                        expected_value=1773419.93,
                        absolute_tolerance=0.01,
                    ),
                    ExpectedNumericMetric(
                        field_path="comparison_revenue",
                        expected_value=1275769.95,
                        absolute_tolerance=0.01,
                    ),
                    ExpectedNumericMetric(
                        field_path="absolute_change",
                        expected_value=-497649.98,
                        absolute_tolerance=0.01,
                    ),
                    ExpectedNumericMetric(
                        field_path="percentage_change",
                        expected_value=-28.06,
                        absolute_tolerance=0.01,
                    ),
                ],
            ),
        ],
    )
