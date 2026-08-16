import argparse
import sys
from pathlib import Path

REPOSITORY_DIRECTORY = Path(__file__).resolve().parents[1]
BACKEND_DIRECTORY = REPOSITORY_DIRECTORY / "backend"
ENV_FILE = BACKEND_DIRECTORY / ".env"

sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.config import Settings  # noqa: E402
from app.providers.azure_openai import AzureOpenAIService  # noqa: E402

DEFAULT_PROMPT = "What is the capital of France? Answer with the city name only."


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a text prompt through the local Azure OpenAI provider adapter."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=DEFAULT_PROMPT,
        help="Text to send. Defaults to a small connection-check prompt.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=64,
        help="Maximum generated tokens; must be at least 16 (default: 64).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    settings = Settings.from_env_file(ENV_FILE)
    with AzureOpenAIService(
        endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
    ) as service:
        answer = service.generate_text(
            args.prompt,
            max_output_tokens=args.max_output_tokens,
        )

    print(f"answer: {answer}")


if __name__ == "__main__":
    main()
