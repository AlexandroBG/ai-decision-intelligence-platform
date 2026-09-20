import pytest
from pydantic import ValidationError

from app.agent.contracts import (
    AgentHistory,
    AgentObservation,
)


def build_observation() -> AgentObservation:
    return AgentObservation(
        call={
            "tool_name": "analyze_revenue",
            "arguments": {
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
            },
        },
        result={
            "tool_name": "analyze_revenue",
            "success": True,
            "output": {
                "baseline_revenue": 1000.0,
                "comparison_revenue": 700.0,
                "absolute_change": -300.0,
                "percentage_change": -0.3,
            },
        },
    )


def test_observation_accepts_valid_tool_exchange() -> None:
    observation = build_observation()

    assert observation.call.tool_name == "analyze_revenue"

    assert observation.result.tool_name == "analyze_revenue"

    assert observation.result.success is True


def test_observation_accepts_failed_result() -> None:
    observation = AgentObservation(
        call={
            "tool_name": "analyze_revenue",
            "arguments": {},
        },
        result={
            "tool_name": "analyze_revenue",
            "success": False,
            "error": ("Baseline period contains no orders."),
        },
    )

    assert observation.result.success is False

    assert observation.result.error == ("Baseline period contains no orders.")


def test_observation_rejects_mismatched_tool_names() -> None:
    with pytest.raises(
        ValidationError,
        match=("Observation call and result must reference the same tool."),
    ):
        AgentObservation(
            call={
                "tool_name": "analyze_revenue",
            },
            result={
                "tool_name": ("detect_revenue_anomalies"),
                "success": True,
            },
        )


def test_observation_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        AgentObservation(
            call={
                "tool_name": "analyze_revenue",
            },
            result={
                "tool_name": "analyze_revenue",
                "success": True,
            },
            unexpected=True,
        )


def test_history_starts_empty() -> None:
    history = AgentHistory()

    assert history.observations == []


def test_history_accepts_observations() -> None:
    observation = build_observation()

    history = AgentHistory(observations=[observation])

    assert len(history.observations) == 1

    assert history.observations[0] == observation


def test_history_preserves_observation_order() -> None:
    first = AgentObservation(
        call={
            "tool_name": "analyze_revenue",
        },
        result={
            "tool_name": "analyze_revenue",
            "success": True,
            "output": {
                "step": 1,
            },
        },
    )

    second = AgentObservation(
        call={
            "tool_name": ("analyze_revenue_drivers"),
        },
        result={
            "tool_name": ("analyze_revenue_drivers"),
            "success": True,
            "output": {
                "step": 2,
            },
        },
    )

    history = AgentHistory(
        observations=[
            first,
            second,
        ]
    )

    assert [observation.call.tool_name for observation in history.observations] == [
        "analyze_revenue",
        "analyze_revenue_drivers",
    ]


def test_history_rejects_invalid_observation() -> None:
    with pytest.raises(ValidationError):
        AgentHistory(
            observations=[
                {
                    "call": {
                        "tool_name": "",
                    },
                    "result": {
                        "tool_name": ("analyze_revenue"),
                        "success": True,
                    },
                }
            ]
        )


def test_history_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        AgentHistory(
            observations=[],
            unexpected=True,
        )
