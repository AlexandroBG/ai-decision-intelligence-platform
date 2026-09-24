import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.evaluation.analysis_report import (
    build_evaluation_analysis_report,
)
from app.evaluation.error_report import (
    collect_suite_runs,
)

INPUT_PATH = PROJECT_ROOT / "artifacts" / "phase10" / "evaluation_suite.json"

OUTPUT_DIRECTORY = PROJECT_ROOT / "artifacts" / "phase11"

OUTPUT_PATH = OUTPUT_DIRECTORY / "error_analysis.json"


def load_evaluation_suite() -> dict[
    str,
    Any,
]:
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(f"Evaluation suite artifact not found: {INPUT_PATH}")

    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def save_analysis(
    payload: dict[
        str,
        Any,
    ],
) -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def print_analysis(
    report: Any,
) -> None:
    print("DecisionAI Error Analysis")

    print("=" * 72)

    print(f"Runs analyzed: {report.total_runs_analyzed}")

    print(f"Runs with errors: {report.runs_with_errors}")

    print(f"Total errors: {report.total_errors}")

    print()
    print("SEVERITY")

    print("-" * 72)

    print(f"High: {report.high_severity_errors}")

    print(f"Medium: {report.medium_severity_errors}")

    print(f"Low: {report.low_severity_errors}")

    print()
    print("ERRORS BY CATEGORY")

    print("-" * 72)

    if report.errors_by_category:
        for item in report.errors_by_category:
            print(f"{item.name}: {item.count}")
    else:
        print("None")

    print()
    print("PRIORITIES")

    print("-" * 72)

    if report.priorities:
        for index, priority in enumerate(
            report.priorities,
            start=1,
        ):
            print(
                f"{index}. "
                f"{priority.code}"
                f" | category="
                f"{priority.category}"
                f" | severity="
                f"{priority.severity}"
                f" | occurrences="
                f"{priority.occurrences}"
                f" | score="
                f"{priority.priority_score}"
            )
    else:
        print("No machine-detected errors to prioritize.")

    print()
    print("TOP PRIORITY")

    print("-" * 72)

    print(report.top_priority_code or "None")

    print()
    print("RECOMMENDED ACTION")

    print("-" * 72)

    print(report.recommended_action)

    print()
    print(f"Artifact: {OUTPUT_PATH}")


def main() -> None:
    suite = load_evaluation_suite()

    case_results = suite.get(
        "cases",
        [],
    )

    runs = collect_suite_runs(case_results=(case_results))

    report = build_evaluation_analysis_report(runs=runs)

    payload = {
        "source_artifact": (str(INPUT_PATH)),
        "analysis": (report.model_dump(mode="json")),
    }

    save_analysis(payload=payload)

    print_analysis(report=report)


if __name__ == "__main__":
    main()
