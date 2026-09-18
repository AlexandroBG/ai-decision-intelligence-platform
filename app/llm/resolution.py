from app.llm.contracts import (
    EvidenceContext,
    LLMInterpretation,
    ResolvedGroundedClaim,
)
from app.llm.registry import (
    build_evidence_registry,
    resolve_evidence,
)


def resolve_grounded_claims(
    evidence: EvidenceContext,
    interpretation: LLMInterpretation,
) -> list[ResolvedGroundedClaim]:
    registry = build_evidence_registry(
        evidence=evidence,
    )

    resolved_claims: list[ResolvedGroundedClaim] = []

    for claim in interpretation.grounded_claims:
        resolved_evidence = [
            resolve_evidence(
                registry=registry,
                evidence_id=evidence_id,
            )
            for evidence_id in claim.evidence_ids
        ]

        resolved_claims.append(
            ResolvedGroundedClaim(
                claim_type=claim.claim_type,
                statement=claim.statement,
                evidence=resolved_evidence,
            )
        )

    return resolved_claims
