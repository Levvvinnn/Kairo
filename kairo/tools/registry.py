from typing import Dict

from kairo.tools.base import Tool


class ToolRegistry:

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())

    def get_tool_descriptions(self):
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self.tools.values()
        ]