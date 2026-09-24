import pandas as pd

from app.agent.contracts import (
    AgentHistory,
    AgentRunResult,
)
from app.api import factory
from app.api.service import RuntimeDecisionService


class FakeLLMClient:
    pass


class FakeAgentLoop:
    def run(
        self,
        question: str,
    ) -> AgentRunResult:
        return AgentRunResult(
            answer="Result.",
            evidence_steps=[],
            grounded_claims=[],
            status="completed",
            termination_reason=None,
            steps_used=1,
            tool_calls=0,
            tool_failures=0,
            history=AgentHistory(),
        )


def test_factory_builds_runtime_service(
    monkeypatch,
) -> None:
    fake_llm_client = FakeLLMClient()

    orders = pd.DataFrame(
        {
            "order_id": [
                "o1",
            ],
        }
    )

    customers = pd.DataFrame(
        {
            "customer_id": [
                "c1",
            ],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": [
                "p1",
            ],
        }
    )

    fake_loop = FakeAgentLoop()

    captured: dict[
        str,
        object,
    ] = {}

    monkeypatch.setattr(
        factory,
        "build_llm_client",
        lambda: fake_llm_client,
    )

    monkeypatch.setattr(
        factory,
        "load_orders",
        lambda: orders,
    )

    monkeypatch.setattr(
        factory,
        "load_customers",
        lambda: customers,
    )

    monkeypatch.setattr(
        factory,
        "load_products",
        lambda: products,
    )

    def fake_build_agent_loop(
        llm_client,
        orders,
        customers,
        products,
    ):
        captured["llm_client"] = llm_client
        captured["orders"] = orders
        captured["customers"] = customers
        captured["products"] = products

        return fake_loop

    monkeypatch.setattr(
        factory,
        "build_agent_loop",
        fake_build_agent_loop,
    )

    service = factory.build_runtime_decision_service()

    assert isinstance(
        service,
        RuntimeDecisionService,
    )

    assert service.runner is fake_loop

    assert captured["llm_client"] is fake_llm_client
    assert captured["orders"] is orders
    assert captured["customers"] is customers
    assert captured["products"] is products
