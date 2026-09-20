from typing import Any

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator(
        "name",
        "description",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Tool text fields must not be empty.")

        return normalized


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("tool_name must not be empty.")

        return normalized


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    output: Any | None = None
    error: str | None = None

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("tool_name must not be empty.")

        return normalized

    @field_validator("error")
    @classmethod
    def normalize_error(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            return None

        return normalized

    @model_validator(mode="after")
    def validate_result_state(
        self,
    ) -> "ToolResult":
        if self.success and self.error is not None:
            raise ValueError("Successful tool results must not contain an error.")

        if not self.success and self.error is None:
            raise ValueError("Failed tool results must contain an error.")

        return self
