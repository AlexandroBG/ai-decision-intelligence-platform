import json
import os
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.agent.runtime import build_agent_loop
from app.evaluation.case_registry import (
    EvaluationCaseConfig,
    get_evaluation_case_config,
)
from app.evaluation.ground_truth import evaluate_ground_truth
from app.evaluation.metrics import evaluate_run
from app.evaluation.provider import classify_provider_error
from app.evaluation.semantic import evaluate_semantics
from app.evaluation.summary import build_multi_run_summary
from app.evaluation.tool_selection import evaluate_tool_selection
from app.llm.errors import LLMProviderError
from app.llm.factory import build_llm_client
from app.llm.protocols import LLMClient
from app.llm.provider import (
    LLMProviderName,
    load_llm_provider,
)

DEFAULT_CASE = "revenue_decline_v1"
DEFAULT_RUNS = 1
DEFAULT_MAX_STEPS = 6

OUTPUT_DIRECTORY = PROJECT_ROOT / "artifacts" / "phase15"


def find_dataset_directory() -> Path:
    preferred_directories = [
        PROJECT_ROOT / "data" / "synthetic" / "revenue_decline_v1",
        PROJECT_ROOT / "data" / "revenue_decline_v1",
        PROJECT_ROOT / "data",
    ]

    for directory in preferred_directories:
        if _contains_dataset(directory=directory):
            return directory

    discovered_orders = sorted(PROJECT_ROOT.rglob("orders.csv"))

    for orders_path in discovered_orders:
        directory = orders_path.parent

        if _contains_dataset(directory=directory):
            return directory

    raise FileNotFoundError("Could not locate DecisionAI dataset.")


def _contains_dataset(
    directory: Path,
) -> bool:
    return all(
        (directory / filename).is_file()
        for filename in (
            "orders.csv",
            "customers.csv",
            "products.csv",
        )
    )


def load_dataset(
    directory: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    orders = pd.read_csv(directory / "orders.csv")

    customers = pd.read_csv(directory / "customers.csv")

    products = pd.read_csv(directory / "products.csv")

    if "order_date" in orders.columns:
        orders["order_date"] = pd.to_datetime(
            orders["order_date"],
            errors="raise",
        )

    if "signup_date" in customers.columns:
        customers["signup_date"] = pd.to_datetime(
            customers["signup_date"],
            errors="raise",
        )

    return (
        orders,
        customers,
        products,
    )


def get_configured_model_name(
    provider: LLMProviderName,
) -> str:
    if provider == "gemini":
        return os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

    return os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna",
    )


def evaluate_once(
    run_number: int,
    case_config: EvaluationCaseConfig,
    client: LLMClient,
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    max_steps: int,
) -> dict[str, Any]:
    case = case_config.case

    loop = build_agent_loop(
        llm_client=client,
        orders=orders,
        customers=customers,
        products=products,
        max_steps=max_steps,
    )

    start_time = perf_counter()

    result = loop.run(
        question=case.question,
    )

    duration_ms = (perf_counter() - start_time) * 1000.0

    run_metrics = evaluate_run(
        result=result,
    )

    tool_selection = evaluate_tool_selection(
        case=case,
        result=result,
    )

    ground_truth = evaluate_ground_truth(
        case=case,
        result=result,
    )

    semantic_evaluation = evaluate_semantics(
        answer=result.answer or "",
        require_recommendation=(case_config.require_recommendation),
    )

    overall_passed = (
        run_metrics.completed
        and tool_selection.passed
        and ground_truth.passed
        and semantic_evaluation.passed
    )

    print()
    print("=" * 72)
    print(f"EVALUATION RUN {run_number}")
    print("=" * 72)

    print(f"Case: {case.case_id}")
    print(f"Agent completed: {run_metrics.completed}")
    print(f"Status: {run_metrics.status}")
    print(f"Run latency: {duration_ms:.2f} ms")
    print(f"Tool success rate: {run_metrics.tool_success_rate:.2%}")
    print(f"Duplicate tool rate: {run_metrics.duplicate_tool_call_rate:.2%}")

    print()
    print("TOOL SELECTION")
    print("-" * 72)

    print(f"Used tools: {tool_selection.used_tools}")
    print(f"Missing required tools: {tool_selection.missing_required_tools}")
    print(f"Unexpected tools: {tool_selection.unexpected_tools}")
    print(f"Required tool coverage: {tool_selection.required_tool_coverage:.2%}")
    print(f"Tool selection passed: {tool_selection.passed}")

    print()
    print("GROUND TRUTH")
    print("-" * 72)

    for metric in ground_truth.results:
        print(f"{metric.tool_name}.{metric.field_path}")
        print(f"  expected = {metric.expected_value}")
        print(f"  actual   = {metric.actual_value}")
        print(f"  error    = {metric.absolute_error}")
        print(f"  passed   = {metric.passed}")

        if metric.error:
            print(f"  problem  = {metric.error}")

    print()

    print(f"Ground-truth score: {ground_truth.score:.2%}")
    print(f"Ground-truth passed: {ground_truth.passed}")

    print()
    print("SEMANTIC SAFETY")
    print("-" * 72)

    print(f"Recommendation required: {case_config.require_recommendation}")
    print(f"Causal overclaim: {semantic_evaluation.causal_overclaim}")
    print(f"Unsupported certainty: {semantic_evaluation.unsupported_certainty}")
    print(f"Overlap summing risk: {semantic_evaluation.overlap_summing_risk}")
    print(f"Recommendation present: {semantic_evaluation.recommendation_present}")
    print(f"Semantic safety score: {semantic_evaluation.safety_score:.2%}")
    print(f"Semantic safety passed: {semantic_evaluation.passed}")

    print()
    print("FINAL ANSWER")
    print("-" * 72)

    print(result.answer)

    print()
    print("OVERALL RESULT")
    print("-" * 72)

    print("PASS" if overall_passed else "FAIL")

    return {
        "run": run_number,
        "run_type": "quality_result",
        "case_id": case.case_id,
        "overall_passed": overall_passed,
        "duration_ms": duration_ms,
        "agent_metrics": run_metrics.model_dump(mode="json"),
        "tool_selection": tool_selection.model_dump(mode="json"),
        "ground_truth": ground_truth.model_dump(mode="json"),
        "semantic_evaluation": (semantic_evaluation.model_dump(mode="json")),
        "answer": result.answer,
        "grounded_claims": [
            claim.model_dump(mode="json") for claim in result.grounded_claims
        ],
    }


def build_provider_error_result(
    run_number: int,
    case_id: str,
    exc: LLMProviderError,
) -> dict[str, Any]:
    error_kind = classify_provider_error(
        exc=exc,
    )

    print()
    print("=" * 72)
    print(f"EVALUATION RUN {run_number}")
    print("=" * 72)

    print("PROVIDER ERROR")
    print("-" * 72)

    print(f"Case: {case_id}")
    print(f"Type: {error_kind}")
    print("This run is NOT counted as an AI quality failure.")

    return {
        "run": run_number,
        "run_type": "provider_error",
        "case_id": case_id,
        "overall_passed": None,
        "provider_error": {
            "kind": error_kind,
            "error_type": type(exc).__name__,
            "message": str(exc),
        },
    }


def get_output_path(
    case_id: str,
    provider: LLMProviderName,
) -> Path:
    return OUTPUT_DIRECTORY / provider / f"{case_id}_eval.json"


def save_results(
    case_config: EvaluationCaseConfig,
    requested_runs: int,
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
    provider: LLMProviderName,
    model_name: str,
) -> Path:
    summary = build_multi_run_summary(
        requested_runs=requested_runs,
        runs=runs,
    )

    output_path = get_output_path(
        case_id=case_config.case.case_id,
        provider=provider,
    )

    payload = {
        "provider": provider,
        "model": model_name,
        "case": case_config.case.model_dump(mode="json"),
        "require_recommendation": (case_config.require_recommendation),
        "summary": summary.model_dump(mode="json"),
        "runs": runs,
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    return output_path


def format_rate(
    value: float | None,
) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2%}"


def format_average(
    value: float | None,
) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2f}"


def print_summary(
    case_id: str,
    requested_runs: int,
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
    output_path: Path,
    provider: LLMProviderName,
    model_name: str,
) -> None:
    summary = build_multi_run_summary(
        requested_runs=requested_runs,
        runs=runs,
    )

    print()
    print("=" * 72)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 72)

    print(f"Provider: {provider}")
    print(f"Model: {model_name}")
    print(f"Case: {case_id}")
    print(f"Requested runs: {summary.requested_runs}")
    print(f"Attempted runs: {summary.attempted_runs}")
    print(f"Quality-evaluated runs: {summary.evaluated_runs}")
    print(f"Provider errors: {summary.provider_errors}")

    print()
    print("QUALITY")
    print("-" * 72)

    print(f"Quality passes: {summary.passed_runs}/{summary.evaluated_runs}")
    print(f"Overall quality pass rate: {format_rate(summary.quality_pass_rate)}")
    print(f"Agent completion rate: {format_rate(summary.completion_rate)}")
    print(f"Tool-selection pass rate: {format_rate(summary.tool_selection_pass_rate)}")
    print(f"Ground-truth pass rate: {format_rate(summary.ground_truth_pass_rate)}")
    print(f"Semantic-safety pass rate: {format_rate(summary.semantic_pass_rate)}")

    print()
    print("EFFICIENCY")
    print("-" * 72)

    print(f"Average steps: {format_average(summary.average_steps)}")
    print(f"Average tool calls: {format_average(summary.average_tool_calls)}")
    print(f"Average tool failures: {format_average(summary.average_tool_failures)}")
    print(f"Average latency: {format_average(summary.average_latency_ms)} ms")
    print(f"Tool success rate: {format_rate(summary.tool_success_rate)}")
    print(f"Duplicate tool-call rate: {format_rate(summary.duplicate_tool_call_rate)}")

    print()
    print("AVAILABILITY")
    print("-" * 72)

    print(
        "Requested-run evaluation rate: "
        f"{format_rate(summary.requested_run_evaluation_rate)}"
    )
    print(f"Provider errors: {summary.provider_errors}")

    print()
    print(f"Artifact: {output_path}")


def main() -> None:
    case_id = os.getenv(
        "EVAL_CASE",
        DEFAULT_CASE,
    )

    run_count = int(
        os.getenv(
            "EVAL_RUNS",
            str(DEFAULT_RUNS),
        )
    )

    max_steps = int(
        os.getenv(
            "EVAL_MAX_STEPS",
            str(DEFAULT_MAX_STEPS),
        )
    )

    if run_count <= 0:
        raise ValueError("EVAL_RUNS must be greater than zero.")

    if max_steps <= 0:
        raise ValueError("EVAL_MAX_STEPS must be greater than zero.")

    case_config = get_evaluation_case_config(
        case_id=case_id,
    )

    dataset_directory = find_dataset_directory()

    orders, customers, products = load_dataset(
        directory=dataset_directory,
    )

    provider = load_llm_provider()

    model_name = get_configured_model_name(
        provider=provider,
    )

    client = build_llm_client()

    print("DecisionAI Evaluation")
    print(f"Provider: {provider}")
    print(f"Model: {model_name}")
    print(f"Case: {case_config.case.case_id}")
    print(f"Requested runs: {run_count}")

    runs: list[
        dict[
            str,
            Any,
        ]
    ] = []

    for run_number in range(
        1,
        run_count + 1,
    ):
        try:
            run = evaluate_once(
                run_number=run_number,
                case_config=case_config,
                client=client,
                orders=orders,
                customers=customers,
                products=products,
                max_steps=max_steps,
            )

        except LLMProviderError as exc:
            run = build_provider_error_result(
                run_number=run_number,
                case_id=(case_config.case.case_id),
                exc=exc,
            )

            runs.append(run)

            print()
            print("Stopping remaining runs after provider failure.")

            break

        runs.append(run)

    output_path = save_results(
        case_config=case_config,
        requested_runs=run_count,
        runs=runs,
        provider=provider,
        model_name=model_name,
    )

    print_summary(
        case_id=case_config.case.case_id,
        requested_runs=run_count,
        runs=runs,
        output_path=output_path,
        provider=provider,
        model_name=model_name,
    )


if __name__ == "__main__":
    main()
