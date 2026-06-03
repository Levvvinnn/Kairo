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

    def chat(self, user_input):
        self.conversation.add_user(user_input)

        response = self.provider.chat(
            self.conversation.get_messages()
        )

        self.conversation.add_assistant(response)
        tool_choice = self.select_tool(user_input)

        if tool_choice.startswith("TOOL:"):

            tool_name = tool_choice.replace(
                "TOOL:",
                ""
            ).strip()

            tool = self.registry.get_tool(
                tool_name
            )

            result = tool.execute()

            return str(result)
        return response
    
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