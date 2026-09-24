import pytest

from app.evaluation.gates import (
    evaluate_suite_gate,
)
from app.evaluation.suite_contracts import (
    EvaluationSuiteSummary,
)


def build_summary(
    *,
    requested_cases: int = 2,
    attempted_cases: int = 2,
    evaluated_cases: int = 2,
    provider_errors: int = 0,
    passed_cases: int = 2,
    case_pass_rate: float | None = 1.0,
    evaluation_coverage: float = 1.0,
    suite_completed: bool = True,
    suite_passed: bool | None = True,
) -> EvaluationSuiteSummary:
    return EvaluationSuiteSummary(
        requested_cases=(requested_cases),
        attempted_cases=(attempted_cases),
        evaluated_cases=(evaluated_cases),
        provider_errors=(provider_errors),
        passed_cases=(passed_cases),
        case_pass_rate=(case_pass_rate),
        evaluation_coverage=(evaluation_coverage),
        suite_completed=(suite_completed),
        suite_passed=(suite_passed),
    )


def test_gate_passes_complete_successful_suite() -> None:
    summary = build_summary()

    result = evaluate_suite_gate(summary=summary)

    assert result.suite_completed is True

    assert result.coverage_passed is True

    assert result.case_pass_rate_passed is True

    assert result.provider_availability_passed is True

    assert result.failed_checks == []

    assert result.gate_passed is True


def test_gate_fails_incomplete_suite() -> None:
    summary = build_summary(
        attempted_cases=1,
        evaluated_cases=1,
        provider_errors=1,
        passed_cases=1,
        case_pass_rate=1.0,
        evaluation_coverage=0.5,
        suite_completed=False,
        suite_passed=None,
    )

    result = evaluate_suite_gate(summary=summary)

    assert result.suite_completed is False

    assert result.coverage_passed is False

    assert result.provider_availability_passed is False

    assert result.gate_passed is False


def test_gate_fails_quality_threshold() -> None:
    summary = build_summary(
        passed_cases=1,
        case_pass_rate=0.5,
        suite_completed=True,
        suite_passed=False,
    )

    result = evaluate_suite_gate(summary=summary)

    assert result.case_pass_rate_passed is False

    assert result.gate_passed is False


def test_gate_supports_custom_thresholds() -> None:
    summary = build_summary(
        passed_cases=9,
        case_pass_rate=0.9,
    )

    result = evaluate_suite_gate(
        summary=summary,
        minimum_case_pass_rate=0.8,
    )

    assert result.case_pass_rate_passed is True

    assert result.gate_passed is True


@pytest.mark.parametrize(
    "threshold_name, threshold_value",
    [
        (
            "minimum_coverage",
            -0.1,
        ),
        (
            "minimum_coverage",
            1.1,
        ),
        (
            "minimum_case_pass_rate",
            -0.1,
        ),
        (
            "minimum_case_pass_rate",
            1.1,
        ),
    ],
)
def test_gate_rejects_invalid_thresholds(
    threshold_name: str,
    threshold_value: float,
) -> None:
    summary = build_summary()

    kwargs = {
        threshold_name: (threshold_value),
    }

    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        evaluate_suite_gate(
            summary=summary,
            **kwargs,
        )
