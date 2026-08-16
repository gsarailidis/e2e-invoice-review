from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field
from stdnum.eu import vat

from app.schemas.invoice import Invoice
from app.schemas.receipt import Receipt

TOTAL_TOLERANCE = Decimal("0.01")
ValidationIssueCode = Literal[
    "vendor_vat_id_invalid",
    "customer_vat_id_invalid",
    "invoice_total_mismatch",
    "receipt_total_mismatch",
]
ValidationSeverity = Literal["error", "warning"]


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ValidationIssueCode
    field: str
    severity: ValidationSeverity
    message: str


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issues: list[ValidationIssue] = Field(default_factory=list)

    @computed_field
    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def _invalid_vat_issue(value: str, *, party: Literal["vendor", "customer"]) -> ValidationIssue:
    return ValidationIssue(
        code=f"{party}_vat_id_invalid",
        field=f"{party}_vat_id",
        severity="error",
        message=f"The extracted {party} VAT ID {value!r} has an invalid EU format or checksum.",
    )


def validate_invoice(invoice: Invoice) -> ValidationResult:
    """Run focused, deterministic checks without changing extracted values."""
    issues: list[ValidationIssue] = []

    if invoice.vendor_vat_id is not None and not vat.is_valid(invoice.vendor_vat_id.value):
        issues.append(_invalid_vat_issue(invoice.vendor_vat_id.value, party="vendor"))
    if invoice.customer_vat_id is not None and not vat.is_valid(invoice.customer_vat_id.value):
        issues.append(_invalid_vat_issue(invoice.customer_vat_id.value, party="customer"))

    if (
        invoice.subtotal is not None
        and invoice.total_tax is not None
        and invoice.invoice_total is not None
    ):
        expected_total = invoice.subtotal.value + invoice.total_tax.value
        difference = abs(expected_total - invoice.invoice_total.value)
        if difference > TOTAL_TOLERANCE:
            issues.append(
                ValidationIssue(
                    code="invoice_total_mismatch",
                    field="invoice_total",
                    severity="error",
                    message=(
                        "The invoice total does not equal subtotal plus VAT within the "
                        f"{TOTAL_TOLERANCE} tolerance."
                    ),
                )
            )

    return ValidationResult(issues=issues)


def validate_receipt(receipt: Receipt) -> ValidationResult:
    """Run focused receipt-total reconciliation without changing extracted values."""
    issues: list[ValidationIssue] = []

    if receipt.subtotal is not None and receipt.total_tax is not None and receipt.total is not None:
        expected_total = receipt.subtotal.value + receipt.total_tax.value
        difference = abs(expected_total - receipt.total.value)
        if difference > TOTAL_TOLERANCE:
            issues.append(
                ValidationIssue(
                    code="receipt_total_mismatch",
                    field="total",
                    severity="error",
                    message=(
                        "The receipt total does not equal subtotal plus VAT within the "
                        f"{TOTAL_TOLERANCE} tolerance."
                    ),
                )
            )

    return ValidationResult(issues=issues)
