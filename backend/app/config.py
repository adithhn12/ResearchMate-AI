import os
from pathlib import Path
from dotenv import load_dotenv

# Find root directory (where .env is located)
# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_ENV = BASE_DIR / ".env"

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)
else:
    load_dotenv()

# Production persistent disk directory (e.g., Render disk mounted at /var/data)
DATA_DIR_ENV = os.getenv("DATA_DIR")
STORAGE_ROOT = Path(DATA_DIR_ENV) if DATA_DIR_ENV else BASE_DIR

class Settings:
    PROJECT_NAME: str = "ResearchMate AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "researchmate-ai-super-secret-key-change-in-prod-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS Origins (comma-separated or * for wildcard)
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "*")
    @property
    def CORS_ORIGINS(self):
        if self.CORS_ORIGINS_RAW.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS_RAW.split(",") if o.strip()]
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Default model: gemini-flash-lite-latest (fastest & high quota, with fallbacks to gemini-3.8-flash, gemini-flash-latest)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    
    # Storage & DB (persistent across deployments when DATA_DIR is configured)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{STORAGE_ROOT / 'researchmate.db'}")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(STORAGE_ROOT / "chroma_data"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(STORAGE_ROOT / "uploaded_papers"))
    
    # Embedding model
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
