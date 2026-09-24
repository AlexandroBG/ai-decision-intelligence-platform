from app.agent.contracts import (
    AgentHistory,
    AgentObservation,
    AgentRunResult,
)
from app.evaluation.contracts import (
    EvaluationCase,
    ExpectedNumericMetric,
    ExpectedToolOutput,
)
from app.evaluation.ground_truth import (
    evaluate_ground_truth,
)
from app.llm.contracts import (
    GroundedClaim,
)
from app.tools.contracts import (
    ToolCall,
    ToolResult,
)


def build_result(
    output: dict[str, object],
    tool_name: str = "analyze_revenue",
) -> AgentRunResult:
    observation = AgentObservation(
        call=ToolCall(
            tool_name=tool_name,
            arguments={},
        ),
        result=ToolResult(
            tool_name=tool_name,
            success=True,
            output=output,
        ),
    )

    return AgentRunResult(
        answer=("Revenue was analyzed."),
        evidence_steps=[1],
        grounded_claims=[
            GroundedClaim(
                statement=("Revenue was analyzed."),
                claim_type="fact",
                evidence_ids=["tool_step_1"],
            )
        ],
        status="completed",
        steps_used=2,
        tool_calls=1,
        tool_failures=0,
        history=AgentHistory(observations=[observation]),
    )


def build_case(
    expected_value: float = -497649.98,
    tolerance: float = 0.01,
) -> EvaluationCase:
    return EvaluationCase(
        case_id=("revenue_decline_v1"),
        question=("Compare July and August revenue."),
        required_tools=["analyze_revenue"],
        expected_outputs=[
            ExpectedToolOutput(
                tool_name=("analyze_revenue"),
                metrics=[
                    ExpectedNumericMetric(
                        field_path=("absolute_change"),
                        expected_value=(expected_value),
                        absolute_tolerance=(tolerance),
                    )
                ],
            )
        ],
    )


def test_ground_truth_passes_exact_value() -> None:
    case = build_case()

    result = build_result(
        output={
            "absolute_change": (-497649.98),
        }
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    assert evaluation.total_checks == 1

    assert evaluation.passed_checks == 1

    assert evaluation.score == 1.0

    assert evaluation.passed is True


def test_ground_truth_passes_value_within_tolerance() -> None:
    case = build_case(
        expected_value=-28.06,
        tolerance=0.01,
    )

    result = build_result(
        output={
            "absolute_change": (-28.055),
        }
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    assert evaluation.passed is True


def test_ground_truth_fails_wrong_value() -> None:
    case = build_case()

    result = build_result(
        output={
            "absolute_change": (-350000.00),
        }
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    metric = evaluation.results[0]

    assert evaluation.passed is False

    assert evaluation.score == 0.0

    assert metric.actual_value == -350000.00

    assert metric.absolute_error is not None


def test_ground_truth_supports_nested_field_path() -> None:
    case = EvaluationCase(
        case_id="nested_case",
        question="Question",
        required_tools=["analyze_revenue"],
        expected_outputs=[
            ExpectedToolOutput(
                tool_name=("analyze_revenue"),
                metrics=[
                    ExpectedNumericMetric(
                        field_path=("revenue.absolute_change"),
                        expected_value=(-497649.98),
                    )
                ],
            )
        ],
    )

    result = build_result(
        output={
            "revenue": {
                "absolute_change": (-497649.98),
            }
        }
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    assert evaluation.passed is True


def test_ground_truth_fails_when_field_is_missing() -> None:
    case = build_case()

    result = build_result(
        output={
            "percentage_change": (-28.06),
        }
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    metric = evaluation.results[0]

    assert evaluation.passed is False

    assert metric.actual_value is None

    assert metric.error == ("Expected output field was not found.")


def test_ground_truth_fails_when_tool_was_not_used() -> None:
    case = build_case()

    result = build_result(
        output={
            "absolute_change": (-497649.98),
        },
        tool_name=("analyze_revenue_drivers"),
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    metric = evaluation.results[0]

    assert evaluation.passed is False

    assert metric.error == ("Successful tool observation not found.")


def test_ground_truth_without_expected_outputs_is_neutral() -> None:
    case = EvaluationCase(
        case_id="no_ground_truth",
        question="Say hello.",
    )

    result = AgentRunResult(
        answer="Hello.",
        status="completed",
        steps_used=1,
        tool_calls=0,
        tool_failures=0,
        history=AgentHistory(),
    )

    evaluation = evaluate_ground_truth(
        case=case,
        result=result,
    )

    assert evaluation.total_checks == 0

    assert evaluation.score == 1.0

    assert evaluation.passed is True
