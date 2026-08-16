from app.pipeline import (
    DocumentInput,
    DocumentMediaType,
    Pipeline,
    ProcessedDocument,
    UnsupportedDocumentTypeError,
)


class DocumentProcessingError(RuntimeError):
    """Raised when the processing pipeline cannot complete safely."""


class DocumentProcessingService:
    def __init__(self, pipeline: Pipeline[DocumentInput, ProcessedDocument]) -> None:
        self._pipeline = pipeline

    def process(
        self,
        document: bytes,
        *,
        media_type: DocumentMediaType,
    ) -> ProcessedDocument:
        try:
            return self._pipeline.run(
                DocumentInput(content=document, media_type=media_type)
            )
        except UnsupportedDocumentTypeError:
            raise
        except Exception as exc:
            raise DocumentProcessingError("Financial document processing failed") from exc
