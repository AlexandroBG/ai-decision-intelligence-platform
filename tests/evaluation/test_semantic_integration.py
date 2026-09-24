from app.evaluation.semantic import (
    evaluate_semantics,
)


def test_revenue_decline_style_answer_passes_semantic_checks() -> None:
    answer = (
        "Revenue decreased by 28.06%. "
        "The Computing category showed the "
        "largest observed deterioration. "
        "Other notable deteriorations were "
        "observed in South and SMB. "
        "Investigate the Computing category "
        "first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.unsupported_certainty is False

    assert evaluation.overlap_summing_risk is False

    assert evaluation.recommendation_present is True

    assert evaluation.safety_score == 1.0

    assert evaluation.passed is True


def test_causal_revenue_answer_fails_semantic_checks() -> None:
    answer = (
        "Computing caused the revenue decline "
        "and definitely explains the problem. "
        "Investigate Computing first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is True

    assert evaluation.unsupported_certainty is True

    assert evaluation.passed is False
