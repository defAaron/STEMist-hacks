# HoneyDesk — Errors & Lessons Learned

> Secret weapon for vibe coding: stop repeating the same fixes.  
> Source: [Context Architecture talk](https://www.youtube.com/watch?v=33wGJy3vb9A) (Yogesh Kondaskar) — review when fixing bugs or starting a debug session.

**Last updated:** 2026-08-02

Record here: bugs found, fixes that worked, approaches that **did not** work, and library/platform quirks.

---

## Active issues

_None blocking the demo path as of last dry run._

---

## Resolved

### E-001 — Dashboard shows event before brief is ready

| Field | Detail |
|-------|--------|
| **Symptom** | New capture appears in feed; detail panel opens with empty or pending brief |
| **Cause** | `POST /capture` returns `201` immediately; pipeline runs in `BackgroundTasks` |
| **Fix** | Poll `/events/{id}` until `brief_victim` populated, or wait 1–2 poll cycles (~2s) |
| **Do not** | Block capture response on LLM — demo needs fast trap spring |

### E-002 — IT brief tab always empty

| Field | Detail |
|-------|--------|
| **Symptom** | “No IT brief available for this event yet.” in `brief-card.tsx` |
| **Cause** | `brief.py` always sets `"it": None`; only victim brief implemented |
| **Fix** | Expected for MVP — use Victim tab for demo; implement IT brief in P1 |
| **Do not** | Remove IT tab without updating PRD — judges may expect the toggle exists |

### E-003 — Token / context exhaustion during long AI sessions

| Field | Detail |
|-------|--------|
| **Symptom** | AI forgets prior decisions; re-explains stack; fixes break earlier fixes |
| **Cause** | LLMs have no durable memory; harness auto-compacts context |
| **Fix** | Use this file + [features.md](./features.md) + [architecture.md](./architecture.md); start sessions with “review docs/errors.md and docs/features.md” |
| **Lesson** | Context architecture beats longer prompts (see video) |

---

## Approaches that did NOT work

### A-001 — Relying on chat history alone for project state

- **Tried:** Long conversational threads without structured markdown context files.
- **Result:** Repeated architecture mistakes, token waste, inconsistent naming.
- **Use instead:** [features.md](./features.md), [errors.md](./errors.md), and [architecture.md](./architecture.md).

### A-002 — SSE before demo path was green

- **Tried:** Prioritizing `GET /stream` over working poll-based dashboard.
- **Result:** BUILDPLAN explicitly cuts SSE if behind schedule.
- **Use instead:** 1s polling in `use-dashboard-data.ts` — acceptable per TRD/BUILDPLAN.

### A-003 — Live LLM briefs as demo dependency

- **Tried:** Requiring OpenAI key for every replay.
- **Result:** Demo fails if key missing or rate-limited.
- **Use instead:** `BRIEF_FAILOVER_CACHE=true` + cached briefs in `scenarios/sc*.json`.

### A-004 — Sending real passwords to `/capture`

- **Tried:** N/A — intentionally never implemented.
- **Why bad:** Ethics, PRD FR-12, judge disqualification risk.
- **Use instead:** `password_entered: true` + field names only; redact in `redact.py`.

---

## Platform / library quirks

### P-001 — FastAPI + SQLite on Render

- Persist SQLite to mounted disk in `render.yaml`; ephemeral filesystem loses events on restart.

### P-002 — CORS for local dev

- Backend needs `CORS_ORIGINS=http://localhost:3000` when frontend runs on `:3000`.
- Missing CORS → browser blocks `/capture` and dashboard looks “dead.”

### P-003 — Simulate endpoint token

- `X-Simulate-Token` only enforced when `SIMULATE_TOKEN` env is set.
- Local dev: `SIMULATE_TOKEN=dev-only-token` must match frontend header.

### P-004 — Next.js + backend split

- Frontend must know API base URL (env); default localhost `:8000` for dev.
- Do not assume same-origin unless proxied.

### P-005 — Decoy “failure” message is intentional

- `use-capture-submit.ts` always shows “Unable to verify” even on successful capture.
- **Not a bug** — honeypot should not confirm credentials to the attacker persona.

---

## Lessons learned (general)

1. **Ship the spring first** — portal → dashboard detonation → brief → replay → export. Everything else is decoration (BUILDPLAN north star).
2. **Rules classify, LLM explains** — never let the model pick technique tags for seeded scenarios; rules path is ≤100ms and deterministic.
3. **Same pipeline for live + replay** — judges trust simulate if it uses identical `runner.py`.
4. **Update this file when something breaks** — especially fixes the AI suggested that failed twice.

---

## Session log

| Date | Entry |
|------|-------|
| 2026-08-02 | Initial file from video framework + codebase / terminal audit |

---

## How to use this file

When debugging, prompt:

> Please review `docs/errors.md` for past bugs and approaches that did not work before fixing [issue].

When a fix lands or a dead end is confirmed, add a row under **Resolved**, **Approaches that did NOT work**, or **Platform quirks**.
