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
├── render.yaml            # Render.com deployment (API)
├── docs/                  # Product, technical, and dev-context docs
├── backend/               # FastAPI API + pipeline + SQLite
│   ├── app/
│   │   ├── api/           # Route handlers (capture, events, simulate, export)
│   │   ├── middleware/    # Rate limits, security headers
│   │   ├── models/        # DB models and event store
│   │   ├── pipeline/      # Classify → Enrich → Brief runner
│   │   ├── scenarios/     # Seeded SC-1..SC-3 JSON fixtures
│   │   └── services/      # Redaction, STIX export
│   ├── tests/
│   └── data/              # Local SQLite (gitignored)
└── frontend/              # Next.js App Router UI
    └── src/
        ├── app/           # Routes (landing, dashboard, decoys)
        ├── components/    # UI, dashboard, shared
        ├── hooks/         # Data fetching and capture submit
        └── lib/           # API client, types, formatters
```

---

## Data flow

```
Decoy pages (/decoy/*)          Dashboard (/dashboard)
        │                                │
        │ POST /capture                  │ GET /events, /stats
        │ POST /simulate                 │ GET /export/stix/{id}
        └────────────┬───────────────────┘
                     ▼
              FastAPI (backend/app)
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    Classify     Enrich       Brief
    (rules)      (geo/UA)    (LLM/cache)
         │           │           │
         └───────────┼───────────┘
                     ▼
              SQLite event store
```

**Design rules:**

1. Rules classify first; LLM explains second.
2. Replay/simulate uses the **same pipeline** as live captures.
3. Secrets are redacted at the capture boundary.
4. Demo failover: cached briefs for SC-1..SC-3.

---

## Key environment variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | Backend | SQLite path (local: `./data/honeydesk.db`) |
| `CORS_ORIGINS` | Backend | Comma-separated frontend origins |
| `SIMULATE_TOKEN` | Backend + Frontend | Protects replay endpoint |
| `NEXT_PUBLIC_API_URL` | Frontend | API base URL |
| `NEXT_PUBLIC_SIMULATE_TOKEN` | Frontend | Must match backend token |
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
