"""Score and rank funds for the VC outreach daily queue.

Usage:
    uv run python scripts/rank_funds.py --top 5 --output ../deliverables/daily_queue/2026-02-24.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import urlparse

try:
    from rich.console import Console
    from rich.table import Table
except ModuleNotFoundError:  # fallback when Rich isn't installed in sandbox
    Console = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]

CONSOLE = Console() if Console else None
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO_ROOT / "data" / "raw" / "gaming_vc_list.csv"
TARGET_MIN = 500_000
TARGET_MAX = 5_000_000
STAGE_WEIGHTS = {
    "pre-seed": 10.0,
    "pre seed": 10.0,
    "seed": 9.0,
    "series a": 6.0,
    "series b": 4.0,
}
TOP_HQ_COUNTRIES = {"united states", "usa", "canada", "united kingdom", "uk"}
EU_TIER_COUNTRIES = {
    "germany",
    "france",
    "netherlands",
    "sweden",
    "finland",
    "denmark",
    "norway",
    "ireland",
    "spain",
    "portugal",
    "belgium",
    "switzerland",
    "austria",
}
SECTOR_KEYWORDS = {
    "gaming",
    "game",
    "games",
    "interactive",
    "esports",
    "ai",
    "artificial intelligence",
    "devtools",
    "developer",
    "infrastructure",
    "immersive",
    "xr",
    "synthetic reality",
    "content platform",
}
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
FUND_KEYWORDS = {
    "capital",
    "ventures",
    "partners",
    "fund",
    "vc",
    "labs",
    "investment",
    "investments",
    "holdings",
}
PERSON_TITLES = {
    "partner",
    "managing partner",
    "venture partner",
    "general partner",
    "managing director",
    "director",
    "principal",
    "co-founder",
    "founder",
    "angel",
    "advisor",
    "operator",
    "executive",
}
MANUAL_BOOSTS = {
    "bitkraft ventures": 10.0,
    "konvoy ventures": 8.0,
    "variant": 12.0,
    "collab+currency": 8.0,
    "mechanism capital": 8.0,
}
MAX_FACTOR_SCORES = {
    "stage": 25.0,
    "check_size": 15.0,
    "geo": 10.0,
    "sector": 25.0,
    "warmth": 15.0,
    "contact": 10.0,
    "penalty": 5.0,
}


@dataclass
class FundRecord:
    name: str
    firm_type: Optional[str]
    stage_focus: list[str]
    check_size_min: Optional[float]
    check_size_max: Optional[float]
    check_size_currency: Optional[str]
    hq_city: Optional[str]
    hq_region: Optional[str]
    hq_country: Optional[str]
    target_countries: list[str]
    overview: str
    thesis: str
    website_url: Optional[str]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    contact_email: Optional[str]
    data_source: Optional[str]
    source_row_id: Optional[str]


@dataclass
class ScoredFund:
    record: FundRecord
    total: float
    breakdown: Dict[str, float]
    keywords_hit: list[str]
    overlap_ratio: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score and rank VC funds")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to source CSV")
    parser.add_argument("--top", type=int, default=5, help="How many funds to return")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write JSON output",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[FundRecord]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found at {path}")
    records: list[FundRecord] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("title") or "").strip()
            if not name:
                continue
            city, region, country = split_hq(row.get("overview__Global HQ"))
            record = FundRecord(
                name=name,
                firm_type=(row.get("overview__Firm type") or "").strip() or None,
                stage_focus=parse_list(row.get("thesis__Funding stages")),
                check_size_min=parse_float(row.get("min")),
                check_size_max=parse_float(row.get("max")),
                check_size_currency=parse_currency_symbol(row.get("thesis__Check size")),
                hq_city=city,
                hq_region=region,
                hq_country=country,
                target_countries=parse_list(row.get("thesis__Target countries")),
                overview=(row.get("overview__Who we are") or "").strip(),
                thesis=(row.get("thesis__Funding requirements") or "").strip(),
                website_url=(row.get("title_links_website") or "").strip() or None,
                linkedin_url=(row.get("title_links_linkedin") or "").strip() or None,
                twitter_url=(row.get("title_links_twitter") or "").strip() or None,
                contact_email=(row.get("Contact_email") or "").strip() or None,
                data_source=row.get("data_source") or "gaming_vc_list.csv",
                source_row_id=row.get("source_row_id") or None,
            )
            if is_fund(record):
                records.append(record)
    return records


def parse_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_list(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_currency_symbol(text_value: Optional[str]) -> Optional[str]:
    if not text_value:
        return None
    symbol = text_value.strip()[0]
    return {"$": "USD", "€": "EUR", "£": "GBP"}.get(symbol)


def split_hq(value: Optional[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not value:
        return (None, None, None)
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        return (None, None, None)
    if len(parts) == 1:
        return (None, None, parts[0])
    if len(parts) == 2:
        return (parts[0], None, parts[1])
    return (parts[0], parts[1], parts[2])


def is_fund(record: FundRecord) -> bool:
    name_text = record.name.lower()
    meta_text = (record.firm_type or "").lower()
    name_has_keyword = any(keyword in name_text for keyword in FUND_KEYWORDS)
    if not name_has_keyword:
        if any(title in meta_text for title in PERSON_TITLES):
            return False
    meta_has_keyword = any(keyword in meta_text for keyword in FUND_KEYWORDS)
    return name_has_keyword or meta_has_keyword


def score_record(record: FundRecord) -> ScoredFund:
    breakdown: Dict[str, float] = {}
    stage_score = sum(STAGE_WEIGHTS.get(stage.lower(), 0.0) for stage in record.stage_focus)
    breakdown["stage"] = min(stage_score, MAX_FACTOR_SCORES["stage"])

    overlap_ratio, check_score = check_size_component(record)
    breakdown["check_size"] = check_score

    breakdown["geo"] = geo_component(record)

    keywords_hit, sector_score = sector_component(record)
    breakdown["sector"] = sector_score

    boost = MANUAL_BOOSTS.get(record.name.lower(), 0.0)
    breakdown["warmth"] = min(boost, MAX_FACTOR_SCORES["warmth"])

    breakdown["contact"] = contact_component(record)

    penalty = penalty_component(record)
    breakdown["penalty"] = min(penalty, MAX_FACTOR_SCORES["penalty"])

    total = (
        breakdown["stage"]
        + breakdown["check_size"]
        + breakdown["geo"]
        + breakdown["sector"]
        + breakdown["warmth"]
        + breakdown["contact"]
        - breakdown["penalty"]
    )
    total = max(0.0, min(100.0, total))
    return ScoredFund(record=record, total=total, breakdown=breakdown, keywords_hit=keywords_hit, overlap_ratio=overlap_ratio)


def check_size_component(record: FundRecord) -> tuple[float, float]:
    min_val = record.check_size_min
    max_val = record.check_size_max
    if min_val is None and max_val is None:
        return (0.0, 0.0)
    rng_min = min_val if min_val is not None else max_val
    rng_max = max_val if max_val is not None else min_val
    if rng_min is None or rng_max is None:
        return (0.0, 0.0)
    if rng_max < rng_min:
        rng_min, rng_max = rng_max, rng_min
    overlap_min = max(rng_min, TARGET_MIN)
    overlap_max = min(rng_max, TARGET_MAX)
    overlap = max(0.0, overlap_max - overlap_min)
    base = TARGET_MAX - TARGET_MIN
    ratio = overlap / base if base else 0.0
    score = min(MAX_FACTOR_SCORES["check_size"], ratio * MAX_FACTOR_SCORES["check_size"])
    return (ratio, score)


def geo_component(record: FundRecord) -> float:
    score = 0.0
    country = (record.hq_country or "").lower()
    if country in TOP_HQ_COUNTRIES:
        score += 6.0
    elif country in EU_TIER_COUNTRIES:
        score += 4.0
    targets = {c.lower() for c in record.target_countries}
    if targets & TOP_HQ_COUNTRIES:
        score += 2.0
    elif targets & EU_TIER_COUNTRIES:
        score += 1.0
    return min(score, MAX_FACTOR_SCORES["geo"])


def sector_component(record: FundRecord) -> tuple[list[str], float]:
    blob = f"{record.overview}\n{record.thesis}".lower()
    hits: list[str] = []
    for keyword in SECTOR_KEYWORDS:
        if keyword and keyword in blob:
            hits.append(keyword)
    unique_hits = list(dict.fromkeys(hits))
    score = min(len(unique_hits) * 4.0, MAX_FACTOR_SCORES["sector"])
    return (unique_hits, score)


def contact_component(record: FundRecord) -> float:
    if not record.contact_email:
        return 0.0
    email = record.contact_email.lower()
    score = 6.0
    domain_match = False
    try:
        email_domain = email.split("@")[-1]
        website_domain = urlparse(record.website_url or "").netloc
        website_domain = website_domain.replace("www.", "") if website_domain else ""
        if website_domain and email_domain.endswith(website_domain):
            score += 2.0
            domain_match = True
    except Exception:
        domain_match = False
    local_part = email.split("@")[0]
    if local_part not in GENERIC_MAILBOXES or domain_match:
        score += 2.0
    return min(score, MAX_FACTOR_SCORES["contact"])


def penalty_component(record: FundRecord) -> float:
    penalty = 0.0
    if not record.stage_focus:
        penalty += 2.0
    if not record.hq_country:
        penalty += 1.0
    if not record.contact_email:
        penalty += 2.0

    # Penalize mega-funds whose maximum check size far exceeds the target band
    max_check = record.check_size_max or record.check_size_min
    if max_check and max_check > TARGET_MAX * 2:
        penalty += min(5.0, ((max_check - (TARGET_MAX * 2)) / (TARGET_MAX * 4)) * 5.0)

    if any("growth" in (stage or "").lower() for stage in record.stage_focus):
        penalty += 1.0

    return min(penalty, MAX_FACTOR_SCORES["penalty"])


def print_table(scored: Sequence[ScoredFund], top_n: int) -> None:
    if not (CONSOLE and Table):
        print(f"Top {top_n} Funds by Score")
        for idx, scored_fund in enumerate(scored[:top_n], start=1):
            highlights = []
            if scored_fund.record.stage_focus:
                highlights.append(f"Stages: {', '.join(scored_fund.record.stage_focus)}")
            if scored_fund.record.check_size_min or scored_fund.record.check_size_max:
                highlights.append(f"Checks: {format_check_range(scored_fund.record)}")
            if scored_fund.keywords_hit:
                highlights.append(f"Keywords: {', '.join(scored_fund.keywords_hit[:3])}")
            if scored_fund.record.contact_email:
                highlights.append(f"Contact: {scored_fund.record.contact_email}")
            print(f"{idx}. {scored_fund.record.name} — {scored_fund.total:.1f} | {' | '.join(highlights)}")
        return

    table = Table(title=f"Top {top_n} Funds by Score")
    table.add_column("Rank", justify="right")
    table.add_column("Fund")
    table.add_column("Score", justify="right")
    table.add_column("Highlights")
    for idx, scored_fund in enumerate(scored[:top_n], start=1):
        highlights = []
        if scored_fund.record.stage_focus:
            highlights.append(
                f"Stages: {', '.join(scored_fund.record.stage_focus)}"
            )
        if scored_fund.record.check_size_min or scored_fund.record.check_size_max:
            highlights.append(
                f"Checks: {format_check_range(scored_fund.record)}"
            )
        if scored_fund.keywords_hit:
            highlights.append(f"Keywords: {', '.join(scored_fund.keywords_hit[:3])}")
        if scored_fund.record.contact_email:
            highlights.append(f"Contact: {scored_fund.record.contact_email}")
        table.add_row(
            str(idx),
            scored_fund.record.name,
            f"{scored_fund.total:.1f}",
            " | ".join(highlights),
        )
    CONSOLE.print(table)


def format_check_range(record: FundRecord) -> str:
    min_val = record.check_size_min
    max_val = record.check_size_max
    currency = record.check_size_currency or "USD"
    def fmt(value: Optional[float]) -> str:
        if value is None:
            return "?"
        if value >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        if value >= 1_000:
            return f"${value/1_000:.0f}K"
        return f"${value:,.0f}"
    if min_val and max_val:
        return f"{fmt(min_val)}–{fmt(max_val)} {currency}"
    if min_val:
        return f"≥{fmt(min_val)} {currency}"
    if max_val:
        return f"≤{fmt(max_val)} {currency}"
    return "N/A"


def write_output(path: Path, scored: Sequence[ScoredFund], csv_path: Path) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_csv": str(csv_path),
        "top_funds": [serialize_entry(entry, idx) for idx, entry in enumerate(scored, start=1)],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    message = f"Saved output to {path}"
    if CONSOLE:
        CONSOLE.print(f"[green]{message}")
    else:
        print(message)


def serialize_entry(entry: ScoredFund, rank: int) -> dict:
    record = entry.record
    return {
        "rank": rank,
        "name": record.name,
        "score": round(entry.total, 2),
        "breakdown": {k: round(v, 2) for k, v in entry.breakdown.items()},
        "firm_type": record.firm_type,
        "hq_city": record.hq_city,
        "hq_region": record.hq_region,
        "hq_country": record.hq_country,
        "stage_focus": record.stage_focus,
        "check_size": format_check_range(record),
        "contact_email": record.contact_email,
        "keywords_hit": entry.keywords_hit,
        "overlap_ratio": round(entry.overlap_ratio, 3),
        "notes": build_notes(entry),
    }


def build_notes(entry: ScoredFund) -> list[str]:
    record = entry.record
    notes: list[str] = []
    if record.hq_country:
        notes.append(f"HQ: {record.hq_city or ''} {record.hq_region or ''} {record.hq_country}".strip())
    if entry.overlap_ratio:
        notes.append(f"Check-size overlap {(entry.overlap_ratio * 100):.0f}% of target band")
    if entry.keywords_hit:
        notes.append(f"Sector keywords: {', '.join(entry.keywords_hit)}")
    if record.contact_email:
        notes.append(f"Contact channel: {record.contact_email}")
    if entry.breakdown.get("warmth"):
        notes.append("Manual strategic boost applied")
    return notes


def main() -> None:
    args = parse_args()
    records = read_csv(args.csv)
    scored = [score_record(record) for record in records]
    scored.sort(key=lambda item: item.total, reverse=True)
    top_n = args.top
    print_table(scored, top_n)
    if args.output:
        write_output(args.output, scored[:top_n], args.csv)


if __name__ == "__main__":
    main()
