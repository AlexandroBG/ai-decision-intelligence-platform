from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        min_length=1,
        max_length=2000,
    )


class DecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal[
        "completed",
        "failed",
    ]

    answer: str | None = None

    steps_used: int = Field(ge=0)

    tool_calls: int = Field(ge=0)

    evidence_steps: list[int] = Field(default_factory=list)


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]

    service: str = Field(min_length=1)

    version: str = Field(min_length=1)


class MetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requests_total: int = Field(ge=0)

    provider_errors_total: int = Field(ge=0)

    agent_completed_total: int = Field(ge=0)

    agent_failed_total: int = Field(ge=0)

    tool_calls_total: int = Field(ge=0)

    llm_calls_total: int = Field(ge=0)
