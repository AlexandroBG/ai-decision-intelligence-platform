import pytest

from app.agent.contracts import (
    AgentDecision,
    AgentHistory,
)
from app.agent.loop import AgentLoop
from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class ExampleTool(BaseTool):
    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name="example_tool",
            description="Example tool.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "received": call.arguments,
            },
        )


class FailingTool(BaseTool):
    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name="failing_tool",
            description="Tool used to verify safe failures.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        raise RuntimeError("PRIVATE_EXCEPTION_DETAIL")


def build_executor() -> ToolExecutor:
    registry = ToolRegistry()

    registry.register(ExampleTool())
    registry.register(FailingTool())

    return ToolExecutor(registry=registry)


def test_agent_loop_returns_immediate_final_answer() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "No tools required.",
                "evidence_steps": [],
                "grounded_claims": [],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Answer directly.")

    assert result.status == "completed"
    assert result.answer == "No tools required."
    assert result.evidence_steps == []
    assert result.grounded_claims == []
    assert result.tool_calls == 0


def test_agent_loop_completes_with_grounded_tool_answer() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {
                            "value": 42,
                        },
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "The tool returned value 42.",
                "evidence_steps": [
                    1,
                ],
                "grounded_claims": [
                    {
                        "statement": ("The tool returned value 42."),
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_1",
                        ],
                    }
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Run the tool.")

    assert result.status == "completed"

    assert result.evidence_steps == [
        1,
    ]

    assert len(result.grounded_claims) == 1

    assert result.grounded_claims[0].evidence_ids == [
        "tool_step_1",
    ]


def test_agent_loop_surfaces_safe_failed_tool_observation() -> None:
    loop = AgentLoop(
        executor=build_executor(),
        decide=lambda question, history: AgentDecision(
            action={
                "action_type": "tool_call",
                "call": {
                    "tool_name": "failing_tool",
                    "arguments": {},
                },
            }
        ),
        max_steps=1,
    )

    result = loop.run(question="Run the failing tool.")
    observation = result.history.observations[0]

    assert result.status == "max_steps_reached"
    assert observation.result.success is False
    assert observation.result.error == "Tool execution failed."
    assert "PRIVATE_EXCEPTION_DETAIL" not in observation.result.error
    assert "PRIVATE_EXCEPTION_DETAIL" not in result.model_dump_json()


def test_agent_loop_rejects_missing_evidence_steps() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {},
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "evidence_steps": [],
                "grounded_claims": [
                    {
                        "statement": "Done.",
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_1",
                        ],
                    }
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "invalid_final_evidence"

    assert result.answer is None


def test_agent_loop_rejects_unknown_evidence_step() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {},
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "evidence_steps": [
                    99,
                ],
                "grounded_claims": [
                    {
                        "statement": "Done.",
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_99",
                        ],
                    }
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "invalid_final_evidence"


def test_agent_loop_rejects_missing_grounded_claims() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {},
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "evidence_steps": [
                    1,
                ],
                "grounded_claims": [],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "invalid_final_grounding"

    assert result.termination_reason == (
        "Final answer must include grounded claims after using tools."
    )


def test_agent_loop_rejects_fact_without_grounding() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {},
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "The tool completed.",
                "evidence_steps": [
                    1,
                ],
                "grounded_claims": [
                    {
                        "statement": ("The tool completed."),
                        "claim_type": "fact",
                        "evidence_ids": [],
                    }
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "invalid_final_grounding"

    assert result.termination_reason == (
        "Agent facts and inferences must reference tool evidence."
    )


def test_agent_loop_rejects_unknown_tool_evidence_id() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {},
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "evidence_steps": [
                    1,
                ],
                "grounded_claims": [
                    {
                        "statement": "Done.",
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_99",
                        ],
                    }
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "invalid_final_grounding"

    assert result.termination_reason == (
        "Agent claim referenced unknown tool evidence."
    )


def test_agent_loop_requires_steps_and_claim_ids_to_match() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        step = len(history.observations)

        if step == 0:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {
                            "step": 1,
                        },
                    },
                }
            )

        if step == 1:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {
                            "step": 2,
                        },
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "evidence_steps": [
                    1,
                    2,
                ],
                "grounded_claims": [
                    {
                        "statement": "Step one completed.",
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_1",
                        ],
                    }
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
        max_steps=3,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "invalid_final_grounding"

    assert result.termination_reason == (
        "Final evidence steps must match the evidence used by grounded claims."
    )


def test_agent_loop_accepts_multiple_grounded_observations() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        step = len(history.observations)

        if step == 0:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {
                            "period": "July",
                        },
                    },
                }
            )

        if step == 1:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {
                            "period": "August",
                        },
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": ("Both periods were analyzed."),
                "evidence_steps": [
                    1,
                    2,
                ],
                "grounded_claims": [
                    {
                        "statement": ("July was analyzed."),
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_1",
                        ],
                    },
                    {
                        "statement": ("August was analyzed."),
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_2",
                        ],
                    },
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
        max_steps=3,
    )

    result = loop.run(question="Compare periods.")

    assert result.status == "completed"

    assert result.evidence_steps == [
        1,
        2,
    ]

    assert len(result.grounded_claims) == 2


def test_agent_loop_allows_unknown_claim_without_evidence() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        if not history.observations:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "example_tool",
                        "arguments": {},
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": ("The tool completed, but causality is not established."),
                "evidence_steps": [
                    1,
                ],
                "grounded_claims": [
                    {
                        "statement": ("The tool completed."),
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_1",
                        ],
                    },
                    {
                        "statement": ("Causality is not established."),
                        "claim_type": "unknown",
                        "evidence_ids": [],
                    },
                ],
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "completed"

    assert len(result.grounded_claims) == 2


def test_agent_loop_returns_duplicate_tool_call_status() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        return AgentDecision(
            action={
                "action_type": "tool_call",
                "call": {
                    "tool_name": "example_tool",
                    "arguments": {
                        "value": 42,
                    },
                },
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
        max_steps=3,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "duplicate_tool_call"

    assert result.grounded_claims == []


def test_agent_loop_returns_failure_limit_status() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        step = len(history.observations)

        return AgentDecision(
            action={
                "action_type": "tool_call",
                "call": {
                    "tool_name": (f"missing_tool_{step}"),
                    "arguments": {},
                },
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
        max_steps=4,
        max_tool_failures=2,
    )

    result = loop.run(question="Investigate.")

    assert result.status == "tool_failure_limit_reached"

    assert result.tool_failures == 2
    assert result.grounded_claims == []


def test_agent_loop_returns_max_steps_status() -> None:
    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        step = len(history.observations)

        return AgentDecision(
            action={
                "action_type": "tool_call",
                "call": {
                    "tool_name": "example_tool",
                    "arguments": {
                        "step": step,
                    },
                },
            }
        )

    loop = AgentLoop(
        executor=build_executor(),
        decide=decide,
        max_steps=2,
    )

    result = loop.run(question="Keep going.")

    assert result.status == "max_steps_reached"

    assert result.steps_used == 2
    assert result.tool_calls == 2
    assert result.grounded_claims == []


def test_agent_loop_rejects_empty_question() -> None:
    loop = AgentLoop(
        executor=build_executor(),
        decide=lambda question, history: AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
                "evidence_steps": [],
                "grounded_claims": [],
            }
        ),
    )

    with pytest.raises(
        ValueError,
        match="Agent question must not be empty.",
    ):
        loop.run(question="   ")


def test_agent_loop_rejects_invalid_max_steps() -> None:
    with pytest.raises(
        ValueError,
        match=("max_steps must be greater than zero."),
    ):
        AgentLoop(
            executor=build_executor(),
            decide=lambda question, history: AgentDecision(
                action={
                    "action_type": "final",
                    "answer": "Done.",
                    "evidence_steps": [],
                    "grounded_claims": [],
                }
            ),
            max_steps=0,
        )


def test_agent_loop_rejects_negative_failure_limit() -> None:
    with pytest.raises(
        ValueError,
        match=("max_tool_failures must not be negative."),
    ):
        AgentLoop(
            executor=build_executor(),
            decide=lambda question, history: AgentDecision(
                action={
                    "action_type": "final",
                    "answer": "Done.",
                    "evidence_steps": [],
                    "grounded_claims": [],
                }
            ),
            max_tool_failures=-1,
        )
