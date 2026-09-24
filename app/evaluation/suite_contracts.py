from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EvaluationSuiteSummary(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    requested_cases: int = Field(
        ge=1,
    )

    attempted_cases: int = Field(
        ge=0,
    )

    evaluated_cases: int = Field(
        ge=0,
    )

    provider_errors: int = Field(
        ge=0,
    )

    passed_cases: int = Field(
        ge=0,
    )

    case_pass_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    evaluation_coverage: float = Field(
        ge=0.0,
        le=1.0,
    )

    suite_completed: bool

    suite_passed: bool | None
