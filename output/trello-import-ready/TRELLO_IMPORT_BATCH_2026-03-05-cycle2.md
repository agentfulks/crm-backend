# TRELLO IMPORT BATCH — March 5, 2026 (Cycle 2)
**Status:** Ready for Manual Import (MATON_API_KEY unavailable)
**Action Required:** Copy-paste into Trello cards

---

## VC OUTREACH ENGINE — 5 NEW PACKETS
**Source File:** `/data/workspace/output/vc_research_batch_2026-03-05-cycle2.md`
**Import To:** "Daily Queue" list

| Priority | Firm | Partner | Lead? | Hook Focus |
|----------|------|---------|-------|------------|
| **P0** | BITKRAFT | Jens Hilgers | Yes | Esports pioneer, Web3 infra |
| **P0** | Konvoy | Jason Chapman | Yes | Gaming-only specialist |
| **P0** | Play Ventures | Henric Suuronen | Yes | F2P/mobile seed expert |
| **P1** | Hiro Capital | Luke Alvarez | Co-lead | Metaverse, gamified fitness |
| **P1** | The Games Fund | Misha Kirillov | Yes | Gaming veteran fund |

**Total VC Packets:** 5 (3 P0, 2 P1)

---

## BDR GAME STUDIOS — 5 NEW TARGETS
**Source File:** `/data/workspace/output/bdr_research_batch_2026-03-05-cycle2.md`
**Import To:** "Research Queue" list

| Priority | Studio | CEO | Focus | Trigger |
|----------|--------|-----|-------|---------|
| P0 | Kwalee | David Darling | Hyper-casual/hybrid | €1.5M 8SEC investment |
| P0 | Supersonic (IronSource) | Nadav Ashkenazy | Hyper-casual publishing | Unity/IronSource integration |
| P0 | Sunday | Thomas Chopard | Hyper-casual | Rising star, 100M+ downloads |
| P1 | Gismart | Dmitri Lipnikov | Casual/music games | 500M+ downloads, expanding |
| P1 | Ruby Games | Mert Can Kurum | Hyper-casual | 1B+ downloads, new M&A activity |

**Note:** All 5 studios include full contact details, personalization hooks, and draft outreach messages

**Combined Downloads:** 9B+ across all studios

---

## IMPORT INSTRUCTIONS

### Path A: Manual Copy-Paste (Current)
1. Open Trello board: VC Outreach Engine
2. Click "Add a card" in "Daily Queue" list
3. Copy title: `[Priority] Firm Name — Partner Name`
4. Copy description from source file
5. Add labels: `Priority: P0/P1`, `Type: Research`, `Workstream: Investor`
6. Repeat for all 5 VC packets

### Path B: Direct Trello API (If API keys available)
```bash
# Requires TRELLO_API_KEY and TRELLO_TOKEN in .env
python scripts/import_vc_batch.py vc_research_batch_2026-03-05-cycle2.md
```

### Path C: MATON Integration (If MATON_API_KEY restored)
```bash
# Requires MATON_API_KEY in .env
python scripts/import_via_maton.py vc_research_batch_2026-03-05-cycle2.md
```

---

## CURRENT BOARD STATUS (As of Last Check)

| List | Count | Age |
|------|-------|-----|
| Daily Queue | ~20 | Mixed |
| Awaiting Approval | 16 | 7+ days (STALE) |
| Approved/Send | 41 | Ready to execute |
| Follow-up | Unknown | — |

**Critical:** 16 stale VC cards need approval decision
**Critical:** 41 approved sends need execution

---

## NEXT ACTIONS

1. **Immediate (5 min):** Import 5 new VC packets via copy-paste
2. **Today (3 hours):** Execute emergency approval block (see LUCAS_ACTION_CHECKLIST_2026-03-05.md)
3. **Ongoing:** Daily 15-min approval habit to prevent backlog

---

*Generated: March 5, 2026 — 03:38 UTC*  
*Files Ready: YES*  
*API Status: MANUAL MODE*
