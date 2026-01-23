from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class Event(Base, UUIDMixin):
    """Analytics event model for tracking user interactions."""

    __tablename__ = "events"

    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    exercise_session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)
    properties: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    server_received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    app_version: Mapped[str] = mapped_column(String(50), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        Index("ix_events_device_session", "device_id", "session_id"),
    )
