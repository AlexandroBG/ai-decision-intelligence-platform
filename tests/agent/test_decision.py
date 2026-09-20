from typing import Any

from app.agent.contracts import (
    AgentDecision,
    AgentHistory,
    AgentObservation,
)
from app.agent.decision import AgentDecisionClient
from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.registry import ToolRegistry


class ExampleTool(BaseTool):
    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name="example_tool",
            description="Example deterministic tool.",
            input_schema={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "integer",
                    }
                },
            },
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={},
        )


class FakeLLMClient:
    def __init__(
        self,
        response: AgentDecision,
    ) -> None:
        self.response = response
        self.prompt: str | None = None
        self.response_model: Any = None

    def generate_structured(
        self,
        prompt: str,
        response_model: type[AgentDecision],
    ) -> AgentDecision:
        self.prompt = prompt
        self.response_model = response_model

        return self.response


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(ExampleTool())

    return registry


def test_decision_client_returns_agent_decision() -> None:
    expected = AgentDecision(
        action={
            "action_type": "final",
            "answer": "Analysis complete.",
        }
    )

    llm_client = FakeLLMClient(response=expected)

    client = AgentDecisionClient(
        llm_client=llm_client,
        registry=build_registry(),
    )

    result = client.decide(
        question="What happened?",
        history=AgentHistory(),
    )

    assert result == expected


def test_decision_client_requests_agent_decision_schema() -> None:
    expected = AgentDecision(
        action={
            "action_type": "final",
            "answer": "Done.",
        }
    )

    llm_client = FakeLLMClient(response=expected)

    client = AgentDecisionClient(
        llm_client=llm_client,
        registry=build_registry(),
    )

    client.decide(
        question="What happened?",
        history=AgentHistory(),
    )

    assert llm_client.response_model is AgentDecision


def test_decision_client_prompt_contains_question() -> None:
    llm_client = FakeLLMClient(
        response=AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
            }
        )
    )

    client = AgentDecisionClient(
        llm_client=llm_client,
        registry=build_registry(),
    )

    client.decide(
        question="Why did revenue decline?",
        history=AgentHistory(),
    )

    assert llm_client.prompt is not None

    assert "Why did revenue decline?" in llm_client.prompt


def test_decision_client_prompt_contains_catalog() -> None:
    llm_client = FakeLLMClient(
        response=AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
            }
        )
    )

    client = AgentDecisionClient(
        llm_client=llm_client,
        registry=build_registry(),
    )

    client.decide(
        question="What happened?",
        history=AgentHistory(),
    )

    assert llm_client.prompt is not None

    assert '"name": "example_tool"' in llm_client.prompt

    assert "Example deterministic tool." in llm_client.prompt


def test_decision_client_prompt_contains_history() -> None:
    history = AgentHistory(
        observations=[
            AgentObservation(
                call={
                    "tool_name": "example_tool",
                    "arguments": {
                        "value": 42,
                    },
                },
                result={
                    "tool_name": "example_tool",
                    "success": True,
                    "output": {
                        "result": 84,
                    },
                },
            )
        ]
    )

    llm_client = FakeLLMClient(
        response=AgentDecision(
            action={
                "action_type": "final",
                "answer": "Done.",
            }
        )
    )

    client = AgentDecisionClient(
        llm_client=llm_client,
        registry=build_registry(),
    )

    client.decide(
        question="What happened?",
        history=history,
    )

    assert llm_client.prompt is not None

    assert '"value": 42' in llm_client.prompt

    assert '"result": 84' in llm_client.prompt
