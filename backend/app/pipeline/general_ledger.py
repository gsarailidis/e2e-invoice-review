import json
from decimal import Decimal

from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models import Model

from app.accounting import (
    GeneralLedgerSelection,
    GeneralLedgerSuggestion,
    get_general_ledger_account,
)
from app.accounting.catalog import general_ledger_catalog_prompt
from app.pipeline.models import ProcessedDocument, ProcessingMetadata, ValidatedDocument
from app.schemas.common import ExtractedField
from app.schemas.invoice import Invoice


def _value[Value](field: ExtractedField[Value] | None) -> Value | None:
    return None if field is None else field.value


def _money(field: ExtractedField[Decimal] | None) -> str | None:
    value = _value(field)
    return None if value is None else format(value, ".2f")


def _normalized_document_data(value: ValidatedDocument) -> dict[str, object]:
    document = value.document
    if isinstance(document, Invoice):
        return {
            "document_type": document.document_type,
            "vendor_name": _value(document.vendor_name),
            "currency": _value(document.currency),
            "subtotal": _money(document.subtotal),
            "total_tax": _money(document.total_tax),
            "total": _money(document.invoice_total),
            "line_items": [
                {
                    "description": _value(item.description),
                    "amount": _money(item.amount),
                }
                for item in document.items
            ],
        }

    return {
        "document_type": document.document_type,
        "merchant_name": _value(document.merchant_name),
        "receipt_type": _value(document.receipt_type),
        "currency": _value(document.currency),
        "subtotal": _money(document.subtotal),
        "total_tax": _money(document.total_tax),
        "total": _money(document.total),
        "line_items": [
            {
                "description": _value(item.description),
                "amount": _money(item.total_price),
            }
            for item in document.items
        ],
    }


class GeneralLedgerClassificationStep:
    """Suggest one locally allowed GL account from normalized financial data."""

    def __init__(self, model: Model) -> None:
        self._agent = Agent(
            model,
            output_type=NativeOutput(
                GeneralLedgerSelection,
                name="general_ledger_selection",
                strict=True,
            ),
            instructions=(
                "Select the single best general ledger account for the expense represented by "
                "the normalized invoice or receipt. Use only an account from this catalog. "
                "Base the choice primarily on merchant/vendor identity and line-item descriptions. "
                "Return a concise rationale.\n\n"
                f"General ledger catalog:\n{general_ledger_catalog_prompt()}"
            ),
        )

    def run(self, value: ValidatedDocument) -> ProcessedDocument:
        prompt = json.dumps(_normalized_document_data(value), indent=2)
        result = self._agent.run_sync(
            f"Suggest a general ledger account for this normalized document:\n{prompt}"
        )
        selection = result.output
        suggestion = GeneralLedgerSuggestion(
            account=get_general_ledger_account(selection.account_code),
            rationale=selection.rationale,
        )
        return ProcessedDocument(
            classification=value.classification,
            document=value.document,
            validation=value.validation,
            metadata=ProcessingMetadata(general_ledger=suggestion),
        )
