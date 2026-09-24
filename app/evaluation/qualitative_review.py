from app.evaluation.qualitative_review_contracts import (
    QualitativeCheck,
    QualitativeReview,
)

QUALITATIVE_CRITERIA = (
    "causal_language",
    "evidence_alignment",
    "scope_adherence",
    "overlapping_contributions",
    "recommendation_strength",
    "unsupported_specificity",
    "answer_completeness",
)


def build_qualitative_review(
    *,
    case_id: str,
    run_number: int,
    checks: list[QualitativeCheck],
) -> QualitativeReview:
    if not case_id.strip():
        raise ValueError("case_id must not be empty.")

    if run_number <= 0:
        raise ValueError("run_number must be greater than zero.")

    _validate_review_criteria(checks=checks)

    concerns_found = sum(1 for check in checks if check.status == "concern")

    unclear_checks = sum(1 for check in checks if check.status == "unclear")

    review_passed = concerns_found == 0 and unclear_checks == 0

    return QualitativeReview(
        case_id=case_id.strip(),
        run_number=run_number,
        checks=checks,
        concerns_found=(concerns_found),
        unclear_checks=(unclear_checks),
        review_passed=(review_passed),
    )


def _validate_review_criteria(
    *,
    checks: list[QualitativeCheck],
) -> None:
    provided_criteria = [check.criterion for check in checks]

    if len(provided_criteria) != len(set(provided_criteria)):
        raise ValueError("Qualitative review contains duplicate criteria.")

    expected = set(QUALITATIVE_CRITERIA)

    provided = set(provided_criteria)

    missing = expected - provided

    unexpected = provided - expected

    if missing:
        raise ValueError(f"Qualitative review is missing criteria: {sorted(missing)}")

    if unexpected:
        raise ValueError(
            f"Qualitative review contains unexpected criteria: {sorted(unexpected)}"
        )
