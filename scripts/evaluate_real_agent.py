import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.agent.runtime import build_agent_loop
from app.llm.client import GeminiClient
from app.llm.config import load_llm_config
from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMResponseError,
)

QUESTION = (
    "Compare revenue from 2025-07-01 to 2025-07-31 "
    "with 2025-08-01 to 2025-08-31. "
    "What is affecting revenue performance, "
    "and what should I investigate first?"
)

DEFAULT_RUNS = 3
DEFAULT_MAX_STEPS = 6

OUTPUT_DIRECTORY = PROJECT_ROOT / "artifacts" / "phase09"

OUTPUT_PATH = OUTPUT_DIRECTORY / "real_agent_eval.json"


def find_dataset_directory() -> Path:
    preferred_directories = [
        PROJECT_ROOT / "data" / "synthetic" / "revenue_decline_v1",
        PROJECT_ROOT / "data" / "revenue_decline_v1",
        PROJECT_ROOT / "data" / "processed",
        PROJECT_ROOT / "data" / "raw",
        PROJECT_ROOT / "data",
    ]

    for directory in preferred_directories:
        if _contains_dataset(directory=directory):
            return directory

    discovered = sorted(PROJECT_ROOT.rglob("orders.csv"))

    for orders_path in discovered:
        directory = orders_path.parent

        if _contains_dataset(directory=directory):
            return directory

    raise FileNotFoundError(
        "Could not locate a directory containing "
        "orders.csv, customers.csv, and products.csv."
    )


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

    _parse_date_column(
        dataframe=orders,
        column="order_date",
    )

    _parse_date_column(
        dataframe=customers,
        column="signup_date",
    )

    return (
        orders,
        customers,
        products,
    )


def _parse_date_column(
    dataframe: pd.DataFrame,
    column: str,
) -> None:
    if column not in dataframe.columns:
        return

    dataframe[column] = pd.to_datetime(
        dataframe[column],
        errors="raise",
    )


def serialize_observations(
    result: Any,
) -> list[
    dict[
        str,
        Any,
    ]
]:
    observations = []

    for step, observation in enumerate(
        result.history.observations,
        start=1,
    ):
        observations.append(
            {
                "step": step,
                "tool_name": (observation.call.tool_name),
                "arguments": (observation.call.arguments),
                "success": (observation.result.success),
                "output": (observation.result.output),
                "error": (observation.result.error),
            }
        )

    return observations


def serialize_claims(
    result: Any,
) -> list[
    dict[
        str,
        Any,
    ]
]:
    return [claim.model_dump(mode="json") for claim in result.grounded_claims]


def build_execution_error(
    run_number: int,
    exc: (LLMInputError | LLMProviderError | LLMResponseError),
) -> dict[
    str,
    Any,
]:
    print("RUN ERROR:")

    print(f"{type(exc).__name__}: {exc}")

    return {
        "run": run_number,
        "execution_error": True,
        "error_type": (type(exc).__name__),
        "error": str(exc),
    }


def evaluate_run(
    run_number: int,
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    client: GeminiClient,
    max_steps: int,
) -> dict[
    str,
    Any,
]:
    print()

    print("=" * 72)

    print(f"REAL GEMINI AGENT RUN {run_number}")

    print("=" * 72)

    loop = build_agent_loop(
        llm_client=client,
        orders=orders,
        customers=customers,
        products=products,
        max_steps=max_steps,
    )

    try:
        result = loop.run(question=QUESTION)
    except (
        LLMInputError,
        LLMProviderError,
        LLMResponseError,
    ) as exc:
        return build_execution_error(
            run_number=run_number,
            exc=exc,
        )

    observations = serialize_observations(result=result)

    claims = serialize_claims(result=result)

    tool_sequence = [observation["tool_name"] for observation in observations]

    print(f"Status: {result.status}")

    print(f"Steps used: {result.steps_used}")

    print(f"Tool calls: {result.tool_calls}")

    print(f"Tool failures: {result.tool_failures}")

    print(f"Evidence steps: {result.evidence_steps}")

    print(f"Tool sequence: {tool_sequence}")

    if result.termination_reason is not None:
        print("Termination reason:")

        print(result.termination_reason)

    print()

    print("FINAL ANSWER")

    print("-" * 72)

    print(result.answer)

    print()

    print("GROUNDED CLAIMS")

    print("-" * 72)

    if not claims:
        print("None.")

    for index, claim in enumerate(
        claims,
        start=1,
    ):
        print(f"{index}. [{claim['claim_type']}] {claim['statement']}")

        print(f"   evidence_ids={claim['evidence_ids']}")

    print()

    print("TOOL OBSERVATIONS")

    print("-" * 72)

    if not observations:
        print("None.")

    for observation in observations:
        print(f"Step {observation['step']}: {observation['tool_name']}")

        print(f"  success={observation['success']}")

        print(
            "  arguments="
            f"{
                json.dumps(
                    observation['arguments'],
                    default=str,
                )
            }"
        )

    return {
        "run": run_number,
        "execution_error": False,
        "status": (result.status),
        "termination_reason": (result.termination_reason),
        "steps_used": (result.steps_used),
        "tool_calls": (result.tool_calls),
        "tool_failures": (result.tool_failures),
        "tool_sequence": (tool_sequence),
        "answer": (result.answer),
        "evidence_steps": (result.evidence_steps),
        "grounded_claims": (claims),
        "observations": (observations),
    }


def build_summary(
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> dict[
    str,
    Any,
]:
    successful_executions = [
        run
        for run in runs
        if not run.get(
            "execution_error",
            False,
        )
    ]

    completed_runs = [
        run for run in successful_executions if run.get("status") == "completed"
    ]

    guardrail_runs = [
        run for run in successful_executions if run.get("status") != "completed"
    ]

    total_tool_calls = sum(
        run.get(
            "tool_calls",
            0,
        )
        for run in successful_executions
    )

    total_tool_failures = sum(
        run.get(
            "tool_failures",
            0,
        )
        for run in successful_executions
    )

    return {
        "requested_runs": len(runs),
        "execution_errors": sum(
            1
            for run in runs
            if run.get(
                "execution_error",
                False,
            )
        ),
        "completed_runs": len(completed_runs),
        "guardrail_terminated_runs": len(guardrail_runs),
        "total_tool_calls": (total_tool_calls),
        "total_tool_failures": (total_tool_failures),
        "statuses": [
            run.get(
                "status",
                "execution_error",
            )
            for run in runs
        ],
        "tool_sequences": [
            run.get(
                "tool_sequence",
                [],
            )
            for run in successful_executions
        ],
    }


def save_evaluation(
    dataset_directory: Path,
    model_name: str,
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "evaluation": ("phase09_real_gemini_agent"),
        "question": (QUESTION),
        "model": (model_name),
        "dataset_directory": str(dataset_directory),
        "summary": build_summary(runs=runs),
        "runs": runs,
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


def print_summary(
    runs: list[
        dict[
            str,
            Any,
        ]
    ],
) -> None:
    summary = build_summary(runs=runs)

    print()

    print("=" * 72)

    print("EVALUATION SUMMARY")

    print("=" * 72)

    print(f"Requested runs: {summary['requested_runs']}")

    print(f"Completed runs: {summary['completed_runs']}")

    print(f"Guardrail terminations: {summary['guardrail_terminated_runs']}")

    print(f"Execution errors: {summary['execution_errors']}")

    print(f"Total tool calls: {summary['total_tool_calls']}")

    print(f"Total tool failures: {summary['total_tool_failures']}")

    print(f"Statuses: {summary['statuses']}")

    print("Tool sequences:")

    for index, sequence in enumerate(
        summary["tool_sequences"],
        start=1,
    ):
        print(f"  Run {index}: {sequence}")

    print()

    print("Evaluation artifact:")

    print(OUTPUT_PATH)


def main() -> None:
    run_count = int(
        os.getenv(
            "AGENT_EVAL_RUNS",
            str(DEFAULT_RUNS),
        )
    )

    max_steps = int(
        os.getenv(
            "AGENT_EVAL_MAX_STEPS",
            str(DEFAULT_MAX_STEPS),
        )
    )

    if run_count <= 0:
        raise ValueError("AGENT_EVAL_RUNS must be greater than zero.")

    if max_steps <= 0:
        raise ValueError("AGENT_EVAL_MAX_STEPS must be greater than zero.")

    dataset_directory = find_dataset_directory()

    print("Project root:")

    print(PROJECT_ROOT)

    print("Dataset:")

    print(dataset_directory)

    orders, customers, products = load_dataset(directory=dataset_directory)

    print(f"Orders: {len(orders)}")

    print(f"Customers: {len(customers)}")

    print(f"Products: {len(products)}")

    config = load_llm_config()

    print(f"Gemini model: {config.model_name}")

    client = GeminiClient(config=config)

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
        runs.append(
            evaluate_run(
                run_number=run_number,
                orders=orders,
                customers=customers,
                products=products,
                client=client,
                max_steps=max_steps,
            )
        )

    save_evaluation(
        dataset_directory=(dataset_directory),
        model_name=(config.model_name),
        runs=runs,
    )

    print_summary(runs=runs)


if __name__ == "__main__":
    main()
