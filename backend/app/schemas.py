from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# --- Auth Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    paper_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Paper Schemas ---
class PaperResponse(BaseModel):
    id: int
    project_id: int
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    publication_year: Optional[int] = None
    keywords: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    page_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaperDetailResponse(PaperResponse):
    chunks_count: Optional[int] = 0

# --- Chat & RAG Schemas ---
class SourceCitation(BaseModel):
    paper_id: int
    paper_title: str
    page_number: int
    snippet: str

class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[int] = None
    project_id: Optional[int] = None
    paper_ids: Optional[List[int]] = None  # Filter papers or search all in project

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    sources: List[SourceCitation] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    project_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

# --- Comparison Schemas ---
class ComparisonItem(BaseModel):
    paper_id: int
    paper_title: str
    authors: Optional[str] = None
    publication_year: Optional[int] = None
    research_objective: str = ""
    methodology: str = ""
    algorithms: Union[str, List[Any]] = ""
    datasets: Union[str, List[Any]] = ""
    metrics: Union[str, List[Any]] = ""
    results: str = ""
    strengths: Union[str, List[Any]] = ""
    limitations: Union[str, List[Any]] = ""
    future_work: Union[str, List[Any]] = ""

    @field_validator('algorithms', 'datasets', 'metrics', 'strengths', 'limitations', 'future_work', mode='before')
    @classmethod
    def join_list_to_str(cls, v):
        if isinstance(v, list):
            return ", ".join(str(item) for item in v)
        if v is None:
            return ""
        return str(v)

class ComparisonRequest(BaseModel):
    project_id: int
    paper_ids: List[int]
    title: Optional[str] = "Methodology & Findings Comparison"

class ComparisonResponse(BaseModel):
    id: int
    project_id: int
    title: str
    paper_ids: List[int]
    comparison_data: List[ComparisonItem]
    summary: Optional[str] = None
    created_at: datetime

# --- Research Gap Schemas ---
class GapFinding(BaseModel):
    title: str
    category: str  # Methodology, Dataset, Scalability, Theoretical, Evaluation, etc.
    description: str
    type: str  # 'explicit_limitation' or 'ai_inferred_gap'
    supporting_papers: List[Dict[str, Any]]  # [{"paper_id": 1, "paper_title": "...", "page": 4}]
    future_direction: str

class GapAnalysisRequest(BaseModel):
    project_id: int
    paper_ids: List[int]
    title: Optional[str] = "Research Gap Analysis"

class GapAnalysisResponse(BaseModel):
    id: int
    project_id: int
    title: str
    paper_ids: List[int]
    recurring_challenges: List[str]
    gaps: List[GapFinding]
    created_at: datetime

# --- Literature Review Schemas ---
class LiteratureReviewGenerateRequest(BaseModel):
    project_id: int
    paper_ids: List[int]
    title: Optional[str] = "Literature Review"
    research_focus: Optional[str] = None

class LiteratureReviewUpdateRequest(BaseModel):
    title: Optional[str] = None
    introduction: Optional[str] = None
    background_related_work: Optional[str] = None
    thematic_analysis: Optional[str] = None
    comparison_existing_approaches: Optional[str] = None
    research_limitations: Optional[str] = None
    research_gaps: Optional[str] = None
    conclusion: Optional[str] = None
    references: Optional[str] = None

class LiteratureReviewResponse(BaseModel):
    id: int
    project_id: int
    title: str
    paper_ids: List[int]
    introduction: Optional[str] = None
    background_related_work: Optional[str] = None
    thematic_analysis: Optional[str] = None
    comparison_existing_approaches: Optional[str] = None
    research_limitations: Optional[str] = None
    research_gaps: Optional[str] = None
    conclusion: Optional[str] = None
    references: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Analytics Schemas ---
class DashboardAnalytics(BaseModel):
    total_papers: int
    total_projects: int
    total_chat_sessions: int
    total_comparisons: int
    total_reviews: int
    recent_uploads: List[PaperResponse]
    recent_activities: List[Dict[str, Any]]
    papers_by_year: List[Dict[str, Any]]
    status_distribution: List[Dict[str, Any]]
