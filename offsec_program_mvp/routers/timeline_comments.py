"""Routers for timeline and comment endpoints.

This router provides endpoints to log events on an engagement's timeline
and to add comments to engagements.  Listing comments on findings is
left as an exercise for further development.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas import timeline as tl_schemas
from ..schemas import comment as cmt_schemas
from .users import get_current_user


router = APIRouter(tags=["timeline", "comments"])


@router.post(
    "/engagements/{engagement_id}/timeline",
    response_model=tl_schemas.TimelineEventOut,
    status_code=status.HTTP_201_CREATED,
)
def add_timeline_event(
    engagement_id: int,
    event_in: tl_schemas.TimelineEventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> tl_schemas.TimelineEventOut:
    """Log a timeline event for the given engagement."""
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    event = models.TimelineEvent(
        engagement_id=engagement_id,
        user_id=current_user.id,
        event_type=event_in.event_type,
        summary=event_in.summary,
        details=event_in.details,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get(
    "/engagements/{engagement_id}/timeline",
    response_model=List[tl_schemas.TimelineEventOut],
)
def list_timeline_events(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[tl_schemas.TimelineEventOut]:
    """Return all timeline events for an engagement ordered by creation time."""
    return (
        db.query(models.TimelineEvent)
        .filter(models.TimelineEvent.engagement_id == engagement_id)
        .order_by(models.TimelineEvent.created_at)
        .all()
    )


@router.post(
    "/engagements/{engagement_id}/comments",
    response_model=cmt_schemas.CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def add_engagement_comment(
    engagement_id: int,
    comment_in: cmt_schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> cmt_schemas.CommentOut:
    """Add a comment to an engagement."""
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    c = models.Comment(
        engagement_id=engagement_id,
        finding_id=None,
        user_id=current_user.id,
        text=comment_in.text,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c