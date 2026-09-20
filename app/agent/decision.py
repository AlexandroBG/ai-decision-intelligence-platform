from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.agent.contracts import (
    AgentDecision,
    AgentHistory,
)
from app.agent.prompts import build_agent_prompt
from app.tools.catalog import build_tool_catalog
from app.tools.registry import ToolRegistry

StructuredResponseT = TypeVar(
    "StructuredResponseT",
    bound=BaseModel,
)


class StructuredLLMClient(Protocol):
    def generate_structured(
        self,
        prompt: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        """Generate a structured LLM response."""


class AgentDecisionClient:
    def __init__(
        self,
        llm_client: StructuredLLMClient,
        registry: ToolRegistry,
    ) -> None:
        self._llm_client = llm_client
        self._registry = registry

    def decide(
        self,
        question: str,
        history: AgentHistory,
    ) -> AgentDecision:
        catalog = build_tool_catalog(registry=self._registry)

        prompt = build_agent_prompt(
            question=question,
            tool_catalog=catalog,
            history=history,
        )

        return self._llm_client.generate_structured(
            prompt=prompt,
            response_model=AgentDecision,
        )
