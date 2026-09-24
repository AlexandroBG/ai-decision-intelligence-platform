from app.agent.contracts import (
    AgentDecision,
    AgentHistory,
)
from app.agent.prompts import build_agent_prompt
from app.llm.protocols import StructuredLLMClient
from app.tools.catalog import build_tool_catalog
from app.tools.registry import ToolRegistry


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
