from app.evaluation.error_analysis import (
    analyze_evaluation_run,
)
from app.evaluation.semantic import (
    evaluate_semantics,
)


def test_previous_real_answer_is_now_detected() -> None:
    answer = (
        "Revenue decreased by 497,649.98 "
        "(28.06%) from July 2025 to "
        "August 2025. The primary factors "
        "affecting revenue performance "
        "include significant deteriorations "
        "in the Computing category and the "
        "South region. You should investigate "
        "the Computing category first, as it "
        "is the largest driver of the "
        "revenue decrease."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.causal_language_risk is True

    assert evaluation.passed is False


def test_preferred_observational_wording_passes() -> None:
    answer = (
        "Revenue decreased by 497,649.98 "
        "(28.06%) from July 2025 to "
        "August 2025. Computing showed "
        "the largest observed revenue "
        "deterioration. Investigate the "
        "Computing category first."
    )

    evaluation = evaluate_semantics(answer=answer)

    assert evaluation.causal_overclaim is False

    assert evaluation.causal_language_risk is False

    assert evaluation.passed is True


def test_causal_language_risk_enters_error_analysis() -> None:
    run = {
        "run": 1,
        "case_id": ("revenue_decline_v1"),
        "run_type": ("quality_result"),
        "agent_metrics": {
            "completed": True,
            "duplicate_tool_calls": 0,
        },
        "tool_selection": {
            "missing_required_tools": [],
            "unexpected_tools": [],
        },
        "ground_truth": {
            "passed": True,
        },
        "semantic_evaluation": {
            "causal_overclaim": False,
            "causal_language_risk": True,
            "unsupported_certainty": False,
            "overlap_summing_risk": False,
            "recommendation_present": True,
            "failed_checks": ["no_causal_language_risk"],
        },
    }

    analysis = analyze_evaluation_run(run=run)

    assert analysis.total_errors == 1

    assert analysis.errors[0].category == "semantic"

    assert analysis.errors[0].code == "causal_language_risk"

    assert analysis.errors[0].severity == "medium"
