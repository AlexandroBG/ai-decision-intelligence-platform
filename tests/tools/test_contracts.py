import pytest
from pydantic import ValidationError

from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)


def test_tool_definition_accepts_valid_data() -> None:
    definition = ToolDefinition(
        name="analyze_revenue",
        description="Analyze revenue.",
    )

    assert definition.name == "analyze_revenue"

    assert definition.description == "Analyze revenue."

    assert definition.input_schema == {}


def test_tool_definition_accepts_input_schema() -> None:
    schema = {
        "type": "object",
        "properties": {
            "baseline_start": {
                "type": "string",
            }
        },
    }

    definition = ToolDefinition(
        name="analyze_revenue",
        description="Analyze revenue.",
        input_schema=schema,
    )

    assert definition.input_schema == schema


def test_tool_definition_strips_whitespace() -> None:
    definition = ToolDefinition(
        name="  analyze_revenue  ",
        description="  Analyze revenue.  ",
    )

    assert definition.name == "analyze_revenue"

    assert definition.description == "Analyze revenue."


def test_tool_definition_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        ToolDefinition(
            name="   ",
            description="Analyze revenue.",
        )


def test_tool_definition_rejects_empty_description() -> None:
    with pytest.raises(ValidationError):
        ToolDefinition(
            name="analyze_revenue",
            description="   ",
        )


def test_tool_call_accepts_arguments() -> None:
    call = ToolCall(
        tool_name="analyze_revenue",
        arguments={
            "baseline_start": "2025-07-01",
        },
    )

    assert call.tool_name == "analyze_revenue"

    assert call.arguments == {
        "baseline_start": "2025-07-01",
    }


def test_tool_call_uses_empty_arguments_by_default() -> None:
    call = ToolCall(tool_name="analyze_revenue")

    assert call.arguments == {}


def test_tool_call_strips_tool_name() -> None:
    call = ToolCall(tool_name="  analyze_revenue  ")

    assert call.tool_name == "analyze_revenue"


def test_tool_call_rejects_empty_tool_name() -> None:
    with pytest.raises(ValidationError):
        ToolCall(tool_name="   ")


def test_tool_result_accepts_success() -> None:
    result = ToolResult(
        tool_name="analyze_revenue",
        success=True,
        output={
            "revenue": 100.0,
        },
    )

    assert result.success is True

    assert result.output == {
        "revenue": 100.0,
    }

    assert result.error is None


def test_tool_result_accepts_success_without_output() -> None:
    result = ToolResult(
        tool_name="example_action",
        success=True,
    )

    assert result.success is True
    assert result.output is None
    assert result.error is None


def test_tool_result_accepts_failure() -> None:
    result = ToolResult(
        tool_name="analyze_revenue",
        success=False,
        error="Something failed.",
    )

    assert result.success is False

    assert result.error == "Something failed."


def test_tool_result_strips_error() -> None:
    result = ToolResult(
        tool_name="analyze_revenue",
        success=False,
        error="  Something failed.  ",
    )

    assert result.error == "Something failed."


def test_tool_result_rejects_success_with_error() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            tool_name="analyze_revenue",
            success=True,
            error="Something failed.",
        )


def test_tool_result_rejects_failure_without_error() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            tool_name="analyze_revenue",
            success=False,
        )


def test_tool_result_rejects_failure_with_empty_error() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            tool_name="analyze_revenue",
            success=False,
            error="   ",
        )


def test_tool_result_strips_tool_name() -> None:
    result = ToolResult(
        tool_name="  analyze_revenue  ",
        success=True,
    )

    assert result.tool_name == "analyze_revenue"


def test_tool_result_rejects_empty_tool_name() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            tool_name="   ",
            success=True,
        )
