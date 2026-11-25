from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.config import settings
from app.database import Base, is_postgres

if is_postgres:
    from pgvector.sqlalchemy import Vector
    EmbeddingColumnType = Vector(settings.EMBEDDING_DIMENSIONS)
else:
    EmbeddingColumnType = Text

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="project", cascade="all, delete-orphan")
    comparisons = relationship("PaperComparison", back_populates="project", cascade="all, delete-orphan")
    gap_analyses = relationship("ResearchGapAnalysis", back_populates="project", cascade="all, delete-orphan")
    literature_reviews = relationship("LiteratureReview", back_populates="project", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(String(500), nullable=True)
    abstract = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    keywords = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=False)
    storage_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    page_count = Column(Integer, default=0)
    status = Column(String(50), default="processing")  # uploaded, processing, indexed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="papers")
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_model = Column(String(100), nullable=True)
    embedding_dimensions = Column(Integer, nullable=True)
    embedding = Column(EmbeddingColumnType, nullable=True)

    paper = relationship("Paper", back_populates="chunks")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="Research Discussion")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    # Stored as JSON string: [{"paper_id": 1, "paper_title": "...", "page_number": 2, "snippet": "..."}]
    sources_json = Column(Text, nullable=True, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")

    @property
    def sources(self):
        if self.sources_json:
            try:
                return json.loads(self.sources_json)
            except Exception:
                return []
        return []

    @sources.setter
    def sources(self, value):
        self.sources_json = json.dumps(value)


class PaperComparison(Base):
    __tablename__ = "paper_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="Methodology Comparison")
    paper_ids_json = Column(Text, nullable=False, default="[]")
    # Structured JSON data: dict of paper_id -> comparison fields
    comparison_data_json = Column(Text, nullable=False, default="{}")
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="comparisons")


class ResearchGapAnalysis(Base):
    __tablename__ = "research_gap_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="Research Gap Report")
    paper_ids_json = Column(Text, nullable=False, default="[]")
    # Structured JSON: { recurring_challenges: [...], limitations: [...], research_gaps: [...], future_directions: [...] }
    analysis_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="gap_analyses")


class LiteratureReview(Base):
    __tablename__ = "literature_reviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="Literature Review")
    paper_ids_json = Column(Text, nullable=False, default="[]")
    introduction = Column(Text, nullable=True)
    background_related_work = Column(Text, nullable=True)
    thematic_analysis = Column(Text, nullable=True)
    comparison_existing_approaches = Column(Text, nullable=True)
    research_limitations = Column(Text, nullable=True)
    research_gaps = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="literature_reviews")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    action = Column(String(100), nullable=False)  # upload_paper, run_chat, run_comparison, etc.
    details = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")
