from app.tools.base import BaseTool
from app.tools.contracts import ToolDefinition


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        name = tool.definition.name

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = tool

    def get(
        self,
        name: str,
    ) -> BaseTool:
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Tool name must not be empty.")

        try:
            return self._tools[normalized_name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {normalized_name}") from exc

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def definitions(
        self,
    ) -> list[ToolDefinition]:
        return [tool.definition for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(
        self,
        name: object,
    ) -> bool:
        if not isinstance(
            name,
            str,
        ):
            return False

        return name in self._tools
