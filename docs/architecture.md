# HoneyDesk — Architecture

| Field | Value |
|-------|-------|
| **Companion** | [PRD.md](./PRD.md) · [TRD.md](./TRD.md) |
| **Last updated** | 2026-08-02 |

High-level map of the monorepo. See [TRD.md](./TRD.md) for full technical specs.

---

## Repository layout

```
STEMist-hacks/
├── README.md              # Project overview and quick start
├── render.yaml            # Render.com Blueprint (API + frontend)
├── docs/                  # Product, technical, and dev-context docs
├── backend/               # FastAPI API + pipeline + SQLite
│   ├── app/
│   │   ├── api/           # Route handlers (auth, capture, events, simulate, export)
│   │   ├── middleware/    # Rate limits, security headers
│   │   ├── models/        # DB models: users, sessions, events
│   │   ├── pipeline/      # Classify → Enrich → Brief runner
│   │   ├── scenarios/     # Seeded SC-1..SC-3 JSON fixtures
│   │   └── services/      # Auth, redaction, STIX export
│   ├── tests/
│   └── data/              # Local SQLite (gitignored)
└── frontend/              # Next.js App Router UI
    └── src/
        ├── app/           # Routes (landing, login/signup, dashboard, decoys)
        ├── components/    # UI, auth, dashboard, shared
        ├── hooks/         # Data fetching and capture submit
        └── lib/           # API client, auth token, types, formatters
```

---

## Data flow

```
Signup/Login (/signup, /login)
        │
        │ Bearer session token (sessionStorage)
        ▼
Decoy pages (/decoy/*)          Dashboard (/dashboard)
        │                                │
        │ POST /capture                  │ GET /events, /stats
        │ POST /simulate                 │ GET /export/stix/{id}
        └────────────┬───────────────────┘
                     ▼
              FastAPI (backend/app)
                     │  require_user → stamp/filter user_id
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    Classify     Enrich       Brief
    (rules)      (geo/UA)    (LLM/cache)
         │           │           │
         └───────────┼───────────┘
                     ▼
         SQLite (users, sessions, events.user_id)
```

**Design rules:**

1. Rules classify first; LLM explains second.
2. Replay/simulate uses the **same pipeline** as live captures.
3. Secrets are redacted at the capture boundary.
4. Demo failover: cached briefs for SC-1..SC-3.
5. Capture, simulate, dashboard reads, and export require auth and are scoped per user.

---

## Key environment variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | Backend | SQLite path (local: `./data/honeydesk.db`) |
| `CORS_ORIGINS` | Backend | Comma-separated frontend origins |
| `SIMULATE_TOKEN` | Backend + Frontend | Optional extra gate on replay |
| `SESSION_TTL_DAYS` | Backend | Bearer session lifetime (default 7) |
| `NEXT_PUBLIC_API_URL` | Frontend | API base URL |
| `NEXT_PUBLIC_SIMULATE_TOKEN` | Frontend | Must match backend token when set |
| `OPENAI_API_KEY` | Backend | Optional live LLM briefs |
| `BRIEF_FAILOVER_CACHE` | Backend | Use cached briefs when LLM unavailable |

---

## Local development

Run both services in separate terminals:

```bash
# Terminal 1 — API
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

See [backend/README.md](../backend/README.md) and [frontend/README.md](../frontend/README.md) for full setup.

---

## Deployment (Render)

| Service | Runtime | Notes |
|---------|---------|-------|
| `honeydesk-api` | Docker (`backend/Dockerfile`) | SQLite on `/var/data` disk; `APP_ENV=production` |
| `honeydesk-web` | Node (`frontend/`) | `NEXT_PUBLIC_API_URL` + simulate token from API |

Blueprint file: [`render.yaml`](../render.yaml). After first deploy, confirm CORS origin matches the web hostname and run the 90-second demo path once on the public URL.
