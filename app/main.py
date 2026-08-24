import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.routers import documents, chat, health
from exception.custom_exception import DocumentPortalException
from src.ingestion import MultimodalDocumentIngestion
from src.retriever import MultimodalQdrantRetriever
from src.generation import MultimodalRAGGenerator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retrieve configuration and fail fast if required env vars are missing
    settings = get_settings()
    
    # Workaround: src/ constructors read credentials via os.getenv() internally rather than accepting them as kwargs, and src/ is intentionally not modified in this phase. Settings are pushed into the process environment before service instantiation so those internal os.getenv() calls resolve correctly.
    os.environ["GOOGLE_API_KEY"] = settings.final_gemini_api_key
    os.environ["GEMINI_API_KEY"] = settings.final_gemini_api_key
    os.environ["GROQ_API_KEY"] = settings.groq_api_key or ""
    os.environ["QDRANT_URL"] = settings.final_qdrant_url
    if settings.qdrant_api_key:
        os.environ["QDRANT_API_KEY"] = settings.qdrant_api_key
    os.environ["QDRANT_COLLECTION_NAME"] = settings.qdrant_collection_name
    os.environ["GEMINI_EMBEDDING_MODEL"] = settings.gemini_embedding_model
    os.environ["GEMINI_EMBEDDING_DIMENSION"] = str(settings.gemini_embedding_dimension)
    os.environ["GROQ_CHAT_MODEL"] = settings.groq_chat_model
    if settings.tesseract_path:
        os.environ["TESSERACT_PATH"] = settings.tesseract_path

    # Instantiate core services exactly once
    app.state.ingestion_service = MultimodalDocumentIngestion(
        collection_name=settings.qdrant_collection_name
    )
    app.state.retrieval_service = MultimodalQdrantRetriever(
        collection_name=settings.qdrant_collection_name
    )
    app.state.generation_service = MultimodalRAGGenerator(
        collection_name=settings.qdrant_collection_name,
        model_name=settings.groq_chat_model
    )
    
    yield
    
    # Shutdown logic: clean up clients with a close method
    for key in ["ingestion_service", "retrieval_service", "generation_service"]:
        service = getattr(app.state, key, None)
        if service:
            if hasattr(service, "close") and callable(getattr(service, "close")):
                try:
                    service.close()
                except Exception:
                    pass
            client = getattr(service, "client", None)
            if client and hasattr(client, "close") and callable(getattr(client, "close")):
                try:
                    client.close()
                except Exception:
                    pass

app = FastAPI(lifespan=lifespan)

# Mount routes
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(health.router, prefix="/health", tags=["health"])

# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(DocumentPortalException)
async def document_portal_exception_handler(request: Request, exc: DocumentPortalException):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
