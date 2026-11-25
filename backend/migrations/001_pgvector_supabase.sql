-- Idempotent Supabase PostgreSQL + pgvector migration for ResearchMate AI
-- Safe to run on both fresh and existing databases: does not drop or overwrite existing data.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS papers (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    title VARCHAR(500) NOT NULL,
    authors VARCHAR(500),
    abstract TEXT,
    publication_year INTEGER,
    keywords VARCHAR(500),
    file_path VARCHAR(500) NOT NULL,
    storage_path VARCHAR(500),
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    page_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'processing',
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS paper_chunks (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER NOT NULL REFERENCES papers(id),
    project_id INTEGER REFERENCES projects(id),
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    embedding_model VARCHAR(100),
    embedding_dimensions INTEGER,
    embedding vector(768)
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) DEFAULT 'Research Discussion',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    sources_json TEXT DEFAULT '[]',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS paper_comparisons (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) DEFAULT 'Methodology Comparison',
    paper_ids_json TEXT NOT NULL DEFAULT '[]',
    comparison_data_json TEXT NOT NULL DEFAULT '{}',
    summary TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS research_gap_analyses (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) DEFAULT 'Research Gap Report',
    paper_ids_json TEXT NOT NULL DEFAULT '[]',
    analysis_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS literature_reviews (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) DEFAULT 'Literature Review',
    paper_ids_json TEXT NOT NULL DEFAULT '[]',
    introduction TEXT,
    background_related_work TEXT,
    thematic_analysis TEXT,
    comparison_existing_approaches TEXT,
    research_limitations TEXT,
    research_gaps TEXT,
    conclusion TEXT,
    "references" TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    project_id INTEGER REFERENCES projects(id),
    action VARCHAR(100) NOT NULL,
    details VARCHAR(500),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- Idempotent column additions for existing pre-migration databases
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

-- Required indexes for relational queries, project isolation, and pgvector similarity search
CREATE INDEX IF NOT EXISTS ix_paper_chunks_project_id
    ON paper_chunks (project_id);

CREATE INDEX IF NOT EXISTS ix_paper_chunks_paper_id
    ON paper_chunks (paper_id);

CREATE INDEX IF NOT EXISTS ix_paper_chunks_embedding_hnsw
    ON paper_chunks USING hnsw (embedding vector_cosine_ops);
