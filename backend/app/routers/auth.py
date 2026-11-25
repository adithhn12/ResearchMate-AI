import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, ActivityLog
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token, get_current_user

logger = logging.getLogger("researchmate.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    normalized_email = _normalize_email(user_in.email)
    if not normalized_email or "@" not in normalized_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address.",
        )
    if not user_in.password or len(user_in.password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters long.",
        )

    existing = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    try:
        new_user = User(
            email=normalized_email,
            hashed_password=hash_password(user_in.password),
            full_name=(user_in.full_name or "").strip() or normalized_email.split("@")[0].title(),
        )
        db.add(new_user)
        db.flush()  # Populate new_user.id within the same transaction

        default_proj = Project(
            user_id=new_user.id,
            name="My First Research Project",
            description="General literature exploration and comparative study",
        )
        db.add(default_proj)

        log = ActivityLog(
            user_id=new_user.id,
            action="register",
            details="User registered and initialized workspace",
        )
        db.add(log)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    except Exception as exc:
        db.rollback()
        logger.exception(f"Registration failed for {normalized_email}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {exc}",
        )

    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user,
    }


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    normalized_email = _normalize_email(login_data.email)
    user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    try:
        log = ActivityLog(user_id=user.id, action="login", details="User logged into ResearchMate AI")
        db.add(log)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning(f"Failed to log login activity for user {user.id}: {exc}")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """One-click instant login for testing and immediate use."""
    demo_email = "researcher@example.com"
    try:
        user = db.query(User).filter(func.lower(User.email) == demo_email).first()
        if not user:
            user = User(
                email=demo_email,
                hashed_password=hash_password("ResearchMate2026!"),
                full_name="Dr. Alex Rivera",
            )
            db.add(user)
            db.flush()

            default_proj = Project(
                user_id=user.id,
                name="Generative AI & LLM Architectures",
                description="Exploration of Retrieval Augmented Generation, attention mechanisms, and multi-agent coordination",
            )
            db.add(default_proj)
            db.commit()
            db.refresh(user)
        else:
            # Ensure demo user always has at least one project
            has_project = db.query(Project).filter(Project.user_id == user.id).first()
            if not has_project:
                default_proj = Project(
                    user_id=user.id,
                    name="Generative AI & LLM Architectures",
                    description="Exploration of Retrieval Augmented Generation, attention mechanisms, and multi-agent coordination",
                )
                db.add(default_proj)
                db.commit()
    except IntegrityError:
        db.rollback()
        user = db.query(User).filter(func.lower(User.email) == demo_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Demo login failed due to database conflict.",
            )
    except Exception as exc:
        db.rollback()
        logger.exception(f"Demo login failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo login failed: {exc}",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
