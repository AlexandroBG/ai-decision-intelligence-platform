from app.evaluation.gate_contracts import (
    EvaluationGateResult,
)
from app.evaluation.suite_contracts import (
    EvaluationSuiteSummary,
)

DEFAULT_MINIMUM_COVERAGE = 1.0
DEFAULT_MINIMUM_CASE_PASS_RATE = 1.0


def evaluate_suite_gate(
    summary: EvaluationSuiteSummary,
    *,
    minimum_coverage: float = DEFAULT_MINIMUM_COVERAGE,
    minimum_case_pass_rate: float = (DEFAULT_MINIMUM_CASE_PASS_RATE),
) -> EvaluationGateResult:
    _validate_threshold(
        name="minimum_coverage",
        value=minimum_coverage,
    )

    _validate_threshold(
        name="minimum_case_pass_rate",
        value=minimum_case_pass_rate,
    )

    suite_completed = summary.suite_completed

    coverage_passed = summary.evaluation_coverage >= minimum_coverage

    case_pass_rate_passed = (
        summary.case_pass_rate is not None
        and summary.case_pass_rate >= minimum_case_pass_rate
    )

    provider_availability_passed = summary.provider_errors == 0

    checks = {
        "suite_completed": (suite_completed),
        "coverage_threshold": (coverage_passed),
        "case_pass_rate_threshold": (case_pass_rate_passed),
        "provider_availability": (provider_availability_passed),
    }

    passed_checks = [name for name, passed in checks.items() if passed]

    failed_checks = [name for name, passed in checks.items() if not passed]

    return EvaluationGateResult(
        suite_completed=(suite_completed),
        coverage_passed=(coverage_passed),
        case_pass_rate_passed=(case_pass_rate_passed),
        provider_availability_passed=(provider_availability_passed),
        passed_checks=(passed_checks),
        failed_checks=(failed_checks),
        gate_passed=(not failed_checks),
    )


def _validate_threshold(
    *,
    name: str,
    value: float,
) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0.")
