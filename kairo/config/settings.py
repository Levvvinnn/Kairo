from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    github_token: str | None = None
    database_path: str = "kairo.db"
    model: str = "gemini-2.5-flash"
    # Canvas LMS configuration
    canvas_base_url: str | None = None
    canvas_api_token: str | None = None
    canvas_client_id: str | None = None
    canvas_client_secret: str | None = None

    # Use pydantic v2-style model config for settings. Allow extra env vars
    # (so unrelated keys in .env don't raise) and load from the repository
    # `.env` file.
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()