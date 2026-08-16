from app.pipeline.models import ClassifiedDocument, ExtractedDocument
from app.providers.azure_document_intelligence import DocumentIntelligenceService


class UnsupportedDocumentTypeError(RuntimeError):
    """Raised when a non-financial document reaches extraction."""


class DocumentExtractionStep:
    def __init__(self, service: DocumentIntelligenceService) -> None:
        self._service = service

    def run(self, value: ClassifiedDocument) -> ExtractedDocument:
        document_type = value.classification.document_type
        if document_type == "invoice":
            document = self._service.analyze_invoice(value.input.content)
        elif document_type == "receipt":
            document = self._service.analyze_receipt(value.input.content)
        else:
            raise UnsupportedDocumentTypeError(
                "Document was classified as other; Document Intelligence was not called"
            )

        return ExtractedDocument(
            classification=value.classification,
            document=document,
        )
