"""Routers for finding template endpoints.

Finding templates provide reusable descriptions, impacts, and recommendations
for common vulnerabilities. This router provides CRUD operations for managing
the template library.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas.finding import (
    FindingTemplateCreate,
    FindingTemplateUpdate,
    FindingTemplateOut,
)
from .users import get_current_user


router = APIRouter(prefix="/finding-templates", tags=["finding-templates"])


@router.post("/", response_model=FindingTemplateOut, status_code=status.HTTP_201_CREATED)
def create_finding_template(
    template_in: FindingTemplateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> FindingTemplateOut:
    """Create a new finding template.

    Templates can be used to quickly populate findings with standard
    descriptions, impacts, and recommendations.
    """
    template = models.FindingTemplate(
        title=template_in.title,
        category=template_in.category,
        severity_default=template_in.severity_default,
        description=template_in.description,
        impact=template_in.impact,
        recommendation=template_in.recommendation,
        cwe_id=template_in.cwe_id,
        attack_techniques=template_in.attack_techniques,
        references=template_in.references,
        created_by_id=current_user.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/", response_model=List[FindingTemplateOut])
def list_finding_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[FindingTemplateOut]:
    """List all finding templates, optionally filtering by category."""
    query = db.query(models.FindingTemplate)
    if category:
        query = query.filter(models.FindingTemplate.category == category)
    return query.order_by(models.FindingTemplate.title).all()


@router.get("/{template_id}", response_model=FindingTemplateOut)
def get_finding_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> FindingTemplateOut:
    """Retrieve a specific finding template by ID."""
    template = (
        db.query(models.FindingTemplate)
        .filter(models.FindingTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Finding template not found")
    return template


@router.patch("/{template_id}", response_model=FindingTemplateOut)
def update_finding_template(
    template_id: int,
    template_in: FindingTemplateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> FindingTemplateOut:
    """Update an existing finding template."""
    template = (
        db.query(models.FindingTemplate)
        .filter(models.FindingTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Finding template not found")

    data = template_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_finding_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a finding template."""
    template = (
        db.query(models.FindingTemplate)
        .filter(models.FindingTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Finding template not found")
    
    db.delete(template)
    db.commit()
