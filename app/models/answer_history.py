import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.word import Word


class AnswerHistory(Base, UUIDMixin):
    __tablename__ = "answer_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    word_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    word: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    exercise_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    pool: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )
    user_answer: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    response_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="answer_history")
    word_rel: Mapped["Word"] = relationship("Word", back_populates="answer_history")
