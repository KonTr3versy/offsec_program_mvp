"""Routers for asset endpoints.

Assets represent the targets of penetration tests.  They can be
created independently and later associated with engagements.  This
router provides endpoints to create new assets and list existing ones.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas import asset as schemas
from .users import get_current_user


router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/", response_model=schemas.AssetDetail, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_in: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.AssetDetail:
    """Create a new asset.

    The created asset is returned with its detail view.
    """
    asset = models.Asset(
        name=asset_in.name,
        asset_type=asset_in.asset_type,
        identifier=asset_in.identifier,
        environment=asset_in.environment,
        business_unit=asset_in.business_unit,
        criticality=asset_in.criticality,
        notes=asset_in.notes,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/", response_model=List[schemas.AssetSummary])
def list_assets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[schemas.AssetSummary]:
    """List all assets."""
    return db.query(models.Asset).order_by(models.Asset.name).all()