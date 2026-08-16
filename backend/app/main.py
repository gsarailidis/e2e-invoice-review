from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import FRONTEND_DEVELOPMENT_ORIGIN, Settings
from app.invoices.routes import router
from app.invoices.service import DocumentProcessingService
from app.pipeline import (
    DocumentClassificationStep,
    DocumentExtractionStep,
    DocumentInput,
    DocumentValidationStep,
    GeneralLedgerClassificationStep,
    Pipeline,
    ProcessedDocument,
)
from app.providers.azure_document_intelligence import DocumentIntelligenceService
from app.providers.azure_openai import (
    close_azure_openai_responses_model,
    create_azure_openai_responses_model,
)

DEFAULT_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        resolved_settings = settings or Settings.from_env_file(DEFAULT_ENV_FILE)
        model = create_azure_openai_responses_model(
            endpoint=resolved_settings.azure_openai_endpoint,
            api_key=resolved_settings.azure_openai_api_key,
        )
        document_intelligence = DocumentIntelligenceService(
            endpoint=resolved_settings.azure_document_intelligence_endpoint,
            api_key=resolved_settings.azure_document_intelligence_key,
        )
        pipeline: Pipeline[DocumentInput, ProcessedDocument] = (
            Pipeline.start(DocumentClassificationStep(model))
            .then(DocumentExtractionStep(document_intelligence))
            .then(DocumentValidationStep())
            .then(GeneralLedgerClassificationStep(model))
        )
        application.state.document_processing_service = DocumentProcessingService(pipeline)

        try:
            yield
        finally:
            try:
                document_intelligence.close()
            finally:
                await close_azure_openai_responses_model(model)

    application = FastAPI(
        title="Invoice Review API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        servers=[{"url": "./"}],
    )

    @application.get("/", include_in_schema=False)
    def api_root() -> RedirectResponse:
        return RedirectResponse(url="docs")

    @application.get("/docs", include_in_schema=False)
    def swagger_ui() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url="openapi.json",
            title=f"{application.title} - Swagger UI",
        )

    @application.get("/redoc", include_in_schema=False)
    def redoc() -> HTMLResponse:
        return get_redoc_html(
            openapi_url="openapi.json",
            title=f"{application.title} - ReDoc",
        )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_DEVELOPMENT_ORIGIN],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    application.include_router(router)
    return application


app = create_app()
