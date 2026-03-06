"""Dashboard API for analytics data."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db

from .etl import MetricsETL
from .models import DashboardData, MetricPeriod

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardResponse(BaseModel):
    """Dashboard API response."""
    success: bool
    data: Optional[DashboardData] = None
    error: Optional[str] = None


class MetricsResponse(BaseModel):
    """Metrics list response."""
    success: bool
    metrics: List[Dict[str, Any]] = []
    error: Optional[str] = None


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    period: str = Query("daily", enum=["daily", "weekly", "monthly"]),
    db: Session = Depends(get_db)
) -> DashboardResponse:
    """Get dashboard data."""
    try:
        etl = MetricsETL(db)
        data = etl.generate_dashboard_data(MetricPeriod(period))
        return DashboardResponse(success=True, data=data)
    except Exception as e:
        logger.error(f"Failed to generate dashboard: {e}")
        return DashboardResponse(success=False, error=str(e))


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    """Get list of available metrics."""
    from .models import PIPELINE_METRICS
    
    try:
        metrics = [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "type": m.type.value,
                "unit": m.unit,
                "refresh_frequency": m.refresh_frequency.value
            }
            for m in PIPELINE_METRICS
        ]
        return MetricsResponse(success=True, metrics=metrics)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return MetricsResponse(success=False, error=str(e))


@router.post("/etl/run")
async def run_etl(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Trigger ETL run."""
    try:
        etl = MetricsETL(db)
        run = etl.run_full_etl()
        
        return {
            "success": run.status == "completed",
            "run_id": run.run_id,
            "status": run.status,
            "metrics_computed": len(run.metrics_computed),
            "errors": len(run.errors),
            "duration_seconds": (
                (run.ended_at - run.started_at).total_seconds()
                if run.ended_at else None
            )
        }
    except Exception as e:
        logger.error(f"ETL run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
