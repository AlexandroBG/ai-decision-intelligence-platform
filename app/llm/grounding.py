from dataclasses import dataclass

from app.llm.contracts import (
    EvidenceContext,
    LLMInterpretation,
)
from app.llm.registry import build_evidence_registry

DEFAULT_MIN_GROUNDING_COVERAGE = 1.0


class GroundingValidationError(ValueError):
    """Raised when LLM grounding is invalid."""


class GroundingCoverageError(GroundingValidationError):
    """Raised when grounding coverage is too low."""


@dataclass(frozen=True)
class GroundingCoverage:
    expected_claims: int
    grounded_claims: int
    coverage_ratio: float


def collect_evidence_ids(
    evidence: EvidenceContext,
) -> set[str]:
    registry = build_evidence_registry(
        evidence=evidence,
    )

    return set(registry.keys())


def validate_grounding(
    evidence: EvidenceContext,
    interpretation: LLMInterpretation,
) -> None:
    valid_evidence_ids = collect_evidence_ids(
        evidence=evidence,
    )

    for claim in interpretation.grounded_claims:
        if (
            claim.claim_type
            in {
                "fact",
                "inference",
            }
            and not claim.evidence_ids
        ):
            raise GroundingValidationError(
                f"{claim.claim_type.capitalize()} "
                "claim must reference at least "
                "one evidence_id."
            )

        for evidence_id in claim.evidence_ids:
            if evidence_id not in valid_evidence_ids:
                raise GroundingValidationError(
                    f"Unknown evidence_id referenced by grounded claim: {evidence_id}"
                )


def calculate_grounding_coverage(
    interpretation: LLMInterpretation,
) -> GroundingCoverage:
    expected_claims = [
        claim
        for claim in interpretation.grounded_claims
        if claim.claim_type
        in {
            "fact",
            "inference",
        }
    ]

    grounded_claims = [claim for claim in expected_claims if claim.evidence_ids]

    expected_count = len(expected_claims)

    grounded_count = len(grounded_claims)

    if expected_count == 0:
        coverage_ratio = 1.0
    else:
        coverage_ratio = grounded_count / expected_count

    return GroundingCoverage(
        expected_claims=expected_count,
        grounded_claims=grounded_count,
        coverage_ratio=coverage_ratio,
    )


def enforce_grounding_coverage(
    interpretation: LLMInterpretation,
    minimum_coverage: float = (DEFAULT_MIN_GROUNDING_COVERAGE),
) -> GroundingCoverage:
    if not 0.0 <= minimum_coverage <= 1.0:
        raise ValueError("minimum_coverage must be between 0 and 1.")

    coverage = calculate_grounding_coverage(
        interpretation=interpretation,
    )

    if coverage.coverage_ratio < minimum_coverage:
        raise GroundingCoverageError(
            "Grounding coverage is below the "
            "required threshold: "
            f"{coverage.coverage_ratio:.2f} "
            f"< {minimum_coverage:.2f}."
        )

    return coverage
