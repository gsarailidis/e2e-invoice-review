from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import ExtractedField, ExtractionSchema


class InvoiceLineItem(ExtractionSchema):
    description: ExtractedField[str] | None = None
    quantity: ExtractedField[Decimal] | None = None
    unit: ExtractedField[str] | None = None
    unit_price: ExtractedField[Decimal] | None = None
    tax: ExtractedField[Decimal] | None = None
    tax_rate: ExtractedField[str] | None = None
    amount: ExtractedField[Decimal] | None = None
    product_code: ExtractedField[str] | None = None


class Invoice(ExtractionSchema):
    document_type: Literal["invoice"] = "invoice"
    document_confidence: float = Field(ge=0, le=1)
    invoice_number: ExtractedField[str] | None = None
    invoice_date: ExtractedField[date] | None = None
    due_date: ExtractedField[date] | None = None
    vendor_name: ExtractedField[str] | None = None
    vendor_vat_id: ExtractedField[str] | None = None
    customer_name: ExtractedField[str] | None = None
    customer_vat_id: ExtractedField[str] | None = None
    purchase_order: ExtractedField[str] | None = None
    currency: ExtractedField[str] | None = None
    subtotal: ExtractedField[Decimal] | None = None
    total_tax: ExtractedField[Decimal] | None = None
    invoice_total: ExtractedField[Decimal] | None = None
    items: list[InvoiceLineItem] = Field(default_factory=list)
