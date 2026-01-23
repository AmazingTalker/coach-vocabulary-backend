from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class TrackEventSchema(BaseModel):
    """Schema for a single tracking event."""

    device_id: Optional[str] = Field(None, max_length=100, description="Device identifier")
    user_id: Optional[str] = Field(None, max_length=100, description="User identifier")
    session_id: str = Field(..., max_length=100, description="Session identifier")
    exercise_session_id: Optional[str] = Field(None, max_length=100, description="Exercise session identifier")
    event_type: str = Field(..., max_length=50, description="Event type (e.g., screen_view, action)")
    event_name: str = Field(..., max_length=100, description="Event name (e.g., home_opened)")
    properties: Optional[dict[str, Any]] = Field(None, description="Additional event properties")
    timestamp: datetime = Field(..., description="Client-side timestamp of the event")
    app_version: str = Field(..., max_length=50, description="Application version")
    platform: str = Field(..., max_length=20, description="Platform (e.g., ios, android, web)")


class TrackRequest(BaseModel):
    """Request schema for batch event tracking."""

    events: list[TrackEventSchema] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of events to track (1-20 events per request)"
    )


class TrackResponse(BaseModel):
    """Response schema for event tracking."""

    success: bool = Field(..., description="Whether the request was processed")
    accepted: int = Field(..., description="Number of events accepted")
    rejected: int = Field(..., description="Number of events rejected")

    class Config:
        from_attributes = True
