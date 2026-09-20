from abc import ABC, abstractmethod

from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.errors import ToolExecutionError


class BaseTool(ABC):
    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Return the public definition of the tool."""

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        if call.tool_name != self.definition.name:
            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error=(
                    "Tool call name does not match "
                    "tool definition: "
                    f"{call.tool_name!r} != "
                    f"{self.definition.name!r}."
                ),
            )

        try:
            result = self._run(
                call=call,
            )
        except ToolExecutionError as exc:
            return ToolResult(
                tool_name=self.definition.name,
                success=False,
                error=str(exc),
            )

        if result.tool_name != self.definition.name:
            return ToolResult(
                tool_name=self.definition.name,
                success=False,
                error=("Tool result name does not match tool definition."),
            )

        return result

    @abstractmethod
    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """Run the concrete tool implementation."""
