import pytest

from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.errors import ToolExecutionError
from app.tools.executor import (
    INVALID_TOOL_NAME,
    ToolExecutor,
)
from app.tools.registry import ToolRegistry


class ExampleTool(BaseTool):
    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name="example_tool",
            description="Example tool.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "arguments": call.arguments,
            },
        )


class FailingTool(BaseTool):
    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name="failing_tool",
            description="Failing tool.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        raise ToolExecutionError("Expected tool failure.")


class BuggyTool(BaseTool):
    @property
    def definition(
        self,
    ) -> ToolDefinition:
        return ToolDefinition(
            name="buggy_tool",
            description="Buggy tool.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        raise RuntimeError("Unexpected programming bug.")


def build_executor() -> ToolExecutor:
    registry = ToolRegistry()

    registry.register(ExampleTool())

    registry.register(FailingTool())

    registry.register(BuggyTool())

    return ToolExecutor(registry=registry)


def test_executor_executes_registered_tool() -> None:
    executor = build_executor()

    result = executor.execute(
        call=ToolCall(
            tool_name="example_tool",
            arguments={
                "value": 42,
            },
        )
    )

    assert result.success is True

    assert result.output == {
        "arguments": {
            "value": 42,
        }
    }


def test_executor_returns_failure_for_unknown_tool() -> None:
    executor = build_executor()

    result = executor.execute(
        call=ToolCall(
            tool_name="missing_tool",
        )
    )

    assert result.success is False

    assert result.error == "Unknown tool: missing_tool"


def test_executor_preserves_tool_failure() -> None:
    executor = build_executor()

    result = executor.execute(
        call=ToolCall(
            tool_name="failing_tool",
        )
    )

    assert result.success is False

    assert result.error == "Expected tool failure."


def test_executor_does_not_modify_arguments() -> None:
    executor = build_executor()

    arguments = {
        "value": 42,
        "nested": {
            "enabled": True,
        },
    }

    result = executor.execute(
        call=ToolCall(
            tool_name="example_tool",
            arguments=arguments,
        )
    )

    assert result.success is True

    assert result.output == {
        "arguments": arguments,
    }


def test_executor_accepts_valid_external_payload() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "tool_name": "example_tool",
            "arguments": {
                "value": 42,
            },
        }
    )

    assert result.success is True

    assert result.tool_name == ("example_tool")

    assert result.output == {
        "arguments": {
            "value": 42,
        }
    }


def test_executor_normalizes_external_tool_name() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "tool_name": "  example_tool  ",
            "arguments": {},
        }
    )

    assert result.success is True

    assert result.tool_name == ("example_tool")


def test_executor_rejects_payload_without_tool_name() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "arguments": {},
        }
    )

    assert result.success is False

    assert result.tool_name == INVALID_TOOL_NAME

    assert result.error == "Invalid tool call payload."


def test_executor_rejects_empty_tool_name() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "tool_name": "   ",
            "arguments": {},
        }
    )

    assert result.success is False

    assert result.tool_name == INVALID_TOOL_NAME

    assert result.error == "Invalid tool call payload."


def test_executor_rejects_non_string_tool_name() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "tool_name": 123,
            "arguments": {},
        }
    )

    assert result.success is False

    assert result.tool_name == INVALID_TOOL_NAME


def test_executor_rejects_invalid_arguments_type() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "tool_name": "example_tool",
            "arguments": [
                "not",
                "a",
                "dictionary",
            ],
        }
    )

    assert result.success is False

    assert result.tool_name == "example_tool"

    assert result.error == "Invalid tool call payload."


def test_executor_rejects_non_mapping_payload() -> None:
    executor = build_executor()

    result = executor.execute_payload("not-a-tool-call")

    assert result.success is False

    assert result.tool_name == INVALID_TOOL_NAME

    assert result.error == "Invalid tool call payload."


def test_executor_external_unknown_tool_returns_failure() -> None:
    executor = build_executor()

    result = executor.execute_payload(
        {
            "tool_name": "missing_tool",
            "arguments": {},
        }
    )

    assert result.success is False

    assert result.tool_name == "missing_tool"

    assert result.error == "Unknown tool: missing_tool"


def test_executor_does_not_hide_unexpected_tool_errors() -> None:
    executor = build_executor()

    with pytest.raises(
        RuntimeError,
        match="Unexpected programming bug.",
    ):
        executor.execute_payload(
            {
                "tool_name": "buggy_tool",
                "arguments": {},
            }
        )
