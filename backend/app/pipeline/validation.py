from app.invoices.validation import validate_invoice, validate_receipt
from app.pipeline.models import ExtractedDocument, ProcessedDocument
from app.schemas.invoice import Invoice


class DocumentValidationStep:
    def run(self, value: ExtractedDocument) -> ProcessedDocument:
        if isinstance(value.document, Invoice):
            validation = validate_invoice(value.document)
        else:
            validation = validate_receipt(value.document)

        return ProcessedDocument(
            classification=value.classification,
            document=value.document,
            validation=validation,
        )
