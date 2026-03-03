"""Seed the funds table from the gaming_vc_list.csv."""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable, List, Optional

from rich.console import Console
from rich.table import Table

# Ensure backend package is importable when script executed directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.models.fund import Fund  # noqa: E402

console = Console()
DATA_SOURCE = "gaming_vc_list.csv"
CSV_PATH = REPO_ROOT / "data" / "raw" / DATA_SOURCE


@dataclass
class ParsedFund:
    name: str
    firm_type: Optional[str]
    hq_city: Optional[str]
    hq_region: Optional[str]
    hq_country: Optional[str]
    stage_focus: Optional[List[str]]
    check_size_min: Optional[Decimal]
    check_size_max: Optional[Decimal]
    check_size_currency: Optional[str]
    target_countries: Optional[List[str]]
    website_url: Optional[str]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    funding_requirements: Optional[str]
    overview: Optional[str]
    contact_email: Optional[str]
    data_source: str
    source_row_id: str


def parse_currency_symbol(amount_text: str | None) -> Optional[str]:
    if not amount_text:
        return None
    symbol = amount_text.strip()[0]
    return {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
    }.get(symbol)


def parse_decimal(value: str | None) -> Optional[Decimal]:
    if not value:
        return None
    try:
        cleansed = value.replace(",", "").strip()
        return Decimal(cleansed)
    except (ValueError, ArithmeticError):
        return None


def normalize_list(field: str | None) -> Optional[List[str]]:
    if not field:
        return None
    items = [item.strip() for item in field.split(",") if item.strip()]
    return items or None


def split_hq_location(value: str | None) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not value:
        return (None, None, None)
    parts = [part.strip() for part in value.split(",") if part.strip()]
    parts = parts[:3]
    while len(parts) < 3:
        parts.insert(0, None)
    if len(parts) > 3:
        parts = parts[-3:]
    city, region, country = parts if len(parts) == 3 else (None, None, None)
    return city, region, country


def parse_rows() -> Iterable[ParsedFund]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            city, region, country = split_hq_location(row.get("overview__Global HQ"))
            yield ParsedFund(
                name=row.get("title", "").strip(),
                firm_type=row.get("overview__Firm type"),
                hq_city=city,
                hq_region=region,
                hq_country=country,
                stage_focus=normalize_list(row.get("thesis__Funding stages")),
                check_size_min=parse_decimal(row.get("min")),
                check_size_max=parse_decimal(row.get("max")),
                check_size_currency=parse_currency_symbol(row.get("thesis__Check size")),
                target_countries=normalize_list(row.get("thesis__Target countries")),
                website_url=row.get("title_links_website"),
                linkedin_url=row.get("title_links_linkedin"),
                twitter_url=row.get("title_links_twitter"),
                funding_requirements=row.get("thesis__Funding requirements"),
                overview=row.get("overview__Who we are"),
                contact_email=row.get("Contact_email"),
                data_source=DATA_SOURCE,
                source_row_id=str(idx),
            )


def upsert_fund(session, parsed: ParsedFund) -> bool:
    existing: Fund | None = session.query(Fund).filter(Fund.name == parsed.name).one_or_none()
    payload = {
        "firm_type": parsed.firm_type,
        "hq_city": parsed.hq_city,
        "hq_region": parsed.hq_region,
        "hq_country": parsed.hq_country,
        "stage_focus": parsed.stage_focus,
        "check_size_min": parsed.check_size_min,
        "check_size_max": parsed.check_size_max,
        "check_size_currency": parsed.check_size_currency,
        "target_countries": parsed.target_countries,
        "website_url": parsed.website_url,
        "linkedin_url": parsed.linkedin_url,
        "twitter_url": parsed.twitter_url,
        "funding_requirements": parsed.funding_requirements,
        "overview": parsed.overview,
        "contact_email": parsed.contact_email,
        "data_source": parsed.data_source,
        "source_row_id": parsed.source_row_id,
    }
    if existing:
        for key, value in payload.items():
            setattr(existing, key, value)
        return False
    fund = Fund(name=parsed.name, **payload)
    session.add(fund)
    return True


def main() -> None:
    if not CSV_PATH.exists():
        console.print(f"[red]CSV not found at {CSV_PATH}")
        raise SystemExit(1)

    created = 0
    updated = 0
    session = SessionLocal()
    try:
        for parsed in parse_rows():
            if not parsed.name:
                continue
            is_new = upsert_fund(session, parsed)
            created += int(is_new)
            updated += int(not is_new)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    table = Table(title="Seed Funds Result")
    table.add_column("Metric")
    table.add_column("Count", justify="right")
    table.add_row("Inserted", str(created))
    table.add_row("Updated", str(updated))
    console.print(table)


if __name__ == "__main__":
    main()
