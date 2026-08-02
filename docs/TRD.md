# HoneyDesk — Technical Requirements Document (TRD)

| Field | Value |
|-------|-------|
| **Product** | HoneyDesk |
| **Companion** | [PRD.md](./PRD.md) |
| **Version** | 1.0 MVP |
| **Status** | Ready for build |
| **Last updated** | 2026-08-02 |

This TRD specifies **how** to build HoneyDesk. Prefer the smallest architecture that ships a reliable trap-spring demo.

---

## 1. System Overview

```
┌──────────────────────┐     ┌──────────────────────┐
│  Decoy: Portal Login  │     │ Decoy: Aid Form (P1)  │
│  Decoy: Discord (P1)  │     │  Simulate / Replay    │
└──────────┬───────────┘     └──────────┬───────────┘
           │ POST /capture               │ POST /simulate
           └──────────────┬──────────────┘
                          ▼
                 ┌─────────────────┐
                 │  FastAPI Core   │
                 │  Capture · Bus  │
                 └────────┬────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   Rule Classifier   Enrichment      LLM Agents
   (deterministic)   (geo/UA/etc)    (Brief · Explain)
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                   Event Store (SQLite)
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
     SSE → Ops Dashboard      STIX / JSON Export
```

**Design rules:**

1. Rules classify first; LLM explains second.
2. Replay/simulate use the **same pipeline** as live captures.
3. Secrets are redacted at the capture boundary.
4. Demo failover: cached briefs for SC-1..SC-3.

---

## 2. Recommended Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Decoys + Dashboard FE | Next.js 15 (App Router) + TypeScript + Tailwind | Fast polish, easy deploy |
| API | Python 3.11+ · FastAPI · Uvicorn | Quick SSE + agents |
| DB | SQLite (`aiosqlite` or SQLModel) | Zero ops |
| Realtime | SSE from FastAPI | Simple live feed |
| LLM | OpenAI-compatible (`gpt-4o-mini` or equiv.) | Cheap briefs |
| Optional agents | LangGraph **or** linear async pipeline | Linear OK if steps emit events |
| Geo (optional) | Static demo coords or free IP API | Map drama |
| STIX | Hand-built JSON (stix2 lib optional) | Good enough for MVP |
| Deploy | Render (API + web) | Sponsor-friendly |
| Package | `uv`/`pip` + `pnpm`/`npm` | Keep simple |

**Note:** A single Next.js app can host decoy routes + dashboard; API can be FastAPI sibling. Monolith FastAPI+Jinja is acceptable if faster for the team — keep API contracts below.

---

## 3. Repository Structure

```
STEMist-hacks/
├── docs/
│   ├── PRD.md
│   └── TRD.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── routes_capture.py
│   │   │   ├── routes_events.py
│   │   │   ├── routes_simulate.py
│   │   │   └── routes_export.py
│   │   ├── pipeline/
│   │   │   ├── runner.py           # orchestrates steps + SSE fanout
│   │   │   ├── classify.py         # deterministic rules + score
│   │   │   ├── enrich.py
│   │   │   ├── brief.py            # LLM victim/IT briefs
│   │   │   └── steps.py            # step event types
│   │   ├── models/
│   │   │   ├── schemas.py
│   │   │   └── db.py
│   │   ├── services/
│   │   │   ├── redact.py
│   │   │   ├── stix_export.py
│   │   │   └── geo.py
│   │   └── scenarios/
│   │       ├── sc1_credential_harvest.json
│   │       ├── sc2_urgency_pii.json
│   │       └── sc3_social_verify.json
│   ├── tests/
│   │   ├── test_classify.py
│   │   ├── test_redact.py
│   │   └── test_stix.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                 # marketing/home optional
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── decoy/portal/page.tsx
│   │   │   ├── decoy/scholarship/page.tsx
│   │   │   └── decoy/discord/page.tsx
│   │   ├── components/
│   │   │   ├── EventFeed.tsx
│   │   │   ├── EventDetail.tsx
│   │   │   ├── PipelinePanel.tsx
│   │   │   ├── AttackMap.tsx
│   │   │   ├── BriefCard.tsx
│   │   │   ├── StatsBar.tsx
│   │   │   └── ReplayControls.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── hooks/
│   │       └── useEventStream.ts
│   ├── package.json
│   └── README.md
├── .env.example
└── README.md
```

---

## 4. Domain Model

### 4.1 Technique enum

```ts
type Technique =
  | "credential_harvest"
  | "urgency_pii_scam"
  | "social_verify"
  | "typosquat"
  | "bot_probe"
  | "unknown";

type Severity = "low" | "medium" | "high" | "critical";
```

### 4.2 Capture (ingress)

```ts
type CaptureRequest = {
  decoy_id: "portal" | "scholarship" | "discord" | string;
  path?: string;
  fields_present: string[];          // e.g. ["email","password"]
  password_entered?: boolean;
  email_domain?: string | null;      // optional, never full secrets
  meta?: {
    dwell_ms?: number;
    referrer?: string;
    campaign?: string;
  };
  // password plaintext MUST NOT be accepted in production path;
  // if sent by mistake, redact service drops it immediately
};
```

### 4.3 Event (stored)

```ts
type HoneyEvent = {
  id: string;
  created_at: string;
  source: "live" | "simulate" | "replay";
  scenario_id?: "SC-1" | "SC-2" | "SC-3";
  decoy_id: string;
  ip: string;
  user_agent: string;
  geo?: { lat: number; lon: number; label: string };
  fields_present: string[];
  password_entered: boolean;
  technique: Technique;
  severity: Severity;
  score: number;                     // 0-100
  reasons: string[];
  data_targeted: string[];           // e.g. ["school_email","password"]
  brief_victim?: string;
  brief_it?: string;
  pipeline_status: "running" | "complete" | "failed";
};
```

### 4.4 Pipeline events (SSE)

```ts
type PipelineStep =
  | "capture"
  | "classify"
  | "enrich"
  | "brief"
  | "persist"
  | "end";

type StreamEvent = {
  type: "step_start" | "step_end" | "event_upsert" | "stats" | "error" | "done";
  event_id?: string;
  step?: PipelineStep;
  status?: "running" | "ok" | "failed" | "skipped";
  detail?: string;
  payload?: unknown;
  ts: string;
};
```

---

## 5. Pipeline Specification

### 5.1 Step order

```
capture_boundary (redact)
    → classify (rules, deterministic)
    → enrich (UA parse, geo, data_targeted)
    → brief (LLM; cache hit for scenarios)
    → persist
    → notify SSE subscribers
```

Emit `step_start` / `step_end` around each stage.

### 5.2 Classification rules (P0 — must be unit tested)

File: `pipeline/classify.py`

| Signal | Weight / effect |
|--------|-----------------|
| `decoy_id == portal` + `password_entered` | → `credential_harvest`, severity ≥ high |
| `decoy_id == scholarship` + fields include ssn/bank/routing | → `urgency_pii_scam`, severity critical |
| `decoy_id == discord` + verify CTA path | → `social_verify`, severity high |
| Bot UA keywords (`curl`, `python-requests`, empty UA) | add `bot_probe` reason; may dual-tag |
| Extremely fast dwell_ms (&lt;300ms) | bot suspicion reason |
| Unknown decoy | `unknown`, medium |

**Contract:** Seeded scenarios SC-1..SC-3 must map to their PRD techniques with **100%** rule accuracy (no LLM required for tag).

LLM may refine `reasons` copy but must not override seeded technique tags for SC-* replays unless explicitly in “live experimental” mode.

### 5.3 Enrichment

- Parse UA → browser/OS family string  
- Geo: if no real IP intel, use **deterministic demo geo** from IP hash or scenario file  
- `data_targeted` derived from `fields_present` + decoy type:

| fields / decoy | data_targeted |
|----------------|---------------|
| email + password | `school_email`, `password` |
| ssn | `ssn` |
| bank / routing | `bank_account` |
| discord verify | `discord_account`, `session_token_risk` |

### 5.4 Brief generation

**Inputs:** technique, severity, reasons, data_targeted, decoy_id, geo label  

**Output JSON:**

```json
{
  "victim": "… ≤120 words …",
  "it": "… optional …",
  "actions": ["…", "…", "…"]
}
```

**System constraints:**

- Age-appropriate, calm, specific  
- No graphic content  
- Always include 2–3 concrete actions  
- Mention this was a honeypot/training catch when `source != live` if useful for honesty in operator UI (victim brief can say “this kind of page”)  

**Failover:** `scenarios/scN_*.json` includes `cached_brief_victim`. On LLM error, use cache and mark `brief_source: cache`.

### 5.5 Optional LangGraph

If using LangGraph, nodes = steps above with shared state. A linear `runner.py` is equally acceptable for MVP if SSE parity is maintained.

---

## 6. API Contracts

Base URL: `http://localhost:8000`

### 6.1 `GET /health`

```json
{ "ok": true, "version": "0.1.0" }
```

### 6.2 `POST /capture`

Headers: standard. IP from `X-Forwarded-For` if trusted proxy, else socket peer.

**Request**

```json
{
  "decoy_id": "portal",
  "path": "/login",
  "fields_present": ["email", "password"],
  "password_entered": true,
  "email_domain": "gmail.com",
  "meta": { "dwell_ms": 8400, "campaign": "demo" }
}
```

**Response 201**

```json
{ "event_id": "uuid", "status": "accepted" }
```

Pipeline runs async after accept; clients follow SSE.

### 6.3 `POST /simulate`

Trusted demo endpoint (protect with `SIMULATE_TOKEN` header in prod deploy).

```json
{ "scenario_id": "SC-1" }
```

Loads scenario fixture, runs full pipeline with `source: replay`.

### 6.4 `GET /events`

Query: `?limit=50`  

Returns newest events (without internal debug).

### 6.5 `GET /events/{id}`

Full event detail including briefs.

### 6.6 `GET /stream` (SSE)

Subscribes to global stream of `StreamEvent`s. On connect, optionally replay last N `event_upsert`s.

### 6.7 `GET /stats`

```json
{
  "attacks_caught": 12,
  "by_technique": { "credential_harvest": 5, "urgency_pii_scam": 4, "social_verify": 3 },
  "last_event_at": "…"
}
```

Seeded baseline counter allowed for demo drama (document as including simulated weekend traffic) **or** derive strictly from DB — pick one and label UI honestly (“including replays” vs “live only”).

### 6.8 `GET /export/stix/{event_id}`

Returns STIX 2.1-shaped bundle JSON file download.

### 6.9 Errors

| Code | When |
|------|------|
| 400 | Invalid payload / empty fields |
| 401 | Bad simulate token |
| 404 | Unknown event/scenario |
| 413 | Oversized body |
| 500 | Unhandled (no secrets in body) |

---

## 7. Redaction & Security Controls

File: `services/redact.py`

| Rule | Behavior |
|------|----------|
| Drop keys `password`, `pass`, `token`, `ssn`, `routing` from any ingress dict | Delete before persist |
| If password string appears in logs | scrub |
| Store `password_entered: bool` only | — |
| Email: optional store domain only | `email_domain` |
| Simulate token required on public deploy | env `SIMULATE_TOKEN` |
| CORS allowlist | dashboard + decoy origins |
| Rate limit `/capture` | e.g. 60/min/IP |
| No endpoint for bulk email send / target upload | hard non-feature |

### 7.1 Ethics engineering

- Dashboard footer: authorized training / defensive honeypot notice  
- README section: acceptable use  
- Decoy interstitial after submit may educate (“You just interacted with a security demo honeypot”) **or** stay silent for immersion during judge demo — **default for recorded demo:** stay immersive on decoy; educate on dashboard  

---

## 8. STIX Export Spec (MVP)

Produce a bundle roughly like:

```json
{
  "type": "bundle",
  "id": "bundle--…",
  "objects": [
    {
      "type": "indicator",
      "id": "indicator--…",
      "pattern": "[ipv4-addr:value = '1.2.3.4']",
      "pattern_type": "stix",
      "valid_from": "…"
    },
    {
      "type": "attack-pattern",
      "id": "attack-pattern--…",
      "name": "Credential Harvest via Fake Student Portal",
      "description": "…"
    },
    {
      "type": "observed-data",
      "id": "observed-data--…",
      "first_observed": "…",
      "last_observed": "…",
      "number_observed": 1,
      "objects": {}
    }
  ]
}
```

Exact STIX validity can be best-effort; button label remains “Share with school IT”. Unit test: JSON has `type=bundle` and ≥1 object.

---

## 9. Scenario Fixtures

Example `sc1_credential_harvest.json`:

```json
{
  "scenario_id": "SC-1",
  "decoy_id": "portal",
  "ip": "203.0.113.50",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)",
  "geo": { "lat": 40.71, "lon": -74.00, "label": "New York, US" },
  "fields_present": ["email", "password"],
  "password_entered": true,
  "email_domain": "studentmail.org",
  "meta": { "dwell_ms": 9200, "campaign": "seed" },
  "expected_technique": "credential_harvest",
  "expected_severity": "high",
  "cached_brief_victim": "This page copied the look of a student aid portal to steal login credentials. If you entered a real password anywhere like this, change it and enable 2FA. Schools and aid offices do not ask you to sign in through random text links. Report the message to a trusted adult or school IT."
}
```

SC-2 / SC-3 analogous with their expected techniques.

---

## 10. Frontend Spec

### 10.1 Routes

| Route | Purpose |
|-------|---------|
| `/dashboard` | Ops desk (primary demo) |
| `/decoy/portal` | P0 trap |
| `/decoy/scholarship` | P1 trap |
| `/decoy/discord` | P1 trap |
| `/` | Short pitch + links to dashboard/decoy |

### 10.2 Dashboard layout (1280×720 safe)

```
┌─────────────────────────────────────────────────────────────┐
│ HoneyDesk   attacks: N    [Replay SC-1][SC-2][SC-3][Sim]   │
├───────────────────────────────┬─────────────────────────────┤
│ Event feed (live)             │ Pipeline panel              │
│                               │ Brief card                  │
│                               │ Data targeted               │
├───────────────────────────────┴─────────────────────────────┤
│ Map / technique breakdown / leaderboard (P1)                │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 Decoy UX

- Credible student/aid visual design (not meme quality)  
- On submit: POST `/capture`, then show generic failure or spinner → “Unable to verify, try again later”  
- Do not show operator dashboard link on the decoy during immersive demo  

### 10.4 Client stream

- `useEventStream` → `EventSource('/stream')`  
- Upsert events by id into local state  
- Highlight newest row for ~2s (the “detonation”)  

---

## 11. Data Storage

| Data | Store |
|------|-------|
| Events | SQLite table `events` (JSON column OK for briefs/reasons) |
| Stats | Derived query (+ optional `stats` table for seeded baseline) |
| Scenario files | Repo JSON |
| Secrets | None in DB |

Migrations: lightweight startup `CREATE TABLE IF NOT EXISTS`.

---

## 12. Configuration

`.env.example`

```bash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./data/honeydesk.db
CORS_ORIGINS=http://localhost:3000
SIMULATE_TOKEN=dev-simulate-token
TRUST_PROXY=false
BRIEF_FAILOVER_CACHE=true
SEED_STATS_BASELINE=9
```

---

## 13. Testing Requirements

### 13.1 Automated

```bash
cd backend && pytest -q
```

Must cover:

1. Redaction drops password fields  
2. SC-1..SC-3 classify to expected technique  
3. `/simulate` creates event with `source=replay`  
4. STIX export returns bundle JSON  

### 13.2 Manual dry-run checklist (5×)

- [ ] Portal submit → feed row &lt;2s  
- [ ] Pipeline steps visible  
- [ ] Victim brief present  
- [ ] Replay SC-1..SC-3  
- [ ] Export downloads  
- [ ] No plaintext password in DB/UI  
- [ ] Ethics note visible on dashboard  

---

## 14. Performance Budgets

| Path | Budget |
|------|--------|
| `/capture` accept | ≤100ms |
| Rules classify | ≤50ms |
| Event on SSE | ≤2s end-to-end |
| LLM brief | ≤5s (cache on scenarios for demo) |
| Dashboard initial load | ≤2s |

---

## 15. Deployment

### 15.1 Services

1. **API** — FastAPI on Render (persistent disk optional for SQLite)  
2. **Web** — Next.js on Render/Vercel pointing at API URL  

### 15.2 Demo env

- Set `SIMULATE_TOKEN`  
- Warm OpenAI key  
- Pre-load nothing critical beyond empty DB (replays inject)  
- Optional: run SC-1 once post-deploy to verify  

### 15.3 Failover

If LLM down: cached briefs. If SSE down: dashboard poll `GET /events` every 1s (fallback mode).

---

## 16. Build Phases (Execution Plan)

### Phase 0 — Hours 0–2: Skeleton

- [ ] Repo folders, health endpoint, Next app shell  
- [ ] `.env.example`  
- [ ] SQLite event table  

### Phase 1 — Hours 2–8: Capture + Portal decoy

- [ ] `/decoy/portal` polished enough for demo  
- [ ] `POST /capture` + redaction  
- [ ] Event persisted  

### Phase 2 — Hours 8–14: Pipeline + Dashboard

- [ ] classify + enrich  
- [ ] SSE stream  
- [ ] Event feed + detail + pipeline panel  
- [ ] Stats counter  

### Phase 3 — Hours 14–20: AI + Replay + Export

- [ ] Brief generation + cache failover  
- [ ] SC-1..SC-3 fixtures + simulate routes  
- [ ] Replay controls  
- [ ] STIX export button  

### Phase 4 — Hours 20–28: P1 polish + ship

- [ ] Scholarship and/or Discord decoy  
- [ ] Map / leaderboard if time  
- [ ] Tests green  
- [ ] Deploy  
- [ ] Record 3–5 min video  
- [ ] README (ethics, architecture, metrics)  

**Hard gate:** No P1 decoys until Phase 3 replay+brief works.

---

## 17. PRD ↔ TRD Traceability

| PRD | TRD |
|-----|-----|
| US-01..03 / FR-01,10 | Portal decoy + `/capture` |
| US-04 / FR-20..24 | `classify.py` + tests |
| US-05 / FR-30..34 | `brief.py` + cache |
| US-06 / FR-60..61 | scenarios + `/simulate` |
| US-07 / FR-42 | SSE pipeline steps |
| US-08 / FR-43 | `/stats` + StatsBar |
| US-09 / FR-50..52 | `stix_export.py` |
| US-10 / FR-62 | UI footer + README |
| G1–G6 | Phase gates + dry-run checklist |

---

## 18. Explicit Non-Requirements (Engineering)

- Cowrie/SSH/Telnet  
- Kubernetes / multi-region  
- Training custom DL malware models  
- Real phishing campaigns / mailers  
- Perfect STIX 2.1 validator compliance  
- Mobile-first UI  
- School SSO / OAuth IdPs (email/password + Bearer sessions + per-user `events.user_id` isolation are in MVP)  


---

## 19. Definition of Done

A feature is done when:

1. Maps to a PRD P0/P1 item  
2. Has test or checklist coverage  
3. Emits pipeline/SSE updates if on the event path  
4. Does not persist plaintext secrets  
5. Is visible in the rehearsed demo script  

**MVP Done** = all PRD P0 + deploy + video + README ethics/metrics.

---

## 20. Appendix A — Sample SSE Timeline (SC-1)

```json
[
  {"type":"step_start","step":"capture","event_id":"e1"},
  {"type":"step_end","step":"capture","status":"ok","detail":"redacted"},
  {"type":"step_start","step":"classify"},
  {"type":"step_end","step":"classify","status":"ok","detail":"credential_harvest score=91"},
  {"type":"step_start","step":"enrich"},
  {"type":"step_end","step":"enrich","status":"ok","detail":"geo=New York, US"},
  {"type":"step_start","step":"brief"},
  {"type":"step_end","step":"brief","status":"ok","detail":"victim_brief_ready"},
  {"type":"event_upsert","payload":{"id":"e1","technique":"credential_harvest","severity":"high"}},
  {"type":"stats","payload":{"attacks_caught":10}},
  {"type":"done"}
]
```

---

## 21. Appendix B — Open Technical Decisions

| Decision | Default | Change when |
|----------|---------|-------------|
| FE host for decoys | Same Next app | Need separate domains for realism |
| Agent framework | Linear pipeline + SSE | Team wants LangGraph explicitly |
| Geo | Scenario/static hash | Easy API key for live intel |
| Auth on dashboard | Email/password + Bearer session; per-user event isolation | Need school SSO / shared rooms |
| Stats baseline | `SEED_STATS_BASELINE` + DB count | Judges ask honesty → label UI |

---

## 22. Appendix C — Prompt Skeleton (Victim Brief)

```
You are a calm security coach for ages 13–19.
Given technique, severity, reasons, and data_targeted, write:
1) victim: <=120 words explaining what the scam page was trying to do
2) actions: 2-3 concrete next steps
Do not give illegal advice. Do not be graphic. Do not claim the user is already hacked.
Return JSON only.
```
