"""Normalize and export priority VC funds for CRM ingestion.

Usage examples:
    uv run python scripts/ingest_funds.py --limit 25 --output ../deliverables/daily_queue/2026-02-24-manifest.json
    python scripts/ingest_funds.py --format jsonl --output ../deliverables/daily_queue/2026-02-24-manifest.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

# Ensure we can import helpers from scripts.rank_funds when running as a script
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parents[1]
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from rank_funds import (  # type: ignore  # noqa: E402
    DEFAULT_CSV,
    ScoredFund,
    build_notes,
    format_check_range,
    read_csv,
    score_record,
)

DEFAULT_OUTPUT = REPO_ROOT.parent / "deliverables" / "daily_queue" / f"{datetime.now().date()}-manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize scored funds for ingestion")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to source CSV")
    parser.add_argument("--limit", type=int, default=25, help="Number of top funds to include")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="File path for manifest (json or jsonl)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "jsonl"],
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def normalize_entry(entry: ScoredFund, rank: int) -> dict:
    record = entry.record
    return {
        "rank": rank,
        "name": record.name,
        "firm_type": record.firm_type,
        "score": {
            "total": round(entry.total, 2),
            "breakdown": {k: round(v, 2) for k, v in entry.breakdown.items()},
        },
        "hq": {
            "city": record.hq_city,
            "region": record.hq_region,
            "country": record.hq_country,
        },
        "stage_focus": record.stage_focus,
        "check_size": {
            "min": record.check_size_min,
            "max": record.check_size_max,
            "currency": record.check_size_currency or "USD",
            "formatted": format_check_range(record),
        },
        "target_countries": record.target_countries,
        "contact": {
            "email": record.contact_email,
        },
        "urls": {
            "website": record.website_url,
            "linkedin": record.linkedin_url,
            "twitter": record.twitter_url,
        },
        "thesis": {
            "overview": record.overview,
            "requirements": record.thesis,
        },
        "keywords_hit": entry.keywords_hit,
        "overlap_ratio": round(entry.overlap_ratio, 3),
        "notes": build_notes(entry),
        "data_source": record.data_source,
        "source_row_id": record.source_row_id,
    }


def write_json(path: Path, entries: Sequence[dict], csv_path: Path) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_csv": str(csv_path),
        "count": len(entries),
        "funds": entries,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved manifest → {path}")


def write_jsonl(path: Path, entries: Iterable[dict], csv_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_csv": str(csv_path),
    }
    lines = [json.dumps(header)] + [json.dumps(entry) for entry in entries]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved manifest (jsonl) → {path}")


def main() -> None:
    args = parse_args()
    records = read_csv(args.csv)
    scored = [score_record(record) for record in records]
    scored.sort(key=lambda item: item.total, reverse=True)
    top_entries = scored[: args.limit]
    normalized = [normalize_entry(entry, idx + 1) for idx, entry in enumerate(top_entries)]

    if args.format == "jsonl":
        write_jsonl(args.output, normalized, args.csv)
    else:
        write_json(args.output, normalized, args.csv)


if __name__ == "__main__":
    main()
