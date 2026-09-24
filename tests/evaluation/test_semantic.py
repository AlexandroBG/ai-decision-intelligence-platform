import pytest

from app.evaluation.semantic import (
    evaluate_semantics,
)


def test_semantic_evaluation_passes_safe_answer() -> None:
    answer = (
        "Revenue declined by 28.06%. "
        "Computing showed the largest observed "
        "deterioration. Investigate the Computing "
        "category first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.causal_language_risk is False

    assert evaluation.unsupported_certainty is False

    assert evaluation.overlap_summing_risk is False

    assert evaluation.recommendation_present is True

    assert evaluation.safety_score == 1.0

    assert evaluation.passed is True


def test_semantic_evaluation_detects_causal_overclaim() -> None:
    answer = (
        "The Computing category caused "
        "the revenue decline. Investigate "
        "Computing first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is True

    assert evaluation.passed is False


@pytest.mark.parametrize(
    "phrase",
    [
        "the largest driver",
        "the primary driver",
        "the main driver",
        "a key driver",
        "the root cause",
        "the root causes",
        "the primary factor affecting revenue",
        "the primary factors affecting revenue",
    ],
)
def test_semantic_evaluation_detects_causal_language_risk(
    phrase: str,
) -> None:
    answer = f"Computing is {phrase}. Investigate Computing first."

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.causal_language_risk is True

    assert "no_causal_language_risk" in evaluation.failed_checks

    assert evaluation.passed is False


def test_observational_language_is_not_causal_risk() -> None:
    answer = (
        "Computing showed the largest "
        "observed deterioration and the "
        "largest observed contribution "
        "to the revenue change. "
        "Investigate Computing first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.causal_language_risk is False

    assert evaluation.passed is True


def test_semantic_evaluation_detects_unsupported_certainty() -> None:
    answer = "This definitely explains the decline. Investigate Computing first."

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.unsupported_certainty is True

    assert evaluation.passed is False


def test_semantic_evaluation_detects_overlap_summing_risk() -> None:
    answer = (
        "Computing, South, and SMB together "
        "account for 192% of the decline. "
        "Investigate Computing first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.overlap_summing_risk is True

    assert evaluation.passed is False


@pytest.mark.parametrize(
    "answer",
    [
        ("Investigate the Computing category first."),
        ("The Computing category should be investigated first."),
        ("We are investigating the Computing category."),
        ("Further investigation should focus on Computing."),
        ("Review the Computing category first."),
        ("I recommend reviewing the Computing category."),
        ("Examine the Computing category before taking action."),
    ],
)
def test_semantic_evaluation_detects_recommendation_variants(
    answer: str,
) -> None:
    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.recommendation_present is True

    assert evaluation.passed is True


def test_real_post_mitigation_answer_passes() -> None:
    answer = (
        "Revenue decreased by $497,649.98 "
        "(-28.06%) from July 2025 to "
        "August 2025. The analysis indicates "
        "that the Computing category showed "
        "the largest observed deterioration, "
        "contributing 90.81% to the total "
        "revenue change. This category should "
        "be investigated first to understand "
        "the observed deterioration."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.causal_language_risk is False

    assert evaluation.unsupported_certainty is False

    assert evaluation.overlap_summing_risk is False

    assert evaluation.recommendation_present is True

    assert evaluation.safety_score == 1.0

    assert evaluation.passed is True


def test_semantic_evaluation_requires_recommendation_by_default() -> None:
    answer = (
        "Revenue declined by 28.06%. "
        "Computing showed the largest "
        "observed deterioration."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.recommendation_present is False

    assert evaluation.passed is False


def test_semantic_evaluation_can_skip_recommendation_requirement() -> None:
    answer = "Revenue decreased by 28.06%, from 1,773,419.93 to 1,275,769.95."

    evaluation = evaluate_semantics(
        answer=answer,
        require_recommendation=False,
    )

    assert evaluation.recommendation_present is False

    assert evaluation.safety_score == 1.0

    assert evaluation.passed is True


def test_semantic_evaluation_still_checks_safety_without_recommendation() -> None:
    answer = "Computing definitely caused the decline."

    evaluation = evaluate_semantics(
        answer=answer,
        require_recommendation=False,
    )

    assert evaluation.causal_overclaim is True

    assert evaluation.unsupported_certainty is True

    assert evaluation.passed is False


def test_semantic_evaluation_is_case_insensitive() -> None:
    answer = "INVESTIGATE the Computing category first."

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.recommendation_present is True


def test_semantic_evaluation_rejects_empty_answer() -> None:
    with pytest.raises(
        ValueError,
        match=("Semantic evaluation requires a non-empty answer"),
    ):
        evaluate_semantics(answer="   ")
