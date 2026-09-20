from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.llm.contracts import GroundedClaim
from app.tools.contracts import (
    ToolCall,
    ToolResult,
)


def validate_evidence_steps(
    value: list[int],
) -> list[int]:
    normalized: list[int] = []
    seen: set[int] = set()

    for step in value:
        if step <= 0:
            raise ValueError("Evidence steps must be positive integers.")

        if step in seen:
            raise ValueError("Evidence steps must not contain duplicates.")

        seen.add(step)
        normalized.append(step)

    return normalized


class AgentToolAction(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    action_type: Literal["tool_call"]
    call: ToolCall


class AgentFinalAction(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    action_type: Literal["final"]
    answer: str

    evidence_steps: list[int] = Field(
        default_factory=list,
    )

    grounded_claims: list[GroundedClaim] = Field(
        default_factory=list,
    )

    @field_validator("answer")
    @classmethod
    def validate_answer(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Final agent answer must not be empty.")

        return normalized

    @field_validator("evidence_steps")
    @classmethod
    def validate_action_evidence_steps(
        cls,
        value: list[int],
    ) -> list[int]:
        return validate_evidence_steps(value=value)


AgentAction = Annotated[
    AgentToolAction | AgentFinalAction,
    Field(discriminator="action_type"),
]


class AgentDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    action: AgentAction

    @model_validator(mode="before")
    @classmethod
    def normalize_provider_action_type(
        cls,
        value: Any,
    ) -> Any:
        if not isinstance(
            value,
            dict,
        ):
            return value

        action = value.get("action")

        if not isinstance(
            action,
            dict,
        ):
            return value

        if action.get("action_type") != "call":
            return value

        normalized_value = value.copy()

        normalized_action = action.copy()

        normalized_action["action_type"] = "tool_call"

        normalized_value["action"] = normalized_action

        return normalized_value


class AgentObservation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    call: ToolCall
    result: ToolResult

    @model_validator(mode="after")
    def validate_tool_identity(
        self,
    ) -> "AgentObservation":
        if self.call.tool_name != self.result.tool_name:
            raise ValueError(
                "Observation call and result must reference the same tool."
            )

        return self


class AgentHistory(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    observations: list[AgentObservation] = Field(
        default_factory=list,
    )


class AgentRunResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    answer: str | None = None

    evidence_steps: list[int] = Field(
        default_factory=list,
    )

    grounded_claims: list[GroundedClaim] = Field(
        default_factory=list,
    )

    status: Literal[
        "completed",
        "max_steps_reached",
        "duplicate_tool_call",
        "tool_failure_limit_reached",
        "invalid_final_evidence",
        "invalid_final_grounding",
    ]

    termination_reason: str | None = None

    steps_used: int = Field(
        ge=1,
    )

    tool_calls: int = Field(
        ge=0,
    )

    tool_failures: int = Field(
        ge=0,
    )

    history: AgentHistory

    @field_validator("answer")
    @classmethod
    def validate_answer(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError("Agent run answer must not be empty.")

        return normalized

    @field_validator("evidence_steps")
    @classmethod
    def validate_result_evidence_steps(
        cls,
        value: list[int],
    ) -> list[int]:
        return validate_evidence_steps(value=value)

    @field_validator("termination_reason")
    @classmethod
    def validate_termination_reason(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError("Termination reason must not be empty.")

        return normalized

    @model_validator(mode="after")
    def validate_run_state(
        self,
    ) -> "AgentRunResult":
        observation_count = len(self.history.observations)

        self._validate_execution_metrics(observation_count=(observation_count))

        self._validate_status_contract(observation_count=(observation_count))

        return self

    def _validate_execution_metrics(
        self,
        observation_count: int,
    ) -> None:
        if self.tool_calls != observation_count:
            raise ValueError(
                "tool_calls must match the number of history observations."
            )

        if self.tool_failures > self.tool_calls:
            raise ValueError("tool_failures cannot exceed tool_calls.")

        observed_failures = sum(
            1
            for observation in self.history.observations
            if not observation.result.success
        )

        if self.tool_failures != observed_failures:
            raise ValueError("tool_failures must match failed history observations.")

    def _validate_status_contract(
        self,
        observation_count: int,
    ) -> None:
        if self.status == "completed":
            self._validate_completed_run(observation_count=(observation_count))

            return

        self._validate_terminated_run()

    def _validate_completed_run(
        self,
        observation_count: int,
    ) -> None:
        if self.answer is None:
            raise ValueError("Completed runs must include an answer.")

        if self.termination_reason is not None:
            raise ValueError("Completed runs must not include a termination reason.")

        if observation_count == 0:
            if self.evidence_steps:
                raise ValueError(
                    "Completed runs without tool "
                    "observations must not include "
                    "evidence steps."
                )

            if self.grounded_claims:
                raise ValueError(
                    "Completed runs without tool "
                    "observations must not include "
                    "grounded claims."
                )

            return

        if any(step > observation_count for step in self.evidence_steps):
            raise ValueError(
                "Evidence steps must reference existing history observations."
            )

        if not self.evidence_steps:
            raise ValueError(
                "Completed runs with tool observations must include evidence steps."
            )

        if not self.grounded_claims:
            raise ValueError(
                "Completed runs with tool observations must include grounded claims."
            )

    def _validate_terminated_run(
        self,
    ) -> None:
        if self.answer is not None:
            raise ValueError(
                "Guardrail-terminated runs must not include a final answer."
            )

        if self.termination_reason is None:
            raise ValueError(
                "Guardrail-terminated runs must include a termination reason."
            )

        if self.evidence_steps:
            raise ValueError(
                "Guardrail-terminated runs must not include final evidence steps."
            )

        if self.grounded_claims:
            raise ValueError(
                "Guardrail-terminated runs must not include grounded claims."
            )
