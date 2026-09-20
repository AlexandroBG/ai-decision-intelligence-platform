import pandas as pd

from app.agent.decision import (
    AgentDecisionClient,
    StructuredLLMClient,
)
from app.agent.loop import AgentLoop
from app.tools.executor import ToolExecutor
from app.tools.factory import build_default_tool_registry


def build_agent_loop(
    llm_client: StructuredLLMClient,
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    max_steps: int = 5,
) -> AgentLoop:
    registry = build_default_tool_registry(
        orders=orders,
        customers=customers,
        products=products,
    )

    executor = ToolExecutor(registry=registry)

    decision_client = AgentDecisionClient(
        llm_client=llm_client,
        registry=registry,
    )

    return AgentLoop(
        executor=executor,
        decide=decision_client.decide,
        max_steps=max_steps,
    )
