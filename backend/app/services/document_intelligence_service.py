from pathlib import Path
from types import TracebackType
from typing import Self

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from pydantic_settings import BaseSettings, SettingsConfigDict


class _DocumentIntelligenceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    azure_document_intelligence_endpoint: str
    azure_document_intelligence_key: str


class DocumentIntelligenceService:
    MODEL_ID = "prebuilt-invoice"

    def __init__(self, endpoint: str, api_key: str) -> None:
        self._client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )

    @classmethod
    def from_env(cls, env_file: Path) -> Self:
        settings = _DocumentIntelligenceSettings(_env_file=env_file)
        return cls(
            endpoint=settings.azure_document_intelligence_endpoint,
            api_key=settings.azure_document_intelligence_key,
        )

    def analyze_invoice(self, invoice_path: Path) -> dict[str, object]:
        if not invoice_path.is_file():
            raise FileNotFoundError(f"Invoice file not found: {invoice_path}")

        with invoice_path.open("rb") as invoice:
            poller = self._client.begin_analyze_document(self.MODEL_ID, body=invoice)
            result = poller.result()

        return result.as_dict()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
