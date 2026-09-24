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


from app.evaluation.qualitative_review import (
    build_qualitative_review,
)
from app.evaluation.qualitative_review_contracts import (
    QualitativeCheck,
)

INPUT_PATH = PROJECT_ROOT / "artifacts" / "phase10" / "evaluation_suite.json"

OUTPUT_DIRECTORY = PROJECT_ROOT / "artifacts" / "phase11"

OUTPUT_PATH = OUTPUT_DIRECTORY / "revenue_decline_v1_qualitative_review.json"

TARGET_CASE_ID = "revenue_decline_v1"


def load_suite() -> dict[
    str,
    Any,
]:
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(f"Evaluation suite artifact not found: {INPUT_PATH}")

    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def find_latest_quality_run(
    suite: dict[
        str,
        Any,
    ],
) -> dict[
    str,
    Any,
]:
    case_results = suite.get(
        "cases",
        [],
    )

    for case_result in case_results:
        if case_result.get("case_id") != TARGET_CASE_ID:
            continue

        quality_runs = [
            run
            for run in case_result.get(
                "runs",
                [],
            )
            if run.get("run_type") == "quality_result"
        ]

        if not quality_runs:
            raise ValueError(f"No quality run found for case: {TARGET_CASE_ID}")

        return quality_runs[-1]

    raise ValueError(f"Case not found in evaluation suite: {TARGET_CASE_ID}")


def build_review(
    run: dict[
        str,
        Any,
    ],
) -> dict[
    str,
    Any,
]:
    review = build_qualitative_review(
        case_id=(TARGET_CASE_ID),
        run_number=int(
            run.get(
                "run",
                1,
            )
        ),
        checks=[
            QualitativeCheck(
                criterion=("causal_language"),
                status="unclear",
                notes=(
                    "The answer uses phrases "
                    "such as 'primary factors "
                    "affecting' and 'largest "
                    "driver'. These phrases "
                    "may imply stronger causal "
                    "meaning than the "
                    "observational evidence "
                    "supports."
                ),
            ),
            QualitativeCheck(
                criterion=("evidence_alignment"),
                status="pass",
                notes=(
                    "The reported revenue "
                    "decline and ranked "
                    "deteriorations are "
                    "aligned with tool "
                    "outputs."
                ),
            ),
            QualitativeCheck(
                criterion=("scope_adherence"),
                status="pass",
                notes=(
                    "The answer compares "
                    "revenue, identifies "
                    "observed deterioration, "
                    "and recommends what to "
                    "investigate first."
                ),
            ),
            QualitativeCheck(
                criterion=("overlapping_contributions"),
                status="pass",
                notes=(
                    "The answer reports "
                    "category and region "
                    "contributions separately "
                    "and does not sum them."
                ),
            ),
            QualitativeCheck(
                criterion=("recommendation_strength"),
                status="pass",
                notes=(
                    "Investigating Computing "
                    "first is proportional to "
                    "its observed deterioration "
                    "and does not prescribe an "
                    "irreversible business "
                    "action."
                ),
            ),
            QualitativeCheck(
                criterion=("unsupported_specificity"),
                status="pass",
                notes=(
                    "The response does not add "
                    "unsupported detailed "
                    "claims beyond the "
                    "available evidence."
                ),
            ),
            QualitativeCheck(
                criterion=("answer_completeness"),
                status="pass",
                notes=(
                    "The response answers the "
                    "revenue-change and "
                    "investigation-priority "
                    "parts of the question."
                ),
            ),
        ],
    )

    return {
        "source_case": (TARGET_CASE_ID),
        "source_answer": (run.get("answer")),
        "automatic_semantic_evaluation": (run.get("semantic_evaluation")),
        "qualitative_review": (review.model_dump(mode="json")),
    }


def save_review(
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


def print_review(
    payload: dict[
        str,
        Any,
    ],
) -> None:
    review = payload["qualitative_review"]

    print("DecisionAI Qualitative Review")

    print("=" * 72)

    print(f"Case: {review['case_id']}")

    print(f"Run: {review['run_number']}")

    print()

    print("CHECKS")

    print("-" * 72)

    for check in review["checks"]:
        print(f"{check['criterion']}: {check['status'].upper()}")

        print(f"  {check['notes']}")

    print()

    print("SUMMARY")

    print("-" * 72)

    print(f"Concerns found: {review['concerns_found']}")

    print(f"Unclear checks: {review['unclear_checks']}")

    print(f"Review passed: {review['review_passed']}")

    print()

    print(f"Artifact: {OUTPUT_PATH}")


def main() -> None:
    suite = load_suite()

    run = find_latest_quality_run(suite=suite)

    payload = build_review(run=run)

    save_review(payload=payload)

    print_review(payload=payload)


if __name__ == "__main__":
    main()
