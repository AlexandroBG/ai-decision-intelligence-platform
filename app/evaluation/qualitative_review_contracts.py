from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

ReviewStatus = Literal[
    "pass",
    "concern",
    "unclear",
]


class QualitativeCheck(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    criterion: str = Field(
        min_length=1,
    )

    status: ReviewStatus

    notes: str = Field(
        min_length=1,
    )


class QualitativeReview(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    case_id: str = Field(
        min_length=1,
    )

    run_number: int = Field(
        ge=1,
    )

    checks: list[QualitativeCheck] = Field(
        min_length=1,
    )

    concerns_found: int = Field(
        ge=0,
    )

    unclear_checks: int = Field(
        ge=0,
    )

    review_passed: bool
