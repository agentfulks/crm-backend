"""Analytics models and metric definitions."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetricType(str, Enum):
    """Types of metrics."""
    COUNT = "count"
    RATIO = "ratio"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    DURATION = "duration"


class MetricPeriod(str, Enum):
    """Time periods for metrics."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class MetricDefinition(BaseModel):
    """Definition of a metric."""
    
    id: str
    name: str
    description: str
    type: MetricType
    unit: str
    formula: str
    data_source: str
    refresh_frequency: MetricPeriod
    

class MetricValue(BaseModel):
    """A single metric value at a point in time."""
    
    metric_id: str
    period: MetricPeriod
    period_start: date
    period_end: date
    value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# Metric Definitions
PIPELINE_METRICS = [
    MetricDefinition(
        id="total_funds",
        name="Total Funds",
        description="Total number of VC funds in database",
        type=MetricType.COUNT,
        unit="funds",
        formula="COUNT(funds)",
        data_source="funds",
        refresh_frequency=MetricPeriod.DAILY
    ),
    MetricDefinition(
        id="funds_by_source",
        name="Funds by Source",
        description="Count of funds by data source",
        type=MetricType.COUNT,
        unit="funds",
        formula="COUNT(funds) GROUP BY data_source",
        data_source="funds",
        refresh_frequency=MetricPeriod.DAILY
    ),
    MetricDefinition(
        id="funds_by_tier",
        name="Funds by Tier",
        description="Count of funds by priority tier",
        type=MetricType.COUNT,
        unit="funds",
        formula="COUNT(funds) GROUP BY priority",
        data_source="funds",
        refresh_frequency=MetricPeriod.DAILY
    ),
    MetricDefinition(
        id="avg_fund_score",
        name="Average Fund Score",
        description="Average scoring across all funds",
        type=MetricType.RATIO,
        unit="score",
        formula="AVG(score) WHERE score IS NOT NULL",
        data_source="funds",
        refresh_frequency=MetricPeriod.DAILY
    ),
    MetricDefinition(
        id="enrichment_rate",
        name="Contact Enrichment Rate",
        description="Percentage of funds with enriched contacts",
        type=MetricType.PERCENTAGE,
        unit="percent",
        formula="COUNT(funds WITH contacts) / COUNT(funds) * 100",
        data_source="contacts",
        refresh_frequency=MetricPeriod.DAILY
    ),
    MetricDefinition(
        id="avg_contacts_per_fund",
        name="Avg Contacts per Fund",
        description="Average number of contacts per fund",
        type=MetricType.COUNT,
        unit="contacts",
        formula="COUNT(contacts) / COUNT(DISTINCT fund_id)",
        data_source="contacts",
        refresh_frequency=MetricPeriod.DAILY
    ),
    MetricDefinition(
        id="outreach_response_rate",
        name="Outreach Response Rate",
        description="Percentage of outreach attempts with response",
        type=MetricType.PERCENTAGE,
        unit="percent",
        formula="COUNT(responded) / COUNT(sent) * 100",
        data_source="outreach_attempts",
        refresh_frequency=MetricPeriod.WEEKLY
    ),
    MetricDefinition(
        id="meetings_scheduled",
        name="Meetings Scheduled",
        description="Number of meetings scheduled",
        type=MetricType.COUNT,
        unit="meetings",
        formula="COUNT(meetings) WHERE status='PLANNED'",
        data_source="meetings",
        refresh_frequency=MetricPeriod.WEEKLY
    ),
    MetricDefinition(
        id="meeting_conversion_rate",
        name="Meeting Conversion Rate",
        description="Percentage of outreach resulting in meetings",
        type=MetricType.PERCENTAGE,
        unit="percent",
        formula="COUNT(meetings) / COUNT(outreach_attempts SENT) * 100",
        data_source="meetings",
        refresh_frequency=MetricPeriod.MONTHLY
    ),
    MetricDefinition(
        id="time_to_response",
        name="Time to Response",
        description="Average time from outreach to response",
        type=MetricType.DURATION,
        unit="days",
        formula="AVG(responded_at - sent_at)",
        data_source="outreach_attempts",
        refresh_frequency=MetricPeriod.WEEKLY
    ),
    MetricDefinition(
        id="funds_contacted",
        name="Funds Contacted",
        description="Number of funds with outreach attempts",
        type=MetricType.COUNT,
        unit="funds",
        formula="COUNT(DISTINCT fund_id FROM outreach_attempts)",
        data_source="outreach_attempts",
        refresh_frequency=MetricPeriod.WEEKLY
    ),
    MetricDefinition(
        id="pipeline_velocity",
        name="Pipeline Velocity",
        description="Rate of fund progression through pipeline",
        type=MetricType.COUNT,
        unit="funds/week",
        formula="COUNT(funds status changed) / 7 days",
        data_source="funds",
        refresh_frequency=MetricPeriod.WEEKLY
    ),
]


class DashboardData(BaseModel):
    """Complete dashboard data payload."""
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period: MetricPeriod
    period_start: date
    period_end: date
    
    # Overview metrics
    total_funds: int = 0
    funds_by_tier: Dict[str, int] = Field(default_factory=dict)
    funds_by_source: Dict[str, int] = Field(default_factory=dict)
    avg_fund_score: float = 0.0
    
    # Enrichment metrics
    enrichment_rate: float = 0.0
    avg_contacts_per_fund: float = 0.0
    total_contacts: int = 0
    contacts_with_email: int = 0
    email_coverage: float = 0.0
    
    # Outreach metrics
    outreach_sent: int = 0
    outreach_responded: int = 0
    response_rate: float = 0.0
    meetings_scheduled: int = 0
    meetings_completed: int = 0
    
    # Pipeline metrics
    funds_by_status: Dict[str, int] = Field(default_factory=dict)
    pipeline_velocity: float = 0.0
    time_in_stage: Dict[str, float] = Field(default_factory=dict)
    
    # Trends (last 30 days)
    trends: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)


class ETLRun(BaseModel):
    """Record of an ETL run."""
    
    run_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed
    
    # Metrics computed
    metrics_computed: List[str] = Field(default_factory=list)
    records_processed: int = 0
    
    # Errors
    errors: List[str] = Field(default_factory=list)
