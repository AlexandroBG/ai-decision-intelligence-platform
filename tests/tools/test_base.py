import pytest

from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.errors import ToolExecutionError


class ExampleTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="example_tool",
            description="Example deterministic tool.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "received_arguments": call.arguments,
            },
        )


class FailingTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="failing_tool",
            description="Tool that raises an expected error.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        raise ToolExecutionError("Example execution failure.")


class UnexpectedFailureTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="unexpected_failure_tool",
            description=("Tool that raises an unexpected programming error."),
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        raise RuntimeError("Unexpected programming failure.")


class WrongResultNameTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="expected_tool",
            description=("Tool returning an invalid result name."),
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name="wrong_tool",
            success=True,
            output={},
        )


class IncompleteTool(BaseTool):
    pass


def test_base_tool_allows_valid_implementation() -> None:
    tool = ExampleTool()

    assert isinstance(
        tool,
        BaseTool,
    )


def test_tool_exposes_definition() -> None:
    tool = ExampleTool()

    assert tool.definition == ToolDefinition(
        name="example_tool",
        description="Example deterministic tool.",
    )


def test_tool_executes_valid_call() -> None:
    tool = ExampleTool()

    call = ToolCall(
        tool_name="example_tool",
        arguments={
            "value": 42,
        },
    )

    result = tool.execute(
        call=call,
    )

    assert result.success is True

    assert result.tool_name == "example_tool"

    assert result.output == {
        "received_arguments": {
            "value": 42,
        }
    }


def test_tool_rejects_mismatched_call_name() -> None:
    tool = ExampleTool()

    call = ToolCall(
        tool_name="another_tool",
    )

    result = tool.execute(
        call=call,
    )

    assert result.success is False

    assert result.tool_name == "another_tool"

    assert result.error is not None

    assert "does not match tool definition" in result.error


def test_tool_converts_expected_error_to_failure_result() -> None:
    tool = FailingTool()

    result = tool.execute(
        call=ToolCall(
            tool_name="failing_tool",
        )
    )

    assert result.success is False

    assert result.tool_name == "failing_tool"

    assert result.error == "Example execution failure."


def test_tool_does_not_hide_unexpected_errors() -> None:
    tool = UnexpectedFailureTool()

    with pytest.raises(
        RuntimeError,
        match="Unexpected programming failure",
    ):
        tool.execute(
            call=ToolCall(
                tool_name="unexpected_failure_tool",
            )
        )


def test_tool_rejects_wrong_result_name() -> None:
    tool = WrongResultNameTool()

    result = tool.execute(
        call=ToolCall(
            tool_name="expected_tool",
        )
    )

    assert result.success is False

    assert result.tool_name == "expected_tool"

    assert result.error == "Tool result name does not match tool definition."


def test_incomplete_tool_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        IncompleteTool()
