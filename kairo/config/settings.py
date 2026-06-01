from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    github_token: str | None = None
    model: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"

settings = Settings()