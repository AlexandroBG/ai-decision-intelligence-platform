import pytest
from pydantic import ValidationError

from app.agent.contracts import (
    AgentDecision,
    AgentFinalAction,
    AgentHistory,
    AgentRunResult,
    AgentToolAction,
)


def build_success_history() -> dict:
    return {
        "observations": [
            {
                "call": {
                    "tool_name": "analyze_revenue",
                },
                "result": {
                    "tool_name": "analyze_revenue",
                    "success": True,
                },
            }
        ]
    }


def build_failed_history() -> dict:
    return {
        "observations": [
            {
                "call": {
                    "tool_name": "missing_tool",
                },
                "result": {
                    "tool_name": "missing_tool",
                    "success": False,
                    "error": "Unknown tool.",
                },
            }
        ]
    }


def build_grounded_claim(
    evidence_id: str = "tool_step_1",
) -> dict:
    return {
        "statement": "Revenue declined.",
        "claim_type": "fact",
        "evidence_ids": [
            evidence_id,
        ],
    }


def test_agent_tool_action_accepts_valid_call() -> None:
    action = AgentToolAction(
        action_type="tool_call",
        call={
            "tool_name": "analyze_revenue",
            "arguments": {
                "baseline_start": "2025-07-01",
            },
        },
    )

    assert action.action_type == "tool_call"

    assert action.call.tool_name == "analyze_revenue"


def test_agent_tool_action_normalizes_tool_name() -> None:
    action = AgentToolAction(
        action_type="tool_call",
        call={
            "tool_name": "  analyze_revenue  ",
        },
    )

    assert action.call.tool_name == "analyze_revenue"


def test_agent_tool_action_rejects_empty_tool_name() -> None:
    with pytest.raises(ValidationError):
        AgentToolAction(
            action_type="tool_call",
            call={
                "tool_name": "   ",
            },
        )


def test_agent_final_action_accepts_answer() -> None:
    action = AgentFinalAction(
        action_type="final",
        answer="Revenue declined.",
    )

    assert action.answer == "Revenue declined."

    assert action.evidence_steps == []
    assert action.grounded_claims == []


def test_agent_final_action_strips_answer() -> None:
    action = AgentFinalAction(
        action_type="final",
        answer="  Revenue declined.  ",
    )

    assert action.answer == "Revenue declined."


def test_agent_final_action_accepts_evidence_steps() -> None:
    action = AgentFinalAction(
        action_type="final",
        answer="Revenue declined.",
        evidence_steps=[
            1,
            2,
        ],
    )

    assert action.evidence_steps == [
        1,
        2,
    ]


def test_agent_final_action_accepts_grounded_claims() -> None:
    action = AgentFinalAction(
        action_type="final",
        answer="Revenue declined.",
        evidence_steps=[
            1,
        ],
        grounded_claims=[build_grounded_claim()],
    )

    assert len(action.grounded_claims) == 1

    assert action.grounded_claims[0].evidence_ids == [
        "tool_step_1",
    ]


def test_agent_final_action_rejects_zero_evidence_step() -> None:
    with pytest.raises(
        ValidationError,
        match=("Evidence steps must be positive integers."),
    ):
        AgentFinalAction(
            action_type="final",
            answer="Revenue declined.",
            evidence_steps=[
                0,
            ],
        )


def test_agent_final_action_rejects_negative_evidence_step() -> None:
    with pytest.raises(
        ValidationError,
        match=("Evidence steps must be positive integers."),
    ):
        AgentFinalAction(
            action_type="final",
            answer="Revenue declined.",
            evidence_steps=[
                -1,
            ],
        )


def test_agent_final_action_rejects_duplicate_evidence_steps() -> None:
    with pytest.raises(
        ValidationError,
        match=("Evidence steps must not contain duplicates."),
    ):
        AgentFinalAction(
            action_type="final",
            answer="Revenue declined.",
            evidence_steps=[
                1,
                1,
            ],
        )


def test_agent_final_action_rejects_empty_answer() -> None:
    with pytest.raises(ValidationError):
        AgentFinalAction(
            action_type="final",
            answer="   ",
        )


def test_agent_decision_accepts_tool_action() -> None:
    decision = AgentDecision(
        action={
            "action_type": "tool_call",
            "call": {
                "tool_name": "analyze_revenue",
                "arguments": {},
            },
        }
    )

    assert isinstance(
        decision.action,
        AgentToolAction,
    )


def test_agent_decision_accepts_final_action() -> None:
    decision = AgentDecision(
        action={
            "action_type": "final",
            "answer": "Investigation complete.",
            "evidence_steps": [],
            "grounded_claims": [],
        }
    )

    assert isinstance(
        decision.action,
        AgentFinalAction,
    )


def test_agent_decision_accepts_grounded_final_action() -> None:
    decision = AgentDecision(
        action={
            "action_type": "final",
            "answer": "Revenue declined.",
            "evidence_steps": [
                1,
            ],
            "grounded_claims": [build_grounded_claim()],
        }
    )

    assert isinstance(
        decision.action,
        AgentFinalAction,
    )

    assert decision.action.evidence_steps == [
        1,
    ]

    assert len(decision.action.grounded_claims) == 1


def test_agent_decision_rejects_unknown_action_type() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action={
                "action_type": "unknown",
            }
        )


def test_agent_decision_rejects_tool_action_without_call() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action={
                "action_type": "tool_call",
            }
        )


def test_agent_decision_rejects_final_action_without_answer() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action={
                "action_type": "final",
            }
        )


def test_agent_decision_rejects_mixed_action() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "call": {
                    "tool_name": "analyze_revenue",
                },
            }
        )


def test_agent_run_result_accepts_completed_run_without_tools() -> None:
    result = AgentRunResult(
        answer="Done.",
        evidence_steps=[],
        grounded_claims=[],
        status="completed",
        termination_reason=None,
        steps_used=1,
        tool_calls=0,
        tool_failures=0,
        history=AgentHistory(),
    )

    assert result.answer == "Done."
    assert result.status == "completed"
    assert result.evidence_steps == []
    assert result.grounded_claims == []


def test_agent_run_result_accepts_completed_run_with_evidence() -> None:
    result = AgentRunResult(
        answer="Revenue declined.",
        evidence_steps=[
            1,
        ],
        grounded_claims=[build_grounded_claim()],
        status="completed",
        termination_reason=None,
        steps_used=2,
        tool_calls=1,
        tool_failures=0,
        history=build_success_history(),
    )

    assert result.answer == ("Revenue declined.")

    assert result.evidence_steps == [
        1,
    ]

    assert len(result.grounded_claims) == 1


def test_agent_run_result_accepts_guardrail_termination() -> None:
    result = AgentRunResult(
        answer=None,
        evidence_steps=[],
        grounded_claims=[],
        status="max_steps_reached",
        termination_reason=("Maximum number of steps reached."),
        steps_used=1,
        tool_calls=0,
        tool_failures=0,
        history=AgentHistory(),
    )

    assert result.answer is None

    assert result.status == "max_steps_reached"


def test_completed_run_requires_answer() -> None:
    with pytest.raises(
        ValidationError,
        match=("Completed runs must include an answer."),
    ):
        AgentRunResult(
            answer=None,
            evidence_steps=[],
            grounded_claims=[],
            status="completed",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_completed_run_with_tools_requires_evidence() -> None:
    with pytest.raises(
        ValidationError,
        match=("Completed runs with tool observations must include evidence steps."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[],
            grounded_claims=[build_grounded_claim()],
            status="completed",
            termination_reason=None,
            steps_used=2,
            tool_calls=1,
            tool_failures=0,
            history=build_success_history(),
        )


def test_completed_run_with_tools_requires_grounded_claims() -> None:
    with pytest.raises(
        ValidationError,
        match=("Completed runs with tool observations must include grounded claims."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[
                1,
            ],
            grounded_claims=[],
            status="completed",
            termination_reason=None,
            steps_used=2,
            tool_calls=1,
            tool_failures=0,
            history=build_success_history(),
        )


def test_completed_run_without_tools_rejects_evidence() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "Completed runs without tool observations must not include evidence steps."
        ),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[
                1,
            ],
            grounded_claims=[],
            status="completed",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_completed_run_without_tools_rejects_grounded_claims() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "Completed runs without tool observations must not include grounded claims."
        ),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[],
            grounded_claims=[build_grounded_claim()],
            status="completed",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_completed_run_rejects_unknown_evidence_step() -> None:
    with pytest.raises(
        ValidationError,
        match=("Evidence steps must reference existing history observations."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[
                2,
            ],
            grounded_claims=[build_grounded_claim(evidence_id="tool_step_2")],
            status="completed",
            termination_reason=None,
            steps_used=2,
            tool_calls=1,
            tool_failures=0,
            history=build_success_history(),
        )


def test_completed_run_rejects_termination_reason() -> None:
    with pytest.raises(
        ValidationError,
        match=("Completed runs must not include a termination reason."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[],
            grounded_claims=[],
            status="completed",
            termination_reason="Stopped.",
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_guardrail_run_rejects_answer() -> None:
    with pytest.raises(
        ValidationError,
        match=("Guardrail-terminated runs must not include a final answer."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[],
            grounded_claims=[],
            status="max_steps_reached",
            termination_reason="Stopped.",
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_guardrail_run_requires_reason() -> None:
    with pytest.raises(
        ValidationError,
        match=("Guardrail-terminated runs must include a termination reason."),
    ):
        AgentRunResult(
            answer=None,
            evidence_steps=[],
            grounded_claims=[],
            status="max_steps_reached",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_guardrail_run_rejects_final_evidence_steps() -> None:
    with pytest.raises(
        ValidationError,
        match=("Guardrail-terminated runs must not include final evidence steps."),
    ):
        AgentRunResult(
            answer=None,
            evidence_steps=[
                1,
            ],
            grounded_claims=[],
            status="max_steps_reached",
            termination_reason="Stopped.",
            steps_used=2,
            tool_calls=1,
            tool_failures=0,
            history=build_success_history(),
        )


def test_guardrail_run_rejects_grounded_claims() -> None:
    with pytest.raises(
        ValidationError,
        match=("Guardrail-terminated runs must not include grounded claims."),
    ):
        AgentRunResult(
            answer=None,
            evidence_steps=[],
            grounded_claims=[build_grounded_claim()],
            status="max_steps_reached",
            termination_reason="Stopped.",
            steps_used=2,
            tool_calls=1,
            tool_failures=0,
            history=build_success_history(),
        )


def test_agent_run_result_rejects_empty_answer() -> None:
    with pytest.raises(ValidationError):
        AgentRunResult(
            answer="   ",
            evidence_steps=[],
            grounded_claims=[],
            status="completed",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_agent_run_result_rejects_wrong_tool_call_count() -> None:
    with pytest.raises(
        ValidationError,
        match=("tool_calls must match the number of history observations."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[
                1,
            ],
            grounded_claims=[build_grounded_claim()],
            status="completed",
            termination_reason=None,
            steps_used=2,
            tool_calls=0,
            tool_failures=0,
            history=build_success_history(),
        )


def test_agent_run_result_rejects_failure_count_above_calls() -> None:
    with pytest.raises(
        ValidationError,
        match=("tool_failures cannot exceed tool_calls."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[],
            grounded_claims=[],
            status="completed",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=1,
            history=AgentHistory(),
        )


def test_agent_run_result_rejects_wrong_failure_count() -> None:
    with pytest.raises(
        ValidationError,
        match=("tool_failures must match failed history observations."),
    ):
        AgentRunResult(
            answer="Done.",
            evidence_steps=[
                1,
            ],
            grounded_claims=[build_grounded_claim()],
            status="completed",
            termination_reason=None,
            steps_used=2,
            tool_calls=1,
            tool_failures=0,
            history=build_failed_history(),
        )
