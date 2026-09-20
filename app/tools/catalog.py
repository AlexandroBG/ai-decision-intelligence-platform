from typing import Any

from app.tools.registry import ToolRegistry


def build_tool_catalog(
    registry: ToolRegistry,
) -> list[dict[str, Any]]:
    return [
        {
            "name": definition.name,
            "description": definition.description,
            "input_schema": definition.input_schema,
        }
        for definition in registry.definitions()
    ]
