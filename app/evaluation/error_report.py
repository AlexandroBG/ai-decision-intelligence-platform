from collections import Counter
from typing import Any

from app.evaluation.error_analysis import (
    analyze_evaluation_run,
)
from app.evaluation.error_report_contracts import (
    ErrorCount,
    ErrorReport,
)


def build_error_report(
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> ErrorReport:
    category_counts: Counter[str] = Counter()

    code_counts: Counter[str] = Counter()

    high_severity_errors = 0
    medium_severity_errors = 0
    low_severity_errors = 0
    runs_with_errors = 0
    total_errors = 0

    for run in runs:
        analysis = analyze_evaluation_run(run=run)

        if analysis.total_errors > 0:
            runs_with_errors += 1

        total_errors += analysis.total_errors

        for error in analysis.errors:
            category_counts[error.category] += 1

            code_counts[error.code] += 1

            if error.severity == "high":
                high_severity_errors += 1

            elif error.severity == "medium":
                medium_severity_errors += 1

            else:
                low_severity_errors += 1

    errors_by_category = _to_error_counts(counts=category_counts)

    errors_by_code = _to_error_counts(counts=code_counts)

    top_error_code = errors_by_code[0].name if errors_by_code else None

    return ErrorReport(
        total_runs_analyzed=len(runs),
        runs_with_errors=(runs_with_errors),
        total_errors=(total_errors),
        high_severity_errors=(high_severity_errors),
        medium_severity_errors=(medium_severity_errors),
        low_severity_errors=(low_severity_errors),
        errors_by_category=(errors_by_category),
        errors_by_code=(errors_by_code),
        top_error_code=(top_error_code),
    )


def collect_suite_runs(
    case_results: list[
        dict[
            str,
            Any,
        ]
    ],
) -> list[
    dict[
        str,
        Any,
    ]
]:
    runs: list[
        dict[
            str,
            Any,
        ]
    ] = []

    for case_result in case_results:
        case_runs = case_result.get(
            "runs",
            [],
        )

        runs.extend(case_runs)

    return runs


def _to_error_counts(
    *,
    counts: Counter[str],
) -> list[ErrorCount]:
    ordered = sorted(
        counts.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    return [
        ErrorCount(
            name=name,
            count=count,
        )
        for name, count in ordered
    ]
