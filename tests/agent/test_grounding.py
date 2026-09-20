import pytest

from app.agent.contracts import (
    AgentHistory,
    AgentObservation,
)
from app.agent.grounding import (
    AgentGroundingError,
    build_agent_evidence_registry,
    build_tool_evidence_id,
    collect_agent_evidence_ids,
    evidence_steps_to_ids,
    validate_agent_grounded_claims,
)
from app.llm.contracts import GroundedClaim


def build_history() -> AgentHistory:
    return AgentHistory(
        observations=[
            AgentObservation(
                call={
                    "tool_name": "analyze_revenue",
                    "arguments": {},
                },
                result={
                    "tool_name": "analyze_revenue",
                    "success": True,
                    "output": {
                        "absolute_change": -100.0,
                    },
                },
            ),
            AgentObservation(
                call={
                    "tool_name": ("analyze_revenue_drivers"),
                    "arguments": {},
                },
                result={
                    "tool_name": ("analyze_revenue_drivers"),
                    "success": True,
                    "output": {
                        "drivers": [],
                    },
                },
            ),
        ]
    )


def test_build_tool_evidence_id() -> None:
    assert build_tool_evidence_id(step=1) == "tool_step_1"

    assert build_tool_evidence_id(step=25) == "tool_step_25"


def test_build_tool_evidence_id_rejects_zero() -> None:
    with pytest.raises(
        ValueError,
        match=("Tool evidence step must be greater than zero."),
    ):
        build_tool_evidence_id(step=0)


def test_build_tool_evidence_id_rejects_negative() -> None:
    with pytest.raises(
        ValueError,
        match=("Tool evidence step must be greater than zero."),
    ):
        build_tool_evidence_id(step=-1)


def test_build_agent_evidence_registry() -> None:
    registry = build_agent_evidence_registry(history=build_history())

    assert set(registry) == {
        "tool_step_1",
        "tool_step_2",
    }


def test_registry_preserves_step_numbers() -> None:
    registry = build_agent_evidence_registry(history=build_history())

    assert registry["tool_step_1"].step == 1

    assert registry["tool_step_2"].step == 2


def test_registry_preserves_tool_names() -> None:
    registry = build_agent_evidence_registry(history=build_history())

    assert registry["tool_step_1"].tool_name == "analyze_revenue"

    assert registry["tool_step_2"].tool_name == "analyze_revenue_drivers"


def test_registry_preserves_success_state() -> None:
    history = AgentHistory(
        observations=[
            AgentObservation(
                call={
                    "tool_name": "missing_tool",
                },
                result={
                    "tool_name": "missing_tool",
                    "success": False,
                    "error": "Unknown tool.",
                },
            )
        ]
    )

    registry = build_agent_evidence_registry(history=history)

    assert registry["tool_step_1"].success is False


def test_empty_history_builds_empty_registry() -> None:
    registry = build_agent_evidence_registry(history=AgentHistory())

    assert registry == {}


def test_collect_agent_evidence_ids() -> None:
    evidence_ids = collect_agent_evidence_ids(history=build_history())

    assert evidence_ids == {
        "tool_step_1",
        "tool_step_2",
    }


def test_evidence_steps_to_ids() -> None:
    evidence_ids = evidence_steps_to_ids(
        evidence_steps=[
            1,
            3,
        ]
    )

    assert evidence_ids == [
        "tool_step_1",
        "tool_step_3",
    ]


def test_validate_grounded_fact_accepts_known_evidence() -> None:
    claims = [
        GroundedClaim(
            statement=("Revenue declined."),
            claim_type="fact",
            evidence_ids=[
                "tool_step_1",
            ],
        )
    ]

    validate_agent_grounded_claims(
        claims=claims,
        history=build_history(),
    )


def test_validate_grounded_inference_accepts_known_evidence() -> None:
    claims = [
        GroundedClaim(
            statement=("The observed drivers deserve further investigation."),
            claim_type="inference",
            evidence_ids=[
                "tool_step_2",
            ],
        )
    ]

    validate_agent_grounded_claims(
        claims=claims,
        history=build_history(),
    )


def test_validate_unknown_allows_no_evidence() -> None:
    claims = [
        GroundedClaim(
            statement=("Causality is not established."),
            claim_type="unknown",
            evidence_ids=[],
        )
    ]

    validate_agent_grounded_claims(
        claims=claims,
        history=build_history(),
    )


def test_validate_fact_rejects_missing_evidence() -> None:
    claims = [
        GroundedClaim(
            statement=("Revenue declined."),
            claim_type="fact",
            evidence_ids=[],
        )
    ]

    with pytest.raises(
        AgentGroundingError,
        match=("Agent facts and inferences must reference tool evidence."),
    ):
        validate_agent_grounded_claims(
            claims=claims,
            history=build_history(),
        )


def test_validate_inference_rejects_missing_evidence() -> None:
    claims = [
        GroundedClaim(
            statement=("South deserves investigation."),
            claim_type="inference",
            evidence_ids=[],
        )
    ]

    with pytest.raises(
        AgentGroundingError,
        match=("Agent facts and inferences must reference tool evidence."),
    ):
        validate_agent_grounded_claims(
            claims=claims,
            history=build_history(),
        )


def test_validate_claim_rejects_unknown_evidence() -> None:
    claims = [
        GroundedClaim(
            statement=("Revenue declined."),
            claim_type="fact",
            evidence_ids=[
                "tool_step_99",
            ],
        )
    ]

    with pytest.raises(
        AgentGroundingError,
        match=("Agent claim referenced unknown tool evidence."),
    ):
        validate_agent_grounded_claims(
            claims=claims,
            history=build_history(),
        )


def test_validate_claim_accepts_multiple_evidence_items() -> None:
    claims = [
        GroundedClaim(
            statement=(
                "Revenue declined and multiple observed signals deserve review."
            ),
            claim_type="inference",
            evidence_ids=[
                "tool_step_1",
                "tool_step_2",
            ],
        )
    ]

    validate_agent_grounded_claims(
        claims=claims,
        history=build_history(),
    )


def test_validate_multiple_claims() -> None:
    claims = [
        GroundedClaim(
            statement=("Revenue declined."),
            claim_type="fact",
            evidence_ids=[
                "tool_step_1",
            ],
        ),
        GroundedClaim(
            statement=("Observed drivers deserve investigation."),
            claim_type="inference",
            evidence_ids=[
                "tool_step_2",
            ],
        ),
        GroundedClaim(
            statement=("Causality is not established."),
            claim_type="unknown",
            evidence_ids=[],
        ),
    ]

    validate_agent_grounded_claims(
        claims=claims,
        history=build_history(),
    )
