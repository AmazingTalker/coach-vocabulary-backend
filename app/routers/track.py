from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.event_repository import EventRepository
from app.schemas.track import TrackRequest, TrackResponse

router = APIRouter(
    prefix="/api/track",
    tags=["track"]
)


@router.post("", response_model=TrackResponse)
def track_events(
    request: TrackRequest,
    db: Session = Depends(get_db)
):
    """
    Track user events for analytics.

    Accepts a batch of 1-20 events. Events without a device_id are rejected.
    This is a public endpoint that does not require authentication.
    """
    valid_events = []
    rejected_count = 0

    for event in request.events:
        if not event.device_id:
            rejected_count += 1
            continue

        valid_events.append({
            "device_id": event.device_id,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "exercise_session_id": event.exercise_session_id,
            "event_type": event.event_type,
            "event_name": event.event_name,
            "properties": event.properties,
            "timestamp": event.timestamp,
            "app_version": event.app_version,
            "platform": event.platform,
        })

    accepted_count = 0
    if valid_events:
        event_repo = EventRepository(db)
        accepted_count = event_repo.create_events_batch(valid_events)

    return TrackResponse(
        success=True,
        accepted=accepted_count,
        rejected=rejected_count
    )
