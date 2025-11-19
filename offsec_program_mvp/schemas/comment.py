"""Pydantic schemas for comments.

Comments can be associated with an engagement or a specific finding and
allow users to collaborate within the application.  The creation schema
includes only the text field; the other fields are derived from the
request context.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""

    text: str


class CommentOut(BaseModel):
    """Schema for returning a comment from the API."""

    id: int
    engagement_id: Optional[int]
    finding_id: Optional[int]
    user_id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True