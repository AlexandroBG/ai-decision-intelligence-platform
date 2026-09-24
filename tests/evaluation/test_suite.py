import pytest

from app.evaluation.suite import (
    build_evaluation_suite_summary,
)


def build_quality_result(
    *,
    passed: bool = True,
) -> dict[str, object]:
    return {
        "result_type": ("quality_result"),
        "passed": passed,
    }


def build_provider_error_result() -> dict[
    str,
    object,
]:
    return {
        "result_type": ("provider_error"),
        "passed": None,
    }


def test_suite_summary_passes_all_cases() -> None:
    results = [
        build_quality_result(),
        build_quality_result(),
    ]

    summary = build_evaluation_suite_summary(
        requested_cases=2,
        case_results=results,
    )

    assert summary.requested_cases == 2

    assert summary.evaluated_cases == 2

    assert summary.provider_errors == 0

    assert summary.passed_cases == 2

    assert summary.case_pass_rate == 1.0

    assert summary.evaluation_coverage == 1.0

    assert summary.suite_completed is True

    assert summary.suite_passed is True


def test_suite_summary_detects_quality_failure() -> None:
    results = [
        build_quality_result(),
        build_quality_result(passed=False),
    ]

    summary = build_evaluation_suite_summary(
        requested_cases=2,
        case_results=results,
    )

    assert summary.case_pass_rate == 0.5

    assert summary.suite_completed is True

    assert summary.suite_passed is False


def test_suite_summary_separates_provider_error() -> None:
    results = [
        build_quality_result(),
        build_provider_error_result(),
    ]

    summary = build_evaluation_suite_summary(
        requested_cases=2,
        case_results=results,
    )

    assert summary.evaluated_cases == 1

    assert summary.provider_errors == 1

    assert summary.case_pass_rate == 1.0

    assert summary.evaluation_coverage == 0.5

    assert summary.suite_completed is False

    assert summary.suite_passed is None


def test_suite_summary_handles_no_evaluated_cases() -> None:
    results = [build_provider_error_result()]

    summary = build_evaluation_suite_summary(
        requested_cases=2,
        case_results=results,
    )

    assert summary.evaluated_cases == 0

    assert summary.case_pass_rate is None

    assert summary.evaluation_coverage == 0.0

    assert summary.suite_passed is None


def test_suite_summary_rejects_invalid_case_count() -> None:
    with pytest.raises(
        ValueError,
        match=("requested_cases must be greater than zero"),
    ):
        build_evaluation_suite_summary(
            requested_cases=0,
            case_results=[],
        )
