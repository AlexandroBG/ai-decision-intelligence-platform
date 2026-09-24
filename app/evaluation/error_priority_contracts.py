from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

PrioritySeverity = Literal[
    "low",
    "medium",
    "high",
]


class ErrorPriority(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    code: str = Field(
        min_length=1,
    )

    category: str = Field(
        min_length=1,
    )

    severity: PrioritySeverity

    occurrences: int = Field(
        ge=1,
    )

    severity_weight: int = Field(
        ge=1,
    )

    priority_score: int = Field(
        ge=1,
    )


class ErrorPriorityReport(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    total_prioritized_errors: int = Field(
        ge=0,
    )

    priorities: list[ErrorPriority] = Field(
        default_factory=list,
    )

    top_priority_code: str | None = None
