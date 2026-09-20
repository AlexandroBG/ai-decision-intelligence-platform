from dataclasses import dataclass

from app.agent.contracts import AgentHistory
from app.llm.contracts import GroundedClaim

TOOL_EVIDENCE_PREFIX = "tool_step_"


@dataclass(frozen=True)
class AgentEvidenceReference:
    evidence_id: str
    step: int
    tool_name: str
    success: bool


class AgentGroundingError(ValueError):
    """Raised when agent claims reference invalid tool evidence."""


def build_tool_evidence_id(
    step: int,
) -> str:
    if step <= 0:
        raise ValueError("Tool evidence step must be greater than zero.")

    return f"{TOOL_EVIDENCE_PREFIX}{step}"


def build_agent_evidence_registry(
    history: AgentHistory,
) -> dict[str, AgentEvidenceReference]:
    registry: dict[
        str,
        AgentEvidenceReference,
    ] = {}

    for step, observation in enumerate(
        history.observations,
        start=1,
    ):
        evidence_id = build_tool_evidence_id(step=step)

        registry[evidence_id] = AgentEvidenceReference(
            evidence_id=evidence_id,
            step=step,
            tool_name=observation.call.tool_name,
            success=observation.result.success,
        )

    return registry


def collect_agent_evidence_ids(
    history: AgentHistory,
) -> set[str]:
    return set(build_agent_evidence_registry(history=history))


def evidence_steps_to_ids(
    evidence_steps: list[int],
) -> list[str]:
    return [build_tool_evidence_id(step=step) for step in evidence_steps]


def validate_agent_grounded_claims(
    claims: list[GroundedClaim],
    history: AgentHistory,
) -> None:
    available_evidence_ids = collect_agent_evidence_ids(history=history)

    for claim in claims:
        _validate_claim_evidence(
            claim=claim,
            available_evidence_ids=(available_evidence_ids),
        )


def _validate_claim_evidence(
    claim: GroundedClaim,
    available_evidence_ids: set[str],
) -> None:
    if (
        claim.claim_type
        in {
            "fact",
            "inference",
        }
        and not claim.evidence_ids
    ):
        raise AgentGroundingError(
            "Agent facts and inferences must reference tool evidence."
        )

    unknown_evidence_ids = [
        evidence_id
        for evidence_id in claim.evidence_ids
        if evidence_id not in available_evidence_ids
    ]

    if unknown_evidence_ids:
        raise AgentGroundingError("Agent claim referenced unknown tool evidence.")
