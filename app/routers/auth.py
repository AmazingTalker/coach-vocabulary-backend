from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.repositories.user_repository import UserRepository
from app.repositories.word_repository import WordRepository
from app.repositories.progress_repository import ProgressRepository

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login or auto-register.
    If username exists, return the user.
    If not, create a new user and initialize word progress.
    """
    user_repo = UserRepository(db)
    word_repo = WordRepository(db)
    progress_repo = ProgressRepository(db)

    user, is_new = user_repo.get_or_create(request.username)

    # Initialize progress for new users
    if is_new:
        words = word_repo.get_all()
        progress_repo.initialize_user_progress(user.id, words)

    return LoginResponse(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
        is_new_user=is_new,
    )
