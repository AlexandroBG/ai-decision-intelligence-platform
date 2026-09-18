from app.llm.contracts import (
    EvidenceContext,
    EvidenceItem,
)


class EvidenceRegistryError(ValueError):
    """Raised when the evidence registry is invalid."""


def build_evidence_registry(
    evidence: EvidenceContext,
) -> dict[str, EvidenceItem]:
    registry: dict[str, EvidenceItem] = {}

    evidence_items: list[EvidenceItem] = [
        evidence.revenue,
        *evidence.analytics_drivers,
        *evidence.ml_anomalies,
    ]

    for item in evidence_items:
        if item.evidence_id in registry:
            raise EvidenceRegistryError(
                f"Duplicate evidence_id detected: {item.evidence_id}"
            )

        registry[item.evidence_id] = item

    return registry


def resolve_evidence(
    registry: dict[str, EvidenceItem],
    evidence_id: str,
) -> EvidenceItem:
    if evidence_id not in registry:
        raise EvidenceRegistryError(f"Unknown evidence_id: {evidence_id}")

    return registry[evidence_id]
