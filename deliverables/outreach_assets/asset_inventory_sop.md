# SOP: Outreach Asset Inventory Management

**Purpose:** Ensure the outreach asset inventory remains accurate, complete, and useful for investor/partner engagement.

**Owner:** [Assign owner — likely Operations or Founder]
**Review cadence:** Weekly (active phases), Monthly (maintenance)

---

## Asset Inventory Structure

The inventory tracks all materials needed for investor and partner outreach:

| Asset Category | Format | Location | Owner | Status |
|----------------|--------|----------|-------|--------|
| Pitch Deck (PDF) | PDF | `/assets/deck/` | [Owner] | 🔴 Missing |
| KPI Snapshot | XLSX | `/assets/metrics/` | [Owner] | 🔴 Missing |
| Calendly Link | URL | This doc | [Owner] | 🔴 Missing |
| Case Studies | MD/PDF | `/assets/case-studies/` | [Owner] | 🟡 Draft |
| One-Pager | PDF | `/assets/sheets/` | [Owner] | 🔴 Missing |
| Demo Video | MP4 | `/assets/video/` | [Owner] | 🔴 Missing |
| Cap Table | XLSX | `/assets/legal/` | [Owner] | 🔴 Missing |
| Financial Model | XLSX | `/assets/finance/` | [Owner] | 🔴 Missing |
| Team Bios | MD/PDF | `/assets/team/` | [Owner] | 🔴 Missing |
| Press Kit | ZIP | `/assets/press/` | [Owner] | 🔴 Missing |

---

## Weekly Maintenance Checklist

**Duration:** 15 minutes every Monday

### Step 1: Verify Asset Status (5 min)
- [ ] Check each asset file exists at listed location
- [ ] Verify files are not corrupted (open PDFs, check XLSX formulas)
- [ ] Confirm version dates are current

### Step 2: Update Status Column (5 min)
- [ ] Mark any newly completed assets as 🟢 Ready
- [ ] Flag assets under development as 🟡 In Progress
- [ ] Mark blocked/missing assets as 🔴 Missing

### Step 3: Note Blockers (5 min)
- [ ] Add blocker notes for any 🔴 or 🟡 items
- [ ] Update "Next Action" column with specific owner and deadline

---

## Monthly Deep Review Checklist

**Duration:** 30 minutes, first Monday of month

### Content Review
- [ ] **Pitch Deck:** Review for outdated metrics, team changes, market shifts
- [ ] **KPI Snapshot:** Ensure latest month added, formulas working
- [ ] **Case Studies:** Check if new customers qualify for documentation
- [ ] **One-Pager:** Verify value prop still accurate

### Access Review
- [ ] **Calendly:** Test booking link, check integration health
- [ ] **File permissions:** Ensure sharing links work
- [ ] **CRM integration:** Verify asset links logged correctly

### Version Control
- [ ] **Archive old versions:** Move outdated assets to `/archive/YYYY-MM/`
- [ ] **Update file names:** Ensure consistent naming: `[Asset]_v[Version]_YYYY-MM-DD.[ext]`
- [ ] **Changelog:** Add updates to `ASSET_CHANGELOG.md`

---

## Asset Creation Workflow

When a new asset is needed:

### 1. Request Phase
```
Requester → Owner: Asset needed + use case + deadline
Owner → Requester: Confirm scope and timeline
```

### 2. Creation Phase
```
Owner: Create asset using approved template
Owner: Self-review against quality checklist
Owner: Submit for review (if required)
```

### 3. Review Phase
```
Reviewer: Check accuracy, branding, completeness
Reviewer: Approve or request revisions
Owner: Address feedback
```

### 4. Publication Phase
```
Owner: Move to approved location
Owner: Update inventory status to 🟢 Ready
Owner: Add to relevant outreach templates
Owner: Notify stakeholders
```

---

## Quality Checklist (All Assets)

Before marking an asset as 🟢 Ready:

- [ ] **Accuracy:** All facts, numbers, and dates verified
- [ ] **Branding:** Logo, colors, fonts match brand guide
- [ ] **Completeness:** All required sections present
- [ ] **Permissions:** Customer logos/quotes approved in writing
- [ ] **File format:** Correct format for intended use
- [ ] **File size:** Optimized for email sharing (<5MB preferred)
- [ ] **Versioning:** File name includes version and date
- [ ] **Backup:** Copy saved to cloud storage

---

## Naming Conventions

| Asset Type | Format | Example |
|------------|--------|---------|
| Pitch deck | `Deck_v[VERSION]_YYYY-MM-DD.pdf` | `Deck_v3_2026-02-25.pdf` |
| KPI snapshot | `KPI_YYYY-MM.xlsx` | `KPI_2026-02.xlsx` |
| Case study | `Case_[COMPANY]_v[VERSION]_YYYY-MM-DD.md` | `Case_AcmeCorp_v1_2026-02-25.md` |
| One-pager | `OnePager_[TYPE]_v[VERSION]_YYYY-MM-DD.pdf` | `OnePager_Investor_v2_2026-02-25.pdf` |

---

## Emergency Update Protocol

**When:** Significant news (funding, major customer, pivot, crisis)

1. **Assess impact:** Which assets are affected?
2. **Prioritize:** Update highest-impact assets first (typically deck + one-pager)
3. **Version bump:** Increment version number
4. **Fast-track review:** Compress review cycle to 24 hours if needed
5. **Communication:** Notify all team members with asset access
6. **Archive:** Move outdated versions immediately

---

## Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **Owner** | Maintains inventory, assigns assets, runs weekly reviews |
| **Creator** | Produces assets to spec, follows templates |
| **Reviewer** | Validates quality, approves for publication |
| **User** | Provides feedback, reports outdated assets |

---

## Red Flags (Escalate Immediately)

Escalate to leadership if:
- 🔴 Missing assets block an active fundraising or sales process
- Multiple assets show inconsistent metrics
- Customer-facing asset contains unapproved claims
- Asset links break during active outreach
- Competitor publishes similar asset with superior positioning

---

## Tools & Access

| Tool | Purpose | Owner |
|------|---------|-------|
| File storage | Asset repository | [Owner] |
| Calendly | Booking management | [Owner] |
| CRM | Asset usage tracking | [Owner] |
| Version control | Change history | [Owner] |
| Analytics | Asset performance | [Owner] |

---

## Templates Reference

All asset creation should start from approved templates:

- `templates/pitch_deck_template.pptx`
- `templates/kpi_snapshot_template.xlsx`
- `templates/case_study_template.md` ← **Created: 2026-02-25**
- `templates/one_pager_template.pptx`

---

## Change Log

| Date | Change | Owner |
|------|--------|-------|
| 2026-02-25 | SOP created | OPS-LEAD |
| | | |

---

**Next Review Date:** [First Monday of next month]
