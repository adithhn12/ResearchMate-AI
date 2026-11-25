-- Idempotent Supabase PostgreSQL + pgvector migration for ResearchMate AI
-- Safe to run on existing databases: does not drop or overwrite existing data.

CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE papers
    ADD COLUMN IF NOT EXISTS storage_path VARCHAR(500);

ALTER TABLE paper_chunks
    ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id),
    ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100),
    ADD COLUMN IF NOT EXISTS embedding_dimensions INTEGER,
    ADD COLUMN IF NOT EXISTS embedding vector(768);

-- Backfill project_id on any existing paper_chunks rows from their parent paper
UPDATE paper_chunks pc
SET project_id = p.project_id
FROM papers p
WHERE pc.paper_id = p.id
  AND pc.project_id IS NULL;

CREATE INDEX IF NOT EXISTS ix_paper_chunks_project_id
    ON paper_chunks (project_id);

CREATE INDEX IF NOT EXISTS ix_paper_chunks_paper_id
    ON paper_chunks (paper_id);

CREATE INDEX IF NOT EXISTS ix_paper_chunks_embedding_hnsw
    ON paper_chunks USING hnsw (embedding vector_cosine_ops);
