# HoneyDesk — Features

> Living feature tracker for AI-assisted development.  
> Source: [Context Architecture talk](https://www.youtube.com/watch?v=33wGJy3vb9A) (Yogesh Kondaskar) — review at session start with [architecture.md](./architecture.md) and [PRD.md](./PRD.md).

**Last updated:** 2026-08-02

---

## Built ✅

### Backend (FastAPI + SQLite)

| Feature | Notes |
|---------|-------|
| `GET /health` | Health check |
| `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` | Email/password accounts; opaque Bearer sessions |
| `POST /capture` | Auth required; stamps `user_id`; redacts secrets; async pipeline |
| `POST /simulate` | Auth required (+ optional simulate token); per-user replay |
| `GET /events`, `GET /events/{id}`, `GET /stats` | Auth required; scoped to the caller’s events |
| `GET /export/stix/{id}` | Auth + ownership check (404 if not yours) |
| Capture → Classify → Enrich → Brief pipeline | Rules classifier; demo geo; cached/LLM/fallback briefs |
| Redaction layer | Never stores plaintext passwords / SSN |
| Seeded scenarios | `sc1.json`, `sc2.json`, `sc3.json` with cached victim briefs |
| Security middleware | Rate limits (incl. auth), timeouts, security headers, optional simulate token |
| Production lockdown | OpenAPI `/docs` off by default in `APP_ENV=production`; `SIMULATE_TOKEN` required |
| Tenant-scoped reads | `list_events` / `get_stats` always require `user_id` (app-level RLS) |
| Test suite | Auth isolation, capture safety, security hardening, classify, pipeline, STIX, DB |

### Frontend (Next.js App Router)

| Feature | Route / file |
|---------|--------------|
| Landing page | `/` — hero, features, FAQ, ethics; CTAs to signup/login |
| Signup / login | `/signup`, `/login` — session token in `sessionStorage` |
| Ops dashboard | `/dashboard` — gated; feed, stats, detail, pipeline, replay, export |
| Portal decoy (P0) | `/decoy/portal` — gated credential harvest trap |
| Scholarship decoy (P1) | `/decoy/scholarship` — urgency / PII form |
| Discord decoy (P1) | `/decoy/discord` — social verify landing |
| Live updates | Poll `/events` + `/stats` every 1s (Bearer auth) |
| Victim brief card | Plain-English brief per event |
| Replay controls | One-click SC-1 / SC-2 / SC-3 |
| STIX export button | “Share with school IT” download |
| Data-targeted panel | Shows fields attacker tried to steal |
| Ethics footer | Dashboard + landing |

### Demo path (90-second script)

1. Create account / log in → 2. Open dashboard → 3. Submit portal decoy → 4. Row detonates + pipeline steps → 5. Victim brief → 6. Replay SC-2 / SC-3 → 7. Export JSON

---

## In progress 🔄

| Feature | Status | Blocker / next step |
|---------|--------|---------------------|
| Render deploy (API + web) | Free-tier Blueprint (`plan: free`, no disk) | Push + create Blueprint; warm URLs; smoke signup → portal → replay → export |
| Demo video | Not recorded | 3 dry runs on deployed URL (localhost backup) then 3–5 min Devpost recording |

---

## Planned (P1 — if P0 demo solid) 📋

| ID | Feature | PRD ref |
|----|---------|---------|
| F-P1-01 | IT brief generation (not just UI tab) | US-16, FR-32 |
| F-P1-02 | Attack map (geo visualization) | US-12, FR-45 |
| F-P1-03 | Leaderboard strip | US-13, FR-46 |
| F-P1-04 | Raw JSON vs brief compare toggle | FR-63 |
| F-P1-05 | SSE live feed (`GET /stream`) | US-01 (optional; polling OK for MVP) |
| F-P1-06 | Dashboard links to scholarship + Discord decoys | UX polish |
| F-P1-07 | Ethics footer on decoy layout | FR-62 consistency |

---

## Backlog (P2 — only if ahead) 💡

- Typosquat teaching landing page (US-17)
- AbuseIPDB / external enrichment (US-18)
- MITRE ATT&CK mapping chips (US-19)
- Live Discord bot (US-20)
- PDF one-pager export (US-21)

---

## Session log

| Date | Added / changed |
|------|-----------------|
| 2026-08-02 | Initial tracker from codebase audit + PRD/BUILDPLAN |
| 2026-08-02 | Moved to `docs/`; root README added |
| 2026-08-02 | Per-user email/password auth + full event isolation |
| 2026-08-02 | Render Blueprint: API + Next.js web; deploy docs in root README |

---

## How to use this file

1. **Start of session:** Ask the AI to read `docs/features.md`, `docs/architecture.md`, and `docs/PRD.md`.
2. **End of session:** Update Built / In progress / Session log with what shipped.
3. **New idea:** Add to Planned or Backlog before prompting implementation.
