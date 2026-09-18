from pydantic import BaseModel, Field, field_validator


class EvidenceRevenue(BaseModel):
    baseline_revenue: float
    comparison_revenue: float
    absolute_change: float
    percentage_change: float


class EvidenceDriver(BaseModel):
    dimension: str
    value: str
    absolute_change: float
    percentage_change: float
    contribution_to_total_change: float


class EvidenceAnomaly(BaseModel):
    date: str
    dimension: str
    value: str
    daily_revenue: float
    anomaly_score: float


class EvidenceContext(BaseModel):
    question: str
    revenue: EvidenceRevenue
    analytics_drivers: list[EvidenceDriver] = Field(
        default_factory=list,
    )
    ml_anomalies: list[EvidenceAnomaly] = Field(
        default_factory=list,
    )

    @field_validator("question")
    @classmethod
    def validate_question(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Question must not be empty.")

        return normalized


class LLMInterpretation(BaseModel):
    summary: str = Field(
        min_length=1,
    )

    facts: list[str] = Field(
        default_factory=list,
    )

    inferences: list[str] = Field(
        default_factory=list,
    )

    unknowns: list[str] = Field(
        default_factory=list,
    )

    recommended_investigations: list[str] = Field(
        default_factory=list,
    )

    @field_validator("summary")
    @classmethod
    def validate_summary(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Summary must not be empty.")

        return normalized

    @field_validator(
        "facts",
        "inferences",
        "unknowns",
        "recommended_investigations",
    )
    @classmethod
    def validate_list_items(
        cls,
        values: list[str],
    ) -> list[str]:
        normalized_values = [value.strip() for value in values if value.strip()]

        return list(dict.fromkeys(normalized_values))
