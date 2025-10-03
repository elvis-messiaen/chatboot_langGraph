# app/core/config.py
"""Configuration centrale de l'application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings de l'application chargées depuis .env"""

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str
    AZURE_OPENAI_API_VERSION: str

    # Database
    DATABASE_URL: str

    # Application
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Instance unique (singleton pattern)
settings = Settings()