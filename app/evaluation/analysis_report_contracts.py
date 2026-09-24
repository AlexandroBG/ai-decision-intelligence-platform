from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.evaluation.error_priority_contracts import (
    ErrorPriority,
)
from app.evaluation.error_report_contracts import (
    ErrorCount,
)


class EvaluationAnalysisReport(BaseModel):
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

    priorities: list[ErrorPriority] = Field(
        default_factory=list,
    )

    top_priority_code: str | None

    recommended_action: str
