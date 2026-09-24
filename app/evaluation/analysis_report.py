from typing import Any

from app.evaluation.analysis_report_contracts import (
    EvaluationAnalysisReport,
)
from app.evaluation.error_priority import (
    build_error_priority_report,
)
from app.evaluation.error_report import (
    build_error_report,
)


def build_evaluation_analysis_report(
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> EvaluationAnalysisReport:
    error_report = build_error_report(runs=runs)

    priority_report = build_error_priority_report(runs=runs)

    recommended_action = _build_recommended_action(
        top_priority_code=(priority_report.top_priority_code),
        total_errors=(error_report.total_errors),
    )

    return EvaluationAnalysisReport(
        total_runs_analyzed=(error_report.total_runs_analyzed),
        runs_with_errors=(error_report.runs_with_errors),
        total_errors=(error_report.total_errors),
        high_severity_errors=(error_report.high_severity_errors),
        medium_severity_errors=(error_report.medium_severity_errors),
        low_severity_errors=(error_report.low_severity_errors),
        errors_by_category=(error_report.errors_by_category),
        errors_by_code=(error_report.errors_by_code),
        priorities=(priority_report.priorities),
        top_priority_code=(priority_report.top_priority_code),
        recommended_action=(recommended_action),
    )


def _build_recommended_action(
    *,
    top_priority_code: str | None,
    total_errors: int,
) -> str:
    if total_errors == 0:
        return (
            "No machine-detected evaluation "
            "errors were observed. Review "
            "qualitative risks and expand "
            "evaluation coverage before "
            "changing system behavior."
        )

    if top_priority_code is None:
        return "Errors were detected, but no priority code could be selected."

    return f"Investigate the highest-priority error first: {top_priority_code}."
