"""Pydantic schemas for intake requests.

Intake requests represent internal or planned requests for a penetration
test or other offensive security engagement.  They may later be
converted into engagements once they are approved.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IntakeCreate(BaseModel):
    """Schema for creating a new intake request."""

    title: str
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    business_unit: Optional[str] = None
    system_name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    desired_window: Optional[str] = None
    engagement_type: Optional[str] = None


class IntakeOut(BaseModel):
    """Schema for returning an intake request from the API."""

    id: int
    title: str
    requester_name: Optional[str]
    requester_email: Optional[str]
    business_unit: Optional[str]
    system_name: Optional[str]
    description: Optional[str]
    risk_level: Optional[str]
    desired_window: Optional[str]
    engagement_type: Optional[str]
    status: str
    linked_engagement_id: Optional[int]
    created_by_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True