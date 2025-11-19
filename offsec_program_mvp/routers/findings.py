"""Routers for finding endpoints.

Findings are specific issues identified during an engagement.  This
router provides endpoints for creating findings within an engagement
and listing them.  Additional endpoints such as updating findings or
linking assets could be added later.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas import finding as schemas
from .users import get_current_user


router = APIRouter(prefix="/engagements/{engagement_id}/findings", tags=["findings"])


@router.post("/", response_model=schemas.FindingDetail, status_code=status.HTTP_201_CREATED)
def create_finding(
    engagement_id: int,
    finding_in: schemas.FindingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.FindingDetail:
    """Create a new finding for a given engagement."""
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    finding = models.Finding(
        engagement_id=engagement_id,
        template_id=finding_in.template_id,
        title=finding_in.title,
        severity=finding_in.severity,
        description=finding_in.description,
        impact=finding_in.impact,
        poc=finding_in.poc,
        recommendation=finding_in.recommendation,
        attack_techniques=finding_in.attack_techniques,
        remediation_status=(
            finding_in.remediation_status or "Not-Started"
        ),
        remediation_owner=finding_in.remediation_owner,
        due_date=finding_in.due_date,
        created_by_id=current_user.id,
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


@router.get("/", response_model=List[schemas.FindingSummary])
def list_findings_for_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[schemas.FindingSummary]:
    """List all findings for the specified engagement, sorted by severity."""
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return (
        db.query(models.Finding)
        .filter(models.Finding.engagement_id == engagement_id)
        .order_by(models.Finding.severity.desc())
        .all()
    )