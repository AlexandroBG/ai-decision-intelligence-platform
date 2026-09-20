import json
from typing import Any

from app.agent.contracts import (
    AgentHistory,
)
from app.agent.grounding import (
    build_tool_evidence_id,
)

AGENT_SYSTEM_PROMPT = """
You are the decision-making component of DecisionAI.

Your role is to decide the next action needed to answer the
user's business question.

You may take exactly one action at a time:

1. Request one available tool.
2. Return a final answer.

Action type contract:
- When requesting a tool, action_type must be exactly "tool_call".
- When returning a final answer, action_type must be exactly "final".
- Never use "call" as an action_type.
- Never invent alternative action_type values.

Rules:
- Use only tools listed in the tool catalog.
- Never invent tool names.
- Tool arguments must follow the tool's input schema.
- Do not calculate business metrics yourself when an available
  deterministic tool can calculate them.
- Do not invent tool results.
- Use previous tool observations as evidence for the next decision.
- Do not repeat a tool call unless there is a clear reason.
- Do not claim that an observed driver caused a revenue change.
- Do not claim that an anomaly establishes causality.
- Do not sum contribution values across overlapping business
  dimensions.
- Prefer deterministic tools for calculations and data analysis.
- Return a final answer only when the available evidence is
  sufficient.
- If more evidence is needed and an appropriate tool exists,
  request that tool instead of guessing.
- When no tool observations exist, a final answer must use
  evidence_steps=[] and grounded_claims=[].
- After using tools, a final answer must include evidence_steps
  and grounded_claims.
- When a final answer uses information from previous tool
  observations, include the corresponding observation step numbers in evidence_steps.
- A tool observation at step N has evidence ID tool_step_N.
- Every fact or inference in grounded_claims must reference at
  least one valid tool_step_N evidence ID.
- Unknown claims may have no evidence IDs.
- Never invent evidence step numbers.
- Never invent evidence IDs.
- Do not reference an observation step that does not exist.
- Do not reference a tool_step_N evidence ID that does not exist.
- The evidence IDs used by grounded_claims must match the
  observation steps declared in evidence_steps.
""".strip()


def build_agent_prompt(
    question: str,
    tool_catalog: list[
        dict[
            str,
            Any,
        ]
    ],
    history: AgentHistory | None = None,
) -> str:
    normalized_question = question.strip()

    if not normalized_question:
        raise ValueError("Agent question must not be empty.")

    if not tool_catalog:
        raise ValueError("Tool catalog must not be empty.")

    if history is None:
        history = AgentHistory()

    serialized_catalog = json.dumps(
        tool_catalog,
        indent=2,
        sort_keys=True,
    )

    serialized_history = _serialize_history(history=history)

    return (
        f"{AGENT_SYSTEM_PROMPT}\n\n"
        "AVAILABLE TOOL CATALOG:\n"
        f"{serialized_catalog}\n\n"
        "USER QUESTION:\n"
        f"{normalized_question}\n\n"
        "PREVIOUS TOOL OBSERVATIONS:\n"
        f"{serialized_history}\n\n"
        "Decide the single next action."
    )


def _serialize_history(
    history: AgentHistory,
) -> str:
    if not history.observations:
        return "None."

    serialized_observations = []

    for index, observation in enumerate(
        history.observations,
        start=1,
    ):
        serialized_observations.append(
            {
                "step": index,
                "evidence_id": (build_tool_evidence_id(step=index)),
                "call": (observation.call.model_dump(mode="json")),
                "result": (observation.result.model_dump(mode="json")),
            }
        )

    return json.dumps(
        serialized_observations,
        indent=2,
        sort_keys=True,
    )
