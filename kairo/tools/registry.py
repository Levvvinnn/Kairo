"""Tool registry for discovering and executing Kairo tools."""

from kairo.tools.base import Tool
from kairo.tools.github_tool import GitHubTool


class ToolRegistry:
    """Maintains a collection of available agent tools."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool by its unique name."""
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Return a registered tool by name."""
        try:
            return self._tools[name]
        except KeyError as error:
            raise KeyError(f"Tool not found: {name}") from error

    def list_tools(self) -> list[Tool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def execute(self, name: str, **kwargs: object) -> str:
        """Execute a registered tool by name."""
        return self.get(name).execute(**kwargs)


def create_default_registry() -> ToolRegistry:
    """Create the default tool registry with built-in tools."""
    registry = ToolRegistry()
    registry.register(GitHubTool())
    return registry
