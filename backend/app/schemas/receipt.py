from datetime import date, time
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import ExtractedField, ExtractionSchema


class ReceiptLineItem(ExtractionSchema):
    description: ExtractedField[str] | None = None
    quantity: ExtractedField[Decimal] | None = None
    quantity_unit: ExtractedField[str] | None = None
    price: ExtractedField[Decimal] | None = None
    total_price: ExtractedField[Decimal] | None = None
    product_code: ExtractedField[str] | None = None


class Receipt(ExtractionSchema):
    document_type: Literal["receipt"] = "receipt"
    document_confidence: float = Field(ge=0, le=1)
    merchant_name: ExtractedField[str] | None = None
    transaction_date: ExtractedField[date] | None = None
    transaction_time: ExtractedField[time] | None = None
    receipt_type: ExtractedField[str] | None = None
    country_region: ExtractedField[str] | None = None
    currency: ExtractedField[str] | None = None
    subtotal: ExtractedField[Decimal] | None = None
    total_tax: ExtractedField[Decimal] | None = None
    total: ExtractedField[Decimal] | None = None
    items: list[ReceiptLineItem] = Field(default_factory=list)
