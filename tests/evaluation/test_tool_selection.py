import pytest
from pydantic import ValidationError

from app.agent.contracts import (
    AgentHistory,
    AgentObservation,
    AgentRunResult,
)
from app.evaluation.contracts import (
    EvaluationCase,
)
from app.evaluation.tool_selection import (
    evaluate_tool_selection,
)
from app.llm.contracts import (
    GroundedClaim,
)
from app.tools.contracts import (
    ToolCall,
    ToolResult,
)


def build_observation(
    tool_name: str,
) -> AgentObservation:
    return AgentObservation(
        call=ToolCall(
            tool_name=tool_name,
            arguments={},
        ),
        result=ToolResult(
            tool_name=tool_name,
            success=True,
            output={
                "value": 1,
            },
        ),
    )


def build_result(
    tool_names: list[str],
) -> AgentRunResult:
    if not tool_names:
        return AgentRunResult(
            answer=("No tools were required."),
            status="completed",
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )

    observations = [build_observation(tool_name=tool_name) for tool_name in tool_names]

    evidence_steps = list(
        range(
            1,
            len(observations) + 1,
        )
    )

    evidence_ids = [f"tool_step_{step}" for step in evidence_steps]

    return AgentRunResult(
        answer=("The requested analysis was completed."),
        evidence_steps=(evidence_steps),
        grounded_claims=[
            GroundedClaim(
                statement=("The requested analysis was completed."),
                claim_type="fact",
                evidence_ids=(evidence_ids),
            )
        ],
        status="completed",
        steps_used=(len(observations) + 1),
        tool_calls=len(observations),
        tool_failures=0,
        history=AgentHistory(observations=(observations)),
    )


def build_case() -> EvaluationCase:
    return EvaluationCase(
        case_id=("revenue_decline_v1"),
        question=("What is affecting revenue performance?"),
        required_tools=[
            "analyze_revenue",
            "analyze_revenue_drivers",
        ],
        optional_tools=[
            "detect_revenue_anomalies",
        ],
    )


def test_evaluation_case_normalizes_text() -> None:
    case = EvaluationCase(
        case_id="  case_1  ",
        question="  Test question  ",
    )

    assert case.case_id == "case_1"

    assert case.question == "Test question"


def test_evaluation_case_rejects_duplicate_tools() -> None:
    with pytest.raises(ValidationError):
        EvaluationCase(
            case_id="case_1",
            question="Question",
            required_tools=[
                "analyze_revenue",
                "analyze_revenue",
            ],
        )


def test_evaluation_case_rejects_required_optional_overlap() -> None:
    with pytest.raises(ValidationError):
        EvaluationCase(
            case_id="case_1",
            question="Question",
            required_tools=[
                "analyze_revenue",
            ],
            optional_tools=[
                "analyze_revenue",
            ],
        )


def test_tool_selection_passes_with_required_tools() -> None:
    case = build_case()

    result = build_result(
        tool_names=[
            "analyze_revenue",
            "analyze_revenue_drivers",
        ]
    )

    evaluation = evaluate_tool_selection(
        case=case,
        result=result,
    )

    assert evaluation.passed is True

    assert evaluation.required_tool_coverage == 1.0

    assert evaluation.missing_required_tools == []

    assert evaluation.unexpected_tools == []


def test_tool_selection_passes_with_optional_tool() -> None:
    case = build_case()

    result = build_result(
        tool_names=[
            "analyze_revenue",
            "analyze_revenue_drivers",
            "detect_revenue_anomalies",
        ]
    )

    evaluation = evaluate_tool_selection(
        case=case,
        result=result,
    )

    assert evaluation.passed is True

    assert evaluation.required_tool_coverage == 1.0


def test_tool_selection_detects_missing_required_tool() -> None:
    case = build_case()

    result = build_result(
        tool_names=[
            "analyze_revenue",
        ]
    )

    evaluation = evaluate_tool_selection(
        case=case,
        result=result,
    )

    assert evaluation.passed is False

    assert evaluation.required_tool_coverage == 0.5

    assert evaluation.missing_required_tools == ["analyze_revenue_drivers"]


def test_tool_selection_detects_unexpected_tool() -> None:
    case = build_case()

    result = build_result(
        tool_names=[
            "analyze_revenue",
            "analyze_revenue_drivers",
            "unknown_tool",
        ]
    )

    evaluation = evaluate_tool_selection(
        case=case,
        result=result,
    )

    assert evaluation.passed is False

    assert evaluation.unexpected_tools == ["unknown_tool"]


def test_tool_selection_with_no_required_tools_has_full_coverage() -> None:
    case = EvaluationCase(
        case_id="simple_case",
        question="Say hello.",
        required_tools=[],
        optional_tools=[],
    )

    result = build_result(tool_names=[])

    evaluation = evaluate_tool_selection(
        case=case,
        result=result,
    )

    assert evaluation.passed is True

    assert evaluation.required_tool_coverage == 1.0
