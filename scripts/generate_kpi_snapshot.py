#!/usr/bin/env python3
"""Generate a KPI snapshot CSV from the daily queue + outreach logs."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DAILY_QUEUE_DIR = REPO_ROOT / "deliverables" / "daily_queue"
OUTREACH_DIR = REPO_ROOT / "deliverables" / "outreach_assets"


def load_daily_queue(run_date: str) -> tuple[list[dict[str, Any]], str | None, Path]:
    """Return funds, timestamp, and source path for a given date (YYYY-MM-DD)."""

    manifest_path = DAILY_QUEUE_DIR / f"{run_date}-manifest.json"
    fallback_path = DAILY_QUEUE_DIR / f"{run_date}.json"
    for path in (manifest_path, fallback_path):
        if path.exists():
            raw = json.loads(path.read_text())
            funds = raw.get("funds") or raw.get("top_funds") or []
            return funds, raw.get("generated_at"), path
    raise FileNotFoundError(
        f"No daily queue snapshot found for {run_date} in {DAILY_QUEUE_DIR}"
    )


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def filter_rows_by_date(rows: Iterable[dict[str, str]], field: str, run_date: str) -> list[dict[str, str]]:
    """Return rows where the ISO date (UTC) matches run_date."""

    results: list[dict[str, str]] = []
    for row in rows:
        dt = parse_date(row.get(field))
        if dt and dt.date().isoformat() == run_date:
            results.append(row)
    return results


def compute_metrics(
    funds: list[dict[str, Any]],
    sent_rows: list[dict[str, str]],
    follow_rows: list[dict[str, str]],
    run_date: str,
) -> list[dict[str, str]]:
    total_packets = len(funds)

    def fund_score(record: dict[str, Any]) -> float | None:
        raw = record.get("score")
        if isinstance(raw, dict):
            raw = raw.get("total")
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    score_values = [val for val in (fund_score(f) for f in funds) if val is not None]
    avg_score = mean(score_values) if score_values else 0.0
    min_score = min(score_values) if score_values else 0.0
    max_score = max(score_values) if score_values else 0.0

    def contact_value(record: dict[str, Any]) -> str | None:
        contact = record.get("contact") or {}
        if isinstance(contact, dict):
            if contact.get("email"):
                return str(contact["email"])
        if record.get("contact_email"):
            return str(record["contact_email"])
        return None

    contacts_ready = [f for f in funds if contact_value(f)]
    missing_contacts = [f.get("name", "Unnamed Fund") for f in funds if not contact_value(f)]
    contact_ready_pct = (len(contacts_ready) / total_packets * 100) if total_packets else 0.0

    sent_today = filter_rows_by_date(sent_rows, "target_send_at_utc", run_date)
    actually_sent_today = [row for row in sent_today if row.get("sent_at_utc")]

    follow_today = filter_rows_by_date(follow_rows, "scheduled_for_utc", run_date)
    outcomes = Counter(row.get("outcome", "").strip().upper() for row in follow_rows)

    metrics = [
        {
            "metric": "report_date",
            "value": run_date,
            "notes": "Generation date (UTC)"
        },
        {
            "metric": "packets_generated",
            "value": str(total_packets),
            "notes": "Count of funds in daily queue snapshot"
        },
        {
            "metric": "avg_score",
            "value": f"{avg_score:.2f}",
            "notes": f"Score range {min_score:.2f}–{max_score:.2f}"
        },
        {
            "metric": "contact_ready_pct",
            "value": f"{contact_ready_pct:.1f}",
            "notes": f"{len(contacts_ready)}/{total_packets} packets have verified contact emails"
        },
        {
            "metric": "missing_contact_funds",
            "value": "; ".join(missing_contacts) if missing_contacts else "None",
            "notes": "Funds lacking direct email in snapshot"
        },
        {
            "metric": "packets_with_target_send_today",
            "value": str(len(sent_today)),
            "notes": "Rows in sent_log matching target send date"
        },
        {
            "metric": "packets_sent",
            "value": str(len(actually_sent_today)),
            "notes": "Subset with sent_at_utc populated"
        },
        {
            "metric": "follow_ups_due_today",
            "value": str(len(follow_today)),
            "notes": "Follow-up log entries scheduled for today"
        },
        {
            "metric": "responses_logged",
            "value": str(outcomes.get("RESPONDED", 0)),
            "notes": "Follow-up log entries with outcome=RESPONDED"
        },
        {
            "metric": "meetings_logged",
            "value": str(outcomes.get("MEETING", 0)),
            "notes": "Follow-up log entries with outcome=MEETING"
        },
        {
            "metric": "generated_at",
            "value": datetime.now(timezone.utc).isoformat(),
            "notes": "Timestamp when KPI file created"
        },
    ]
    return metrics


def write_metrics_csv(metrics: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value", "notes"])
        writer.writeheader()
        writer.writerows(metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate KPI snapshot CSV")
    parser.add_argument("run_date", help="Date in YYYY-MM-DD format")
    parser.add_argument(
        "--output",
        help="Optional explicit output path",
        default=None,
    )
    args = parser.parse_args()

    funds, generated_at, source_path = load_daily_queue(args.run_date)
    sent_rows = load_csv_rows(OUTREACH_DIR / "sent_log.csv")
    follow_rows = load_csv_rows(OUTREACH_DIR / "follow_up_log.csv")

    metrics = compute_metrics(funds, sent_rows, follow_rows, args.run_date)
    metrics.append(
        {
            "metric": "daily_queue_source",
            "value": str(source_path.relative_to(REPO_ROOT)),
            "notes": generated_at or ""
        }
    )

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = (
            OUTREACH_DIR
            / "kpi_snapshot"
            / f"{args.run_date}-kpis.csv"
        )

    write_metrics_csv(metrics, output_path)
    print(f"Wrote KPI snapshot to {output_path}")


if __name__ == "__main__":
    main()
