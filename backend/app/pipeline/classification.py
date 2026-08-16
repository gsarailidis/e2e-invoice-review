from pydantic_ai import Agent, BinaryContent, NativeOutput
from pydantic_ai.models import Model

from app.pipeline.models import (
    ClassifiedDocument,
    DocumentClassification,
    DocumentInput,
    DocumentMediaType,
    DocumentType,
)

__all__ = [
    "DocumentClassification",
    "DocumentClassificationStep",
    "DocumentMediaType",
    "DocumentType",
]


class DocumentClassificationStep:
    """Classify an uploaded financial document with native structured output."""

    def __init__(self, model: Model) -> None:
        self._agent = Agent(
            model,
            output_type=NativeOutput(
                DocumentClassification,
                name="document_classification",
                strict=True,
            ),
            instructions=(
                "Classify the supplied document from its visible contents. "
                "Do not infer facts that are not present in the document."
            ),
        )

    def run(self, value: DocumentInput) -> ClassifiedDocument:
        result = self._agent.run_sync(
            [
                "Classify this document.",
                BinaryContent(data=value.content, media_type=value.media_type),
            ]
        )
        return ClassifiedDocument(input=value, classification=result.output)
