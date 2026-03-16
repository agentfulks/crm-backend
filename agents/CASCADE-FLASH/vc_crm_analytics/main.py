# ============================================================
# VC Outreach CRM Analytics Engine - FastAPI Application
# Phase 2: Core API Endpoints
# ============================================================

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, timedelta
from enum import Enum
import asyncpg
import uuid
import json
import os

app = FastAPI(
    title="VC Outreach CRM Analytics API",
    description="Real-time analytics for email engagement and Trello card velocity",
    version="1.0.0"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/vc_crm")

async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# ============================================================
# PYDANTIC MODELS
# ============================================================

class EmailEventType(str, Enum):
    OPEN = "open"
    CLICK = "click"
    BOUNCE = "bounce"
    DELIVERED = "delivered"
    SPAM_REPORT = "spam_report"
    UNSUBSCRIBE = "unsubscribe"

class EmailEventCreate(BaseModel):
    email_id: uuid.UUID
    event_type: EmailEventType
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    link_url: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)
    occurred_at: Optional[datetime] = None

class EmailEventResponse(BaseModel):
    id: uuid.UUID
    email_id: uuid.UUID
    event_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    occurred_at: datetime

class CampaignStats(BaseModel):
    campaign_id: uuid.UUID
    campaign_name: str
    total_emails: int
    unique_opens: int
    unique_clicks: int
    bounces: int
    open_rate_pct: float
    click_rate_pct: float

class CardMovementCreate(BaseModel):
    card_id: str
    from_list_id: Optional[str]
    to_list_id: str
    moved_by_user_id: Optional[str] = None
    moved_at: Optional[datetime] = None

class CardMovementResponse(BaseModel):
    id: uuid.UUID
    card_id: str
    from_list_id: Optional[str]
    to_list_id: str
    moved_at: datetime
    cycle_time_seconds: Optional[int]
    lead_time_seconds: Optional[int]

class VelocityMetrics(BaseModel):
    period_type: str
    period_start: datetime
    period_end: datetime
    cards_completed: int
    cards_started: int
    avg_cycle_time_hours: Optional[float]
    avg_lead_time_hours: Optional[float]
    throughput_per_day: float

class RealTimeMetrics(BaseModel):
    timestamp: datetime
    emails_sent_last_hour: int
    emails_opened_last_hour: int
    cards_moved_last_hour: int
    cards_completed_last_hour: int
    current_velocity_daily: float

# ============================================================
# EMAIL TRACKING ENDPOINTS
# ============================================================

@app.post("/api/v1/email-events", response_model=EmailEventResponse, status_code=201)
async def create_email_event(
    event: EmailEventCreate,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Record an email engagement event (open, click, bounce, etc.)"""
    email_row = await conn.fetchrow(
        "SELECT contact_id FROM emails WHERE id = $1", event.email_id
    )
    if not email_row:
        raise HTTPException(status_code=404, detail="Email not found")
    
    row = await conn.fetchrow(
        """
        INSERT INTO email_events 
            (email_id, contact_id, event_type, ip_address, user_agent, 
             referer, link_url, metadata, occurred_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, COALESCE($9, NOW()))
        RETURNING id, email_id, event_type, ip_address, user_agent, occurred_at
        """,
        event.email_id, email_row['contact_id'], event.event_type.value,
        event.ip_address, event.user_agent, event.referer, event.link_url,
        json.dumps(event.metadata), event.occurred_at
    )
    return EmailEventResponse(**row)


@app.get("/track/pixel/{token}.gif")
async def tracking_pixel(token: uuid.UUID, conn: asyncpg.Connection = Depends(get_db)):
    """Tracking pixel endpoint - serves 1x1 transparent GIF"""
    email_row = await conn.fetchrow(
        "SELECT id, contact_id FROM emails WHERE tracking_pixel_token = $1", token
    )
    if email_row:
        await conn.execute(
            """INSERT INTO email_events (email_id, contact_id, event_type, occurred_at)
               VALUES ($1, $2, 'open', NOW()) ON CONFLICT DO NOTHING""",
            email_row['id'], email_row['contact_id']
        )
    
    pixel_data = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return Response(content=pixel_data, media_type="image/gif")


# ============================================================
# CAMPAIGN ANALYTICS ENDPOINTS
# ============================================================

@app.get("/api/v1/campaigns/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(campaign_id: uuid.UUID, conn: asyncpg.Connection = Depends(get_db)):
    """Get real-time statistics for a campaign"""
    row = await conn.fetchrow(
        "SELECT * FROM v_campaign_stats WHERE campaign_id = $1", campaign_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignStats(**row)


@app.get("/api/v1/campaigns/{campaign_id}/timeseries")
async def get_campaign_timeseries(
    campaign_id: uuid.UUID,
    granularity: Literal["hour", "day"] = Query(default="day"),
    days: int = Query(default=30, ge=1, le=90),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get time-series data for campaign engagement"""
    rows = await conn.fetch(
        """
        SELECT 
            DATE_TRUNC($1, ee.occurred_at) AS time_bucket,
            ee.event_type,
            COUNT(DISTINCT ee.email_id) AS unique_count
        FROM email_events ee
        JOIN emails e ON e.id = ee.email_id
        WHERE e.campaign_id = $2 AND ee.occurred_at >= NOW() - ($3 || ' days')::INTERVAL
        GROUP BY DATE_TRUNC($1, ee.occurred_at), ee.event_type
        ORDER BY time_bucket DESC
        """,
        granularity, campaign_id, days
    )
    result = {}
    for row in rows:
        bucket = row['time_bucket'].isoformat()
        if bucket not in result:
            result[bucket] = {"time": bucket, "opens": 0, "clicks": 0}
        if row['event_type'] in ('open', 'click'):
            result[bucket][row['event_type'] + "s"] = row['unique_count']
    return list(result.values())


# ============================================================
# VELOCITY/CARD MOVEMENT ENDPOINTS
# ============================================================

@app.post("/api/v1/card-movements", response_model=CardMovementResponse, status_code=201)
async def create_card_movement(
    movement: CardMovementCreate,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Record a card movement between Trello lists"""
    row = await conn.fetchrow(
        """
        INSERT INTO card_movements 
            (card_id, from_list_id, to_list_id, moved_by_user_id, moved_at)
        VALUES ($1, $2, $3, $4, COALESCE($5, NOW()))
        RETURNING id, card_id, from_list_id, to_list_id, moved_at, 
                  cycle_time_seconds, lead_time_seconds
        """,
        movement.card_id, movement.from_list_id, movement.to_list_id,
        movement.moved_by_user_id, movement.moved_at
    )
    return CardMovementResponse(**row)


@app.get("/api/v1/velocity/current")
async def get_current_velocity(
    days: int = Query(default=14, ge=1, le=90),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Calculate current velocity metrics on-the-fly"""
    row = await conn.fetchrow(
        """
        SELECT 
            COUNT(DISTINCT cm.card_id) AS cards_completed,
            AVG(cm.cycle_time_seconds / 3600.0) AS avg_cycle_time_hours,
            AVG(cm.lead_time_seconds / 3600.0) AS avg_lead_time_hours,
            COUNT(DISTINCT cm.card_id)::FLOAT / NULLIF($1, 0) AS throughput_per_day
        FROM card_movements cm
        JOIN trello_lists tl ON tl.id = cm.to_list_id
        WHERE tl.list_type = 'done' AND cm.moved_at >= NOW() - ($1 || ' days')::INTERVAL
        """,
        days
    )
    return {
        "period_days": days,
        "cards_completed": row['cards_completed'] or 0,
        "avg_cycle_time_hours": round(row['avg_cycle_time_hours'] or 0, 2),
        "avg_lead_time_hours": round(row['avg_lead_time_hours'] or 0, 2),
        "throughput_per_day": round(row['throughput_per_day'] or 0, 2)
    }


@app.get("/api/v1/cards/{card_id}/history")
async def get_card_history(card_id: str, conn: asyncpg.Connection = Depends(get_db)):
    """Get full movement history for a specific card"""
    rows = await conn.fetch(
        """
        SELECT 
            cm.id, cm.from_list_id, fl.name AS from_list_name,
            cm.to_list_id, tl.name AS to_list_name,
            cm.moved_at, cm.cycle_time_seconds, cm.lead_time_seconds
        FROM card_movements cm
        LEFT JOIN trello_lists fl ON fl.id = cm.from_list_id
        JOIN trello_lists tl ON tl.id = cm.to_list_id
        WHERE cm.card_id = $1 ORDER BY cm.moved_at ASC
        """,
        card_id
    )
    return [dict(row) for row in rows]


# ============================================================
# REAL-TIME ANALYTICS ENDPOINTS
# ============================================================

@app.get("/api/v1/analytics/realtime", response_model=RealTimeMetrics)
async def get_realtime_metrics(conn: asyncpg.Connection = Depends(get_db)):
    """Get real-time analytics snapshot"""
    results = await conn.fetchrow(
        """
        WITH email_metrics AS (
            SELECT 
                COUNT(DISTINCT CASE WHEN e.sent_at >= NOW() - INTERVAL '1 hour' 
                               THEN e.id END) AS sent_last_hour,
                COUNT(DISTINCT CASE WHEN ee.event_type = 'open' 
                               AND ee.occurred_at >= NOW() - INTERVAL '1 hour'
                               THEN ee.email_id END) AS opened_last_hour
            FROM emails e
            LEFT JOIN email_events ee ON ee.email_id = e.id
        ),
        card_metrics AS (
            SELECT 
                COUNT(*) AS moved_last_hour,
                COUNT(CASE WHEN tl.list_type = 'done' THEN 1 END) AS completed_last_hour
            FROM card_movements cm
            JOIN trello_lists tl ON tl.id = cm.to_list_id
            WHERE cm.moved_at >= NOW() - INTERVAL '1 hour'
        ),
        current_velocity AS (
            SELECT COUNT(DISTINCT card_id)::FLOAT AS daily_velocity
            FROM card_movements cm
            JOIN trello_lists tl ON tl.id = cm.to_list_id
            WHERE tl.list_type = 'done' AND cm.moved_at >= NOW() - INTERVAL '1 day'
        )
        SELECT 
            em.sent_last_hour, em.opened_last_hour,
            cm.moved_last_hour, cm.completed_last_hour,
            cv.daily_velocity
        FROM email_metrics em
        CROSS JOIN card_metrics cm
        CROSS JOIN current_velocity cv
        """
    )
    return RealTimeMetrics(
        timestamp=datetime.utcnow(),
        emails_sent_last_hour=results['sent_last_hour'] or 0,
        emails_opened_last_hour=results['opened_last_hour'] or 0,
        cards_moved_last_hour=results['moved_last_hour'] or 0,
        cards_completed_last_hour=results['completed_last_hour'] or 0,
        current_velocity_daily=results['daily_velocity'] or 0.0
    )


# ============================================================
# BATCH INGESTION ENDPOINT (for high-volume event streaming)
# ============================================================

class BatchEmailEvents(BaseModel):
    events: List[EmailEventCreate]

@app.post("/api/v1/email-events/batch", status_code=202)
async def create_batch_email_events(
    batch: BatchEmailEvents,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Batch insert email events - optimized for high-volume ingestion"""
    values = []
    for event in batch.events:
        values.append((
            event.email_id, event.event_type.value,
            event.ip_address, event.user_agent,
            event.link_url, json.dumps(event.metadata or {}),
            event.occurred_at or datetime.utcnow()
        ))
    
    await conn.copy_records_to_table(
        'email_events',
        records=values,
        columns=['email_id', 'event_type', 'ip_address', 'user_agent', 
                 'link_url', 'metadata', 'occurred_at']
    )
    return {"ingested": len(values)}
