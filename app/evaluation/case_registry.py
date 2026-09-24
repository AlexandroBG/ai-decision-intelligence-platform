from dataclasses import dataclass

from app.evaluation.cases import (
    build_revenue_comparison_only_v1_case,
    build_revenue_decline_v1_case,
)
from app.evaluation.contracts import (
    EvaluationCase,
)


@dataclass(frozen=True)
class EvaluationCaseConfig:
    case: EvaluationCase
    require_recommendation: bool


def get_evaluation_case_config(
    case_id: str,
) -> EvaluationCaseConfig:
    normalized_case_id = case_id.strip()

    if normalized_case_id == "revenue_decline_v1":
        return EvaluationCaseConfig(
            case=build_revenue_decline_v1_case(),
            require_recommendation=True,
        )

    if normalized_case_id == "revenue_comparison_only_v1":
        return EvaluationCaseConfig(
            case=(build_revenue_comparison_only_v1_case()),
            require_recommendation=False,
        )

    available_cases = ", ".join(list_evaluation_cases())

    raise ValueError(
        f"Unknown evaluation case: "
        f"{normalized_case_id!r}. "
        f"Available cases: "
        f"{available_cases}."
    )


def list_evaluation_cases() -> tuple[str, ...]:
    return (
        "revenue_decline_v1",
        "revenue_comparison_only_v1",
    )
