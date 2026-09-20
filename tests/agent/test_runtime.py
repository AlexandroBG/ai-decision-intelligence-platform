from typing import TypeVar

import pandas as pd
from pydantic import BaseModel

from app.agent.contracts import AgentDecision
from app.agent.runtime import build_agent_loop

StructuredResponseT = TypeVar(
    "StructuredResponseT",
    bound=BaseModel,
)


class FakeSequentialLLMClient:
    def __init__(
        self,
        decisions: list[AgentDecision],
    ) -> None:
        self._decisions = decisions.copy()
        self.prompts: list[str] = []

    def generate_structured(
        self,
        prompt: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        self.prompts.append(prompt)

        if not self._decisions:
            raise AssertionError("Fake LLM ran out of decisions.")

        decision = self._decisions.pop(0)

        return response_model.model_validate(decision.model_dump())


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "o1",
                "o2",
                "o3",
                "o4",
            ],
            "customer_id": [
                "c1",
                "c2",
                "c1",
                "c2",
            ],
            "product_id": [
                "p1",
                "p2",
                "p1",
                "p2",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-10",
                    "2025-07-20",
                    "2025-08-10",
                    "2025-08-20",
                ]
            ),
            "quantity": [
                2,
                1,
                1,
                1,
            ],
            "unit_price": [
                100.0,
                200.0,
                100.0,
                100.0,
            ],
            "discount": [
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "sales_channel": [
                "Partner",
                "Web",
                "Partner",
                "Web",
            ],
        }
    )


def build_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [
                "c1",
                "c2",
            ],
            "signup_date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-02-01",
                ]
            ),
            "segment": [
                "Enterprise",
                "SMB",
            ],
            "region": [
                "South",
                "North",
            ],
            "acquisition_channel": [
                "Organic",
                "Paid",
            ],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": [
                "p1",
                "p2",
            ],
            "product_name": [
                "Laptop",
                "Router",
            ],
            "category": [
                "Computing",
                "Networking",
            ],
            "unit_cost": [
                60.0,
                120.0,
            ],
        }
    )


def test_runtime_connects_llm_tool_and_final_answer() -> None:
    llm_client = FakeSequentialLLMClient(
        decisions=[
            AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "analyze_revenue",
                        "arguments": {
                            "baseline_start": "2025-07-01",
                            "baseline_end": "2025-07-31",
                            "comparison_start": "2025-08-01",
                            "comparison_end": "2025-08-31",
                        },
                    },
                }
            ),
            AgentDecision(
                action={
                    "action_type": "final",
                    "answer": ("Revenue declined by 50%."),
                    "evidence_steps": [
                        1,
                    ],
                    "grounded_claims": [
                        {
                            "statement": ("Revenue declined by 50%."),
                            "claim_type": "fact",
                            "evidence_ids": [
                                "tool_step_1",
                            ],
                        }
                    ],
                }
            ),
        ]
    )

    loop = build_agent_loop(
        llm_client=llm_client,
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    result = loop.run(question="How did revenue change?")

    assert result.status == "completed"

    assert result.answer == ("Revenue declined by 50%.")

    assert result.evidence_steps == [
        1,
    ]

    assert len(result.grounded_claims) == 1

    assert result.steps_used == 2
    assert result.tool_calls == 1
    assert result.tool_failures == 0


def test_runtime_returns_tool_result_to_next_llm_decision() -> None:
    llm_client = FakeSequentialLLMClient(
        decisions=[
            AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "analyze_revenue",
                        "arguments": {
                            "baseline_start": "2025-07-01",
                            "baseline_end": "2025-07-31",
                            "comparison_start": "2025-08-01",
                            "comparison_end": "2025-08-31",
                        },
                    },
                }
            ),
            AgentDecision(
                action={
                    "action_type": "final",
                    "answer": "Done.",
                    "evidence_steps": [
                        1,
                    ],
                    "grounded_claims": [
                        {
                            "statement": ("Revenue comparison completed."),
                            "claim_type": "fact",
                            "evidence_ids": [
                                "tool_step_1",
                            ],
                        }
                    ],
                }
            ),
        ]
    )

    loop = build_agent_loop(
        llm_client=llm_client,
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    result = loop.run(question="How did revenue change?")

    assert result.status == "completed"

    assert len(llm_client.prompts) == 2

    second_prompt = llm_client.prompts[1]

    assert '"evidence_id": "tool_step_1"' in second_prompt

    assert '"baseline_revenue": 400.0' in second_prompt

    assert '"comparison_revenue": 200.0' in second_prompt

    assert '"absolute_change": -200.0' in second_prompt

    assert '"percentage_change": -0.5' in second_prompt


def test_runtime_supports_multiple_real_tool_calls() -> None:
    llm_client = FakeSequentialLLMClient(
        decisions=[
            AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "analyze_revenue",
                        "arguments": {
                            "baseline_start": "2025-07-01",
                            "baseline_end": "2025-07-31",
                            "comparison_start": "2025-08-01",
                            "comparison_end": "2025-08-31",
                        },
                    },
                }
            ),
            AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": ("analyze_revenue_drivers"),
                        "arguments": {
                            "baseline_start": "2025-07-01",
                            "baseline_end": "2025-07-31",
                            "comparison_start": "2025-08-01",
                            "comparison_end": "2025-08-31",
                            "max_drivers": 3,
                        },
                    },
                }
            ),
            AgentDecision(
                action={
                    "action_type": "final",
                    "answer": (
                        "Revenue declined and the "
                        "observed drivers should be "
                        "investigated."
                    ),
                    "evidence_steps": [
                        1,
                        2,
                    ],
                    "grounded_claims": [
                        {
                            "statement": ("Revenue declined."),
                            "claim_type": "fact",
                            "evidence_ids": [
                                "tool_step_1",
                            ],
                        },
                        {
                            "statement": (
                                "The observed drivers should be investigated."
                            ),
                            "claim_type": "inference",
                            "evidence_ids": [
                                "tool_step_2",
                            ],
                        },
                    ],
                }
            ),
        ]
    )

    loop = build_agent_loop(
        llm_client=llm_client,
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
        max_steps=4,
    )

    result = loop.run(question="What affected revenue?")

    assert result.status == "completed"

    assert result.evidence_steps == [
        1,
        2,
    ]

    assert len(result.grounded_claims) == 2

    assert result.steps_used == 3
    assert result.tool_calls == 2
    assert result.tool_failures == 0

    assert [
        observation.call.tool_name for observation in result.history.observations
    ] == [
        "analyze_revenue",
        "analyze_revenue_drivers",
    ]


def test_runtime_exposes_tool_catalog_to_llm() -> None:
    llm_client = FakeSequentialLLMClient(
        decisions=[
            AgentDecision(
                action={
                    "action_type": "final",
                    "answer": "Done.",
                    "evidence_steps": [],
                    "grounded_claims": [],
                }
            )
        ]
    )

    loop = build_agent_loop(
        llm_client=llm_client,
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    result = loop.run(question="What happened?")

    assert result.status == "completed"
    assert result.tool_calls == 0

    prompt = llm_client.prompts[0]

    assert '"name": "analyze_revenue"' in prompt

    assert '"name": "analyze_revenue_drivers"' in prompt

    assert '"name": "detect_revenue_anomalies"' in prompt


def test_runtime_keeps_original_question_across_steps() -> None:
    llm_client = FakeSequentialLLMClient(
        decisions=[
            AgentDecision(
                action={
                    "action_type": "tool_call",
                    "call": {
                        "tool_name": "analyze_revenue",
                        "arguments": {
                            "baseline_start": "2025-07-01",
                            "baseline_end": "2025-07-31",
                            "comparison_start": "2025-08-01",
                            "comparison_end": "2025-08-31",
                        },
                    },
                }
            ),
            AgentDecision(
                action={
                    "action_type": "final",
                    "answer": "Done.",
                    "evidence_steps": [
                        1,
                    ],
                    "grounded_claims": [
                        {
                            "statement": ("Revenue analysis completed."),
                            "claim_type": "fact",
                            "evidence_ids": [
                                "tool_step_1",
                            ],
                        }
                    ],
                }
            ),
        ]
    )

    loop = build_agent_loop(
        llm_client=llm_client,
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    question = "What is affecting revenue performance?"

    result = loop.run(question=question)

    assert result.status == "completed"

    assert all(question in prompt for prompt in llm_client.prompts)
