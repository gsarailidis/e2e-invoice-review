from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.accounting import GeneralLedgerSuggestion
from app.invoices.validation import ValidationResult
from app.schemas.invoice import Invoice
from app.schemas.receipt import Receipt

DocumentMediaType = Literal["application/pdf", "image/png", "image/jpeg"]
DocumentType = Literal["invoice", "receipt", "other"]
NormalizedDocument = Invoice | Receipt


class DocumentClassification(BaseModel):
    """Provider-independent classification used to route a financial document."""

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = Field(
        description=(
            "invoice for a request for payment, receipt for proof of a completed payment, "
            "or other when neither applies"
        )
    )


@dataclass(frozen=True)
class DocumentInput:
    content: bytes
    media_type: DocumentMediaType

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Document must not be empty")


@dataclass(frozen=True)
class ClassifiedDocument:
    input: DocumentInput
    classification: DocumentClassification


@dataclass(frozen=True)
class ExtractedDocument:
    classification: DocumentClassification
    document: NormalizedDocument


class ValidatedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classification: DocumentClassification
    document: Annotated[NormalizedDocument, Field(discriminator="document_type")]
    validation: ValidationResult


class ProcessingMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    general_ledger: GeneralLedgerSuggestion


class ProcessedDocument(ValidatedDocument):
    metadata: ProcessingMetadata
