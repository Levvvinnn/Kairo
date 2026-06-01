from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    github_token: str | None = None
    database_path: str = "kairo.db"
    model: str = "gemini-2.5-flash"

    # Use pydantic v2-style model config for settings. Allow extra env vars
    # (so unrelated keys in .env don't raise) and load from the repository
    # `.env` file.
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()