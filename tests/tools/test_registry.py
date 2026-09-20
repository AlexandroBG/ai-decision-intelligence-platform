import pytest

from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.registry import ToolRegistry


class RevenueTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="analyze_revenue",
            description="Analyze revenue performance.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "status": "revenue analyzed",
            },
        )


class AnomalyTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="detect_anomalies",
            description="Detect unusual business behavior.",
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "status": "anomalies detected",
            },
        )


def test_registry_starts_empty() -> None:
    registry = ToolRegistry()

    assert len(registry) == 0

    assert registry.names() == []

    assert registry.definitions() == []


def test_registry_registers_tool() -> None:
    registry = ToolRegistry()

    registry.register(RevenueTool())

    assert len(registry) == 1

    assert "analyze_revenue" in registry


def test_registry_returns_registered_tool() -> None:
    registry = ToolRegistry()

    tool = RevenueTool()

    registry.register(tool)

    result = registry.get("analyze_revenue")

    assert result is tool


def test_registry_strips_lookup_name() -> None:
    registry = ToolRegistry()

    tool = RevenueTool()

    registry.register(tool)

    result = registry.get("  analyze_revenue  ")

    assert result is tool


def test_registry_rejects_empty_lookup_name() -> None:
    registry = ToolRegistry()

    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        registry.get("   ")


def test_registry_rejects_unknown_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(
        KeyError,
        match="Unknown tool",
    ):
        registry.get("missing_tool")


def test_registry_rejects_duplicate_tool_name() -> None:
    registry = ToolRegistry()

    registry.register(RevenueTool())

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(RevenueTool())


def test_registry_returns_names() -> None:
    registry = ToolRegistry()

    registry.register(RevenueTool())

    registry.register(AnomalyTool())

    assert registry.names() == [
        "analyze_revenue",
        "detect_anomalies",
    ]


def test_registry_returns_definitions() -> None:
    registry = ToolRegistry()

    registry.register(RevenueTool())

    registry.register(AnomalyTool())

    definitions = registry.definitions()

    assert definitions == [
        ToolDefinition(
            name="analyze_revenue",
            description="Analyze revenue performance.",
        ),
        ToolDefinition(
            name="detect_anomalies",
            description="Detect unusual business behavior.",
        ),
    ]


def test_registry_contains_returns_false_for_non_string() -> None:
    registry = ToolRegistry()

    registry.register(RevenueTool())

    assert 123 not in registry
