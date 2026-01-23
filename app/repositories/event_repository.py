from typing import Any

from sqlalchemy.orm import Session

from app.models.event import Event


class EventRepository:
    """Repository for event data access."""

    def __init__(self, db: Session):
        self.db = db

    def create_events_batch(self, events: list[dict[str, Any]]) -> int:
        """
        Bulk insert events into the database.

        Args:
            events: List of event dictionaries with fields matching the Event model.

        Returns:
            Number of events inserted.
        """
        if not events:
            return 0

        event_objects = [Event(**event_data) for event_data in events]
        self.db.add_all(event_objects)
        self.db.commit()

        return len(event_objects)
