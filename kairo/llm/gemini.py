from openai import OpenAI

from kairo.config.settings import settings

class GeminiProvider:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    def chat(self, messages):
        response = self.client.chat.completions.create(
            model=settings.model,
            messages=messages,
        )

        return response.choices[0].message.content