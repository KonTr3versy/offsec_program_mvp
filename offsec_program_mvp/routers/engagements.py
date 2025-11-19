"""Routers for engagement endpoints.

Engagements are the primary objects managed by this application.
Endpoints in this router allow clients to create, list, retrieve and
update engagements as well as generate structured reports.  Nested
data such as findings, assets, timeline events and comments are
returned for the detail view and the report.
"""

from typing import List, Optional, Dict
from collections import Counter
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from .. import models
from ..schemas import engagement as schemas
from ..schemas import finding as finding_schemas
from .users import get_current_user


router = APIRouter(prefix="/engagements", tags=["engagements"])


@router.post("/", response_model=schemas.EngagementDetail, status_code=status.HTTP_201_CREATED)
def create_engagement(
    engagement_in: schemas.EngagementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.EngagementDetail:
    """Create a new engagement and return its detail representation."""
    # Ensure program year exists or create it
    program_year = (
        db.query(models.ProgramYear)
        .filter(models.ProgramYear.year == engagement_in.program_year)
        .first()
    )
    if not program_year:
        program_year = models.ProgramYear(year=engagement_in.program_year)
        db.add(program_year)
        db.flush()

    engagement = models.Engagement(
        name=engagement_in.name,
        engagement_type=engagement_in.engagement_type,
        business_unit=engagement_in.business_unit,
        start_date=engagement_in.start_date,
        end_date=engagement_in.end_date,
        scope_summary=engagement_in.scope_summary,
        objectives=engagement_in.objectives,
        methodology=engagement_in.methodology,
        status="Planned",
        program_year_id=program_year.id,
        owner_id=current_user.id,
    )
    db.add(engagement)
    db.commit()
    db.refresh(engagement)

    detail = schemas.EngagementDetail.from_orm(engagement)
    detail.program_year = program_year.year
    return detail


@router.get("/", response_model=List[schemas.EngagementSummary])
def list_engagements(
    engagement_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[schemas.EngagementSummary]:
    """List engagements, optionally filtering by type or status."""
    query = db.query(models.Engagement).options(
        joinedload(models.Engagement.program_year)
    )
    if engagement_type:
        query = query.filter(models.Engagement.engagement_type == engagement_type)
    if status_filter:
        query = query.filter(models.Engagement.status == status_filter)

    engagements = query.order_by(models.Engagement.start_date.desc().nullslast()).all()
    results: List[schemas.EngagementSummary] = []
    for e in engagements:
        summary = schemas.EngagementSummary.from_orm(e)
        summary.year = e.program_year.year if e.program_year else None
        results.append(summary)
    return results


@router.get("/{engagement_id}", response_model=schemas.EngagementDetail)
def get_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.EngagementDetail:
    """Retrieve a detailed representation of an engagement."""
    engagement = (
        db.query(models.Engagement)
        .options(
            joinedload(models.Engagement.assets).joinedload(models.EngagementAsset.asset),
            joinedload(models.Engagement.findings)
            .joinedload(models.Finding.assets)
            .joinedload(models.FindingAsset.asset),
            joinedload(models.Engagement.timeline_events),
            joinedload(models.Engagement.comments),
        )
        .filter(models.Engagement.id == engagement_id)
        .first()
    )
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    program_year = (
        db.query(models.ProgramYear)
        .filter(models.ProgramYear.id == engagement.program_year_id)
        .first()
    )
    detail = schemas.EngagementDetail.from_orm(engagement)
    detail.program_year = program_year.year if program_year else None

    # Populate nested assets
    detail.assets = [
        schemas.AssetSummary.from_orm(ea.asset) for ea in engagement.assets
    ]
    # Populate nested findings summary
    detail.findings = [
        finding_schemas.FindingSummary(
            id=f.id,
            title=f.title,
            severity=f.severity,
            status=f.status,
            remediation_status=f.remediation_status,
            due_date=f.due_date,
        )
        for f in engagement.findings
    ]
    # Timeline events and comments are returned directly via their schemas
    detail.timeline_events = [
        schemas.TimelineEventOut.from_orm(ev) for ev in engagement.timeline_events
    ]
    detail.comments = [
        schemas.CommentOut.from_orm(c) for c in engagement.comments
    ]
    return detail


@router.patch("/{engagement_id}", response_model=schemas.EngagementDetail)
def update_engagement(
    engagement_id: int,
    engagement_in: schemas.EngagementUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.EngagementDetail:
    """Update fields on an engagement.  Returns the updated detail."""
    engagement = (
        db.query(models.Engagement)
        .filter(models.Engagement.id == engagement_id)
        .first()
    )
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    data = engagement_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(engagement, field, value)
    db.commit()
    db.refresh(engagement)

    program_year = (
        db.query(models.ProgramYear)
        .filter(models.ProgramYear.id == engagement.program_year_id)
        .first()
    )
    detail = schemas.EngagementDetail.from_orm(engagement)
    detail.program_year = program_year.year if program_year else None
    return detail


@router.get("/{engagement_id}/report", response_model=schemas.EngagementReport)
def get_engagement_report(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.EngagementReport:
    """Generate a structured report for an engagement.

    The report includes metadata, scope, methodology, a summary of
    findings by severity, detailed findings with affected assets and
    any overall recommendations.  This endpoint is read-only and does
    not persist any changes.
    """
    engagement = (
        db.query(models.Engagement)
        .options(
            joinedload(models.Engagement.program_year),
            joinedload(models.Engagement.assets).joinedload(models.EngagementAsset.asset),
            joinedload(models.Engagement.findings)
            .joinedload(models.Finding.assets)
            .joinedload(models.FindingAsset.asset),
        )
        .filter(models.Engagement.id == engagement_id)
        .first()
    )
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Metadata
    metadata = schemas.EngagementReportMetadata(
        id=engagement.id,
        name=engagement.name,
        engagement_type=engagement.engagement_type,
        program_year=engagement.program_year.year
        if engagement.program_year
        else None,
        business_unit=engagement.business_unit,
        status=engagement.status,
        start_date=engagement.start_date,
        end_date=engagement.end_date,
        owner_id=engagement.owner_id,
    )

    # Scope section
    scope_assets = [
        schemas.AssetSummary.from_orm(ea.asset) for ea in engagement.assets
    ]
    scope = schemas.EngagementReportScope(
        scope_summary=engagement.scope_summary,
        objectives=engagement.objectives,
        assets=scope_assets,
    )

    # Findings summary by severity
    severity_counts = Counter(f.severity for f in engagement.findings)
    findings_summary: Dict[str, int] = dict(severity_counts)

    # Detailed findings
    findings_items: List[finding_schemas.FindingReportItem] = []
    for f in engagement.findings:
        f_assets = [
            schemas.AssetSummary.from_orm(link.asset) for link in f.assets
        ]
        item = finding_schemas.FindingReportItem(
            id=f.id,
            title=f.title,
            severity=f.severity,
            status=f.status,
            description=f.description,
            impact=f.impact,
            poc=f.poc,
            recommendation=f.recommendation,
            attack_techniques=f.attack_techniques,
            remediation_status=f.remediation_status,
            remediation_owner=f.remediation_owner,
            due_date=f.due_date,
            detection_status=f.detection_status,
            detection_notes=f.detection_notes,
            risk_accepted=f.risk_accepted,
            risk_accepted_notes=f.risk_accepted_notes,
            assets=f_assets,
        )
        findings_items.append(item)

    report = schemas.EngagementReport(
        metadata=metadata,
        executive_summary=engagement.exec_summary,
        scope=scope,
        methodology=engagement.methodology,
        findings_summary=findings_summary,
        findings=findings_items,
        recommendations_overall=engagement.recommendations_overall,
    )
    return report


@router.get("/{engagement_id}/export/csv")
def export_engagement_csv(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Export engagement findings as CSV.

    Returns a CSV file with all findings from the engagement including
    severity, status, remediation details, and affected assets.
    """
    engagement = (
        db.query(models.Engagement)
        .options(
            joinedload(models.Engagement.findings)
            .joinedload(models.Finding.assets)
            .joinedload(models.FindingAsset.asset),
        )
        .filter(models.Engagement.id == engagement_id)
        .first()
    )
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Finding ID", "Title", "Severity", "Status", "Description",
        "Impact", "Recommendation", "Remediation Status", "Remediation Owner",
        "Due Date", "Detection Status", "Risk Accepted", "Affected Assets",
        "ATT&CK Techniques"
    ])
    
    for finding in engagement.findings:
        assets_str = ", ".join([
            f"{link.asset.name} ({link.asset.identifier or 'N/A'})"
            for link in finding.assets
        ]) if finding.assets else "N/A"
        
        writer.writerow([
            finding.id,
            finding.title,
            finding.severity,
            finding.status,
            finding.description or "",
            finding.impact or "",
            finding.recommendation or "",
            finding.remediation_status,
            finding.remediation_owner or "",
            finding.due_date.isoformat() if finding.due_date else "",
            finding.detection_status or "",
            "Yes" if finding.risk_accepted else "No",
            assets_str,
            finding.attack_techniques or ""
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=engagement_{engagement_id}_findings.csv"
        }
    )


@router.get("/{engagement_id}/export/markdown")
def export_engagement_markdown(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Export engagement report as Markdown.

    Returns a formatted Markdown document suitable for documentation
    or conversion to other formats.
    """
    engagement = (
        db.query(models.Engagement)
        .options(
            joinedload(models.Engagement.program_year),
            joinedload(models.Engagement.assets).joinedload(models.EngagementAsset.asset),
            joinedload(models.Engagement.findings)
            .joinedload(models.Finding.assets)
            .joinedload(models.FindingAsset.asset),
        )
        .filter(models.Engagement.id == engagement_id)
        .first()
    )
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    md_lines = []
    
    md_lines.append(f"# {engagement.name}")
    md_lines.append("")
    md_lines.append("## Engagement Metadata")
    md_lines.append("")
    md_lines.append(f"- **Type**: {engagement.engagement_type}")
    md_lines.append(f"- **Status**: {engagement.status}")
    md_lines.append(f"- **Business Unit**: {engagement.business_unit or 'N/A'}")
    md_lines.append(f"- **Program Year**: {engagement.program_year.year if engagement.program_year else 'N/A'}")
    if engagement.start_date:
        md_lines.append(f"- **Start Date**: {engagement.start_date.isoformat()}")
    if engagement.end_date:
        md_lines.append(f"- **End Date**: {engagement.end_date.isoformat()}")
    md_lines.append("")
    
    if engagement.exec_summary:
        md_lines.append("## Executive Summary")
        md_lines.append("")
        md_lines.append(engagement.exec_summary)
        md_lines.append("")
    
    if engagement.scope_summary:
        md_lines.append("## Scope")
        md_lines.append("")
        md_lines.append(engagement.scope_summary)
        md_lines.append("")
    
    if engagement.assets:
        md_lines.append("### In-Scope Assets")
        md_lines.append("")
        for ea in engagement.assets:
            asset = ea.asset
            md_lines.append(f"- **{asset.name}** ({asset.asset_type}): {asset.identifier or 'N/A'}")
        md_lines.append("")
    
    if engagement.objectives:
        md_lines.append("## Objectives")
        md_lines.append("")
        md_lines.append(engagement.objectives)
        md_lines.append("")
    
    if engagement.methodology:
        md_lines.append("## Methodology")
        md_lines.append("")
        md_lines.append(engagement.methodology)
        md_lines.append("")
    
    md_lines.append("## Findings Summary")
    md_lines.append("")
    severity_counts = Counter(f.severity for f in engagement.findings)
    if severity_counts:
        md_lines.append("| Severity | Count |")
        md_lines.append("|----------|-------|")
        for severity in ["Critical", "High", "Medium", "Low", "Info"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                md_lines.append(f"| {severity} | {count} |")
    else:
        md_lines.append("No findings recorded.")
    md_lines.append("")
    
    if engagement.findings:
        md_lines.append("## Detailed Findings")
        md_lines.append("")
        
        for i, finding in enumerate(engagement.findings, 1):
            md_lines.append(f"### {i}. {finding.title}")
            md_lines.append("")
            md_lines.append(f"- **Severity**: {finding.severity}")
            md_lines.append(f"- **Status**: {finding.status}")
            md_lines.append(f"- **Remediation Status**: {finding.remediation_status}")
            if finding.remediation_owner:
                md_lines.append(f"- **Remediation Owner**: {finding.remediation_owner}")
            if finding.due_date:
                md_lines.append(f"- **Due Date**: {finding.due_date.isoformat()}")
            md_lines.append("")
            
            if finding.assets:
                md_lines.append("**Affected Assets:**")
                for link in finding.assets:
                    asset = link.asset
                    md_lines.append(f"- {asset.name} ({asset.identifier or 'N/A'})")
                md_lines.append("")
            
            if finding.description:
                md_lines.append("**Description:**")
                md_lines.append("")
                md_lines.append(finding.description)
                md_lines.append("")
            
            if finding.impact:
                md_lines.append("**Impact:**")
                md_lines.append("")
                md_lines.append(finding.impact)
                md_lines.append("")
            
            if finding.poc:
                md_lines.append("**Proof of Concept:**")
                md_lines.append("")
                md_lines.append(finding.poc)
                md_lines.append("")
            
            if finding.recommendation:
                md_lines.append("**Recommendation:**")
                md_lines.append("")
                md_lines.append(finding.recommendation)
                md_lines.append("")
            
            if finding.attack_techniques:
                md_lines.append(f"**ATT&CK Techniques:** {finding.attack_techniques}")
                md_lines.append("")
    
    if engagement.recommendations_overall:
        md_lines.append("## Overall Recommendations")
        md_lines.append("")
        md_lines.append(engagement.recommendations_overall)
        md_lines.append("")
    
    md_content = "\n".join(md_lines)
    
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=engagement_{engagement_id}_report.md"
        }
    )