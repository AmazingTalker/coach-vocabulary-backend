from typing import Optional
from uuid import UUID
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


def get_user_id(x_user_id: Optional[str] = Header(None)) -> UUID:
    """Extract and validate user ID from header."""
    if not x_user_id:
        raise HTTPException(
            status_code=400,
            detail="X-User-Id header is required"
        )

    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid X-User-Id format"
        )


def get_current_user(
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Get the current user from database."""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user
