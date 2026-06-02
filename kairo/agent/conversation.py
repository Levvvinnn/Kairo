class ConversationManager:

    def __init__(self):
        self.messages = []

    def add_user(self, content):
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant(self, content):
        self.messages.append({
            "role": "assistant",
            "content": content
        })

    def get_messages(self):
        return self.messages