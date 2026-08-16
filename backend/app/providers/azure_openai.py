from types import TracebackType
from typing import Self

from openai import OpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.azure import AzureProvider

AZURE_OPENAI_MODEL_ID = "gpt-5.6-terra"


class AzureOpenAIResponseError(RuntimeError):
    """Raised when Azure OpenAI returns no text for a text-generation request."""


class AzureOpenAIService:
    MODEL_ID = AZURE_OPENAI_MODEL_ID

    def __init__(self, endpoint: str, api_key: str) -> None:
        self._client = OpenAI(
            base_url=f"{endpoint.rstrip('/')}/",
            api_key=api_key,
        )

    def generate_text(self, prompt: str, *, max_output_tokens: int = 512) -> str:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty")
        if max_output_tokens < 16:
            raise ValueError("max_output_tokens must be at least 16")

        response = self._client.responses.create(
            model=self.MODEL_ID,
            input=prompt,
            max_output_tokens=max_output_tokens,
            store=False,
        )
        output_text = response.output_text.strip()
        if not output_text:
            raise AzureOpenAIResponseError("Azure OpenAI returned no text output")
        return output_text

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


def create_azure_openai_responses_model(
    *, endpoint: str, api_key: str
) -> OpenAIResponsesModel:
    """Build the Pydantic AI model while keeping Azure configuration in this adapter."""
    provider = AzureProvider(
        azure_endpoint=f"{endpoint.rstrip('/')}/",
        api_key=api_key,
    )
    return OpenAIResponsesModel(
        AZURE_OPENAI_MODEL_ID,
        provider=provider,
        settings=OpenAIResponsesModelSettings(openai_store=False),
    )


async def close_azure_openai_responses_model(model: OpenAIResponsesModel) -> None:
    """Close the provider-owned asynchronous client during application shutdown."""
    await model.client.close()
