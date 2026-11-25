import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Find root directory (where .env is located)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_ENV = BASE_DIR / ".env"

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)
else:
    load_dotenv()

# Temporary local directory only (uploaded PDFs are persisted in Supabase Storage)
TEMP_UPLOAD_DIR = Path(tempfile.gettempdir()) / "researchmate_uploads"
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    PROJECT_NAME: str = "ResearchMate AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY") or "researchmate-ai-super-secret-key-change-in-prod-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS Origins (comma-separated or * for wildcard)
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS") or "*"

    @property
    def CORS_ORIGINS(self):
        if self.CORS_ORIGINS_RAW.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS_RAW.split(",") if o.strip()]

    # Gemini API (LLM + External Embeddings)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "gemini-embedding-001")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "16"))

    # Database (Supabase PostgreSQL in production; local SQLite fallback for tests if unset)
    _RAW_DATABASE_URL: str = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'researchmate.db'}"
    DATABASE_URL: str = (
        _RAW_DATABASE_URL.replace("postgres://", "postgresql://", 1)
        if _RAW_DATABASE_URL.startswith("postgres://")
        else _RAW_DATABASE_URL
    )

    # Supabase Storage (for uploaded PDFs)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "research-papers").strip()

    # Temporary filesystem directory on Render (cleaned up immediately after processing)
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(TEMP_UPLOAD_DIR))

    # Bounded ingestion limits for 512 MB Render Free Tier
    MAX_UPLOAD_FILE_MB: int = int(os.getenv("MAX_UPLOAD_FILE_MB", "25"))
    MAX_PDF_PAGES: int = int(os.getenv("MAX_PDF_PAGES", "150"))
    MAX_FILES_PER_UPLOAD: int = int(os.getenv("MAX_FILES_PER_UPLOAD", "5"))


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
