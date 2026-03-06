# ERD: VC Outreach CRM Database Schema

## Mermaid Diagram

```mermaid
erDiagram
    FIRMS {
        uuid id PK
        varchar name
        varchar website
        varchar location
        numeric check_size_min
        numeric check_size_max
        varchar[] stage_focus
        varchar[] sector_focus
        numeric aum
        timestamptz created_at
        timestamptz updated_at
    }

    CONTACTS {
        uuid id PK
        uuid firm_id FK
        varchar name
        varchar title
        varchar email
        varchar linkedin
        boolean is_primary
        timestamptz created_at
        timestamptz updated_at
    }

    OUTREACH_ATTEMPTS {
        uuid id PK
        uuid firm_id FK
        uuid contact_id FK
        varchar method
        varchar status
        timestamptz sent_at
        timestamptz replied_at
        boolean meeting_booked
        text notes
        timestamptz created_at
        timestamptz updated_at
    }

    NOTES {
        uuid id PK
        uuid firm_id FK
        text content
        varchar created_by
        timestamptz created_at
        timestamptz updated_at
    }

    FIRMS ||--o{ CONTACTS : has
    FIRMS ||--o{ OUTREACH_ATTEMPTS : receives
    FIRMS ||--o{ NOTES : has
    CONTACTS ||--o{ OUTREACH_ATTEMPTS : targeted_by
```

## ASCII ERD

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                FIRMS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ PK │ id                │ uuid           │ UUID primary key              │
│    │ name              │ varchar(255)   │ Firm name                     │
│    │ website           │ varchar(512)   │ Website URL                   │
│    │ location          │ varchar(255)   │ Office location               │
│    │ check_size_min    │ numeric(15,2)  │ Min check size (USD)          │
│    │ check_size_max    │ numeric(15,2)  │ Max check size (USD)          │
│    │ stage_focus       │ varchar[]      │ Investment stages             │
│    │ sector_focus      │ varchar[]      │ Sectors of interest           │
│    │ aum               │ numeric(15,2)  │ Assets under management       │
│    │ created_at        │ timestamptz    │ Creation timestamp            │
│    │ updated_at        │ timestamptz    │ Last update timestamp         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────────┐  ┌─────────────┐
│      CONTACTS       │  │   OUTREACH_ATTEMPTS     │  │    NOTES    │
├─────────────────────┤  ├─────────────────────────┤  ├─────────────┤
│ PK │ id             │  │ PK │ id                 │  │ PK │ id     │
│ FK │ firm_id        │  │ FK │ firm_id            │  │ FK │ firm_id│
│    │ name           │  │ FK │ contact_id         │  │    │ content│
│    │ title          │  │    │ method             │  │    │ created│
│    │ email          │  │    │ status             │  │    │ created│
│    │ linkedin       │  │    │ sent_at            │  │    │ updated│
│    │ is_primary     │  │    │ replied_at         │  └─────────────┘
│    │ created_at     │  │    │ meeting_booked     │
│    │ updated_at     │  │    │ notes              │
└─────────────────────┘  │    │ created_at         │
           │             │    │ updated_at         │
           │             └─────────────────────────┘
           │                         ▲
           └─────────────────────────┘
              (contact_id FK)
```

## Relationship Summary

| Parent | Child | Cardinality | On Delete | Description |
|--------|-------|-------------|-----------|-------------|
| firms | contacts | 1:N | CASCADE | Firm has many contacts |
| firms | outreach_attempts | 1:N | CASCADE | Firm receives many outreach attempts |
| firms | notes | 1:N | CASCADE | Firm has many notes |
| contacts | outreach_attempts | 1:N | SET NULL | Contact targeted by outreach |

## Constraints

- **Unique**: Only one primary contact per firm (`is_primary = TRUE`)
- **Check**: Outreach method must be one of: email, linkedin, twitter, warm_intro, phone, in_person, other
- **Check**: Outreach status must be one of: draft, sent, delivered, opened, replied, bounced, unsubscribed, no_response
