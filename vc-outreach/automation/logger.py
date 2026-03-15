"""Audit trail logger for VC Intake Automation."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from dataclasses import asdict, dataclass


@dataclass
class AuditEntry:
    """Single audit log entry."""
    timestamp: str
    action: str
    card_id: str
    card_name: str
    details: Dict[str, Any]
    status: str
    error: str = ""


class AuditLogger:
    """JSONL audit logger for all automation actions."""
    
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure log directory exists."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(
        self,
        action: str,
        card_id: str,
        card_name: str,
        details: Dict[str, Any],
        status: str = "success",
        error: str = ""
    ) -> None:
        """Log an action to the audit file."""
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            card_id=card_id,
            card_name=card_name,
            details=details,
            status=status,
            error=error
        )
        
        with open(self.log_path, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")
    
    def log_card_processed(
        self,
        card_id: str,
        card_name: str,
        original_list: str,
        target_list: str,
        priority_score: str,
        enrichment_data: Dict[str, Any]
    ) -> None:
        """Log a successful card processing."""
        self.log(
            action="process_card",
            card_id=card_id,
            card_name=card_name,
            details={
                "original_list": original_list,
                "target_list": target_list,
                "priority_score": priority_score,
                "enrichment": enrichment_data
            },
            status="success"
        )
    
    def log_error(
        self,
        action: str,
        card_id: str,
        card_name: str,
        error: str,
        details: Dict[str, Any] = None
    ) -> None:
        """Log an error."""
        self.log(
            action=action,
            card_id=card_id,
            card_name=card_name,
            details=details or {},
            status="error",
            error=error
        )
    
    def log_skipped(
        self,
        card_id: str,
        card_name: str,
        reason: str
    ) -> None:
        """Log a skipped card."""
        self.log(
            action="skip_card",
            card_id=card_id,
            card_name=card_name,
            details={"reason": reason},
            status="skipped"
        )
    
    def read_logs(self, limit: int = None) -> list:
        """Read log entries (most recent first)."""
        if not self.log_path.exists():
            return []
        
        entries = []
        with open(self.log_path, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        entries.reverse()
        if limit:
            entries = entries[:limit]
        return entries
