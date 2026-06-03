from kairo.llm.gemini import GeminiProvider
from kairo.agent.conversation import ConversationManager

from kairo.tools.registry import ToolRegistry
from kairo.tools.github_tool import GitHubTool


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

        return response