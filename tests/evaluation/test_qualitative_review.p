import pytest

from app.evaluation.qualitative_review import (
    QUALITATIVE_CRITERIA,
    build_qualitative_review,
)
from app.evaluation.qualitative_review_contracts import (
    QualitativeCheck,
)


def build_passing_checks() -> list[
    QualitativeCheck
]:
    return [
        QualitativeCheck(
            criterion=criterion,
            status="pass",
            notes=(
                "No concern observed."
            ),
        )
        for criterion
        in QUALITATIVE_CRITERIA
    ]


def test_clean_review_passes() -> None:
    review = (
        build_qualitative_review(
            case_id=(
                "revenue_decline_v1"
            ),
            run_number=1,
            checks=(
                build_passing_checks()
            ),
        )
    )

    assert (
        review.concerns_found
        == 0
    )

    assert (
        review.unclear_checks
        == 0
    )

    assert (
        review.review_passed
        is True
    )


def test_concern_fails_review() -> None:
    checks = (
        build_passing_checks()
    )

    checks[0] = (
        QualitativeCheck(
            criterion=(
                "causal_language"
            ),
            status="concern",
            notes=(
                "The answer uses "
                "'root cause' without "
                "causal evidence."
            ),
        )
    )

    review = (
        build_qualitative_review(
            case_id=(
                "revenue_decline_v1"
            ),
            run_number=1,
            checks=checks,
        )
    )

    assert (
        review.concerns_found
        == 1
    )

    assert (
        review.review_passed
        is False
    )


def test_unclear_check_fails_review() -> None:
    checks = (
        build_passing_checks()
    )

    checks[1] = (
        QualitativeCheck(
            criterion=(
                "evidence_alignment"
            ),
            status="unclear",
            notes=(
                "Evidence provenance "
                "requires manual review."
            ),
        )
    )

    review = (
        build_qualitative_review(
            case_id=(
                "revenue_decline_v1"
            ),
            run_number=1,
            checks=checks,
        )
    )

    assert (
        review.unclear_checks
        == 1
    )

    assert (
        review.review_passed
        is False
    )


def test_missing_criterion_is_rejected() -> None:
    checks = (
        build_passing_checks()
    )[:-1]

    with pytest.raises(
        ValueError,
        match=(
            "missing criteria"
        ),
    ):
        build_qualitative_review(
            case_id=(
                "revenue_decline_v1"
            ),
            run_number=1,
            checks=checks,
        )


def test_duplicate_criterion_is_rejected() -> None:
    checks = (
        build_passing_checks()
    )

    checks[-1] = (
        QualitativeCheck(
            criterion=(
                "causal_language"
            ),
            status="pass",
            notes=(
                "Duplicate test."
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "duplicate criteria"
        ),
    ):
        build_qualitative_review(
            case_id=(
                "revenue_decline_v1"
            ),
            run_number=1,
            checks=checks,
        )


def test_invalid_run_number_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "greater than zero"
        ),
    ):
        build_qualitative_review(
            case_id=(
                "revenue_decline_v1"
            ),
            run_number=0,
            checks=(
                build_passing_checks()
            ),
        )


def test_empty_case_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "case_id must not "
            "be empty"
        ),
    ):
        build_qualitative_review(
            case_id="   ",
            run_number=1,
            checks=(
                build_passing_checks()
            ),
        )