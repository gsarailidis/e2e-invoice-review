from datetime import date, time
from decimal import Decimal
from io import BytesIO
from types import TracebackType
from typing import Self

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzedDocument,
    AnalyzeResult,
    DocumentField,
)
from azure.core.credentials import AzureKeyCredential

from app.schemas.common import ExtractedField
from app.schemas.invoice import Invoice, InvoiceLineItem
from app.schemas.receipt import Receipt, ReceiptLineItem


class DocumentIntelligenceMappingError(RuntimeError):
    """Raised when an Azure analysis result cannot be mapped to a document model."""


def _extracted[ExtractedValue](
    field: DocumentField, value: ExtractedValue
) -> ExtractedField[ExtractedValue]:
    return ExtractedField(
        value=value,
        content=field.content,
        confidence=field.confidence,
    )


def _field(document: AnalyzedDocument, name: str) -> DocumentField | None:
    if document.fields is None:
        return None
    return document.fields.get(name)


def _string(field: DocumentField | None) -> ExtractedField[str] | None:
    if field is None or field.value_string is None:
        return None
    return _extracted(field, field.value_string)


def _date(field: DocumentField | None) -> ExtractedField[date] | None:
    if field is None or field.value_date is None:
        return None
    return _extracted(field, field.value_date)


def _time(field: DocumentField | None) -> ExtractedField[time] | None:
    if field is None or field.value_time is None:
        return None
    return _extracted(field, field.value_time)


def _number(field: DocumentField | None) -> ExtractedField[Decimal] | None:
    if field is None or field.value_number is None:
        return None
    return _extracted(field, Decimal(str(field.value_number)))


def _money(field: DocumentField | None) -> ExtractedField[Decimal] | None:
    if field is None or field.value_currency is None:
        return None
    return _extracted(field, Decimal(str(field.value_currency.amount)))


def _country_region(field: DocumentField | None) -> ExtractedField[str] | None:
    if field is None or field.value_country_region is None:
        return None
    return _extracted(field, field.value_country_region)


def _currency(*fields: DocumentField | None) -> ExtractedField[str] | None:
    for field in fields:
        if (
            field is not None
            and field.value_currency is not None
            and field.value_currency.currency_code
        ):
            return _extracted(field, field.value_currency.currency_code.upper())
    return None


def _invoice_items(field: DocumentField | None) -> list[InvoiceLineItem]:
    if field is None or field.value_array is None:
        return []

    items: list[InvoiceLineItem] = []
    for item_field in field.value_array:
        values = item_field.value_object
        if values is None:
            continue
        items.append(
            InvoiceLineItem(
                description=_string(values.get("Description")),
                quantity=_number(values.get("Quantity")),
                unit=_string(values.get("Unit")),
                unit_price=_money(values.get("UnitPrice")),
                tax=_money(values.get("Tax")),
                tax_rate=_string(values.get("TaxRate")),
                amount=_money(values.get("Amount")),
                product_code=_string(values.get("ProductCode")),
            )
        )
    return items


def _receipt_items(field: DocumentField | None) -> list[ReceiptLineItem]:
    if field is None or field.value_array is None:
        return []

    items: list[ReceiptLineItem] = []
    for item_field in field.value_array:
        values = item_field.value_object
        if values is None:
            continue
        items.append(
            ReceiptLineItem(
                description=_string(values.get("Description")),
                quantity=_number(values.get("Quantity")),
                quantity_unit=_string(values.get("QuantityUnit")),
                price=_money(values.get("Price")),
                total_price=_money(values.get("TotalPrice")),
                product_code=_string(values.get("ProductCode")),
            )
        )
    return items


def _first_document(result: AnalyzeResult) -> AnalyzedDocument:
    if not result.documents:
        raise DocumentIntelligenceMappingError(
            f"{result.model_id} returned no analyzed documents"
        )
    return result.documents[0]


def _map_invoice(result: AnalyzeResult) -> Invoice:
    document = _first_document(result)
    subtotal = _field(document, "SubTotal")
    total_tax = _field(document, "TotalTax")
    invoice_total = _field(document, "InvoiceTotal")

    return Invoice(
        document_confidence=document.confidence,
        invoice_number=_string(_field(document, "InvoiceId")),
        invoice_date=_date(_field(document, "InvoiceDate")),
        due_date=_date(_field(document, "DueDate")),
        vendor_name=_string(_field(document, "VendorName")),
        vendor_vat_id=_string(_field(document, "VendorTaxId")),
        customer_name=_string(_field(document, "CustomerName")),
        customer_vat_id=_string(_field(document, "CustomerTaxId")),
        purchase_order=_string(_field(document, "PurchaseOrder")),
        currency=_currency(invoice_total, subtotal, total_tax),
        subtotal=_money(subtotal),
        total_tax=_money(total_tax),
        invoice_total=_money(invoice_total),
        items=_invoice_items(_field(document, "Items")),
    )


def _map_receipt(result: AnalyzeResult) -> Receipt:
    document = _first_document(result)
    subtotal = _field(document, "Subtotal")
    total_tax = _field(document, "TotalTax")
    total = _field(document, "Total")

    return Receipt(
        document_confidence=document.confidence,
        merchant_name=_string(_field(document, "MerchantName")),
        transaction_date=_date(_field(document, "TransactionDate")),
        transaction_time=_time(_field(document, "TransactionTime")),
        receipt_type=_string(_field(document, "ReceiptType")),
        country_region=_country_region(_field(document, "CountryRegion")),
        currency=_currency(total, subtotal, total_tax),
        subtotal=_money(subtotal),
        total_tax=_money(total_tax),
        total=_money(total),
        items=_receipt_items(_field(document, "Items")),
    )


class DocumentIntelligenceService:
    INVOICE_MODEL_ID = "prebuilt-invoice"
    RECEIPT_MODEL_ID = "prebuilt-receipt"

    def __init__(self, endpoint: str, api_key: str) -> None:
        self._client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )

    def analyze_invoice(self, document: bytes) -> Invoice:
        result = self._analyze(document, self.INVOICE_MODEL_ID)
        return _map_invoice(result)

    def analyze_receipt(self, document: bytes) -> Receipt:
        result = self._analyze(document, self.RECEIPT_MODEL_ID)
        return _map_receipt(result)

    def _analyze(self, document: bytes, model_id: str) -> AnalyzeResult:
        if not document:
            raise ValueError("Document must not be empty")

        with BytesIO(document) as stream:
            poller = self._client.begin_analyze_document(model_id, body=stream)
            return poller.result()

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
