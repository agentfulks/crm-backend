"""Scheduler for automated sync jobs."""
from __future__ import annotations

import logging
import signal
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    """Represents a scheduled job."""
    name: str
    cron_expression: str
    callback: Callable
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True


class CronScheduler:
    """
    Simple cron-like scheduler for automation jobs.
    
    Supports standard cron expressions with minute granularity.
    """
    
    def __init__(self):
        self.jobs: Dict[str, ScheduledJob] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def add_job(
        self,
        name: str,
        cron_expression: str,
        callback: Callable,
        enabled: bool = True
    ) -> ScheduledJob:
        """
        Add a job to the scheduler.
        
        Args:
            name: Job identifier
            cron_expression: Cron expression (e.g., "0 6 * * *" for 6am daily)
            callback: Function to call when job runs
            enabled: Whether job is enabled
        """
        job = ScheduledJob(
            name=name,
            cron_expression=cron_expression,
            callback=callback,
            enabled=enabled
        )
        self.jobs[name] = job
        self._calculate_next_run(job)
        logger.info(f"Added job '{name}' with schedule: {cron_expression}")
        return job
    
    def remove_job(self, name: str) -> bool:
        """Remove a job from the scheduler."""
        if name in self.jobs:
            del self.jobs[name]
            return True
        return False
    
    def enable_job(self, name: str) -> bool:
        """Enable a job."""
        if name in self.jobs:
            self.jobs[name].enabled = True
            return True
        return False
    
    def disable_job(self, name: str) -> bool:
        """Disable a job."""
        if name in self.jobs:
            self.jobs[name].enabled = False
            return True
        return False
    
    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self._running and not self._stop_event.is_set():
            now = datetime.now()
            
            for job in self.jobs.values():
                if not job.enabled:
                    continue
                
                if job.next_run and now >= job.next_run:
                    try:
                        logger.info(f"Running job: {job.name}")
                        job.callback()
                        job.last_run = now
                    except Exception as e:
                        logger.error(f"Job {job.name} failed: {e}")
                    finally:
                        self._calculate_next_run(job)
            
            # Sleep for 1 minute between checks
            self._stop_event.wait(60)
    
    def _calculate_next_run(self, job: ScheduledJob) -> None:
        """Calculate next run time from cron expression."""
        # Simple cron parser - supports: minute hour day month weekday
        parts = job.cron_expression.split()
        
        if len(parts) != 5:
            logger.error(f"Invalid cron expression: {job.cron_expression}")
            return
        
        minute_str, hour_str, day_str, month_str, weekday_str = parts
        
        now = datetime.now()
        next_run = now.replace(second=0, microsecond=0)
        
        # If time already passed today, start from tomorrow
        if next_run.minute > int(minute_str) or (
            next_run.minute == int(minute_str) and next_run.hour >= int(hour_str)
        ):
            next_run = next_run.replace(day=next_run.day + 1)
        
        # Set hour and minute
        try:
            next_run = next_run.replace(hour=int(hour_str), minute=int(minute_str))
        except ValueError:
            # Handle day overflow
            from datetime import timedelta
            next_run = next_run + timedelta(days=1)
            next_run = next_run.replace(hour=int(hour_str), minute=int(minute_str))
        
        job.next_run = next_run
        logger.debug(f"Job '{job.name}' next run: {next_run}")
    
    def get_status(self) -> List[Dict]:
        """Get status of all jobs."""
        return [
            {
                "name": job.name,
                "enabled": job.enabled,
                "schedule": job.cron_expression,
                "last_run": job.last_run.isoformat() if job.last_run else None,
                "next_run": job.next_run.isoformat() if job.next_run else None,
            }
            for job in self.jobs.values()
        ]


# Global scheduler instance
_scheduler: Optional[CronScheduler] = None


def get_scheduler() -> CronScheduler:
    """Get or create global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = CronScheduler()
    return _scheduler


def setup_sync_schedule(
    sync_callback: Callable,
    cron_expression: str = "0 6 * * *"
) -> None:
    """Set up daily sync schedule."""
    scheduler = get_scheduler()
    scheduler.add_job("daily_sync", cron_expression, sync_callback)


def run_scheduler_forever() -> None:
    """Run scheduler until interrupted."""
    scheduler = get_scheduler()
    scheduler.start()
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    
    # Keep main thread alive
    while scheduler._running:
        time.sleep(1)
