from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ErrorCount(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
    )

    count: int = Field(
        ge=1,
    )


class ErrorReport(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    total_runs_analyzed: int = Field(
        ge=0,
    )

    runs_with_errors: int = Field(
        ge=0,
    )

    total_errors: int = Field(
        ge=0,
    )

    high_severity_errors: int = Field(
        ge=0,
    )

    medium_severity_errors: int = Field(
        ge=0,
    )

    low_severity_errors: int = Field(
        ge=0,
    )

    errors_by_category: list[ErrorCount] = Field(
        default_factory=list,
    )

    errors_by_code: list[ErrorCount] = Field(
        default_factory=list,
    )

    top_error_code: str | None = None
