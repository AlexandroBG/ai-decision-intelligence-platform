import pytest

from app.agent.contracts import (
    AgentHistory,
    AgentObservation,
)
from app.agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    build_agent_prompt,
)


def build_catalog() -> list[dict]:
    return [
        {
            "name": "analyze_revenue",
            "description": ("Compare revenue between two periods."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "baseline_start": {
                        "type": "string",
                        "format": "date",
                    },
                    "baseline_end": {
                        "type": "string",
                        "format": "date",
                    },
                    "comparison_start": {
                        "type": "string",
                        "format": "date",
                    },
                    "comparison_end": {
                        "type": "string",
                        "format": "date",
                    },
                },
            },
        },
        {
            "name": "analyze_revenue_drivers",
            "description": ("Identify observed revenue deterioration."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "max_drivers": {
                        "type": "integer",
                        "minimum": 0,
                    }
                },
            },
        },
    ]


def build_history() -> AgentHistory:
    observation = AgentObservation(
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

    return AgentHistory(observations=[observation])


def test_system_prompt_requires_single_action() -> None:
    assert "exactly one action at a time" in AGENT_SYSTEM_PROMPT


def test_system_prompt_requires_registered_tools() -> None:
    assert "Use only tools listed in the tool catalog." in AGENT_SYSTEM_PROMPT

    assert "Never invent tool names." in AGENT_SYSTEM_PROMPT


def test_system_prompt_prefers_deterministic_tools() -> None:
    assert "Prefer deterministic tools" in AGENT_SYSTEM_PROMPT


def test_system_prompt_prohibits_invented_results() -> None:
    assert "Do not invent tool results." in AGENT_SYSTEM_PROMPT


def test_system_prompt_requires_observation_use() -> None:
    assert "Use previous tool observations" in AGENT_SYSTEM_PROMPT


def test_system_prompt_discourages_repeated_calls() -> None:
    assert "Do not repeat a tool call" in AGENT_SYSTEM_PROMPT


def test_system_prompt_preserves_causality_boundary() -> None:
    assert "observed driver caused" in AGENT_SYSTEM_PROMPT

    assert "anomaly establishes causality" in AGENT_SYSTEM_PROMPT


def test_system_prompt_prohibits_cross_dimension_summing() -> None:
    assert "Do not sum contribution values" in AGENT_SYSTEM_PROMPT


def test_system_prompt_requires_final_evidence_steps() -> None:
    assert (
        "include the corresponding observation step "
        "numbers in evidence_steps" in AGENT_SYSTEM_PROMPT
    )


def test_system_prompt_prohibits_invented_evidence_steps() -> None:
    assert "Never invent evidence step numbers." in AGENT_SYSTEM_PROMPT


def test_system_prompt_prohibits_unknown_evidence_steps() -> None:
    assert (
        "Do not reference an observation step "
        "that does not exist." in AGENT_SYSTEM_PROMPT
    )


def test_agent_prompt_includes_question() -> None:
    prompt = build_agent_prompt(
        question="What is affecting revenue?",
        tool_catalog=build_catalog(),
    )

    assert "What is affecting revenue?" in prompt


def test_agent_prompt_strips_question() -> None:
    prompt = build_agent_prompt(
        question="  What is affecting revenue?  ",
        tool_catalog=build_catalog(),
    )

    assert "USER QUESTION:\nWhat is affecting revenue?" in prompt


def test_agent_prompt_includes_tool_names() -> None:
    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
    )

    assert '"name": "analyze_revenue"' in prompt

    assert '"name": "analyze_revenue_drivers"' in prompt


def test_agent_prompt_includes_tool_schema() -> None:
    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
    )

    assert '"baseline_start"' in prompt

    assert '"format": "date"' in prompt


def test_agent_prompt_includes_tool_descriptions() -> None:
    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
    )

    assert "Compare revenue between two periods." in prompt


def test_agent_prompt_shows_empty_history() -> None:
    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
    )

    assert "PREVIOUS TOOL OBSERVATIONS:\nNone." in prompt


def test_agent_prompt_includes_history() -> None:
    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
        history=build_history(),
    )

    assert '"tool_name": "analyze_revenue"' in prompt

    assert '"baseline_revenue": 1000.0' in prompt

    assert '"comparison_revenue": 700.0' in prompt

    assert '"percentage_change": -0.3' in prompt


def test_agent_prompt_includes_history_step_number() -> None:
    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
        history=build_history(),
    )

    assert '"step": 1' in prompt


def test_agent_prompt_preserves_history_order() -> None:
    first = AgentObservation(
        call={
            "tool_name": "analyze_revenue",
        },
        result={
            "tool_name": "analyze_revenue",
            "success": True,
            "output": {
                "step": "first",
            },
        },
    )

    second = AgentObservation(
        call={
            "tool_name": "analyze_revenue_drivers",
        },
        result={
            "tool_name": "analyze_revenue_drivers",
            "success": True,
            "output": {
                "step": "second",
            },
        },
    )

    history = AgentHistory(
        observations=[
            first,
            second,
        ]
    )

    prompt = build_agent_prompt(
        question="What happened?",
        tool_catalog=build_catalog(),
        history=history,
    )

    first_position = prompt.index('"step": "first"')

    second_position = prompt.index('"step": "second"')

    assert first_position < second_position


def test_agent_prompt_is_deterministic() -> None:
    catalog = build_catalog()
    history = build_history()

    first = build_agent_prompt(
        question="What happened?",
        tool_catalog=catalog,
        history=history,
    )

    second = build_agent_prompt(
        question="What happened?",
        tool_catalog=catalog,
        history=history,
    )

    assert first == second


def test_agent_prompt_rejects_empty_question() -> None:
    with pytest.raises(
        ValueError,
        match="Agent question must not be empty.",
    ):
        build_agent_prompt(
            question="   ",
            tool_catalog=build_catalog(),
        )


def test_agent_prompt_rejects_empty_catalog() -> None:
    with pytest.raises(
        ValueError,
        match="Tool catalog must not be empty.",
    ):
        build_agent_prompt(
            question="What happened?",
            tool_catalog=[],
        )
