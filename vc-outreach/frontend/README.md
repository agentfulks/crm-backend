# VC Outreach Engine - Frontend Approvals Dashboard

A Next.js 14+ App Router dashboard for reviewing and approving VC outreach cards from Trello.

## Features

- **List View**: See all cards awaiting approval with fund, partner, priority, and hook
- **Detail View**: Full card packet with editable draft message and notes
- **Actions**: 
  - Approve (moves card to next list)
  - Reject (adds comment)
  - Edit (saves draft message and notes)
- **Keyboard Shortcuts**:
  - `A` - Approve
  - `R` - Reject
  - `Ctrl+S` - Save changes

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local and add your MATON_API_KEY
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

## Environment Variables

- `MATON_API_KEY` - Your Maton gateway API key for Trello access

## API Routes

- `GET /api/trello/cards` - List all cards awaiting approval
- `GET /api/trello/cards/[cardId]` - Get single card details
- `POST /api/trello/cards/[cardId]/approve` - Approve a card
- `POST /api/trello/cards/[cardId]/reject` - Reject a card
- `PUT /api/trello/cards/[cardId]/update` - Update card content

## Tech Stack

- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- Trello API via Maton Gateway
- Lucide React icons