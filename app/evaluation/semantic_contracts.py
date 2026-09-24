from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class SemanticEvaluation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    causal_overclaim: bool

    causal_language_risk: bool

    unsupported_certainty: bool

    overlap_summing_risk: bool

    recommendation_present: bool

    failed_checks: list[str] = Field(
        default_factory=list,
    )

    passed_checks: list[str] = Field(
        default_factory=list,
    )

    safety_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    passed: bool
