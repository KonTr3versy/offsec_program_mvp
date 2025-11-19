"""Routers for intake request endpoints.

Intake requests represent initial requests for penetration tests or
engagements.  Endpoints in this router allow clients to create new
requests and list existing ones.  Conversion of intake requests into
engagements would normally be handled here as well but is omitted
from the MVP.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas import intake as schemas
from .users import get_current_user


router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/", response_model=schemas.IntakeOut, status_code=status.HTTP_201_CREATED)
def create_intake_request(
    intake_in: schemas.IntakeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.IntakeOut:
    """Create a new intake request.

    The current user will be recorded as the creator of the request.  The
    request will be given the initial status "New".
    """
    ir = models.IntakeRequest(
        title=intake_in.title,
        requester_name=intake_in.requester_name,
        requester_email=intake_in.requester_email,
        business_unit=intake_in.business_unit,
        system_name=intake_in.system_name,
        description=intake_in.description,
        risk_level=intake_in.risk_level,
        desired_window=intake_in.desired_window,
        engagement_type=intake_in.engagement_type,
        status="New",
        created_by_id=current_user.id,
    )
    db.add(ir)
    db.commit()
    db.refresh(ir)
    return ir


@router.get("/", response_model=List[schemas.IntakeOut])
def list_intake_requests(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[schemas.IntakeOut]:
    """List intake requests, optionally filtering by status."""
    query = db.query(models.IntakeRequest)
    if status_filter:
        query = query.filter(models.IntakeRequest.status == status_filter)
    return query.order_by(models.IntakeRequest.created_at.desc()).all()