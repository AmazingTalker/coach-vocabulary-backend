import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.word import Word


class SpeechLog(Base, UUIDMixin):
    __tablename__ = "speech_logs"

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
    recording_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    native_transcript: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    cloud_transcript: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="speech_logs")
    word_rel: Mapped["Word"] = relationship("Word", back_populates="speech_logs")
