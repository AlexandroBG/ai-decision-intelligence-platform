import pytest

from app.agent.contracts import (
    AgentHistory,
    AgentObservation,
    AgentRunResult,
)
from app.evaluation.metrics import (
    build_evaluation_summary,
    evaluate_run,
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
    arguments: dict[str, object],
    success: bool = True,
) -> AgentObservation:
    return AgentObservation(
        call=ToolCall(
            tool_name=tool_name,
            arguments=arguments,
        ),
        result=ToolResult(
            tool_name=tool_name,
            success=success,
            output=({"value": 1} if success else None),
            error=(None if success else "Expected tool failure."),
        ),
    )


def build_completed_result(
    observations: list[AgentObservation],
) -> AgentRunResult:
    if not observations:
        return AgentRunResult(
            answer="No tool evidence was required.",
            status="completed",
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )

    evidence_steps = list(
        range(
            1,
            len(observations) + 1,
        )
    )

    evidence_ids = [f"tool_step_{step}" for step in evidence_steps]

    return AgentRunResult(
        answer=("Revenue performance was analyzed."),
        evidence_steps=(evidence_steps),
        grounded_claims=[
            GroundedClaim(
                statement=("Revenue performance was analyzed."),
                claim_type="fact",
                evidence_ids=(evidence_ids),
            )
        ],
        status="completed",
        steps_used=(len(observations) + 1),
        tool_calls=(len(observations)),
        tool_failures=sum(
            1 for observation in observations if not observation.result.success
        ),
        history=AgentHistory(observations=(observations)),
    )


def test_evaluate_run_for_successful_completed_run() -> None:
    observations = [
        build_observation(
            tool_name="analyze_revenue",
            arguments={
                "period": "august",
            },
        ),
        build_observation(
            tool_name=("analyze_revenue_drivers"),
            arguments={
                "period": "august",
            },
        ),
    ]

    result = build_completed_result(observations=observations)

    metrics = evaluate_run(result=result)

    assert metrics.completed is True
    assert metrics.steps_used == 3
    assert metrics.tool_calls == 2
    assert metrics.successful_tool_calls == 2
    assert metrics.tool_failures == 0
    assert metrics.tool_success_rate == 1.0
    assert metrics.duplicate_tool_calls == 0
    assert metrics.duplicate_tool_call_rate == 0.0


def test_evaluate_run_detects_duplicate_tool_calls() -> None:
    arguments = {
        "baseline_start": ("2025-07-01"),
        "comparison_start": ("2025-08-01"),
    }

    observations = [
        build_observation(
            tool_name="analyze_revenue",
            arguments=arguments,
        ),
        build_observation(
            tool_name="analyze_revenue",
            arguments=arguments,
        ),
    ]

    result = build_completed_result(observations=observations)

    metrics = evaluate_run(result=result)

    assert metrics.duplicate_tool_calls == 1

    assert metrics.duplicate_tool_call_rate == 0.5


def test_duplicate_detection_is_independent_of_argument_order() -> None:
    observations = [
        build_observation(
            tool_name="analyze_revenue",
            arguments={
                "a": 1,
                "b": 2,
            },
        ),
        build_observation(
            tool_name="analyze_revenue",
            arguments={
                "b": 2,
                "a": 1,
            },
        ),
    ]

    result = build_completed_result(observations=observations)

    metrics = evaluate_run(result=result)

    assert metrics.duplicate_tool_calls == 1


def test_evaluate_run_counts_tool_failure() -> None:
    observations = [
        build_observation(
            tool_name="analyze_revenue",
            arguments={
                "period": "august",
            },
            success=True,
        ),
        build_observation(
            tool_name=("detect_revenue_anomalies"),
            arguments={
                "period": "august",
            },
            success=False,
        ),
    ]

    result = build_completed_result(observations=observations)

    metrics = evaluate_run(result=result)

    assert metrics.tool_calls == 2

    assert metrics.successful_tool_calls == 1

    assert metrics.tool_failures == 1

    assert metrics.tool_success_rate == 0.5


def test_zero_tool_run_has_neutral_tool_rates() -> None:
    result = build_completed_result(observations=[])

    metrics = evaluate_run(result=result)

    assert metrics.tool_calls == 0

    assert metrics.tool_success_rate == 1.0

    assert metrics.duplicate_tool_call_rate == 0.0


def test_build_evaluation_summary() -> None:
    first_result = build_completed_result(
        observations=[
            build_observation(
                tool_name=("analyze_revenue"),
                arguments={
                    "period": "august",
                },
            ),
            build_observation(
                tool_name=("analyze_revenue_drivers"),
                arguments={
                    "period": "august",
                },
            ),
        ]
    )

    second_result = build_completed_result(
        observations=[
            build_observation(
                tool_name=("analyze_revenue"),
                arguments={
                    "period": "august",
                },
            ),
        ]
    )

    summary = build_evaluation_summary(
        results=[
            first_result,
            second_result,
        ]
    )

    assert summary.total_runs == 2
    assert summary.completed_runs == 2
    assert summary.completion_rate == 1.0

    assert summary.total_steps == 5

    assert summary.average_steps == 2.5

    assert summary.total_tool_calls == 3

    assert summary.average_tool_calls == 1.5

    assert summary.successful_tool_calls == 3

    assert summary.tool_success_rate == 1.0

    assert summary.duplicate_tool_calls == 0


def test_build_evaluation_summary_rejects_empty_input() -> None:
    with pytest.raises(
        ValueError,
        match=("Evaluation requires at least one agent run"),
    ):
        build_evaluation_summary(results=[])
