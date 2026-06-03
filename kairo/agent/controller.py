from kairo.llm.gemini import GeminiProvider
from kairo.agent.conversation import ConversationManager

from kairo.tools.registry import ToolRegistry
from kairo.tools.github_tool import GitHubTool
from kairo.agent.prompts import SYSTEM_PROMPT


class AgentController:

    def __init__(self):
        self.provider = GeminiProvider()
        self.conversation = ConversationManager()

        self.registry = ToolRegistry()

        # Register tools here
        self.registry.register(
            GitHubTool()
        )

    def chat(self, user_input: str):

        tool_choice = self.select_tool(user_input)

        if tool_choice.startswith("TOOL:"):

            tool_name = tool_choice.replace(
                "TOOL:",
                ""
            ).strip()

            tool = self.registry.get_tool(tool_name)

            result = tool.execute()

            response = self.provider.chat([
                {
                    "role": "system",
                    "content": "You are Kairo. Summarize tool results clearly."
                },
                {
                    "role": "user",
                    "content": (
                        f"User asked: {user_input}\n\n"
                        f"Tool result: {result}"
                    )
                }
            ])

            return response

        return self.provider.chat([
            {
                "role": "user",
                "content": user_input
            }
        ])
    
    def select_tool(self, user_input):

        tools = self.registry.get_tool_descriptions()

        prompt = SYSTEM_PROMPT.format(
            tools=tools
        )

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