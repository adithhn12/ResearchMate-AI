import os
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path so 'app' package resolves whether launched
# from repository root (e.g. uvicorn backend.app.main:app), from backend/ (e.g. uvicorn app.main:app),
# or via root main:app wrapper
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("researchmate.app")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth,
    projects,
    papers,
    chat,
    compare,
    research_gaps,
    literature_reviews,
    analytics
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Literature Review and Research Assistant Backend"
)

# CORS middleware supporting localhost and production Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(papers.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(compare.router, prefix=settings.API_V1_STR)
app.include_router(research_gaps.router, prefix=settings.API_V1_STR)
app.include_router(literature_reviews.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

# Static files for uploaded PDFs if needed
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "gemini_model": settings.GEMINI_MODEL,
        "docs_url": "/docs"
    }

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.on_event("startup")
def log_startup_routes():
    logger.info("=" * 60)
    logger.info(f"ResearchMate AI Backend Online (v{settings.VERSION})")
    logger.info(f"API V1 Prefix: {settings.API_V1_STR}")
    logger.info(f"Docs URL: /docs | OpenAPI: /openapi.json")
    logger.info(f"Health Checks: /health and {settings.API_V1_STR}/health")
    logger.info(f"CORS Allowed Origins: {settings.CORS_ORIGINS}")
    logger.info("Registered API Endpoints:")
    schema = app.openapi()
    for path, path_item in schema.get("paths", {}).items():
        methods = [m.upper() for m in path_item.keys() if m != "parameters"]
        logger.info(f"  [{','.join(methods):<15}] {path}")
    logger.info("=" * 60)
