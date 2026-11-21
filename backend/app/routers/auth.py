from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User, Project, ActivityLog
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name or user_in.email.split("@")[0].title()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Automatically create a default research project for new user
    default_proj = Project(
        user_id=new_user.id,
        name="My First Research Project",
        description="General literature exploration and comparative study"
    )
    db.add(default_proj)

    # Log activity
    log = ActivityLog(
        user_id=new_user.id,
        action="register",
        details="User registered and initialized workspace"
    )
    db.add(log)
    db.commit()

    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Log activity
    log = ActivityLog(user_id=user.id, action="login", details="User logged into ResearchMate AI")
    db.add(log)
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """One-click instant login for testing and immediate use."""
    demo_email = "researcher@example.com"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        user = User(
            email=demo_email,
            hashed_password=hash_password("ResearchMate2026!"),
            full_name="Dr. Alex Rivera"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Default project
        default_proj = Project(
            user_id=user.id,
            name="Generative AI & LLM Architectures",
            description="Exploration of Retrieval Augmented Generation, attention mechanisms, and multi-agent coordination"
        )
        db.add(default_proj)
        db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
