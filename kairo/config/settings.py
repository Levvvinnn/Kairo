"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for Kairo."""

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    github_token: str | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    database_path: str = Field(default="kairo.db", validation_alias="KAIRO_DATABASE_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )
