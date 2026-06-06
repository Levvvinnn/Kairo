from kairo.llm.gemini import GeminiProvider
from kairo.agent.conversation import ConversationManager

from kairo.tools.directory_tool import DirectoryTool
from kairo.tools.project_analyzer import ProjectAnalyzerTool
from kairo.tools.registry import ToolRegistry
from kairo.tools.github_tool import GitHubTool
from kairo.tools.file_tool import FileTool
from kairo.agent.prompts import SYSTEM_PROMPT

import json

from kairo.tools.search_tool import SearchTool
from kairo.tools.tree_tool import FileTreeTool

class AgentController:

    def __init__(self):
        self.provider = GeminiProvider()
        self.conversation = ConversationManager()

        self.registry = ToolRegistry()

        self.registry.register(
            DirectoryTool()
        )
        self.registry.register(
            GitHubTool()
        )
        self.registry.register(
            FileTool()
        )
        self.registry.register(
            SearchTool()
        )
        self.registry.register(
            FileTreeTool()
        )
        self.registry.register(
            ProjectAnalyzerTool()
        )

    def chat(self, user_input: str):

        tool_choice = self.select_tool(user_input)

        print("DEBUG:", tool_choice)

        try:

            tool_call = json.loads(tool_choice)

            tool_name = tool_call["tool"]
            arguments = tool_call["arguments"]

            tool = self.registry.get_tool(tool_name)

            result = tool.execute(**arguments)

            response = self.provider.chat([
                {
                    "role": "system",
                    "content": (
                        "You are Kairo. "
                        "Summarize tool results clearly."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User asked: {user_input}\n\n"
                        f"Tool result:\n{result}"
                    )
                }
            ])

            return response

        except Exception:
            pass

        return self.provider.chat([
            {
                "role": "user",
                "content": user_input
            }
        ])
        
    def select_tool(self, user_input):

        tools = self.registry.get_tool_descriptions()

        prompt = SYSTEM_PROMPT

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        return self.provider.chat(messages)