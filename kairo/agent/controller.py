from kairo.llm.gemini import GeminiProvider
from kairo.agent.conversation import ConversationManager

class AgentController:

    def __init__(self):
        self.provider = GeminiProvider()
        self.conversation = ConversationManager()

    def chat(self, user_input):

        self.conversation.add_user(user_input)

        response = self.provider.chat(
            self.conversation.get_messages()
        )

        self.conversation.add_assistant(response)

        return response