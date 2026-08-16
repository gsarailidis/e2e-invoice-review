from pathlib import Path
from typing import Self

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration loaded once at the application boundary."""

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    azure_document_intelligence_endpoint: str
    azure_document_intelligence_key: str
    azure_openai_endpoint: str
    azure_openai_api_key: str

    @classmethod
    def from_env_file(cls, env_file: Path) -> Self:
        return cls(_env_file=env_file)
