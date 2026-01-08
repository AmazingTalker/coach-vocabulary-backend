import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.word import Word


class WordProgress(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "word_progress"

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
    pool: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="P0",
        index=True
    )
    learned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_practice_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    next_available_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    is_in_review_phase: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    review_completed_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="word_progress")
    word: Mapped["Word"] = relationship("Word", back_populates="word_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "word_id", name="uq_user_word"),
    )
