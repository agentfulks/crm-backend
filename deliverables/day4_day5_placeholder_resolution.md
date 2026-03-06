# Day 4 & Day 5 Email Drafts — Placeholder Resolution Report

## Summary

**10 emails reviewed** across Day 4 (5 emails) and Day 5 (5 emails).

**2 placeholder types identified:**
1. Sender name placeholder: `[Name]` / `[NAME]`
2. Phone number placeholder: `[PHONE]` (Day 5 only)

---

## Placeholder Inventory

### Day 4 Emails (Animoca, Delphi, Shima, Sfermion, Everyrealm)

| File | `[Name]` | `[PHONE]` | Notes |
|------|----------|-----------|-------|
| `01_animoca_ventures_james_ho.md` | ✅ Found | ❌ None | Casual sign-off, single line |
| `02_delphi_ventures_yan_liberman.md` | ✅ Found | ❌ None | Academic tone |
| `03_shima_capital_yida_gao.md` | ✅ Found | ❌ None | Ultra-concise format |
| `04_sfermion_andrew_steinwold.md` | ✅ Found | ❌ None | Podcast listener angle |
| `05_everyrealm_janine_yorio.md` | ✅ Found | ❌ None | Strategic partnership angle |

### Day 5 Emails (Framework, King River, Patron, TGF, TIRTA)

| File | `[NAME]` | `[PHONE]` | Notes |
|------|----------|-----------|-------|
| `framework_ventures.md` | ✅ Found | ✅ Found | Full formal signature block |
| `king_river_capital.md` | ✅ Found | ✅ Found | Full formal signature block |
| `patron.md` | ✅ Found | ✅ Found | Full formal signature block |
| `the_games_fund.md` | ✅ Found | ✅ Found | Full formal signature block |
| `tirta_ventures.md` | ✅ Found | ✅ Found | Full formal signature block |

---

## Placeholder Replacements Required

### 1. `[Name]` / `[NAME]` → Sender Name

**Recommended Replacement:** `Lucas Fulks`

**Rationale:**
- Founder/CEO sending cold outreach to VCs
- Personal connection drives higher reply rates
- Consistent with Lucas's founder-operator positioning

**Files to Update:**
```
/deliverables/day4_vc_batch/email_drafts/
  - 01_animoca_ventures_james_ho.md (Line: "Best, [Name]")
  - 02_delphi_ventures_yan_liberman.md (Line: "Best, [Name]")
  - 03_shima_capital_yida_gao.md (Line: "[Name]")
  - 04_sfermion_andrew_steinwold.md (Line: "Best, [Name]")
  - 05_everyrealm_janine_yorio.md (Line: "Best, [Name]")

/deliverables/day5_vc_batch/email_drafts/
  - framework_ventures.md (Lines: "Best, [NAME]" + signature block)
  - king_river_capital.md (Lines: "Best, [NAME]" + signature block)
  - patron.md (Lines: "Best, [NAME]" + signature block)
  - the_games_fund.md (Lines: "Best, [NAME]" + signature block)
  - tirta_ventures.md (Lines: "Best, [NAME]" + signature block)
```

### 2. `[PHONE]` → Phone Number

**Recommended Replacement:** `[INSERT PHONE]` — **REQUIRES CONFIRMATION**

**Rationale:**
- Phone number not provided in company profile
- Required for 5 Day 5 emails with formal signature blocks
- Day 4 emails don't include phone (more casual format)

**Files to Update:**
```
/deliverables/day5_vc_batch/email_drafts/
  - framework_ventures.md (Line: "[PHONE]")
  - king_river_capital.md (Line: "[PHONE]")
  - patron.md (Line: "[PHONE]")
  - the_games_fund.md (Line: "[PHONE]")
  - tirta_ventures.md (Line: "[PHONE]")
```

---

## Formatting Inconsistency Detected

### Issue: Mixed Placeholder Case
- **Day 4:** Uses `[Name]` (title case)
- **Day 5:** Uses `[NAME]` (uppercase)

### Recommendation: Standardize
**Preferred format:** `[Name]` (title case)

**Reasoning:** Title case is cleaner and more professional in final output.

**Action:** Update Day 5 files to use `[Name]` for consistency across the campaign.

---

## Company Profile Reference

**NEXUS AI — Key Talking Points Present in All Drafts:**

| Metric | Value | Coverage |
|--------|-------|----------|
| **Product** | AI infrastructure for dynamic game worlds | ✅ All 10 emails |
| **ARR** | $180K | ✅ All 10 emails |
| **Growth** | 40% MoM | ✅ All 10 emails |
| **Partnerships** | 8 studios (2 AA) | ✅ All 10 emails |
| **MAU** | 1.2M | ✅ 8/10 emails |
| **Inference** | 50M+ requests/month | ✅ 2/10 emails |
| **Team** | ex-Unity AI, ex-OpenAI, ex-Roblox | ✅ All 10 emails |
| **Ask** | $3M Seed extension | ✅ All 10 emails |

**Consistency Rating: EXCELLENT**
- All core metrics present
- Fundraising ask clear
- Team credentials consistent
- Value prop aligned to each VC's thesis

---

## Ready to Send Checklist

### Pre-Flight Requirements

- [ ] **CONFIRM:** Lucas's phone number for Day 5 signature blocks
- [ ] **REPLACE:** `[Name]` → `Lucas Fulks` in all 10 emails
- [ ] **REPLACE:** `[NAME]` → `Lucas Fulks` in 5 Day 5 emails
- [ ] **REPLACE:** `[PHONE]` → `[actual number]` in 5 Day 5 emails
- [ ] **STANDARDIZE:** Normalize placeholder case to `[Name]` across all drafts
- [ ] **VERIFY:** Email addresses for all 10 recipients
- [ ] **ATTACH:** Pitch deck PDF
- [ ] **PREPARE:** Demo link (Loom or interactive)

### Quality Checks

- [ ] **Proofread:** All 10 emails for typos
- [ ] **Verify:** Portfolio company references are current
- [ ] **Check:** Fund sizes and investment mandates are accurate
- [ ] **Confirm:** No conflicting asks (e.g., different check sizes)

### Send Sequence

- [ ] **Day 4 batch:** Stagger sends by 15-30 min to avoid spam filters
- [ ] **Day 5 batch:** Send 24-48 hours after Day 4
- [ ] **Tracking:** Set up open/reply tracking
- [ ] **Follow-up:** Prepare 3-day and 7-day follow-up templates

---

## Quick Reference: Exact Replacement Strings

### Day 4 Replacements

```bash
# Run these sed commands in day4_vc_batch/email_drafts/
sed -i 's/\[Name\]/Lucas Fulks/g' *.md
```

### Day 5 Replacements

```bash
# Run these sed commands in day5_vc_batch/email_drafts/
sed -i 's/\[NAME\]/Lucas Fulks/g' *.md
sed -i 's/\[PHONE\]/[YOUR_PHONE_NUMBER]/g' *.md  # UPDATE THIS
```

---

## Action Items Summary

| Priority | Task | Owner | Status |
|----------|------|-------|--------|
| P0 | Provide phone number for signature blocks | Lucas | ⏳ PENDING |
| P0 | Apply name replacements across all 10 files | Agent | 🔧 READY |
| P1 | Standardize placeholder case to `[Name]` | Agent | 🔧 READY |
| P1 | Final proofread before send | Agent | 📋 QUEUED |
| P2 | Set up tracking and follow-up sequences | Lucas | 📋 QUEUED |

---

**Report Generated:** 2026-02-27
**Total Emails:** 10
**Total Placeholders:** 15 (10 name + 5 phone)
**Blocked on:** Phone number confirmation
