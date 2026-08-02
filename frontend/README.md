# HoneyDesk frontend

Next.js App Router UI for the HoneyDesk defensive honeypot.

## Routes

| Route | Purpose | API |
|-------|---------|-----|
| `/` | Product landing | — |
| `/dashboard` | Ops desk (feed, pipeline, brief, replay, export) | `GET /events`, `GET /events/{id}`, `GET /stats`, `POST /simulate`, `GET /export/stix/{id}` |
| `/decoy/portal` | P0 credential-harvest trap | `POST /capture` |
| `/decoy/scholarship` | P1 urgency/PII trap | `POST /capture` |
| `/decoy/discord` | P1 social-verify trap | `POST /capture` |

Live updates use **1s polling** of `GET /events` (backend has no `/stream` SSE yet).

## Setup

```bash
cp .env.example .env.local
npm install
npm run dev
```

Requires the API on `NEXT_PUBLIC_API_URL` (default `http://127.0.0.1:8000`) with CORS allowing `http://localhost:3000`. Set `NEXT_PUBLIC_SIMULATE_TOKEN` to match backend `SIMULATE_TOKEN`.

## Design system (summary)

- **Accent:** `#F9E8A2` (honey) for highlights, selected rows, technique chips — never body text on white
- **Neutrals:** warm paper background `#F7F6F2`, surface `#FFFCF7`, ink `#1C1917`, muted stone grays
- **Typography:** Syne (headings/brand), Figtree (body), Geist Mono (IDs/IPs)
- **Spacing:** Tailwind 4px scale; page gutters via `px-page` (`clamp(1rem, 3vw, 2rem)`)
- **Components:** shadcn/ui (Radix) only
