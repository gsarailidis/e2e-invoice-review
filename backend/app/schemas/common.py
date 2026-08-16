from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExtractionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExtractedField[FieldValue](ExtractionSchema):
    value: FieldValue
    content: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source: Literal["document_intelligence"] = "document_intelligence"
