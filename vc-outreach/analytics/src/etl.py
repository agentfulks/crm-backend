"""ETL pipeline for metrics computation."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.fund import Fund
from app.models.outreach_attempt import OutreachAttempt
from app.models.meeting import Meeting

from .models import (
    DashboardData,
    ETLRun,
    MetricPeriod,
    MetricValue,
    PIPELINE_METRICS
)

logger = logging.getLogger(__name__)


class MetricsETL:
    """ETL pipeline for computing and storing metrics."""
    
    def __init__(self, session: Session):
        self.session = session
        self._run: Optional[ETLRun] = None
    
    def run_full_etl(self) -> ETLRun:
        """Run complete ETL pipeline."""
        self._run = ETLRun(
            run_id=str(uuid4()),
            started_at=datetime.utcnow()
        )
        
        logger.info(f"Starting ETL run {self._run.run_id}")
        
        try:
            # Compute all metrics
            for metric_def in PIPELINE_METRICS:
                try:
                    self._compute_metric(metric_def)
                    self._run.metrics_computed.append(metric_def.id)
                except Exception as e:
                    logger.error(f"Failed to compute {metric_def.id}: {e}")
                    self._run.errors.append(f"{metric_def.id}: {str(e)}")
            
            self._run.status = "completed"
            self._run.ended_at = datetime.utcnow()
            
            duration = (self._run.ended_at - self._run.started_at).total_seconds()
            logger.info(
                f"ETL complete: {len(self._run.metrics_computed)} metrics, "
                f"{len(self._run.errors)} errors, {duration:.1f}s"
            )
            
        except Exception as e:
            logger.error(f"ETL run failed: {e}")
            self._run.status = "failed"
            self._run.ended_at = datetime.utcnow()
            self._run.errors.append(str(e))
            raise
        
        return self._run
    
    def _compute_metric(self, metric_def) -> MetricValue:
        """Compute a single metric."""
        today = date.today()
        
        # Determine period
        if metric_def.refresh_frequency == MetricPeriod.DAILY:
            period_start = today
            period_end = today
        elif metric_def.refresh_frequency == MetricPeriod.WEEKLY:
            period_start = today - timedelta(days=today.weekday())
            period_end = period_start + timedelta(days=6)
        elif metric_def.refresh_frequency == MetricPeriod.MONTHLY:
            period_start = today.replace(day=1)
            # Next month first day - 1
            if today.month == 12:
                period_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:
            period_start = today
            period_end = today
        
        # Execute metric-specific query
        value = self._execute_metric_query(metric_def)
        
        metric_value = MetricValue(
            metric_id=metric_def.id,
            period=metric_def.refresh_frequency,
            period_start=period_start,
            period_end=period_end,
            value=value
        )
        
        return metric_value
    
    def _execute_metric_query(self, metric_def) -> float:
        """Execute query for a specific metric."""
        metric_id = metric_def.id
        
        if metric_id == "total_funds":
            result = self.session.execute(
                select(func.count(Fund.id))
            ).scalar()
            return float(result or 0)
        
        elif metric_id == "avg_fund_score":
            result = self.session.execute(
                select(func.avg(Fund.score)).where(Fund.score.isnot(None))
            ).scalar()
            return float(result or 0)
        
        elif metric_id == "enrichment_rate":
            total = self.session.execute(select(func.count(Fund.id))).scalar()
            with_contacts = self.session.execute(
                select(func.count(func.distinct(Contact.fund_id)))
            ).scalar()
            return (with_contacts / total * 100) if total else 0
        
        elif metric_id == "avg_contacts_per_fund":
            funds = self.session.execute(select(func.count(Fund.id))).scalar()
            contacts = self.session.execute(select(func.count(Contact.id))).scalar()
            return (contacts / funds) if funds else 0
        
        elif metric_id == "outreach_response_rate":
            sent = self.session.execute(
                select(func.count(OutreachAttempt.id))
                .where(OutreachAttempt.status.in_(['SENT', 'RESPONDED']))
            ).scalar()
            responded = self.session.execute(
                select(func.count(OutreachAttempt.id))
                .where(OutreachAttempt.status == 'RESPONDED')
            ).scalar()
            return (responded / sent * 100) if sent else 0
        
        elif metric_id == "meetings_scheduled":
            result = self.session.execute(
                select(func.count(Meeting.id))
                .where(Meeting.status == 'PLANNED')
            ).scalar()
            return float(result or 0)
        
        elif metric_id == "funds_by_tier":
            # This is a grouped metric, return count of all
            result = self.session.execute(
                select(func.count(Fund.id)).where(Fund.priority.isnot(None))
            ).scalar()
            return float(result or 0)
        
        return 0.0
    
    def generate_dashboard_data(
        self,
        period: MetricPeriod = MetricPeriod.DAILY
    ) -> DashboardData:
        """Generate complete dashboard data."""
        today = date.today()
        
        dashboard = DashboardData(
            period=period,
            period_start=today,
            period_end=today
        )
        
        # Fund overview
        dashboard.total_funds = self.session.execute(
            select(func.count(Fund.id))
        ).scalar() or 0
        
        # Funds by tier
        tier_counts = self.session.execute(
            select(Fund.priority, func.count(Fund.id))
            .group_by(Fund.priority)
        ).all()
        dashboard.funds_by_tier = {
            tier: count for tier, count in tier_counts if tier
        }
        
        # Funds by source
        source_counts = self.session.execute(
            select(Fund.data_source, func.count(Fund.id))
            .group_by(Fund.data_source)
        ).all()
        dashboard.funds_by_source = {
            source: count for source, count in source_counts if source
        }
        
        # Average score
        dashboard.avg_fund_score = self.session.execute(
            select(func.avg(Fund.score)).where(Fund.score.isnot(None))
        ).scalar() or 0
        
        # Enrichment metrics
        total_funds = dashboard.total_funds
        funds_with_contacts = self.session.execute(
            select(func.count(func.distinct(Contact.fund_id)))
        ).scalar() or 0
        dashboard.enrichment_rate = (
            funds_with_contacts / total_funds * 100
        ) if total_funds else 0
        
        total_contacts = self.session.execute(
            select(func.count(Contact.id))
        ).scalar() or 0
        dashboard.total_contacts = total_contacts
        dashboard.avg_contacts_per_fund = (
            total_contacts / funds_with_contacts
        ) if funds_with_contacts else 0
        
        contacts_with_email = self.session.execute(
            select(func.count(Contact.id)).where(Contact.email.isnot(None))
        ).scalar() or 0
        dashboard.contacts_with_email = contacts_with_email
        dashboard.email_coverage = (
            contacts_with_email / total_contacts * 100
        ) if total_contacts else 0
        
        # Outreach metrics
        dashboard.outreach_sent = self.session.execute(
            select(func.count(OutreachAttempt.id))
            .where(OutreachAttempt.status.in_(['SENT', 'RESPONDED']))
        ).scalar() or 0
        
        dashboard.outreach_responded = self.session.execute(
            select(func.count(OutreachAttempt.id))
            .where(OutreachAttempt.status == 'RESPONDED')
        ).scalar() or 0
        
        dashboard.response_rate = (
            dashboard.outreach_responded / dashboard.outreach_sent * 100
        ) if dashboard.outreach_sent else 0
        
        # Meetings
        dashboard.meetings_scheduled = self.session.execute(
            select(func.count(Meeting.id)).where(Meeting.status == 'PLANNED')
        ).scalar() or 0
        
        dashboard.meetings_completed = self.session.execute(
            select(func.count(Meeting.id)).where(Meeting.status == 'COMPLETED')
        ).scalar() or 0
        
        # Funds by status
        status_counts = self.session.execute(
            select(Fund.status, func.count(Fund.id)).group_by(Fund.status)
        ).all()
        dashboard.funds_by_status = {
            status: count for status, count in status_counts if status
        }
        
        return dashboard
