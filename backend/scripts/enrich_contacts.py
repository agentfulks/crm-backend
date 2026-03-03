"""Generate daily contact enrichment datasets from the ranked fund manifest."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
REPO_ROOT = BACKEND_ROOT.parent
DELIVERABLES_DIR = REPO_ROOT / "deliverables"
DEFAULT_CONTACT_DIR = DELIVERABLES_DIR / "contact_enrichment"
DEFAULT_DAILY_QUEUE_DIR = DELIVERABLES_DIR / "daily_queue"

try:
    # Reuse generic mailbox list from ranking helpers for consistent logic
    from rank_funds import GENERIC_MAILBOXES
except ModuleNotFoundError:  # pragma: no cover - defensive fallback
    GENERIC_MAILBOXES = {
        "info",
        "hello",
        "team",
        "contact",
        "hi",
        "partners",
        "pitch",
        "invest",
    }


CONTACT_TYPES = ("direct_partner", "general_inbox", "missing")


@dataclass(slots=True)
class FundManifestEntry:
    """Normalized representation of a fund entry from the manifest."""

    rank: int
    name: str
    score: float
    hq_country: Optional[str]
    contact_email: Optional[str]
    website_url: Optional[str]
    notes: List[str]


@dataclass(slots=True)
class ContactOverride:
    """Manual override for partner details and verification."""

    fund_name: str
    contact_name: Optional[str]
    title: Optional[str]
    email: Optional[str]
    source_url: Optional[str]
    notes: Optional[str]
    verification_status: Optional[str]
    last_verified_at: Optional[str]


@dataclass(slots=True)
class ContactRow:
    """Final row emitted to the enrichment CSV."""

    fund_name: str
    rank: int
    priority: str
    score: float
    hq_country: Optional[str]
    contact_name: Optional[str]
    title: Optional[str]
    email: Optional[str]
    contact_type: str
    verification_status: str
    needs_enrichment: bool
    source_url: Optional[str]
    notes: Optional[str]


def default_paths(report_date: date) -> tuple[Path, Path, Path]:
    """Return default manifest, csv, and summary paths for the given date."""

    manifest = DEFAULT_DAILY_QUEUE_DIR / f"{report_date.isoformat()}-manifest.json"
    output_csv = DEFAULT_CONTACT_DIR / f"{report_date.isoformat()}-contacts.csv"
    summary = DEFAULT_CONTACT_DIR / f"{report_date.isoformat()}-summary.md"
    return manifest, output_csv, summary


def parse_args() -> argparse.Namespace:
    today = date.today()
    default_manifest, default_csv, default_summary = default_paths(today)
    parser = argparse.ArgumentParser(description="Generate contact enrichment dataset")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
        help="Path to ranked fund manifest JSON",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_CONTACT_DIR / "manual_overrides.csv",
        help="Path to manual overrides CSV",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=default_csv,
        help="Destination CSV path",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=default_summary,
        help="Summary markdown output path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap on number of funds to process",
    )
    return parser.parse_args()


def load_manifest(path: Path, limit: Optional[int] = None) -> tuple[List[FundManifestEntry], date]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found at {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    generated_at = payload.get("generated_at")
    report_date = _parse_manifest_date(generated_at) if generated_at else date.today()
    entries: List[FundManifestEntry] = []
    funds = payload.get("funds") or payload.get("top_funds") or []
    for entry in funds:
        fund = FundManifestEntry(
            rank=int(entry.get("rank", len(entries) + 1)),
            name=str(entry.get("name")),
            score=_extract_score(entry),
            hq_country=_extract_hq_country(entry),
            contact_email=_extract_contact_email(entry),
            website_url=_extract_website(entry),
            notes=_extract_notes(entry),
        )
        entries.append(fund)
        if limit is not None and len(entries) >= limit:
            break
    return entries, report_date


def _extract_score(entry: dict) -> float:
    score = entry.get("score")
    if isinstance(score, dict):
        return float(score.get("total", 0.0))
    try:
        return float(score or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _extract_contact_email(entry: dict) -> Optional[str]:
    contact = entry.get("contact")
    if isinstance(contact, dict):
        value = contact.get("email")
        return value or None
    return None


def _extract_hq_country(entry: dict) -> Optional[str]:
    hq = entry.get("hq")
    if isinstance(hq, dict):
        return hq.get("country") or None
    return None


def _extract_website(entry: dict) -> Optional[str]:
    urls = entry.get("urls")
    if isinstance(urls, dict):
        return urls.get("website") or None
    return None


def _extract_notes(entry: dict) -> List[str]:
    notes = entry.get("notes")
    if isinstance(notes, list):
        return [str(note) for note in notes if note]
    return []


def _parse_manifest_date(ts: str) -> date:
    try:
        dt = datetime.fromisoformat(ts)
        return dt.date()
    except ValueError:
        return date.today()


def load_overrides(path: Path) -> Dict[str, ContactOverride]:
    if not path.exists():
        return {}
    overrides: Dict[str, ContactOverride] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            fund_name = (row.get("fund_name") or "").strip()
            if not fund_name:
                continue
            override = ContactOverride(
                fund_name=fund_name,
                contact_name=_normalize_optional(row.get("contact_name")),
                title=_normalize_optional(row.get("title")),
                email=_normalize_optional(row.get("email")),
                source_url=_normalize_optional(row.get("source_url")),
                notes=_normalize_optional(row.get("notes")),
                verification_status=_normalize_optional(row.get("verification_status")),
                last_verified_at=_normalize_optional(row.get("last_verified_at")),
            )
            overrides[normalize_name(fund_name)] = override
    return overrides


def _normalize_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def normalize_name(name: str) -> str:
    return name.strip().casefold()


def determine_priority(score: float) -> str:
    if score >= 70:
        return "Priority A"
    if score >= 55:
        return "Priority B"
    return "Priority C"


def classify_contact(email: Optional[str], has_named_contact: bool) -> str:
    if not email:
        return "missing"
    local_part = email.split("@")[0].lower()
    if local_part in GENERIC_MAILBOXES:
        return "general_inbox"
    if has_named_contact:
        return "direct_partner"
    # If no named contact but email is non-generic, treat as direct to highlight higher quality
    return "direct_partner"


def build_contact_rows(
    manifest_entries: Iterable[FundManifestEntry], overrides: Dict[str, ContactOverride]
) -> List[ContactRow]:
    rows: List[ContactRow] = []
    for fund in manifest_entries:
        override = overrides.get(normalize_name(fund.name))
        contact_name = override.contact_name if override else None
        title = override.title if override else None
        email = override.email if (override and override.email) else fund.contact_email
        source_url = override.source_url if override and override.source_url else fund.website_url
        combined_notes = _combine_notes(fund.notes, override.notes if override else None)
        verification_status = _determine_verification_status(override, email)
        contact_type = classify_contact(email, bool(contact_name or title))
        needs_enrichment = contact_type != "direct_partner"
        row = ContactRow(
            fund_name=fund.name,
            rank=fund.rank,
            priority=determine_priority(fund.score),
            score=round(fund.score, 2),
            hq_country=fund.hq_country,
            contact_name=contact_name,
            title=title,
            email=email,
            contact_type=contact_type,
            verification_status=verification_status,
            needs_enrichment=needs_enrichment,
            source_url=source_url,
            notes=combined_notes,
        )
        rows.append(row)
    return rows


def _combine_notes(fund_notes: List[str], override_note: Optional[str]) -> Optional[str]:
    notes = [note for note in fund_notes if note]
    if override_note:
        notes.append(override_note)
    if not notes:
        return None
    return " | ".join(notes)


def _determine_verification_status(override: Optional[ContactOverride], email: Optional[str]) -> str:
    if override and override.verification_status:
        return override.verification_status
    if email:
        return "pending_verification"
    return "no_contact"


def write_csv(path: Path, rows: Iterable[ContactRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "fund_name",
        "rank",
        "priority",
        "score",
        "hq_country",
        "contact_name",
        "title",
        "email",
        "contact_type",
        "verification_status",
        "needs_enrichment",
        "source_url",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "fund_name": row.fund_name,
                    "rank": row.rank,
                    "priority": row.priority,
                    "score": row.score,
                    "hq_country": row.hq_country or "",
                    "contact_name": row.contact_name or "",
                    "title": row.title or "",
                    "email": row.email or "",
                    "contact_type": row.contact_type,
                    "verification_status": row.verification_status,
                    "needs_enrichment": str(row.needs_enrichment).lower(),
                    "source_url": row.source_url or "",
                    "notes": row.notes or "",
                }
            )


def write_summary(path: Path, rows: List[ContactRow], report_date: date) -> None:
    totals = _compute_totals(rows)
    lines = [
        f"# Contact Enrichment Summary — {report_date.isoformat()}",
        "",
        f"- Funds processed: {totals['total']}",
        f"- Direct partner contacts: {totals['direct']} ({totals['direct_pct']:.1f}% coverage)",
        f"- General inbox only: {totals['general']}",
        f"- Missing emails: {totals['missing']}",
        f"- Needs enrichment: {totals['needs_enrichment']}",
        "",
    ]
    needing = [row for row in rows if row.needs_enrichment]
    if needing:
        lines.append("## Funds Requiring Enrichment")
        lines.append("| Rank | Fund | Contact Type | Email |")
        lines.append("| --- | --- | --- | --- |")
        for row in needing:
            email_display = row.email or "—"
            lines.append(
                f"| {row.rank} | {row.fund_name} | {row.contact_type} | {email_display} |"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print("Summary written to", path)


def _compute_totals(rows: List[ContactRow]) -> dict:
    total = len(rows)
    direct = sum(1 for row in rows if row.contact_type == "direct_partner")
    general = sum(1 for row in rows if row.contact_type == "general_inbox")
    missing = sum(1 for row in rows if row.contact_type == "missing")
    needs = sum(1 for row in rows if row.needs_enrichment)
    direct_pct = (direct / total * 100) if total else 0.0
    return {
        "total": total,
        "direct": direct,
        "general": general,
        "missing": missing,
        "needs_enrichment": needs,
        "direct_pct": direct_pct,
    }


def main() -> None:
    args = parse_args()
    manifest_entries, manifest_date = load_manifest(args.manifest, args.limit)
    overrides = load_overrides(args.overrides)
    rows = build_contact_rows(manifest_entries, overrides)
    write_csv(args.output_csv, rows)
    write_summary(args.summary, rows, manifest_date)
    print(f"Processed {len(rows)} funds → {args.output_csv}")


if __name__ == "__main__":
    main()
