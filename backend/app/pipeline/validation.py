from app.invoices.validation import validate_invoice, validate_receipt
from app.pipeline.models import ExtractedDocument, ValidatedDocument
from app.schemas.invoice import Invoice


class DocumentValidationStep:
    def run(self, value: ExtractedDocument) -> ValidatedDocument:
        if isinstance(value.document, Invoice):
            validation = validate_invoice(value.document)
        else:
            validation = validate_receipt(value.document)

        return ValidatedDocument(
            classification=value.classification,
            document=value.document,
            validation=validation,
        )
