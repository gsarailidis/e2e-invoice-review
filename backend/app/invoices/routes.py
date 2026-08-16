from typing import Annotated, cast

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.config import DOCUMENT_MEDIA_TYPES, MAX_UPLOAD_BYTES
from app.invoices.service import DocumentProcessingError, DocumentProcessingService
from app.pipeline import DocumentMediaType, ProcessedDocument, UnsupportedDocumentTypeError

router = APIRouter()


def _processing_service(request: Request) -> DocumentProcessingService:
    service = getattr(request.app.state, "document_processing_service", None)
    if not isinstance(service, DocumentProcessingService):
        raise RuntimeError("Document processing service is not initialized")
    return service


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/api/documents/process",
    response_model=ProcessedDocument,
    status_code=status.HTTP_200_OK,
    tags=["documents"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "The uploaded document is empty"},
        status.HTTP_413_CONTENT_TOO_LARGE: {"description": "The upload exceeds 4 MB"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": "Unsupported document media type"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Missing upload or document classified as other"
        },
        status.HTTP_502_BAD_GATEWAY: {"description": "A processing provider failed"},
    },
)
def process_document(
    file: Annotated[UploadFile, File(description="One PDF, PNG, or JPEG document")],
    service: Annotated[DocumentProcessingService, Depends(_processing_service)],
) -> ProcessedDocument:
    if file.content_type not in DOCUMENT_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Supported document types are PDF, PNG, and JPEG",
        )

    document = file.file.read(MAX_UPLOAD_BYTES + 1)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded document is empty",
        )
    if len(document) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Uploaded document exceeds the 4 MB limit",
        )

    try:
        return service.process(
            document,
            media_type=cast(DocumentMediaType, file.content_type),
        )
    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The uploaded file is not an invoice or receipt",
        ) from exc
    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A document processing provider could not complete the request",
        ) from exc
