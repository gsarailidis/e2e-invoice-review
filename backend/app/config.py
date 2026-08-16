from pathlib import Path
from typing import Self

from pydantic_settings import BaseSettings, SettingsConfigDict

MAX_UPLOAD_BYTES = 4 * 1024 * 1024
FRONTEND_DEVELOPMENT_ORIGIN = "http://localhost:5173"
DOCUMENT_MEDIA_TYPES = frozenset({"application/pdf", "image/png", "image/jpeg"})


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
