from typing import Dict

from kairo.tools.base import Tool
from kairo.tools.github_tool import GitHubTool


class ToolRegistry:
    """Registry of tools with several convenience accessors.

    Provide both `get` and `get_tool` names, and an `execute` helper so
    callers using either API still work.
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        if tool.name in self.tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self.tools[tool.name] = tool

    def get_tool(self, name: str):
        try:
            return self.tools[name]
        except KeyError as error:
            raise KeyError(f"Tool not found: {name}") from error

    # backward-compatible alias
    def get(self, name: str):
        return self.get_tool(name)

    def list_tools(self):
        return list(self.tools.keys())

    def get_tool_descriptions(self):
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]

    def execute(self, name: str, **kwargs: object) -> object:
        return self.get_tool(name).execute(**kwargs)


def create_default_registry() -> ToolRegistry:
    """Create a registry pre-populated with built-in tools."""
    registry = ToolRegistry()
    registry.register(GitHubTool())
    return registry