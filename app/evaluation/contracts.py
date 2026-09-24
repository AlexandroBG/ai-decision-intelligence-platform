from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class RunEvaluationMetrics(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    status: str = Field(
        min_length=1,
    )

    completed: bool

    steps_used: int = Field(
        ge=1,
    )

    tool_calls: int = Field(
        ge=0,
    )

    successful_tool_calls: int = Field(
        ge=0,
    )

    tool_failures: int = Field(
        ge=0,
    )

    duplicate_tool_calls: int = Field(
        ge=0,
    )

    tool_success_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    duplicate_tool_call_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    invalid_final_evidence: bool

    invalid_final_grounding: bool


class EvaluationSummary(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    total_runs: int = Field(
        ge=1,
    )

    completed_runs: int = Field(
        ge=0,
    )

    completion_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    total_steps: int = Field(
        ge=0,
    )

    average_steps: float = Field(
        ge=0.0,
    )

    total_tool_calls: int = Field(
        ge=0,
    )

    average_tool_calls: float = Field(
        ge=0.0,
    )

    successful_tool_calls: int = Field(
        ge=0,
    )

    total_tool_failures: int = Field(
        ge=0,
    )

    average_tool_failures: float = Field(
        ge=0.0,
    )

    tool_success_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    duplicate_tool_calls: int = Field(
        ge=0,
    )

    duplicate_tool_call_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    invalid_final_evidence_runs: int = Field(
        ge=0,
    )

    invalid_final_evidence_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    invalid_final_grounding_runs: int = Field(
        ge=0,
    )

    invalid_final_grounding_rate: float = Field(
        ge=0.0,
        le=1.0,
    )


class ExpectedNumericMetric(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    field_path: str = Field(
        min_length=1,
    )

    expected_value: float

    absolute_tolerance: float = Field(
        default=0.01,
        ge=0.0,
    )

    @field_validator("field_path")
    @classmethod
    def normalize_field_path(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Field path must not be empty.")

        return normalized


class ExpectedToolOutput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    tool_name: str = Field(
        min_length=1,
    )

    metrics: list[ExpectedNumericMetric] = Field(
        min_length=1,
    )

    @field_validator("tool_name")
    @classmethod
    def normalize_tool_name(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Tool name must not be empty.")

        return normalized

    @model_validator(mode="after")
    def validate_unique_metric_paths(
        self,
    ) -> "ExpectedToolOutput":
        paths = [metric.field_path for metric in self.metrics]

        if len(paths) != len(set(paths)):
            raise ValueError("Expected metric field paths must be unique.")

        return self


class EvaluationCase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    case_id: str = Field(
        min_length=1,
    )

    question: str = Field(
        min_length=1,
    )

    required_tools: list[str] = Field(
        default_factory=list,
    )

    optional_tools: list[str] = Field(
        default_factory=list,
    )

    expected_outputs: list[ExpectedToolOutput] = Field(
        default_factory=list,
    )

    @field_validator(
        "case_id",
        "question",
    )
    @classmethod
    def normalize_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Text values must not be empty.")

        return normalized

    @field_validator(
        "required_tools",
        "optional_tools",
    )
    @classmethod
    def normalize_tools(
        cls,
        value: list[str],
    ) -> list[str]:
        normalized_tools: list[str] = []
        seen: set[str] = set()

        for tool_name in value:
            normalized = tool_name.strip()

            if not normalized:
                raise ValueError("Tool names must not be empty.")

            if normalized in seen:
                raise ValueError("Tool lists must not contain duplicates.")

            seen.add(normalized)

            normalized_tools.append(normalized)

        return normalized_tools

    @model_validator(mode="after")
    def validate_case(
        self,
    ) -> "EvaluationCase":
        self._validate_tool_groups()
        self._validate_expected_outputs()

        return self

    def _validate_tool_groups(
        self,
    ) -> None:
        overlap = set(self.required_tools) & set(self.optional_tools)

        if overlap:
            raise ValueError("A tool cannot be both required and optional.")

    def _validate_expected_outputs(
        self,
    ) -> None:
        expected_tool_names = [expected.tool_name for expected in self.expected_outputs]

        if len(expected_tool_names) != len(set(expected_tool_names)):
            raise ValueError("Expected outputs must not contain duplicate tools.")

        allowed_tools = set(self.required_tools) | set(self.optional_tools)

        unknown_expected_tools = set(expected_tool_names) - allowed_tools

        if unknown_expected_tools:
            raise ValueError(
                "Expected outputs must reference required or optional tools."
            )


class ToolSelectionEvaluation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    used_tools: list[str] = Field(
        default_factory=list,
    )

    required_tools: list[str] = Field(
        default_factory=list,
    )

    optional_tools: list[str] = Field(
        default_factory=list,
    )

    missing_required_tools: list[str] = Field(
        default_factory=list,
    )

    unexpected_tools: list[str] = Field(
        default_factory=list,
    )

    required_tool_coverage: float = Field(
        ge=0.0,
        le=1.0,
    )

    passed: bool


class GroundTruthMetricResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    tool_name: str = Field(
        min_length=1,
    )

    field_path: str = Field(
        min_length=1,
    )

    expected_value: float

    actual_value: float | None = None

    absolute_error: float | None = Field(
        default=None,
        ge=0.0,
    )

    tolerance: float = Field(
        ge=0.0,
    )

    passed: bool

    error: str | None = None


class GroundTruthEvaluation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    total_checks: int = Field(
        ge=0,
    )

    passed_checks: int = Field(
        ge=0,
    )

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    passed: bool

    results: list[GroundTruthMetricResult] = Field(
        default_factory=list,
    )
