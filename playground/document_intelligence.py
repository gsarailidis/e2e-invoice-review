import json
import sys
from pathlib import Path

REPOSITORY_DIRECTORY = Path(__file__).resolve().parents[1]
BACKEND_DIRECTORY = REPOSITORY_DIRECTORY / "backend"
ENV_FILE = BACKEND_DIRECTORY / ".env"
INVOICE_PATH = REPOSITORY_DIRECTORY / "samples" / "generated" / "01-en-happy-classic.pdf"

sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.services.document_intelligence_service import (  # noqa: E402
    DocumentIntelligenceService,
)


def main() -> None:
    with DocumentIntelligenceService.from_env(ENV_FILE) as service:
        invoice_data = service.analyze_invoice(INVOICE_PATH)

    print(json.dumps(invoice_data, indent=2, default=str))


if __name__ == "__main__":
    main()
