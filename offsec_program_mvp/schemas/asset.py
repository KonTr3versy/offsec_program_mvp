"""Pydantic schemas for assets.

These models define the structure of asset data accepted by and returned
from the API.  Assets are reusable objects representing hosts, ranges,
applications, domains, cloud accounts or OT devices.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    """Shared fields for asset creation and updates."""

    name: str = Field(..., example="NICKEL")
    asset_type: str = Field(
        ..., example="Host"
    )  # Host, IP-Range, App, Domain, URL, Cloud-Account, OT-Device
    identifier: Optional[str] = Field(None, example="10.0.76.27")
    environment: Optional[str] = Field(
        None, example="Prod"
    )  # Prod, Non-Prod, Lab, OT
    business_unit: Optional[str] = None
    criticality: Optional[str] = None
    notes: Optional[str] = None


class AssetCreate(AssetBase):
    """Schema for creating an asset."""

    pass


class AssetUpdate(BaseModel):
    """Schema for updating an existing asset.

    All fields are optional to allow partial updates.
    """

    name: Optional[str] = None
    asset_type: Optional[str] = None
    identifier: Optional[str] = None
    environment: Optional[str] = None
    business_unit: Optional[str] = None
    criticality: Optional[str] = None
    notes: Optional[str] = None


class AssetSummary(BaseModel):
    """Condensed representation of an asset for lists and references."""

    id: int
    name: str
    asset_type: str
    identifier: Optional[str]
    environment: Optional[str]
    criticality: Optional[str]

    class Config:
        orm_mode = True


class AssetDetail(AssetSummary):
    """Detailed representation of an asset including additional fields."""

    business_unit: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True