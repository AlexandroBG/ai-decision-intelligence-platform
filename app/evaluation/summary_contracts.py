from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class MultiRunEvaluationSummary(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    requested_runs: int = Field(
        ge=1,
    )

    attempted_runs: int = Field(
        ge=0,
    )

    evaluated_runs: int = Field(
        ge=0,
    )

    provider_errors: int = Field(
        ge=0,
    )

    passed_runs: int = Field(
        ge=0,
    )

    quality_pass_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    completion_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    tool_selection_pass_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    ground_truth_pass_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    semantic_pass_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    tool_success_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    duplicate_tool_call_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    average_steps: float | None = Field(
        default=None,
        ge=0.0,
    )

    average_tool_calls: float | None = Field(
        default=None,
        ge=0.0,
    )

    average_tool_failures: float | None = Field(
        default=None,
        ge=0.0,
    )

    average_latency_ms: float | None = Field(
        default=None,
        ge=0.0,
    )

    requested_run_evaluation_rate: float = Field(
        ge=0.0,
        le=1.0,
    )
