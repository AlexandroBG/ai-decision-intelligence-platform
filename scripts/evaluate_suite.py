import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.evaluation.case_registry import (
    get_evaluation_case_config,
    list_evaluation_cases,
)
from app.evaluation.gates import (
    evaluate_suite_gate,
)
from app.evaluation.suite import (
    build_evaluation_suite_summary,
)
from app.evaluation.summary import (
    build_multi_run_summary,
)
from app.llm.client import GeminiClient
from app.llm.config import load_llm_config
from app.llm.errors import (
    LLMProviderError,
)
from scripts.evaluate_revenue_decline_case import (
    build_provider_error_result,
    evaluate_once,
    find_dataset_directory,
    load_dataset,
)

DEFAULT_RUNS_PER_CASE = 1
DEFAULT_MAX_STEPS = 6

OUTPUT_DIRECTORY = PROJECT_ROOT / "artifacts" / "phase10"

OUTPUT_PATH = OUTPUT_DIRECTORY / "evaluation_suite.json"


def evaluate_case(
    *,
    case_id: str,
    runs_per_case: int,
    client: GeminiClient,
    orders: Any,
    customers: Any,
    products: Any,
    max_steps: int,
) -> dict[str, Any]:
    case_config = get_evaluation_case_config(case_id=case_id)

    runs: list[
        dict[
            str,
            Any,
        ]
    ] = []

    provider_error = False

    print()
    print("#" * 72)

    print(f"CASE: {case_id}")

    print("#" * 72)

    for run_number in range(
        1,
        runs_per_case + 1,
    ):
        try:
            run = evaluate_once(
                run_number=(run_number),
                case_config=(case_config),
                client=client,
                orders=orders,
                customers=customers,
                products=products,
                max_steps=max_steps,
            )

        except LLMProviderError as exc:
            run = build_provider_error_result(
                run_number=(run_number),
                case_id=(case_id),
                exc=exc,
            )

            runs.append(run)

            provider_error = True

            break

        runs.append(run)

    summary = build_multi_run_summary(
        requested_runs=(runs_per_case),
        runs=runs,
    )

    if provider_error or (summary.evaluated_runs != runs_per_case):
        result_type = "provider_error"

        passed = None

    else:
        result_type = "quality_result"

        passed = summary.quality_pass_rate == 1.0

    return {
        "case_id": (case_id),
        "result_type": (result_type),
        "passed": (passed),
        "summary": (summary.model_dump(mode="json")),
        "runs": runs,
    }


def build_suite_report(
    *,
    case_results: list[
        dict[
            str,
            Any,
        ]
    ],
    requested_cases: int,
    runs_per_case: int,
) -> dict[str, Any]:
    suite_summary = build_evaluation_suite_summary(
        requested_cases=(requested_cases),
        case_results=(case_results),
    )

    gate = evaluate_suite_gate(summary=(suite_summary))

    return {
        "suite_summary": (suite_summary.model_dump(mode="json")),
        "gate": (gate.model_dump(mode="json")),
        "runs_per_case": (runs_per_case),
        "cases": (case_results),
    }


def save_suite_results(
    *,
    case_results: list[
        dict[
            str,
            Any,
        ]
    ],
    requested_cases: int,
    runs_per_case: int,
) -> None:
    payload = build_suite_report(
        case_results=(case_results),
        requested_cases=(requested_cases),
        runs_per_case=(runs_per_case),
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


def format_rate(
    value: float | None,
) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2%}"


def format_suite_result(
    passed: bool | None,
) -> str:
    if passed is True:
        return "PASS"

    if passed is False:
        return "FAIL"

    return "INCOMPLETE"


def print_suite_summary(
    *,
    case_results: list[
        dict[
            str,
            Any,
        ]
    ],
    requested_cases: int,
) -> None:
    summary = build_evaluation_suite_summary(
        requested_cases=(requested_cases),
        case_results=(case_results),
    )

    gate = evaluate_suite_gate(summary=summary)

    print()
    print("=" * 72)

    print("DECISIONAI EVALUATION SUITE")

    print("=" * 72)

    for result in case_results:
        print(f"{result['case_id']}: {format_suite_result(result['passed'])}")

    print()
    print("SUITE SUMMARY")

    print("-" * 72)

    print(f"Requested cases: {summary.requested_cases}")

    print(f"Attempted cases: {summary.attempted_cases}")

    print(f"Evaluated cases: {summary.evaluated_cases}")

    print(f"Provider errors: {summary.provider_errors}")

    print(f"Passed cases: {summary.passed_cases}")

    print(f"Case pass rate: {format_rate(summary.case_pass_rate)}")

    print(f"Evaluation coverage: {format_rate(summary.evaluation_coverage)}")

    print(f"Suite completed: {summary.suite_completed}")

    print(f"OVERALL SUITE: {format_suite_result(summary.suite_passed)}")

    print()
    print("EVALUATION GATE")

    print("-" * 72)

    print(f"Suite completed check: {gate.suite_completed}")

    print(f"Coverage check: {gate.coverage_passed}")

    print(f"Case pass-rate check: {gate.case_pass_rate_passed}")

    print(f"Provider availability check: {gate.provider_availability_passed}")

    print(f"Failed checks: {gate.failed_checks}")

    print(f"RELEASE GATE: {'PASS' if gate.gate_passed else 'FAIL'}")

    print()
    print(f"Artifact: {OUTPUT_PATH}")


def main() -> None:
    runs_per_case = int(
        os.getenv(
            "EVAL_RUNS_PER_CASE",
            str(DEFAULT_RUNS_PER_CASE),
        )
    )

    max_steps = int(
        os.getenv(
            "EVAL_MAX_STEPS",
            str(DEFAULT_MAX_STEPS),
        )
    )

    if runs_per_case <= 0:
        raise ValueError("EVAL_RUNS_PER_CASE must be greater than zero.")

    if max_steps <= 0:
        raise ValueError("EVAL_MAX_STEPS must be greater than zero.")

    case_ids = list_evaluation_cases()

    dataset_directory = find_dataset_directory()

    orders, customers, products = load_dataset(directory=(dataset_directory))

    config = load_llm_config()

    client = GeminiClient(config=config)

    print("DecisionAI Evaluation Suite")

    print(f"Model: {config.model_name}")

    print(f"Cases: {len(case_ids)}")

    print(f"Runs per case: {runs_per_case}")

    case_results: list[
        dict[
            str,
            Any,
        ]
    ] = []

    for case_id in case_ids:
        result = evaluate_case(
            case_id=case_id,
            runs_per_case=(runs_per_case),
            client=client,
            orders=orders,
            customers=customers,
            products=products,
            max_steps=max_steps,
        )

        case_results.append(result)

        if result["result_type"] == "provider_error":
            print()
            print("Stopping evaluation suite after provider failure.")

            break

    save_suite_results(
        case_results=(case_results),
        requested_cases=(len(case_ids)),
        runs_per_case=(runs_per_case),
    )

    print_suite_summary(
        case_results=(case_results),
        requested_cases=(len(case_ids)),
    )


if __name__ == "__main__":
    main()
