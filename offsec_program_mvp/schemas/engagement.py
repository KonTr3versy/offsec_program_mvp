"""Pydantic schemas for engagements and engagement reports.

These models define the structure of engagement data going into and
coming out of the API.  They are used to validate requests and to
serialise engagement objects for responses and reports.
"""

from datetime import date, datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from .asset import AssetSummary
from .finding import FindingSummary, FindingReportItem
from .timeline import TimelineEventOut
from .comment import CommentOut


class EngagementBase(BaseModel):
    """Fields common to creating and updating an engagement."""

    name: str = Field(..., example="Q2 2025 PCI Network Test")
    engagement_type: str = Field(
        ..., example="Infra"
    )  # Infra, WebApp, PCI, OT, External, Purple
    business_unit: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    scope_summary: Optional[str] = None
    objectives: Optional[str] = None
    methodology: Optional[str] = None


class EngagementCreate(EngagementBase):
    """Schema for creating an engagement."""

    program_year: int = Field(..., example=2025)


class EngagementUpdate(BaseModel):
    """Schema for updating an engagement.

    All fields are optional to allow partial updates.
    """

    name: Optional[str] = None
    engagement_type: Optional[str] = None
    business_unit: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    scope_summary: Optional[str] = None
    objectives: Optional[str] = None
    methodology: Optional[str] = None
    status: Optional[str] = None
    exec_summary: Optional[str] = None
    recommendations_overall: Optional[str] = None


class EngagementSummary(BaseModel):
    """Condensed representation of an engagement for listing views."""

    id: int
    name: str
    engagement_type: str
    business_unit: Optional[str]
    status: str
    year: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        orm_mode = True


class EngagementDetail(BaseModel):
    """Detailed representation of an engagement including nested data."""

    id: int
    name: str
    engagement_type: str
    business_unit: Optional[str]
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    scope_summary: Optional[str]
    objectives: Optional[str]
    methodology: Optional[str]
    exec_summary: Optional[str]
    recommendations_overall: Optional[str]
    program_year: Optional[int]
    owner_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    assets: List[AssetSummary] = []
    findings: List[FindingSummary] = []
    timeline_events: List[TimelineEventOut] = []
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True


class EngagementReportScope(BaseModel):
    """Scope and objectives section of an engagement report."""

    scope_summary: Optional[str]
    objectives: Optional[str]
    assets: List[AssetSummary]


class EngagementReportMetadata(BaseModel):
    """Metadata for an engagement report."""

    id: int
    name: str
    engagement_type: str
    program_year: Optional[int]
    business_unit: Optional[str]
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    owner_id: Optional[int]


class EngagementReport(BaseModel):
    """Structured representation of an engagement report.

    This is used by the report endpoint to return all information
    necessary to generate a full report document.  The report contains
    metadata, executive summary, scope, methodology, a summary of
    findings by severity, a list of detailed findings and any overall
    recommendations.
    """

    metadata: EngagementReportMetadata
    executive_summary: Optional[str]
    scope: EngagementReportScope
    methodology: Optional[str]
    findings_summary: Dict[str, int]
    findings: List[FindingReportItem]
    recommendations_overall: Optional[str]