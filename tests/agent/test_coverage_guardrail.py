from app.agent.contracts import (
    AgentDecision,
    AgentHistory,
)
from app.agent.coverage import (
    REVENUE_ANALYSIS_TOOL,
    REVENUE_DRIVERS_TOOL,
    build_coverage_retry_question,
    infer_required_tools,
    missing_required_tools,
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


class NamedTool(BaseTool):
    def __init__(
        self,
        name: str,
    ) -> None:
        self._name = name

    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name=self._name,
            description=(f"Test tool for {self._name}."),
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "arguments": call.arguments,
            },
        )


def build_coverage_executor() -> ToolExecutor:
    registry = ToolRegistry()

    registry.register(
        NamedTool(
            name=REVENUE_ANALYSIS_TOOL,
        )
    )

    registry.register(
        NamedTool(
            name=REVENUE_DRIVERS_TOOL,
        )
    )

    return ToolExecutor(
        registry=registry,
    )


def test_complex_revenue_question_requires_both_tools() -> None:
    question = (
        "What affected revenue performance from July 2025 "
        "to August 2025, and what should I investigate first?"
    )

    required_tools = infer_required_tools(
        question=question,
    )

    assert required_tools == (
        REVENUE_ANALYSIS_TOOL,
        REVENUE_DRIVERS_TOOL,
    )


def test_simple_revenue_driver_question_does_not_force_guardrail() -> None:
    question = "What is affecting revenue performance?"

    required_tools = infer_required_tools(
        question=question,
    )

    assert required_tools == ()


def test_comparison_only_question_does_not_force_composite_guardrail() -> None:
    question = "Compare revenue from July 2025 to August 2025."

    required_tools = infer_required_tools(
        question=question,
    )

    assert required_tools == ()


def test_driver_only_question_does_not_force_composite_guardrail() -> None:
    question = "Which revenue drivers should I investigate first?"

    required_tools = infer_required_tools(
        question=question,
    )

    assert required_tools == ()


def test_unrelated_question_has_no_required_tools() -> None:
    required_tools = infer_required_tools(
        question=("Explain the available system features."),
    )

    assert required_tools == ()


def test_missing_required_tools_detects_partial_coverage() -> None:
    history = AgentHistory(
        observations=[
            {
                "call": {
                    "tool_name": REVENUE_DRIVERS_TOOL,
                    "arguments": {},
                },
                "result": {
                    "tool_name": REVENUE_DRIVERS_TOOL,
                    "success": True,
                    "output": {},
                },
            }
        ]
    )

    missing_tools = missing_required_tools(
        question=(
            "What affected revenue performance "
            "from July 2025 to August 2025, "
            "and what should I investigate first?"
        ),
        history=history,
    )

    assert missing_tools == (REVENUE_ANALYSIS_TOOL,)


def test_no_missing_tools_when_complex_coverage_is_complete() -> None:
    history = AgentHistory(
        observations=[
            {
                "call": {
                    "tool_name": REVENUE_DRIVERS_TOOL,
                    "arguments": {},
                },
                "result": {
                    "tool_name": REVENUE_DRIVERS_TOOL,
                    "success": True,
                    "output": {},
                },
            },
            {
                "call": {
                    "tool_name": REVENUE_ANALYSIS_TOOL,
                    "arguments": {},
                },
                "result": {
                    "tool_name": REVENUE_ANALYSIS_TOOL,
                    "success": True,
                    "output": {},
                },
            },
        ]
    )

    missing_tools = missing_required_tools(
        question=(
            "What affected revenue performance "
            "from July 2025 to August 2025, "
            "and what should I investigate first?"
        ),
        history=history,
    )

    assert missing_tools == ()


def test_failed_tool_does_not_satisfy_coverage() -> None:
    history = AgentHistory(
        observations=[
            {
                "call": {
                    "tool_name": REVENUE_ANALYSIS_TOOL,
                    "arguments": {},
                },
                "result": {
                    "tool_name": REVENUE_ANALYSIS_TOOL,
                    "success": False,
                    "output": {},
                    "error": "Test failure.",
                },
            },
            {
                "call": {
                    "tool_name": REVENUE_DRIVERS_TOOL,
                    "arguments": {},
                },
                "result": {
                    "tool_name": REVENUE_DRIVERS_TOOL,
                    "success": True,
                    "output": {},
                },
            },
        ]
    )

    missing_tools = missing_required_tools(
        question=(
            "What affected revenue performance "
            "from July 2025 to August 2025, "
            "and what should I investigate first?"
        ),
        history=history,
    )

    assert missing_tools == (REVENUE_ANALYSIS_TOOL,)


def test_retry_question_mentions_missing_tool() -> None:
    retry_question = build_coverage_retry_question(
        original_question=("What affected revenue performance from July to August?"),
        missing_tools=(REVENUE_ANALYSIS_TOOL,),
    )

    assert "RUNTIME COVERAGE FEEDBACK" in retry_question

    assert REVENUE_ANALYSIS_TOOL in retry_question

    assert "Do not repeat successful tool calls." in retry_question


def test_agent_loop_recovers_from_premature_final_answer() -> None:
    original_question = (
        "What affected revenue performance "
        "from July 2025 to August 2025, "
        "and what should I investigate first?"
    )

    def decide(
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        observation_count = len(history.observations)

        if observation_count == 0:
            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": (REVENUE_DRIVERS_TOOL),
                        "arguments": {
                            "baseline_start": ("2025-07-01"),
                            "baseline_end": ("2025-07-31"),
                            "comparison_start": ("2025-08-01"),
                            "comparison_end": ("2025-08-31"),
                        },
                    },
                }
            )

        if observation_count == 1 and "RUNTIME COVERAGE FEEDBACK" not in question:
            return AgentDecision(
                action={
                    "action_type": "final",
                    "answer": ("Computing should be investigated first."),
                    "evidence_steps": [
                        1,
                    ],
                    "grounded_claims": [
                        {
                            "statement": ("Driver evidence was analyzed."),
                            "claim_type": "fact",
                            "evidence_ids": [
                                "tool_step_1",
                            ],
                        }
                    ],
                }
            )

        if observation_count == 1:
            assert "RUNTIME COVERAGE FEEDBACK" in question

            assert REVENUE_ANALYSIS_TOOL in question

            return AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": (REVENUE_ANALYSIS_TOOL),
                        "arguments": {
                            "baseline_start": ("2025-07-01"),
                            "baseline_end": ("2025-07-31"),
                            "comparison_start": ("2025-08-01"),
                            "comparison_end": ("2025-08-31"),
                        },
                    },
                }
            )

        return AgentDecision(
            action={
                "action_type": "final",
                "answer": (
                    "Revenue declined and the "
                    "driver evidence identifies "
                    "areas to investigate."
                ),
                "evidence_steps": [
                    1,
                    2,
                ],
                "grounded_claims": [
                    {
                        "statement": ("Driver evidence was analyzed."),
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_1",
                        ],
                    },
                    {
                        "statement": ("Aggregate revenue was analyzed."),
                        "claim_type": "fact",
                        "evidence_ids": [
                            "tool_step_2",
                        ],
                    },
                ],
            }
        )

    loop = AgentLoop(
        executor=build_coverage_executor(),
        decide=decide,
        max_steps=4,
    )

    result = loop.run(
        question=original_question,
    )

    assert result.status == "completed"

    assert result.tool_calls == 2

    assert result.steps_used == 4

    assert [
        observation.call.tool_name for observation in result.history.observations
    ] == [
        REVENUE_DRIVERS_TOOL,
        REVENUE_ANALYSIS_TOOL,
    ]

    assert result.evidence_steps == [
        1,
        2,
    ]
