import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import Settings  # noqa: E402
from app.pipeline import (  # noqa: E402
    DocumentClassificationStep,
    DocumentInput,
    DocumentMediaType,
)
from app.providers.azure_openai import create_azure_openai_responses_model  # noqa: E402

ENV_FILE = BACKEND / ".env"
DEFAULT_DOCUMENT = ROOT / "samples" / "generated" / "01-en-happy-classic.pdf"
MEDIA_TYPES: dict[str, DocumentMediaType] = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".pdf": "application/pdf",
    ".png": "image/png",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify a PDF, PNG, or JPEG with Azure OpenAI structured output."
    )
    parser.add_argument(
        "document",
        nargs="?",
        type=Path,
        default=DEFAULT_DOCUMENT,
        help="Document to classify (defaults to the fictional English invoice).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    document = args.document.resolve()
    media_type = MEDIA_TYPES.get(document.suffix.lower())
    if media_type is None:
        supported = ", ".join(sorted(MEDIA_TYPES))
        raise ValueError(f"Unsupported document extension; expected one of: {supported}")

    settings = Settings.from_env_file(ENV_FILE)
    model = create_azure_openai_responses_model(
        endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
    )
    step = DocumentClassificationStep(model)
    result = step.run(DocumentInput(content=document.read_bytes(), media_type=media_type))

    print(f"document: {document}")
    print(result.classification.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
