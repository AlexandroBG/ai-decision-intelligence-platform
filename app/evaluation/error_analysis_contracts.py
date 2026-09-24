from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

ErrorCategory = Literal[
    "execution",
    "tool_selection",
    "ground_truth",
    "semantic",
    "grounding",
    "provider",
]


ErrorSeverity = Literal[
    "low",
    "medium",
    "high",
]


class EvaluationError(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    category: ErrorCategory

    severity: ErrorSeverity

    code: str = Field(
        min_length=1,
    )

    message: str = Field(
        min_length=1,
    )

    case_id: str = Field(
        min_length=1,
    )

    run_number: int = Field(
        ge=1,
    )


class ErrorAnalysisResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    total_errors: int = Field(
        ge=0,
    )

    errors: list[EvaluationError] = Field(
        default_factory=list,
    )

    has_high_severity_error: bool

    categories: list[ErrorCategory] = Field(
        default_factory=list,
    )
