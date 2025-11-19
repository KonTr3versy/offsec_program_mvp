"""Pydantic schemas for timeline events.

Timeline events capture important actions or status changes in an
engagement.  They can be created by users or automatically logged by
the application.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimelineEventCreate(BaseModel):
    """Schema for creating a timeline event."""

    event_type: str
    summary: str
    details: Optional[str] = None


class TimelineEventOut(BaseModel):
    """Schema for returning a timeline event from the API."""

    id: int
    engagement_id: int
    user_id: Optional[int]
    event_type: str
    summary: str
    details: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True