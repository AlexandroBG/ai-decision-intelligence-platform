from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EvidenceRevenue(BaseModel):
    evidence_id: str
    source: Literal["analytics"]
    evidence_type: Literal["revenue_summary"]

    baseline_revenue: float
    comparison_revenue: float
    absolute_change: float
    percentage_change: float


class EvidenceDriver(BaseModel):
    evidence_id: str
    source: Literal["analytics"]
    evidence_type: Literal["driver"]

    dimension: str
    value: str
    absolute_change: float
    percentage_change: float
    contribution_to_total_change: float


class EvidenceAnomaly(BaseModel):
    evidence_id: str
    source: Literal["ml"]
    evidence_type: Literal["anomaly"]

    date: str
    dimension: str
    value: str
    daily_revenue: float
    anomaly_score: float


type EvidenceItem = EvidenceRevenue | EvidenceDriver | EvidenceAnomaly


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


class GroundedClaim(BaseModel):
    claim_type: Literal[
        "fact",
        "inference",
        "unknown",
    ]

    statement: str

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    @field_validator("statement")
    @classmethod
    def validate_statement(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Grounded claim statement must not be empty.")

        return normalized

    @field_validator("evidence_ids")
    @classmethod
    def validate_evidence_ids(
        cls,
        values: list[str],
    ) -> list[str]:
        normalized = [value.strip() for value in values if value.strip()]

        return list(dict.fromkeys(normalized))


class LLMInterpretation(BaseModel):
    summary: str = Field(
        min_length=1,
    )

    recommended_investigations: list[str] = Field(
        default_factory=list,
    )

    grounded_claims: list[GroundedClaim] = Field(
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
        "recommended_investigations",
    )
    @classmethod
    def validate_list_items(
        cls,
        values: list[str],
    ) -> list[str]:
        normalized_values = [value.strip() for value in values if value.strip()]

        return list(dict.fromkeys(normalized_values))

    @property
    def facts(self) -> list[str]:
        return [
            claim.statement
            for claim in self.grounded_claims
            if claim.claim_type == "fact"
        ]

    @property
    def inferences(self) -> list[str]:
        return [
            claim.statement
            for claim in self.grounded_claims
            if claim.claim_type == "inference"
        ]

    @property
    def unknowns(self) -> list[str]:
        return [
            claim.statement
            for claim in self.grounded_claims
            if claim.claim_type == "unknown"
        ]


class ResolvedGroundedClaim(BaseModel):
    claim_type: Literal[
        "fact",
        "inference",
        "unknown",
    ]

    statement: str

    evidence: list[EvidenceItem] = Field(
        default_factory=list,
    )


class GroundingMetadata(BaseModel):
    expected_claims: int
    grounded_claims: int
    coverage_ratio: float


class ContextSelectionMetadata(BaseModel):
    analytics_driver_budget: int
    analytics_drivers_available: int
    analytics_drivers_selected: int
    analytics_drivers_omitted: int
    analytics_driver_retention_ratio: float
    analytics_driver_budget_utilization: float
    analytics_driver_context_pressure: bool

    ml_anomaly_budget: int
    ml_anomalies_available: int
    ml_anomalies_selected: int
    ml_anomalies_omitted: int
    ml_anomaly_retention_ratio: float
    ml_anomaly_budget_utilization: float
    ml_anomaly_context_pressure: bool


class GroundedInterpretationResult(BaseModel):
    interpretation: LLMInterpretation
    grounding: GroundingMetadata
    context_selection: ContextSelectionMetadata

    resolved_claims: list[ResolvedGroundedClaim] = Field(
        default_factory=list,
    )
