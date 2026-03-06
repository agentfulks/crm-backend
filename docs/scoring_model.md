# Investor Fund Scoring Model (v0.1)

_Last updated: 24 Feb 2026_

## Objective
Rank all funds in `data/raw/gaming_vc_list.csv` (and, imminently, the CRM `funds` table) so that the **Daily Queue** always receives the five highest-leverage targets for packet prep and outreach. Scores must be reproducible, explainable, and automatable so we can promote them into the backend ingestion + Trello automation flows.

## Inputs
| Field | Source | Notes |
| --- | --- | --- |
| `stage_focus` | CSV / CRM `funds.stage_focus` | Parsed list (Pre-Seed, Seed, Series A, etc.) |
| `check_size_min` / `check_size_max` | CSV / CRM | Normalized to USD where possible |
| `hq_country` + `hq_region` | CSV / CRM | Used for geo fit |
| `target_countries` | CSV / CRM | Indicates declared deployment geos |
| `overview__Who we are`, `thesis__Funding requirements` | CSV text blobs | Keyword extraction for sector fit |
| `contact_email` | CSV / CRM contacts join | Proxy for outreach readiness |
| Manual boosts | Config file | Allows hand-picked acceleration for strategic funds |

## Scoring Factors & Weights
| Factor | Max Pts | Logic |
| --- | --- | --- |
| **Stage Fit** | 25 | +10 for Pre-Seed, +9 for Seed, +6 for Series A. Clamped at 25. |
| **Check Size Fit** | 15 | Measure overlap between fund range and $0.5–5.0M target band. Full overlap ⇒ 15, partial overlap scaled linearly. |
| **Geo Fit** | 10 | +6 if HQ in US/Canada/UK, +4 if HQ in EU Tier-1 (DE, FR, NL, SE, FI, DK, ES, PT, IE, NO). +2 if `target_countries` includes these even if HQ elsewhere. |
| **Sector Signal** | 25 | Keyword hits (`gaming`, `game`, `interactive`, `AI`, `devtools`, `XR`, `immersive`, `infrastructure`, `developer tools`, `synthetic reality`, `content platforms`). Each unique keyword adds 4 points (clamped 25). |
| **Warmth / Strategic Boost** | 15 | Manual config for must-win funds (BITKRAFT, Konvoy, Variant, Collab+Currency, Mechanism, etc.). Default 0. |
| **Contact Readiness** | 10 | +6 if direct email present; +2 if domain matches website; +2 if contact field references partner/role. |
| **Data Freshness Guardrail** | -5 | Subtract up to 5 points if required fields missing (no stages AND no geo AND no contact). Ensures incomplete entries sink to bottom. |

Total score is clamped to 0–100. The script also emits a per-factor breakdown for explainability.

## Implementation
Code lives in `backend/scripts/rank_funds.py` and is designed to be run via uv:

```bash
cd backend
uv run python scripts/rank_funds.py --top 10 --output ../deliverables/daily_queue/2026-02-24.json
```

Key behaviors:
1. Parses the CSV (or future CRM query) into structured `FundRecord` objects.
2. Applies the weight table above and emits `(score, breakdown)` for each record.
3. Sorts descending and prints a Rich table plus JSON blob.
4. JSON schema per fund:
   ```json
   {
     "name": "BITKRAFT Ventures",
     "score": 91.2,
     "breakdown": {"stage": 25, "check_size": 12.5, ...},
     "hq_country": "United States",
     "stage_focus": ["Seed", "Series A"],
     "check_size": "$500K – $10M",
     "contact_email": "pitch@bitkraft.vc",
     "keywords_hit": ["gaming", "interactive", "immersive"],
     "notes": "Global gaming/immersive thesis; explicit $500K–$10M range"
   }
   ```
5. CLI flags allow future Trello pushes (`--create-cards`) and CRM sourcing once DATABASE_URL is usable.

## Example (24 Feb 2026)
Top five (matches Trello Daily Queue):

| Rank | Fund | Score | Highlights |
| --- | --- | --- | --- |
| 1 | BITKRAFT Ventures | 91.2 | Multi-stage gaming thesis, $500K–$10M checks, global remit, contact email present. |
| 2 | Konvoy Ventures | 88.4 | HQ in Denver, pure-play gaming infra, Pre-Seed–Series A, explicit $500K–$3M focus. |
| 3 | Variant | 84.6 | Web3/user-ownership thesis, Pre-Seed/Seed focus, multi-geo coverage, needs contact enrichment (penalized). |
| 4 | Collab+Currency | 82.0 | Crypto/culture fund, check sizes within band, contact email exists, thesis mentions gaming/culture. |
| 5 | Mechanism Capital | 79.5 | Crypto-gaming + DeFi focus, global checks, contact channel available but generic. |

(The JSON snapshot for this run is saved at `deliverables/daily_queue/2026-02-24.json`.)

## Next Steps
1. **Data source swap:** replace CSV reader with CRM query once the hosted Postgres is live.
2. **Expose via API:** surface `/api/funds/top?limit=5` endpoint so the frontend + automation jobs can pull directly.
3. **Trello integration:** wire `--create-cards` flag to authenticated Trello client + Butler schedule for 08:00 CST daily drops.
4. **Feedback loop:** persist scores in CRM for auditing; log overrides (manual boosts) to `audit_log` table.
5. **Contact enrichment coupling:** once contact workflow is ready, treat “verified contact” as prerequisite to hitting Daily Queue to avoid dead leads.
