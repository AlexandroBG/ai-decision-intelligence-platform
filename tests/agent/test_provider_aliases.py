import pytest
from pydantic import ValidationError

from app.agent.contracts import (
    AgentDecision,
    AgentToolAction,
)


def test_agent_decision_normalizes_call_alias() -> None:
    decision = AgentDecision(
        action={
            "action_type": "call",
            "call": {
                "tool_name": ("analyze_revenue"),
                "arguments": {
                    "baseline_start": ("2025-07-01"),
                    "baseline_end": ("2025-07-31"),
                    "comparison_start": ("2025-08-01"),
                    "comparison_end": ("2025-08-31"),
                },
            },
        }
    )

    assert isinstance(
        decision.action,
        AgentToolAction,
    )

    assert decision.action.action_type == "tool_call"

    assert decision.action.call.tool_name == "analyze_revenue"


def test_agent_decision_keeps_tool_call_canonical() -> None:
    decision = AgentDecision(
        action={
            "action_type": "tool_call",
            "call": {
                "tool_name": ("analyze_revenue"),
                "arguments": {},
            },
        }
    )

    assert isinstance(
        decision.action,
        AgentToolAction,
    )

    assert decision.action.action_type == "tool_call"


def test_agent_decision_does_not_normalize_unknown_action() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action={
                "action_type": "execute",
                "call": {
                    "tool_name": ("analyze_revenue"),
                    "arguments": {},
                },
            }
        )


def test_agent_decision_does_not_normalize_function_alias() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action={
                "action_type": "function",
                "call": {
                    "tool_name": ("analyze_revenue"),
                    "arguments": {},
                },
            }
        )
