# VC Outreach Dashboard

Frontend for the VC Outreach Engine — manage investor packets, approvals, and queue status.

## Features

- **Dashboard Overview:** Real-time queue status (queued, awaiting approval, approved, sent)
- **Packet List:** View all packets with filtering by status
- **Packet Detail:** Full fund information with approve/reject actions
- **Responsive Design:** Works on desktop and mobile

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **TanStack Query (React Query)** for data fetching
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd /data/workspace/frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── api.ts              # API client (with mock data for now)
├── types.ts            # TypeScript type definitions
├── hooks/
│   └── usePackets.ts   # React Query hooks for data fetching
├── components/
│   ├── PacketCard.tsx      # Packet list item
│   ├── PacketDetail.tsx    # Packet detail modal
│   └── QueueStatus.tsx     # Dashboard stats
├── App.tsx             # Main app component
├── main.tsx            # Entry point
└── index.css           # Tailwind imports
```

## Mock Data

The frontend currently uses mock data for development. To connect to the real backend:

1. Set the API URL in your environment:
   ```bash
   export VITE_API_URL=http://localhost:8000/api
   ```

2. Update `src/api.ts` and set `USE_MOCK = false`

3. Ensure the backend is running with the packet API endpoints

## Backend Dependencies

The following backend endpoints are expected:

- `GET /api/packets` — List packets (with optional status filter)
- `GET /api/packets/:id` — Get packet by ID
- `POST /api/packets/:id/approve` — Approve a packet
- `POST /api/packets/:id/reject` — Reject a packet
- `GET /api/queue/status` — Get daily queue status

**Current Status:** The backend has Fund API but Packet API needs to be added. The frontend works with mock data for now.

## Usage

1. **Dashboard View:** See overall queue status at a glance
2. **Filter Packets:** Use the filter bar to view packets by status
3. **View Details:** Click any packet card to see full details
4. **Approve/Reject:** In the detail view, use the action buttons for packets awaiting approval

## Next Steps

- [ ] Connect to real backend API
- [ ] Add authentication
- [ ] Add packet creation form
- [ ] Add search functionality
- [ ] Add sorting options
- [ ] Real-time updates via WebSocket

## License

Private — Fulk-em
