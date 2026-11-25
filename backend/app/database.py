import logging
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("researchmate.database")

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
is_postgres = settings.DATABASE_URL.startswith("postgresql")

if is_sqlite:
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "", 1)
    if db_path_str and db_path_str != ":memory:":
        Path(db_path_str).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} if is_sqlite else {},
    pool_pre_ping=True,
    pool_size=5 if is_postgres else 5,
    max_overflow=5 if is_postgres else 10,
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """
    Initialize database tables, pgvector extension, and idempotent schema migrations
    without dropping or overwriting existing production data.
    """
    if is_postgres:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)

    if is_postgres:
        dims = int(settings.EMBEDDING_DIMENSIONS)
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE papers ADD COLUMN IF NOT EXISTS storage_path VARCHAR(500)"))
            conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id)"))
            conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100)"))
            conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS embedding_dimensions INTEGER"))
            conn.execute(text(f"ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS embedding vector({dims})"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_paper_chunks_project_id ON paper_chunks (project_id)"))
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_paper_chunks_embedding_hnsw "
                    "ON paper_chunks USING hnsw (embedding vector_cosine_ops)"
                )
            )
    elif is_sqlite:
        with engine.begin() as conn:
            paper_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(papers)")).fetchall()}
            if "storage_path" not in paper_cols:
                conn.execute(text("ALTER TABLE papers ADD COLUMN storage_path VARCHAR(500)"))

            chunk_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(paper_chunks)")).fetchall()}
            if "project_id" not in chunk_cols:
                conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN project_id INTEGER"))
            if "embedding_model" not in chunk_cols:
                conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN embedding_model VARCHAR(100)"))
            if "embedding_dimensions" not in chunk_cols:
                conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN embedding_dimensions INTEGER"))
            if "embedding" not in chunk_cols:
                conn.execute(text("ALTER TABLE paper_chunks ADD COLUMN embedding TEXT"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_paper_chunks_project_id ON paper_chunks (project_id)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
