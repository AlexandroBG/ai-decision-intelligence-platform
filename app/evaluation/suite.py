from typing import Any

from app.evaluation.suite_contracts import (
    EvaluationSuiteSummary,
)


def build_evaluation_suite_summary(
    requested_cases: int,
    case_results: list[
        dict[
            str,
            Any,
        ]
    ],
) -> EvaluationSuiteSummary:
    if requested_cases <= 0:
        raise ValueError("requested_cases must be greater than zero.")

    attempted_cases = len(case_results)

    quality_results = [
        result
        for result in case_results
        if result.get("result_type") == "quality_result"
    ]

    provider_error_results = [
        result
        for result in case_results
        if result.get("result_type") == "provider_error"
    ]

    evaluated_cases = len(quality_results)

    provider_errors = len(provider_error_results)

    passed_cases = sum(1 for result in quality_results if result.get("passed") is True)

    evaluation_coverage = evaluated_cases / requested_cases

    if evaluated_cases == 0:
        case_pass_rate = None
    else:
        case_pass_rate = passed_cases / evaluated_cases

    suite_completed = evaluated_cases == requested_cases

    if not suite_completed:
        suite_passed = None
    else:
        suite_passed = passed_cases == requested_cases

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
