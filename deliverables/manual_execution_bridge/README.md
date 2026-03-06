# MANUAL EXECUTION BRIDGE - README
# ==============================================================================
# Generated: 2026-02-25
# Purpose: Enable manual execution of 5 VC outreach packets without Trello API
# ==============================================================================

## WHAT'S IN THIS FOLDER

This folder contains everything Lucas needs to manually send the 5 priority
outreach packets, even without Trello API automation.

### Files Created

| File | Purpose |
|------|---------|
| `P1_BITKRAFT_email.txt` | Ready-to-send email for BITKRAFT Ventures |
| `P2_Konvoy_email.txt` | Ready-to-send email for Konvoy Ventures |
| `P3_Mechanism_email.txt` | Ready-to-send email for Mechanism Capital |
| `P4_CollabCurrency_email.txt` | Ready-to-send email for Collab+Currency |
| `P5_Variant_email.txt` | Ready-to-send email for Variant |
| `trello_cards_import.csv` | CSV file for bulk Trello card import |
| `create_trello_cards.sh` | Bash script to auto-create cards (needs API creds) |
| `create_trello_cards.py` | Python script to auto-create cards (needs API creds) |
| `sent_log_planned.csv` | Pre-populated sent log (5 planned sends) |
| `README.md` | This file |

## QUICK START (3 OPTIONS)

### OPTION A: Manual Email Send (Fastest - 15 minutes)

1. Open each `P*_email.txt` file
2. Copy the email body (everything below "EMAIL BODY")
3. Paste into your email client
4. Fill in: [Calendly link], [Your title], [Company name]
5. Attach: pitch_deck/latest.pdf + kpi_snapshot/2026-02-24-kpis.csv
6. Send
7. Update `sent_log_planned.csv` with actual send time (replace blank with timestamp)

### OPTION B: Trello CSV Import (If you want cards first)

1. Open your Trello board
2. Go to: Board Menu → More → Copy board → Import CSV
3. OR use Trello's bulk import feature
4. Upload: `trello_cards_import.csv`
5. This creates all 5 cards with descriptions and labels
6. Then manually add the checklist items to each card

### OPTION C: Automated Card Creation (Once you have API keys)

**Bash version:**
```bash
# Set your credentials
export TRELLO_API_KEY="your_key_here"
export TRELLO_TOKEN="your_token_here"
export TRELLO_BOARD_ID="your_board_id_here"

# Run the script
cd /data/workspace/deliverables/manual_execution_bridge
chmod +x create_trello_cards.sh
./create_trello_cards.sh
```

**Python version:**
```bash
# Set your credentials
export TRELLO_API_KEY="your_key_here"
export TRELLO_TOKEN="your_token_here"
export TRELLO_BOARD_ID="your_board_id_here"

# Run the script
cd /data/workspace/deliverables/manual_execution_bridge
python3 create_trello_cards.py
```

Get your API credentials at: https://trello.com/app-key

## THE 5 PACKETS

| Priority | Fund | Contact | Email | Check Size | Hook |
|----------|------|---------|-------|------------|------|
| P1 | BITKRAFT Ventures | Martin Garcia | martin@bitkraft.vc | $500K-$10M | Synthetic Reality / founder-built |
| P2 | Konvoy Ventures | Taylor Hurst | taylor@konvoy.vc | $500K-$3M | Infrastructure play |
| P3 | Mechanism Capital | Steve Cho | steve@mechanism.capital | $1M-$2M | Crypto-gaming + AI |
| P4 | Collab+Currency | Derek Edwards | derek@collabcurrency.com | $100K-$3M | Crypto x culture |
| P5 | Variant | Spencer Noon | spencer@variant.fund | $1M-$5M | User ownership |

## BEFORE YOU SEND

1. **Fill in your details:**
   - [Calendly link] → Replace with your actual link
   - [Your title] → Your title
   - [Company name] → Your company name

2. **Verify attachments exist:**
   - `/data/workspace/deliverables/outreach_assets/pitch_deck/latest.pdf`
   - `/data/workspace/deliverables/outreach_assets/kpi_snapshot/2026-02-24-kpis.csv`

3. **Best send times:**
   - BITKRAFT, Mechanism, Variant: Tue-Thu, 9-11am EST
   - Konvoy: Tue-Thu, 8-10am MST
   - Collab+Currency: Tue-Thu, 9-11am PST

## AFTER YOU SEND

1. Update `sent_log_planned.csv`:
   - Replace the blank `sent_at_utc` with actual timestamp
   - Example: `2026-02-25T16:30:00Z`

2. Copy the updated rows to the main sent_log:
   ```bash
   cp sent_log_planned.csv /data/workspace/deliverables/outreach_assets/sent_log.csv
   ```

3. Set follow-up reminders:
   - Day 3: February 28, 2026
   - Day 7: March 4, 2026

## FOLLOW-UP TEMPLATES

Day 3 and Day 7 follow-up templates are in:
`/data/workspace/deliverables/outreach_assets/CRM_LOGGING_SOP.md`

## TIME ESTIMATES

| Task | Time |
|------|------|
| Read 5 email files | 5 min |
| Customize & send all 5 | 15 min |
| Update sent_log | 2 min |
| Set follow-up reminders | 3 min |
| **Total** | **25 min** |

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Calendly link missing | Remove from template; offer times manually |
| Pitch deck not ready | Send without; follow up with deck |
| Email bounces | Flag in notes; find alternative contact |
| Want to customize template | Edit the P*_email.txt file before sending |
| Trello import fails | Use Option A (manual) or Option C (script) |

## SUPPORT

- Email templates source: `../outreach_assets/email_templates.md`
- Full execution plan: `../outreach_assets/MANUAL_EXECUTION_PLAN.md`
- CRM logging SOP: `../outreach_assets/CRM_LOGGING_SOP.md`
- Original manifest: `../daily_queue/2026-02-25-manifest.json`

================================================================================
READY TO SEND. GOOD LUCK.
================================================================================
