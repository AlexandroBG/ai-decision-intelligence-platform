from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EvaluationGateResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    suite_completed: bool

    coverage_passed: bool

    case_pass_rate_passed: bool

    provider_availability_passed: bool

    failed_checks: list[str] = Field(
        default_factory=list,
    )

    passed_checks: list[str] = Field(
        default_factory=list,
    )

    gate_passed: bool
