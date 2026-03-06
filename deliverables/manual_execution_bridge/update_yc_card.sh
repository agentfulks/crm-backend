#!/bin/bash
# Manual Execution Script: Update Y Combinator Trello Card
# Created: 2026-02-27
# Purpose: Update YC card with Jared Friedman contact details (blocked - no API credentials)

# --- CARD UPDATE CONTENT ---
# Copy/paste this into the Y Combinator card in Trello:

cat << 'CARD_CONTENT'
## Contact Target: Jared Friedman

**Partner:** Jared Friedman  
**Title:** Managing Partner, Software Group  
**Email:** jared@ycombinator.com  
**Confidence:** HIGH

### Why This Target
- Leads YC Software Group (primary fit for AI infrastructure)
- Strong AI background (worked at pioneering AI company pre-YC)
- Co-founded Scribd (YC W06), CS from Harvard
- YC portfolio includes gaming companies (Players' Lounge, DreamCraft)
- AI focus: ~50% of recent YC batches are AI/agent companies

### Alternative Contact
**Diana Hu** - General Partner  
**Email:** diana@ycombinator.com  
**Background:** Co-founder/CTO Escher Reality (AR backend, acquired by Niantic/Pokémon Go)  
**Relevance:** Gaming-adjacent, AR/ML infrastructure, CMU CS/EE with ML focus

### Additional Alternatives
- Ankit Gupta (ankit@ycombinator.com) - AI/ML specialist, deep learning researcher
- Gustaf Alströmer (gustaf@ycombinator.com) - Growth/infrastructure focus

---
**Status:** READY FOR OUTREACH  
**Next Step:** Draft personalized email to jared@ycombinator.com  
**Move to:** Awaiting Approval or Approved/Send
CARD_CONTENT

echo ""
echo "=== MANUAL UPDATE INSTRUCTIONS ==="
echo "1. Open Trello board"
echo "2. Find Y Combinator card in Daily Queue"
echo "3. Edit card description - paste content above"
echo "4. Move card to 'Awaiting Approval' or 'Approved/Send' column"
echo "5. Remove 'blocked - no contact' label if present"
echo ""
echo "=== EMAIL READY ==="
echo "To: jared@ycombinator.com"
echo ""
