import json
import sys
from decimal import Decimal
from pathlib import Path

REPOSITORY_DIRECTORY = Path(__file__).resolve().parents[1]
BACKEND_DIRECTORY = REPOSITORY_DIRECTORY / "backend"
ENV_FILE = BACKEND_DIRECTORY / ".env"
MANIFEST_PATH = REPOSITORY_DIRECTORY / "samples" / "manifest.json"
SAMPLES_DIRECTORY = REPOSITORY_DIRECTORY / "samples" / "generated"

sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.accounting import GENERAL_LEDGER_ACCOUNTS  # noqa: E402
from app.config import Settings  # noqa: E402
from app.pipeline import (  # noqa: E402
    DocumentClassificationStep,
    DocumentExtractionStep,
    DocumentInput,
    DocumentMediaType,
    DocumentValidationStep,
    GeneralLedgerClassificationStep,
    Pipeline,
    ProcessedDocument,
)
from app.providers.azure_document_intelligence import (  # noqa: E402
    DocumentIntelligenceService,
)
from app.providers.azure_openai import (  # noqa: E402
    create_azure_openai_responses_model,
)
from app.schemas.common import ExtractedField  # noqa: E402
from app.schemas.invoice import Invoice  # noqa: E402

ExpectedValue = str | None
SELECTED_CASES = {
    "01-en-happy-classic.pdf": 4,
    "06-de-invalid-vendor-vat.pdf": None,
    "08-en-total-mismatch.pdf": None,
    "13-nl-fuel-receipt.png": 1,
}
MEDIA_TYPES: dict[str, DocumentMediaType] = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".pdf": "application/pdf",
    ".png": "image/png",
}
CASE_INSENSITIVE_FIELDS = {"customer_name", "vendor_name"}
GENERAL_LEDGER_CODES = {account.code for account in GENERAL_LEDGER_ACCOUNTS}


def _manifest_entries() -> dict[str, dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise ValueError("Sample manifest must contain a list")
    return {
        entry["filename"]: entry
        for entry in manifest
        if isinstance(entry, dict) and isinstance(entry.get("filename"), str)
    }


def _value[Value](field: ExtractedField[Value] | None) -> Value | None:
    return None if field is None else field.value


def _money(field: ExtractedField[Decimal] | None) -> str | None:
    value = _value(field)
    return None if value is None else format(value, ".2f")


def _text(field: ExtractedField[str] | None) -> str | None:
    return _value(field)


def _projection(result: ProcessedDocument) -> dict[str, ExpectedValue]:
    document = result.document
    if isinstance(document, Invoice):
        return {
            "currency": _text(document.currency),
            "customer_name": _text(document.customer_name),
            "customer_vat_id": _text(document.customer_vat_id),
            "document_type": document.document_type,
            "due_date": None if document.due_date is None else document.due_date.value.isoformat(),
            "invoice_date": (
                None if document.invoice_date is None else document.invoice_date.value.isoformat()
            ),
            "invoice_number": _text(document.invoice_number),
            "invoice_total": _money(document.invoice_total),
            "purchase_order": _text(document.purchase_order),
            "subtotal": _money(document.subtotal),
            "total_tax": _money(document.total_tax),
            "vendor_name": _text(document.vendor_name),
            "vendor_vat_id": _text(document.vendor_vat_id),
        }

    return {
        "currency": _text(document.currency),
        "customer_name": None,
        "customer_vat_id": None,
        "document_type": document.document_type,
        "due_date": None,
        "invoice_date": (
            None
            if document.transaction_date is None
            else document.transaction_date.value.isoformat()
        ),
        "invoice_number": None,
        "invoice_total": _money(document.total),
        "purchase_order": None,
        "subtotal": _money(document.subtotal),
        "total_tax": _money(document.total_tax),
        "vendor_name": _text(document.merchant_name),
        "vendor_vat_id": None,
    }


def _field_comparison(
    expected: dict[str, ExpectedValue], actual: dict[str, ExpectedValue]
) -> dict[str, object]:
    def matches(key: str) -> bool:
        expected_value = expected.get(key)
        actual_value = actual.get(key)
        if (
            key in CASE_INSENSITIVE_FIELDS
            and isinstance(expected_value, str)
            and isinstance(actual_value, str)
        ):
            return expected_value.casefold() == actual_value.casefold()
        return expected_value == actual_value

    differences = {
        key: {"expected": expected.get(key), "actual": actual.get(key)}
        for key in sorted(expected.keys() | actual.keys())
        if not matches(key)
    }
    return {"matches": not differences, "differences": differences}


def _evaluate(
    pipeline: Pipeline[DocumentInput, ProcessedDocument],
    filename: str,
    manifest_entry: dict[str, object],
    expected_item_count: int | None,
) -> tuple[dict[str, object], bool]:
    document_path = SAMPLES_DIRECTORY / filename
    media_type = MEDIA_TYPES[document_path.suffix.lower()]
    result = pipeline.run(
        DocumentInput(content=document_path.read_bytes(), media_type=media_type)
    )

    expected_fields = manifest_entry.get("expected")
    expected_issue_codes = manifest_entry.get("expected_issue_codes")
    if not isinstance(expected_fields, dict) or not isinstance(expected_issue_codes, list):
        raise ValueError(f"Invalid manifest entry for {filename}")

    field_comparison = _field_comparison(expected_fields, _projection(result))
    actual_issue_codes = [issue.code for issue in result.validation.issues]
    issues_match = actual_issue_codes == expected_issue_codes
    item_count = len(result.document.items)
    items_match = expected_item_count is None or item_count == expected_item_count
    general_ledger = result.metadata.general_ledger
    ledger_matches = general_ledger.account.code in GENERAL_LEDGER_CODES
    matches = (
        field_comparison["matches"] is True
        and issues_match
        and items_match
        and ledger_matches
    )

    return (
        {
            "filename": filename,
            "result": result.model_dump(mode="json"),
            "manifest_fields": field_comparison,
            "issues": {
                "expected": expected_issue_codes,
                "actual": actual_issue_codes,
                "matches": issues_match,
            },
            "line_items": {
                "expected": expected_item_count,
                "actual": item_count,
                "matches": items_match,
            },
            "general_ledger": {
                "account": general_ledger.account.model_dump(),
                "rationale": general_ledger.rationale,
                "source": general_ledger.source,
                "matches_catalog": ledger_matches,
            },
            "matches": matches,
        },
        matches,
    )


def main() -> int:
    settings = Settings.from_env_file(ENV_FILE)
    model = create_azure_openai_responses_model(
        endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
    )
    entries = _manifest_entries()

    with DocumentIntelligenceService(
        endpoint=settings.azure_document_intelligence_endpoint,
        api_key=settings.azure_document_intelligence_key,
    ) as document_intelligence:
        pipeline = (
            Pipeline.start(DocumentClassificationStep(model))
            .then(DocumentExtractionStep(document_intelligence))
            .then(DocumentValidationStep())
            .then(GeneralLedgerClassificationStep(model))
        )
        evaluations = [
            _evaluate(pipeline, filename, entries[filename], item_count)
            for filename, item_count in SELECTED_CASES.items()
        ]

    results = [result for result, _ in evaluations]
    all_checks_pass = all(matches for _, matches in evaluations)
    print(json.dumps({"results": results, "matches": all_checks_pass}, indent=2))
    return 0 if all_checks_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
