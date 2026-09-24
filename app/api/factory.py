from app.agent.runtime import build_agent_loop
from app.api.service import RuntimeDecisionService
from app.data.loaders import (
    load_customers,
    load_orders,
    load_products,
)
from app.llm.factory import build_llm_client


def build_runtime_decision_service() -> RuntimeDecisionService:
    llm_client = build_llm_client()

    orders = load_orders()
    customers = load_customers()
    products = load_products()

    agent_loop = build_agent_loop(
        llm_client=llm_client,
        orders=orders,
        customers=customers,
        products=products,
    )

    return RuntimeDecisionService(
        runner=agent_loop,
    )
