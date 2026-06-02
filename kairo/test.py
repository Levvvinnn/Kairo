from kairo.llm.gemini import GeminiProvider

provider = GeminiProvider()

response = provider.chat([
    {
        "role": "user",
        "content": "Say hello"
    }
])

print(response)