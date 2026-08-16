import json
import sys
from decimal import Decimal
from pathlib import Path

REPOSITORY_DIRECTORY = Path(__file__).resolve().parents[1]
BACKEND_DIRECTORY = REPOSITORY_DIRECTORY / "backend"
ENV_FILE = BACKEND_DIRECTORY / ".env"
MANIFEST_PATH = REPOSITORY_DIRECTORY / "samples" / "manifest.json"
INVOICE_PATH = REPOSITORY_DIRECTORY / "samples" / "generated" / "01-en-happy-classic.pdf"
RECEIPT_PATH = REPOSITORY_DIRECTORY / "samples" / "generated" / "13-nl-fuel-receipt.png"

sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.config import Settings  # noqa: E402
from app.providers.azure_document_intelligence import (  # noqa: E402
    DocumentIntelligenceService,
)
from app.schemas.common import ExtractedField  # noqa: E402
from app.schemas.invoice import Invoice  # noqa: E402
from app.schemas.receipt import Receipt  # noqa: E402

ExpectedValue = str | None
CASE_INSENSITIVE_FIELDS = {"customer_name", "vendor_name"}


def _expected_for(filename: str) -> dict[str, ExpectedValue]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise ValueError("Sample manifest must contain a list")

    for entry in manifest:
        if not isinstance(entry, dict) or entry.get("filename") != filename:
            continue
        expected = entry.get("expected")
        if not isinstance(expected, dict):
            break
        if not all(
            isinstance(key, str) and (isinstance(value, str) or value is None)
            for key, value in expected.items()
        ):
            raise ValueError(f"Invalid expected values for {filename}")
        return expected

    raise ValueError(f"No expected values found for {filename}")


def _value[Value](field: ExtractedField[Value] | None) -> Value | None:
    return None if field is None else field.value


def _money(field: ExtractedField[Decimal] | None) -> str | None:
    value = _value(field)
    return None if value is None else format(value, ".2f")


def _text(field: ExtractedField[str] | None) -> str | None:
    return _value(field)


def _invoice_projection(invoice: Invoice) -> dict[str, ExpectedValue]:
    return {
        "currency": _text(invoice.currency),
        "customer_name": _text(invoice.customer_name),
        "customer_vat_id": _text(invoice.customer_vat_id),
        "document_type": invoice.document_type,
        "due_date": None if invoice.due_date is None else invoice.due_date.value.isoformat(),
        "invoice_date": (
            None if invoice.invoice_date is None else invoice.invoice_date.value.isoformat()
        ),
        "invoice_number": _text(invoice.invoice_number),
        "invoice_total": _money(invoice.invoice_total),
        "purchase_order": _text(invoice.purchase_order),
        "subtotal": _money(invoice.subtotal),
        "total_tax": _money(invoice.total_tax),
        "vendor_name": _text(invoice.vendor_name),
        "vendor_vat_id": _text(invoice.vendor_vat_id),
    }


def _receipt_projection(receipt: Receipt) -> dict[str, ExpectedValue]:
    return {
        "currency": _text(receipt.currency),
        "customer_name": None,
        "customer_vat_id": None,
        "document_type": receipt.document_type,
        "due_date": None,
        "invoice_date": (
            None
            if receipt.transaction_date is None
            else receipt.transaction_date.value.isoformat()
        ),
        "invoice_number": None,
        "invoice_total": _money(receipt.total),
        "purchase_order": None,
        "subtotal": _money(receipt.subtotal),
        "total_tax": _money(receipt.total_tax),
        "vendor_name": _text(receipt.merchant_name),
        "vendor_vat_id": None,
    }


def _comparison(
    expected: dict[str, ExpectedValue], actual: dict[str, ExpectedValue]
) -> dict[str, object]:
    def values_match(key: str) -> bool:
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
        if not values_match(key)
    }
    return {"matches": not differences, "differences": differences}


def main() -> int:
    settings = Settings.from_env_file(ENV_FILE)
    with DocumentIntelligenceService(
        endpoint=settings.azure_document_intelligence_endpoint,
        api_key=settings.azure_document_intelligence_key,
    ) as service:
        invoice = service.analyze_invoice(INVOICE_PATH.read_bytes())
        receipt = service.analyze_receipt(RECEIPT_PATH.read_bytes())

    invoice_comparison = _comparison(
        _expected_for(INVOICE_PATH.name), _invoice_projection(invoice)
    )
    receipt_comparison = _comparison(
        _expected_for(RECEIPT_PATH.name), _receipt_projection(receipt)
    )
    line_item_checks = {
        "invoice_expected": 4,
        "invoice_actual": len(invoice.items),
        "invoice_matches": len(invoice.items) == 4,
        "receipt_expected": 1,
        "receipt_actual": len(receipt.items),
        "receipt_matches": len(receipt.items) == 1,
    }

    print(
        json.dumps(
            {
                "invoice": {
                    "model": invoice.model_dump(mode="json"),
                    "manifest_comparison": invoice_comparison,
                },
                "receipt": {
                    "model": receipt.model_dump(mode="json"),
                    "manifest_comparison": receipt_comparison,
                },
                "line_item_checks": line_item_checks,
            },
            indent=2,
        )
    )

    all_checks_pass = (
        invoice_comparison["matches"] is True
        and receipt_comparison["matches"] is True
        and line_item_checks["invoice_matches"] is True
        and line_item_checks["receipt_matches"] is True
    )
    return 0 if all_checks_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
