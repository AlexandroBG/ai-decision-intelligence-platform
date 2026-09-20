from typing import Any

from pydantic import ValidationError

from app.tools.contracts import (
    ToolCall,
    ToolResult,
)
from app.tools.registry import ToolRegistry

INVALID_TOOL_NAME = "invalid_tool_call"


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        try:
            tool = self._registry.get(call.tool_name)
        except KeyError:
            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error=(f"Unknown tool: {call.tool_name}"),
            )

        return tool.execute(call=call)

    def execute_payload(
        self,
        payload: Any,
    ) -> ToolResult:
        try:
            call = ToolCall.model_validate(payload)
        except ValidationError:
            return ToolResult(
                tool_name=self._extract_tool_name(payload),
                success=False,
                error="Invalid tool call payload.",
            )

        return self.execute(call=call)

    @staticmethod
    def _extract_tool_name(
        payload: Any,
    ) -> str:
        if not isinstance(
            payload,
            dict,
        ):
            return INVALID_TOOL_NAME

        tool_name = payload.get("tool_name")

        if not isinstance(
            tool_name,
            str,
        ):
            return INVALID_TOOL_NAME

        normalized_name = tool_name.strip()

        if not normalized_name:
            return INVALID_TOOL_NAME

        return normalized_name
