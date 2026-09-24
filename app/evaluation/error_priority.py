from collections import defaultdict
from typing import Any

from app.evaluation.error_analysis import (
    analyze_evaluation_run,
)
from app.evaluation.error_priority_contracts import (
    ErrorPriority,
    ErrorPriorityReport,
)

SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def build_error_priority_report(
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> ErrorPriorityReport:
    grouped_errors: dict[
        str,
        list[
            tuple[
                str,
                str,
            ]
        ],
    ] = defaultdict(list)

    for run in runs:
        analysis = analyze_evaluation_run(run=run)

        for error in analysis.errors:
            grouped_errors[error.code].append(
                (
                    error.category,
                    error.severity,
                )
            )

    priorities: list[ErrorPriority] = []

    for (
        code,
        entries,
    ) in grouped_errors.items():
        category = entries[0][0]

        severity = _highest_severity(severities=[entry[1] for entry in entries])

        occurrences = len(entries)

        severity_weight = SEVERITY_WEIGHTS[severity]

        priority_score = occurrences * severity_weight

        priorities.append(
            ErrorPriority(
                code=code,
                category=category,
                severity=severity,
                occurrences=(occurrences),
                severity_weight=(severity_weight),
                priority_score=(priority_score),
            )
        )

    priorities.sort(
        key=lambda priority: (
            -priority.priority_score,
            -priority.severity_weight,
            -priority.occurrences,
            priority.code,
        )
    )

    top_priority_code = priorities[0].code if priorities else None

    return ErrorPriorityReport(
        total_prioritized_errors=len(priorities),
        priorities=priorities,
        top_priority_code=(top_priority_code),
    )


def _highest_severity(
    *,
    severities: list[str],
) -> str:
    return max(
        severities,
        key=lambda severity: SEVERITY_WEIGHTS[severity],
    )
