#!/usr/bin/env python3
import json

# Data from the board query
board_data = {
  "id": "699d2728fd2ae8c35d1f7a24",
  "cards": [
    {
      "id": "699d299cd1deaca4a5e7f204",
      "name": "VC outreach campaign setup",
      "idList": "699d2728fd2ae8c35d1f7a46",
      "desc": "Define ICP, build target list, craft multi-touch outbound system.",
      "labels": ["Type: Research", "Priority: P1", "Effort: L", "Workstream: Product"]
    },
    {
      "id": "699d30ec21f4e2916322c73d",
      "name": "Daily intake automation",
      "idList": "699d2728fd2ae8c35d1f7a46",
      "desc": "Auto-create investor packet cards from CRM top 5 scored entries each morning.",
      "labels": ["Type: Ops", "Priority: P0", "Effort: L", "Workstream: Ops"]
    },
    {
      "id": "699d30d2cdc8c20dfc3efbf5",
      "name": "Approval workflow SOP",
      "idList": "699d2728fd2ae8c35d1f7a46",
      "desc": "Define how Lucas reviews daily packets + reminder cadence (no auto-sending).",
      "labels": ["Type: Ops", "Priority: P1", "Effort: M", "Workstream: Ops"]
    },
    {
      "id": "699d30d8cf61ae9c1d204f8b",
      "name": "API/ingestion service",
      "idList": "699d2728fd2ae8c35d1f7a47",
      "desc": "Build backend service to read/write CRM (FastAPI) for sourcing + frontend use.",
      "labels": ["Type: Feature", "Priority: P0", "Effort: XL", "Workstream: Engineering"]
    },
    {
      "id": "699d30db3fbcf416bc4fac35",
      "name": "Source automation v1",
      "idList": "699d2728fd2ae8c35d1f7a47",
      "desc": "Implement scripts/APIs to pull seed-stage gaming/AI/devtools VCs into CRM daily.",
      "labels": ["Type: Outreach", "Priority: P1", "Effort: L", "Workstream: BDR"]
    },
    {
      "id": "699d30decdd9a9fcf0d56254",
      "name": "Contact enrichment workflow",
      "idList": "699d2728fd2ae8c35d1f7a47",
      "desc": "Append partner names, email, thesis notes for each VC entry.",
      "labels": ["Type: Outreach", "Priority: P1", "Effort: L", "Workstream: BDR"]
    },
    {
      "id": "699d30e16a9de3cf1c7a0ce3",
      "name": "Scoring + prioritization model",
      "idList": "699d2728fd2ae8c35d1f7a47",
      "desc": "Score VCs on sector fit, check size, network ties to sort daily queue.",
      "labels": ["Type: Research", "Priority: P1", "Effort: M", "Workstream: Product"]
    },
    {
      "id": "699d30e59c2a595f3e0ffdb8",
      "name": "Frontend approvals dashboard",
      "idList": "699d2728fd2ae8c35d1f7a47",
      "desc": "Next.js UI for reviewing queue, editing drafts, and pushing to Trello.",
      "labels": ["Type: Feature", "Priority: P1", "Effort: XL", "Workstream: Engineering"]
    },
    {
      "id": "699d30e992a45f203a2f93e8",
      "name": "Analytics + metrics pipeline",
      "idList": "699d2728fd2ae8c35d1f7a47",
      "desc": "Daily snapshot of outreach volume, approvals, meetings booked.",
      "labels": ["Type: Ops", "Priority: P2", "Effort: L", "Workstream: Ops"]
    },
    {
      "id": "699d30cfa968ba373c1263ee",
      "name": "Outreach asset inventory",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "Canonical sources live inside `deliverables/outreach_assets/`. Mirror this summary every time assets change so packet cards stay accurate.",
      "labels": ["Type: Ops", "Priority: P1", "Effort: M", "Workstream: Ops"]
    },
    {
      "id": "699d30cb1870f04a4b40c18e",
      "name": "Define ICP + success metrics",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "Target: independent Seed-Series A gaming/AI/devtools funds in US/UK/Canada/EU with $0.5-$5M checks and active deployment in last 36 months.",
      "labels": ["Type: Research", "Priority: P1", "Effort: M", "Workstream: Product"]
    },
    {
      "id": "699d30d569421a60335dbdb9",
      "name": "Postgres CRM schema + infra",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "Design DB schema (firms, contacts, outreach_attempts, notes) and provision Postgres instance.",
      "labels": ["Type: Tech Debt", "Priority: P0", "Effort: L", "Workstream: Engineering"]
    },
    {
      "id": "699d313479762c071b6dc86a",
      "name": "Investor packet template",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "Template for investor packets with Snapshot, Personalization, Outreach Plan, Attachments, Follow-up sections.",
      "labels": ["Type: Ops", "Priority: P1", "Effort: M", "Workstream: Ops"]
    },
    {
      "id": "699eb148736656420850f61a",
      "name": "[PACKET] Griffin Gaming Partners - Gaming VC",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Focus:** Gaming VC | **HQ:** Los Angeles, CA | **Check Size:** $1M-$5M | **Stage:** Seed to Series A | **Contact:** Peter Levin (peter@griffingp.com) | Former NBC Universal VP. Led investments in Discord, Roblox, Scopely.",
      "labels": [],
      "score": 88.5,
      "tier": "Priority A"
    },
    {
      "id": "699eb149c796d9a6995eac02",
      "name": "[PACKET] 2048 Ventures - AI/Devtools VC",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Focus:** AI/Devtools VC | **HQ:** New York, NY | **Check Size:** $500K-$2M | **Stage:** Pre-seed to Seed | **Contact:** Alex Iskold (alex@2048.vc) | Engineer-founder focused on developer tools, AI infrastructure. Former Techstars NYC MD.",
      "labels": [],
      "score": 82,
      "tier": "Priority B"
    },
    {
      "id": "699f2e29234e164a0bcd26f6",
      "name": "Packet: Andreessen Horowitz (a16z) Gaming",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Andreessen Horowitz (a16z) Gaming | **HQ:** Menlo Park, CA | **Stage:** Seed, Series A, Series B | **Check size:** $500K - $50M | **Score:** 4/4 (Priority A) | a16z has one of the largest gaming investment teams. Recent $600M Games Fund One. Thesis: 'Games are becoming the new social networks.' Map our AI-enabled sourcing engine to their infrastructure thesis.",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 95,
      "tier": "Priority A"
    },
    {
      "id": "699f2e2a1fff1b08b542bc2b",
      "name": "Packet: Lightspeed Venture Partners",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Lightspeed Venture Partners | **HQ:** Menlo Park, CA / Global | **Stage:** Seed, Series A, Series B | **Check size:** $1M - $50M | **Score:** 4/4 (Priority A) | Lightspeed has been aggressively deploying into gaming and interactive media. 'Frontier' thesis emphasizes AI-first companies. Our AI-enabled sourcing engine directly maps to their investment thesis.",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 92,
      "tier": "Priority A"
    },
    {
      "id": "699f2e2be997c5f0d2e19395",
      "name": "Packet: Griffin Gaming Partners",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Griffin Gaming Partners | **HQ:** Santa Monica, CA / London | **Stage:** Seed, Series A, Series B | **Check size:** $500K - $15M | **Score:** 3/4 (Priority A) | Griffin is the largest VC fund dedicated solely to gaming ($1B+ AUM). Multi-stage approach allows flexible entry points. High sector alignment with gaming/AI thesis.",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 85,
      "tier": "Priority A"
    },
    {
      "id": "699f2e2cf8ab00d19b23c73a",
      "name": "Packet: 1UP Ventures",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** 1UP Ventures | **HQ:** Seattle, WA | **Stage:** Pre-Seed, Seed | **Check size:** $100K - $2M | **Score:** 3/4 (Priority A) | 1UP is focused exclusively on independent game developers. Provides capital + collaborative community of 100+ indie studios. Founded by game industry veterans.",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 78,
      "tier": "Priority A"
    },
    {
      "id": "699f2e2ccb97f5cb286ed2fa",
      "name": "Packet: Galaxy Interactive",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Galaxy Interactive | **HQ:** New York, NY | **Stage:** Series A, Series B | **Check size:** $2M - $20M | **Score:** 3/4 (Priority A) | Galaxy Interactive is the gaming and interactive media arm of Galaxy Digital. They invest at the intersection of gaming, blockchain, and immersive experiences. Focus on the 'metaverse economy.'",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 80,
      "tier": "Priority A"
    },
    {
      "id": "699f2f2de0e903d780f2fa81",
      "name": "Packet: Griffin Gaming Partners",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Griffin Gaming Partners | **HQ:** Santa Monica, CA | **Stage:** Multi-stage | **Check size:** $500K - $15M | **Score:** 88.5/100 (Priority A) | Griffin is the largest VC fund dedicated solely to gaming ($1B+ AUM). Multi-stage approach. High sector alignment with gaming/AI thesis. Contact: Phil Sanderson (needs enrichment).",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 88.5,
      "tier": "Priority A"
    },
    {
      "id": "699f2f2d8cc01cf16b94081b",
      "name": "Packet: The Games Fund",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** The Games Fund (TGF) | **HQ:** Los Angeles, CA | **Stage:** Pre-Seed, Seed | **Check size:** $250K - $2M | **Score:** 86.0/100 (Priority A) | Specialist gaming VC focused on early-stage studios and interactive entertainment. LA-based with EU presence. Contact: Maria Kochmola (needs enrichment).",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 86,
      "tier": "Priority A"
    },
    {
      "id": "699f2f2e10a170fb85f10c18",
      "name": "Packet: Makers Fund",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Makers Fund | **HQ:** Global (London, Singapore, San Francisco) | **Stage:** Series A | **Check size:** $2M - $10M | **Score:** 85.5/100 (Priority A) | Global gaming and interactive entertainment investor. Multi-office presence enables global deal flow. Contact: Jay Chi (needs enrichment).",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 85.5,
      "tier": "Priority A"
    },
    {
      "id": "699f2f2fab92a33d8e4ee713",
      "name": "Packet: Hiro Capital",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Hiro Capital | **HQ:** London, UK | **Stage:** Seed to Series B | **Check size:** $500K - $5M | **Score:** 84.5/100 (Priority B) | Focuses on games, esports, and digital sports. European base with US investments. Contact: Luke Alvarez (needs enrichment).",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 84.5,
      "tier": "Priority B"
    },
    {
      "id": "699f2f3015e86bffaebdeaf0",
      "name": "Packet: Transcend Fund",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Transcend Fund | **HQ:** San Francisco, CA | **Stage:** Seed, Series A | **Check size:** $1M - $5M | **Score:** 83.0/100 (Priority B) | Invests in gaming, interactive entertainment, and digital media. SF-based with strong Bay Area network. Contact: Shanti Bergel (needs enrichment).",
      "labels": ["Priority: P1", "Effort: M", "Type: Outreach", "Workstream: Investor"],
      "score": 83,
      "tier": "Priority B"
    },
    {
      "id": "699f1f47ecced948130f290c",
      "name": "Packet: Galaxy Interactive",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Galaxy Interactive | **HQ:** New York / Los Angeles | **Stage:** Series A, B, Growth | **Check size:** $1M - $50M | **AUM:** $975M+ | Focus: Interactive entertainment, gaming, virtual worlds, Web3/metaverse infrastructure. Contact: Sam Englebardt (sam@galaxy.com), Richard Kim (richard@galaxy.com).",
      "labels": [],
      "score": 80,
      "tier": "Priority A"
    },
    {
      "id": "699f1f485f4be68925e964c7",
      "name": "Packet: Hiro Capital",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Hiro Capital | **HQ:** London, UK | **Stage:** Seed, Series A, Series B | **Check size:** $500K - $10M | **AUM:** $450M+ | Focus: Games, Esports, Digital Sports, Metaverse technologies, Space/Defence. Contact: Luke Alvarez (luke@hiro.capital), Ian Livingstone (ian@hiro.capital) - Co-founder of Games Workshop & Eidos.",
      "labels": [],
      "score": 84.5,
      "tier": "Priority B"
    },
    {
      "id": "699f1f4843ec5899e52e0ad3",
      "name": "Packet: Makers Fund",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Makers Fund | **HQ:** San Francisco, CA | **Stage:** Seed, Series A, Series B, Growth | **Check size:** $500K - $40M | **AUM:** $500M+ | Focus: Gaming, Interactive Entertainment, Game Technology, Infrastructure. Contact: Michael Cheung (michael@makersfund.com), Jay Chi (jay@makersfund.com).",
      "labels": [],
      "score": 85.5,
      "tier": "Priority A"
    },
    {
      "id": "699f1f49b0573bb0edf462f2",
      "name": "Packet: Play Ventures",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Play Ventures | **HQ:** Singapore / Helsinki | **Stage:** Pre-seed, Seed, Series A | **Check size:** $100K - $5M | **AUM:** $200M+ | Focus: Gaming, Games-inspired Consumer Products, Gaming Infrastructure. Contact: Henric Suuronen (henric@playventures.vc), Harri Manninen (harri@playventures.vc).",
      "labels": [],
      "score": 77,
      "tier": "Priority B"
    },
    {
      "id": "699f1f490db3409d91d90e4c",
      "name": "Packet: Transcend Fund",
      "idList": "699d2728fd2ae8c35d1f7a48",
      "desc": "**Fund:** Transcend Fund | **HQ:** San Francisco, CA | **Stage:** Pre-seed, Seed, Series A | **Check size:** $250K - $5M | **AUM:** $100M+ | Focus: Games, Digital Entertainment, Interactive Media, Next-gen Social Gaming. Contact: Shanti Bergel (shanti@transcend.fund), Andrew Sheppard (andrew@transcend.fund).",
      "labels": [],
      "score": 83,
      "tier": "Priority B"
    }
  ]
}

# Find Awaiting Approval list ID
awaiting_list_id = "699d2728fd2ae8c35d1f7a48"

# Filter cards in Awaiting Approval
cards_in_awaiting = []
for card in board_data["cards"]:
    if card.get("idList") == awaiting_list_id:
        cards_in_awaiting.append(card)

print(f"Total cards in Awaiting Approval: {len(cards_in_awaiting)}\n")

# Categorize
categories = {
    "process_setup": [],
    "investor_packets": []
}

for card in cards_in_awaiting:
    name = card["name"]
    if "packet" in name.lower():
        categories["investor_packets"].append({
            "id": card["id"],
            "name": name,
            "desc": card.get("desc", ""),
            "score": card.get("score", 0),
            "tier": card.get("tier", "Unknown")
        })
    else:
        categories["process_setup"].append({
            "id": card["id"],
            "name": name,
            "desc": card.get("desc", "")
        })

print("=" * 60)
print("PROCESS/SETUP CARDS")
print("=" * 60)
for card in categories["process_setup"]:
    print(f"\n📋 {card['name']}")
    print(f"   {card['desc'][:100]}...")

print(f"\n\n" + "=" * 60)
print(f"INVESTOR PACKETS ({len(categories['investor_packets'])} total)")
print("=" * 60)

# Sort investor packets by score
sorted_packets = sorted(categories["investor_packets"], key=lambda x: x.get("score", 0), reverse=True)

for card in sorted_packets:
    print(f"\n📊 {card['name']}")
    print(f"   Score: {card.get('score', 'N/A')}/100 | Tier: {card.get('tier', 'N/A')}")

# Group by tier
p1_packets = [c for c in sorted_packets if c.get("score", 0) >= 85]
p2_packets = [c for c in sorted_packets if 80 <= c.get("score", 0) < 85]
p3_packets = [c for c in sorted_packets if c.get("score", 0) < 80]

print(f"\n\n" + "=" * 60)
print("PRIORITIZATION SUMMARY")
print("=" * 60)
print(f"\n🎯 P1 (Send this week): {len(p1_packets)} packets")
for card in p1_packets[:5]:
    print(f"   • {card['name']} (Score: {card.get('score', 'N/A')})")

print(f"\n📅 P2 (Next week): {len(p2_packets)} packets")
for card in p2_packets:
    print(f"   • {card['name']} (Score: {card.get('score', 'N/A')})")

print(f"\n📦 P3 (Backlog): {len(p3_packets)} packets")
for card in p3_packets:
    print(f"   • {card['name']} (Score: {card.get('score', 'N/A')})")

# Save full data for later processing
import os
os.makedirs("/data/workspace/deliverables/vc_awaiting_review", exist_ok=True)

with open("/data/workspace/deliverables/vc_awaiting_review/cards_analysis.json", "w") as f:
    json.dump({
        "process_setup": categories["process_setup"],
        "investor_packets": sorted_packets,
        "p1": p1_packets,
        "p2": p2_packets,
        "p3": p3_packets
    }, f, indent=2)

print("\n\n✅ Analysis saved to /data/workspace/deliverables/vc_awaiting_review/cards_analysis.json")
