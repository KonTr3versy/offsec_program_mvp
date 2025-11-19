"""Pydantic schemas for findings.

Findings represent specific vulnerabilities or issues discovered during an
engagement.  They are tied to an engagement and may reference a
standard template.  The schemas here define the data structure for
creating, updating and returning findings via the API.
"""

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field

from .asset import AssetSummary
from .comment import CommentOut


class FindingBase(BaseModel):
    """Fields common to creating or updating a finding."""

    title: str = Field(..., example="Unauthenticated Telnet Access")
    severity: str = Field(..., example="High")  # Info, Low, Medium, High, Critical
    description: Optional[str] = None
    impact: Optional[str] = None
    poc: Optional[str] = None
    recommendation: Optional[str] = None
    attack_techniques: Optional[str] = Field(
        None, example="T1040,T1046"
    )  # ATT&CK technique IDs


class FindingCreate(FindingBase):
    """Schema for creating a new finding."""

    template_id: Optional[int] = None
    remediation_status: Optional[str] = "Not-Started"
    remediation_owner: Optional[str] = None
    due_date: Optional[date] = None


class FindingUpdate(BaseModel):
    """Schema for updating an existing finding.

    Each field is optional to allow partial updates.
    """

    title: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[str] = None
    poc: Optional[str] = None
    recommendation: Optional[str] = None
    attack_techniques: Optional[str] = None
    remediation_status: Optional[str] = None
    remediation_owner: Optional[str] = None
    due_date: Optional[date] = None
    detection_status: Optional[str] = None
    detection_notes: Optional[str] = None
    risk_accepted: Optional[bool] = None
    risk_accepted_notes: Optional[str] = None


class FindingSummary(BaseModel):
    """Condensed representation of a finding for lists."""

    id: int
    title: str
    severity: str
    status: str
    remediation_status: str
    due_date: Optional[date]

    class Config:
        orm_mode = True


class FindingDetail(BaseModel):
    """Detailed representation of a finding including related data."""

    id: int
    engagement_id: int
    template_id: Optional[int]
    title: str
    severity: str
    status: str
    description: Optional[str]
    impact: Optional[str]
    poc: Optional[str]
    recommendation: Optional[str]
    attack_techniques: Optional[str]
    remediation_status: str
    remediation_owner: Optional[str]
    due_date: Optional[date]
    detection_status: Optional[str]
    detection_notes: Optional[str]
    risk_accepted: bool
    risk_accepted_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_id: Optional[int]

    assets: List[AssetSummary] = []
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True


class FindingReportItem(BaseModel):
    """Representation of a finding within an engagement report.

    This schema contains all fields needed to generate the report as
    well as a list of assets affected by the finding.
    """

    id: int
    title: str
    severity: str
    status: str
    description: Optional[str]
    impact: Optional[str]
    poc: Optional[str]
    recommendation: Optional[str]
    attack_techniques: Optional[str]
    remediation_status: str
    remediation_owner: Optional[str]
    due_date: Optional[date]
    detection_status: Optional[str]
    detection_notes: Optional[str]
    risk_accepted: bool
    risk_accepted_notes: Optional[str]
    assets: List[AssetSummary]


class FindingTemplateBase(BaseModel):
    """Fields common to creating or updating a finding template."""

    title: str = Field(..., example="SQL Injection")
    category: Optional[str] = Field(None, example="Web")
    severity_default: Optional[str] = Field(None, example="High")
    description: Optional[str] = None
    impact: Optional[str] = None
    recommendation: Optional[str] = None
    cwe_id: Optional[str] = Field(None, example="CWE-89")
    attack_techniques: Optional[str] = Field(None, example="T1190")
    references: Optional[str] = None


class FindingTemplateCreate(FindingTemplateBase):
    """Schema for creating a new finding template."""
    pass


class FindingTemplateUpdate(BaseModel):
    """Schema for updating a finding template."""

    title: Optional[str] = None
    category: Optional[str] = None
    severity_default: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[str] = None
    recommendation: Optional[str] = None
    cwe_id: Optional[str] = None
    attack_techniques: Optional[str] = None
    references: Optional[str] = None


class FindingTemplateOut(BaseModel):
    """Schema for returning a finding template."""

    id: int
    title: str
    category: Optional[str]
    severity_default: Optional[str]
    description: Optional[str]
    impact: Optional[str]
    recommendation: Optional[str]
    cwe_id: Optional[str]
    attack_techniques: Optional[str]
    references: Optional[str]
    created_by_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True