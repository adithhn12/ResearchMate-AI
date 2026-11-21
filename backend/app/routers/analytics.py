from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Project, Paper, ChatSession, PaperComparison, LiteratureReview, ActivityLog
from app.schemas import DashboardAnalytics, PaperResponse
from app.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

@router.get("/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total counts
    papers_query = db.query(Paper).join(Project).filter(Project.user_id == current_user.id)
    projects_count = db.query(Project).filter(Project.user_id == current_user.id).count()
    chats_count = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    comps_count = db.query(PaperComparison).filter(PaperComparison.user_id == current_user.id).count()
    reviews_count = db.query(LiteratureReview).filter(LiteratureReview.user_id == current_user.id).count()

    if project_id:
        papers_query = papers_query.filter(Paper.project_id == project_id)

    total_papers = papers_query.count()

    # Recent uploads (last 5)
    recent_papers = papers_query.order_by(Paper.created_at.desc()).limit(5).all()
    recent_uploads = [PaperResponse.from_orm(p) for p in recent_papers]

    # Recent activity logs (last 10)
    act_query = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id)
    if project_id:
        act_query = act_query.filter(ActivityLog.project_id == project_id)
    recent_acts = act_query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    activity_list = []
    for a in recent_acts:
        activity_list.append({
            "id": a.id,
            "action": a.action,
            "details": a.details,
            "created_at": a.created_at.isoformat()
        })

    # Papers by publication year
    year_data = []
    years_counted = (
        db.query(Paper.publication_year, func.count(Paper.id))
        .join(Project)
        .filter(Project.user_id == current_user.id)
    )
    if project_id:
        years_counted = years_counted.filter(Paper.project_id == project_id)
    
    years_counted = (
        years_counted
        .filter(Paper.publication_year.isnot(None))
        .group_by(Paper.publication_year)
        .order_by(Paper.publication_year.asc())
        .all()
    )

    for yr, cnt in years_counted:
        year_data.append({"year": str(yr), "count": cnt})

    # Status distribution
    status_counts = (
        db.query(Paper.status, func.count(Paper.id))
        .join(Project)
        .filter(Project.user_id == current_user.id)
    )
    if project_id:
        status_counts = status_counts.filter(Paper.project_id == project_id)
    status_counts = status_counts.group_by(Paper.status).all()

    status_data = []
    for st, cnt in status_counts:
        status_data.append({"status": st.capitalize(), "count": cnt})

    return {
        "total_papers": total_papers,
        "total_projects": projects_count,
        "total_chat_sessions": chats_count,
        "total_comparisons": comps_count,
        "total_reviews": reviews_count,
        "recent_uploads": recent_uploads,
        "recent_activities": activity_list,
        "papers_by_year": year_data,
        "status_distribution": status_data
    }
