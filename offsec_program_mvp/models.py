"""SQLAlchemy ORM models for the Offensive Security Program MVP.

These classes define the shape of the database tables and their
relationships.  Each model corresponds to a table in the database and
defines columns, types and relationships.  Changes to these classes
should be accompanied by migrations when using a production database.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    """Represents an application user.

    Users can have roles such as red, blue, manager or admin. Passwords
    should be stored as a hashed value.  For the MVP this table is very
    simple; future improvements might include SSO integration or
    additional profile information.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    role = Column(String(20), nullable=False, default="red")  # red, blue, manager, admin
    password_hash = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ProgramYear(Base):
    """Top-level container for all engagements in a given year.

    A program year can optionally have a theme and objectives which can
    summarise the goals of the offensive security program for that year.
    """

    __tablename__ = "program_years"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, unique=True)
    theme = Column(Text)
    objectives = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    engagements = relationship("Engagement", back_populates="program_year")


class IntakeRequest(Base):
    """Represents a request for an engagement.

    Intake requests originate from internal stakeholders or are derived
    from planned program milestones.  They can be converted into
    engagements once approved.
    """

    __tablename__ = "intake_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    requester_name = Column(String(100))
    requester_email = Column(String(100))
    business_unit = Column(String(100))
    system_name = Column(String(200))
    description = Column(Text)
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    desired_window = Column(String(200))
    engagement_type = Column(String(50))  # Infra, WebApp, PCI, OT, External, Purple
    status = Column(String(50), nullable=False, default="New")  # New, Reviewed, Approved, Rejected, Converted

    linked_engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    created_by = relationship("User")
    linked_engagement = relationship(
        "Engagement", back_populates="intake_request", uselist=False
    )


class Engagement(Base):
    """Represents a concrete offensive security engagement.

    Each engagement is tied to a program year and may have an associated
    intake request.  An engagement contains the scope, objectives,
    methodology and associated findings, assets, timeline events and
    comments.
    """

    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    program_year_id = Column(Integer, ForeignKey("program_years.id"))
    engagement_type = Column(
        String(50), nullable=False
    )  # Infra, WebApp, PCI, OT, External, Purple
    business_unit = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(
        String(50), nullable=False, default="Planned"
    )  # Planned, In-Progress, Reporting, Completed, On-Hold
    start_date = Column(Date)
    end_date = Column(Date)
    scope_summary = Column(Text)
    objectives = Column(Text)
    methodology = Column(Text)
    exec_summary = Column(Text)
    recommendations_overall = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program_year = relationship("ProgramYear", back_populates="engagements")
    owner = relationship("User")
    intake_request = relationship(
        "IntakeRequest", back_populates="linked_engagement"
    )
    assets = relationship(
        "EngagementAsset",
        back_populates="engagement",
        cascade="all, delete-orphan",
    )
    findings = relationship(
        "Finding", back_populates="engagement", cascade="all, delete-orphan"
    )
    timeline_events = relationship(
        "TimelineEvent",
        back_populates="engagement",
        cascade="all, delete-orphan",
    )
    comments = relationship(
        "Comment", back_populates="engagement", cascade="all, delete-orphan"
    )


class Asset(Base):
    """Represents an asset that can be in scope for engagements.

    Assets can be hosts, IP ranges, applications, domains, cloud accounts or
    OT devices.  They are reusable across engagements so that tests on the
    same host can be tracked over time.
    """

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    asset_type = Column(
        String(50), nullable=False
    )  # Host, IP-Range, App, Domain, URL, Cloud-Account, OT-Device
    identifier = Column(String(255))
    environment = Column(String(50))  # Prod, Non-Prod, Lab, OT
    business_unit = Column(String(100))
    criticality = Column(String(20))  # Low, Medium, High
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    engagements = relationship(
        "EngagementAsset",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
    finding_links = relationship(
        "FindingAsset",
        back_populates="asset",
        cascade="all, delete-orphan",
    )


class EngagementAsset(Base):
    """Association table linking engagements and assets.

    This table allows an asset to be linked to multiple engagements and
    records the role of the asset within the engagement (primary,
    supporting, etc.).
    """

    __tablename__ = "engagement_assets"

    id = Column(Integer, primary_key=True)
    engagement_id = Column(
        Integer, ForeignKey("engagements.id"), nullable=False
    )
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    role = Column(String(50))  # Primary, Supporting, etc.
    notes = Column(Text)

    # Relationships
    engagement = relationship("Engagement", back_populates="assets")
    asset = relationship("Asset", back_populates="engagements")


class FindingTemplate(Base):
    """Library entry for reusable finding descriptions.

    Finding templates contain canonical descriptions, impacts and
    recommendations that can be copied into new findings when they are
    created.  They are not linked directly to an engagement.
    """

    __tablename__ = "finding_templates"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category = Column(
        String(50)
    )  # Network, Web, Cloud, OT, etc.
    severity_default = Column(String(20))  # Info, Low, Medium, High, Critical
    description = Column(Text)
    impact = Column(Text)
    recommendation = Column(Text)
    cwe_id = Column(String(50))
    attack_techniques = Column(Text)  # comma-separated IDs
    references = Column(Text)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    created_by = relationship("User")


class Finding(Base):
    """Represents an instance of a finding in an engagement.

    A finding may optionally reference a template and contains its own
    description, PoC, recommendation and impact.  Additional fields
    track remediation and detection status.
    """

    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("finding_templates.id"), nullable=True)

    title = Column(String(200), nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(
        String(50), nullable=False, default="New"
    )  # New, Validated, Exploited, Mitigated, False-Positive
    description = Column(Text)
    impact = Column(Text)
    poc = Column(Text)
    recommendation = Column(Text)
    attack_techniques = Column(Text)  # ATT&CK IDs

    remediation_status = Column(String(50), nullable=False, default="Not-Started")
    remediation_owner = Column(String(100))
    due_date = Column(Date)

    detection_status = Column(String(50))  # Not-Logged, Logged-Not-Alerted, Alerted, Verified-Alert
    detection_notes = Column(Text)

    risk_accepted = Column(Boolean, default=False, nullable=False)
    risk_accepted_notes = Column(Text)

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    engagement = relationship("Engagement", back_populates="findings")
    template = relationship("FindingTemplate")
    created_by = relationship("User")
    assets = relationship(
        "FindingAsset", back_populates="finding", cascade="all, delete-orphan"
    )
    comments = relationship(
        "Comment", back_populates="finding", cascade="all, delete-orphan"
    )


class FindingAsset(Base):
    """Association table linking findings to the assets they affect."""

    __tablename__ = "finding_assets"

    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Relationships
    finding = relationship("Finding", back_populates="assets")
    asset = relationship("Asset", back_populates="finding_links")


class TimelineEvent(Base):
    """Represents a significant event in an engagement's timeline."""

    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)
    summary = Column(String(255), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    engagement = relationship("Engagement", back_populates="timeline_events")
    user = relationship("User")


class Comment(Base):
    """Represents a comment on an engagement or a finding."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    engagement = relationship("Engagement", back_populates="comments")
    finding = relationship("Finding", back_populates="comments")
    user = relationship("User")