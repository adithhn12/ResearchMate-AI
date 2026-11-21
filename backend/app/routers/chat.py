from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, Paper, ChatSession, ChatMessage, ActivityLog
from app.schemas import ChatMessageCreate, ChatMessageResponse, ChatSessionResponse
from app.auth import get_current_user
from app.services.vector_store import vector_store
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/chat", tags=["AI Research Assistant"])

@router.get("/sessions/{project_id}", response_model=List[ChatSessionResponse])
def get_project_sessions(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sessions = db.query(ChatSession).filter(
        ChatSession.project_id == project_id,
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()

    return sessions

@router.post("/sessions", response_model=ChatSessionResponse)
def create_session(
    project_id: int,
    title: Optional[str] = "Research Discussion",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    session = ChatSession(
        project_id=project_id,
        user_id=current_user.id,
        title=title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/message", response_model=ChatMessageResponse)
def send_message(
    msg_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session or create one
    session = None
    if msg_in.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == msg_in.session_id,
            ChatSession.user_id == current_user.id
        ).first()

    if not session:
        # Resolve target project
        target_proj_id = msg_in.project_id
        if not target_proj_id and msg_in.paper_ids:
            p_obj = db.query(Paper).filter(Paper.id == msg_in.paper_ids[0]).first()
            if p_obj:
                target_proj_id = p_obj.project_id

        if target_proj_id:
            proj = db.query(Project).filter(Project.id == target_proj_id, Project.user_id == current_user.id).first()
        else:
            proj = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).first()

        if not proj:
            raise HTTPException(status_code=400, detail="Please create a research project first")
        session = ChatSession(
            project_id=proj.id,
            user_id=current_user.id,
            title=msg_in.content[:40] + "..." if len(msg_in.content) > 40 else msg_in.content
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 1. Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=msg_in.content
    )
    db.add(user_msg)
    db.commit()

    # Resolve target papers for accurate scoping & diversity
    if msg_in.paper_ids and len(msg_in.paper_ids) > 0:
        target_papers = db.query(Paper).filter(
            Paper.id.in_(msg_in.paper_ids),
            Paper.project_id == session.project_id
        ).all()
    else:
        target_papers = db.query(Paper).filter(
            Paper.project_id == session.project_id,
            Paper.status == "indexed"
        ).all()

    active_paper_ids = [p.id for p in target_papers]
    selected_titles = [p.title for p in target_papers]

    # 2. Retrieve relevant chunks via ChromaDB with source diversity
    retrieved_chunks = vector_store.query_chunks(
        project_id=session.project_id,
        query=msg_in.content,
        n_results=8,
        paper_ids=active_paper_ids if len(active_paper_ids) > 0 else None
    )

    # 3. Fetch past conversation history
    past_msgs = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.desc()).limit(8).all()
    history = [{"role": m.role, "content": m.content} for m in reversed(past_msgs[:-1])]

    # 4. Generate grounded Gemini response
    rag_result = gemini_service.chat_rag(
        query=msg_in.content,
        retrieved_chunks=retrieved_chunks,
        conversation_history=history,
        selected_papers=selected_titles
    )

    # 5. Save assistant response
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=rag_result["content"]
    )
    assistant_msg.sources = rag_result["sources"]
    db.add(assistant_msg)

    # Update session timestamp
    session.updated_at = assistant_msg.created_at
    if session.title == "Research Discussion" and len(msg_in.content) > 3:
        session.title = msg_in.content[:40] + "..." if len(msg_in.content) > 40 else msg_in.content

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        project_id=session.project_id,
        action="chat_rag",
        details=f"Inquired: '{msg_in.content[:60]}...'"
    )
    db.add(log)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg

@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    db.delete(session)
    db.commit()
    return {"message": "Chat session deleted"}
