# HoneyDesk — Sprint Build Plan (Several Hours)


| Field          | Value                                                |
| -------------- | ---------------------------------------------------- |
| **Companion**  | [PRD.md](./PRD.md) · [TRD.md](./TRD.md)              |
| **Assumption** | Solo or 2 people · **~6 hours** nonstop              |
| **Goal**       | Working trap-spring demo + deploy + video-ready path |
| **Rule**       | If behind schedule, cut down — never cut the spring  |


---

## 0. North Star (do not negotiate)

**90-second demo must work:**

1. Open dashboard
2. Open portal decoy → submit fake login
3. Dashboard row detonates + pipeline steps animate
4. Victim brief appears
5. Click Replay SC-2 / SC-3
6. Download “Share with school IT” JSON

If anything else is unfinished, **ship anyway**.

---



## 1. Time Budget (6-hour default)


| Block                          | Time      | Outcome                            |
| ------------------------------ | --------- | ---------------------------------- |
| **B0** Setup                   | 0:00–0:30 | Repo runs locally                  |
| **B1** Capture + decoy         | 0:30–1:45 | Portal submit creates event        |
| **B2** Pipeline + dashboard    | 1:45–3:30 | Live feed + classify + pipeline UI |
| **B3** Brief + replay + export | 3:30–4:45 | AI brief, SC-1..3, STIX download   |
| **B4** Polish + deploy + video | 4:45–6:00 | Public URL, dry runs, record       |


**Checkpoints (kill features if red):**


| Gate | By   | Must be true                                                  |
| ---- | ---- | ------------------------------------------------------------- |
| G-A  | 1:45 | Portal → DB event exists                                      |
| G-B  | 3:30 | Dashboard shows new event without refresh (SSE or 1s poll OK) |
| G-C  | 4:45 | Replay + brief + export work                                  |
| G-D  | 5:30 | Deployed URL works OR localhost recording backup ready        |


---



## 2. Panic Paths



### If you only have **~3 hours**

Ship **monolith FastAPI + Jinja/HTMX** (skip Next.js):

1. One portal HTML page
2. In-memory/SQLite events
3. Dashboard page with poll every 1s (skip SSE)
4. Rules classifier only
5. **Cached briefs only** (no live LLM required)
6. Replay 3 buttons
7. JSON export
8. Record from localhost if deploy fails



### If you have **~8 hours**

After G-C, add in order:

1. Scholarship decoy (SC-2 live, not just replay)
2. Simple map + technique breakdown
3. Discord verify decoy
4. IT brief toggle
5. Render deploy polish + README

---



## 3. Cut List (do not touch until G-C is green)

**Cut immediately if behind:**

- LangGraph (use linear `runner.py`)  
- Real geo IP APIs (hardcode scenario geo)  
- Discord bot, typosquat, leaderboard, ATT&CK  
- Auth, rate limits beyond basics  
- pytest suite (manual checklist only)  
- Perfect STIX validity  
- Beautiful marketing landing page  
- Mobile layout

**Never cut:**

- Portal decoy  
- Redaction (no plaintext passwords)  
- Technique tags on events  
- Pipeline visibility (even fake step timing is OK)  
- Replay SC-1..SC-3  
- Victim brief (cached OK)  
- Export button

---



## 4. Recommended Stack for Speed

**Default for 6h (matches TRD, slightly simplified):**


| Piece        | Choice                                                   | Why                              |
| ------------ | -------------------------------------------------------- | -------------------------------- |
| FE           | Next.js one app: `/dashboard` + `/decoy/portal`          | One deploy surface               |
| BE           | FastAPI                                                  | Fast SSE/JSON                    |
| DB           | SQLite file                                              | Zero setup                       |
| Live updates | SSE **or** poll `/events` every 1s                       | Poll is fine if SSE burns time   |
| Briefs       | Cached JSON first → LLM if time                          | Demo never depends on API        |
| Agents UI    | Emit step events with `asyncio.sleep(0.2)` between steps | Looks multi-agent even if linear |


**Solo speed tip:** If Next.js setup is slow, do **FastAPI + Jinja** for everything and spend saved hour on decoy polish + video.

---



## 5. Hour-by-Hour Checklist



### B0 — Setup (30 min)

- [ ] Create `backend/` + `frontend/` (or monolith)  
- [ ] `uvicorn` health `GET /health` → `{"ok": true}`  
- [ ] FE runs; can open blank `/dashboard` and `/decoy/portal`  
- [ ] `.env` with `OPENAI_API_KEY` (optional until B3)  
- [ ] Commit: `chore: skeleton`

**Exit:** both servers up.

---



### B1 — Capture + Portal (75 min)

**Backend**

- [ ] `POST /capture` accepts `{decoy_id, fields_present, password_entered, ...}`  
- [ ] Redact: drop any password/ssn fields before save  
- [ ] Insert row into SQLite `events`  
- [ ] Return `{event_id}`  

**Frontend**

- [ ] Portal looks like a boring school/aid login (credible, not meme)  
- [ ] Submit → POST `/capture` with `password_entered: true` (do **not** send password)  
- [ ] Show “Unable to verify, try again later”  

**Gate G-A:** submit once → confirm row in DB/`GET /events`.

**If late:** ugly HTML form is fine; polish later.

---



### B2 — Pipeline + Dashboard (105 min)

**Backend**

- [ ] `classify.py` rules: portal+password → `credential_harvest` / high  
- [ ] `enrich.py`: `data_targeted`, fake geo label  
- [ ] `runner.py`: capture → classify → enrich → persist; emit step events  
- [ ] `GET /events`, `GET /events/{id}`, `GET /stats`  
- [ ] Live: `GET /stream` SSE **or** skip and document polling  

**Frontend dashboard**

- [ ] Stats bar: attacks caught  
- [ ] Event feed (newest top); highlight newest 2s  
- [ ] Detail panel: technique, severity, reasons, data targeted  
- [ ] Pipeline panel: Capture → Classify → Enrich → Brief (Brief can be pending)  

**Gate G-B:** submit portal → feed updates without manual full reload.

**If late:** polling every 1s; hardcode pipeline animation on new event.

---



### B3 — Brief + Replay + Export (75 min)

**Scenarios (do these files first — 15 min)**

- [ ] `SC-1` credential harvest (portal)  
- [ ] `SC-2` urgency PII (scholarship fields)  
- [ ] `SC-3` social verify (discord)  
- [ ] Each has `expected_technique` + `cached_brief_victim`  

**Backend**

- [ ] `POST /simulate` `{scenario_id}` runs same runner with `source=replay`  
- [ ] Brief step: use cache always for SC-*; try LLM for live if key present  
- [ ] `GET /export/stix/{id}` returns downloadable JSON bundle  

**Frontend**

- [ ] Buttons: Replay SC-1 / SC-2 / SC-3  
- [ ] Brief card in detail panel  
- [ ] “Share with school IT” download  

**Gate G-C:** all three replays produce correct technique + brief + export works on one event.

**If late:** skip live LLM entirely; cache-only briefs still win the AI story if pipeline shows a Brief step.

---



### B4 — Polish + Deploy + Video (75 min)

**T-75 to T-40 — Polish (35 min)**

- [ ] Dashboard ethics footer one-liner  
- [ ] Technique colors / severity badges  
- [ ] Seed stats baseline so counter doesn’t show `1`  
- [ ] Decoy CSS pass (15 min max)  
- [ ] Home page: name + one sentence + links  

**T-40 to T-15 — Deploy (25 min)**

- [ ] Deploy API + FE (Render preferred)  
- [ ] Set env vars / CORS  
- [ ] Hit Replay SC-1 on prod  
- [ ] If deploy fails → record localhost; keep trying deploy after video  

**T-15 to T-0 — Video + dry runs (15 min)**

- [ ] 3 dry runs of the 90s script  
- [ ] Record 3–5 min Devpost video (script below)  
- [ ] README: what it is, how to run, ethics, architecture diagram one paragraph  

**Gate G-D:** judges can open a URL **or** video shows full working path clearly.

---



## 6. Demo Script (memorize / teleprompter)

```
0:00  Students get fake scholarship + portal scams — not movie hackers.
0:10  This is HoneyDesk: a defensive honeypot for student threats.
0:20  Here's a fake aid/student login. I'll submit a test account.
0:35  Dashboard springs: credential harvest, high severity.
0:50  Pipeline: Capture → Classify → Enrich → Brief.
1:00  Plain-English brief: what happened + what to do.
1:10  Replay scholarship + Discord scenarios.
1:20  Export STIX for school IT. Trap → teach → brief.
```

---



## 7. Parallelization (2 people)


| Person A (backend)            | Person B (frontend)             |
| ----------------------------- | ------------------------------- |
| Capture, DB, classify, runner | Portal decoy UI                 |
| Simulate + scenarios JSON     | Dashboard shell + feed          |
| Brief + STIX                  | Pipeline panel + replay buttons |
| Deploy API                    | Deploy FE + video assist        |


Sync every **30 minutes** at gates G-A/B/C.

**Solo order:** B0 → B1 FE+BE together → B2 BE then FE → B3 → B4.

---



## 8. Definition of Ship (minimum)

You may submit when **all** are true:

- [ ] Portal decoy submits safely (no plaintext password stored)  
- [ ] Dashboard shows technique + severity  
- [ ] Pipeline steps visible for an event  
- [ ] Victim brief shown (cached OK)  
- [ ] SC-1, SC-2, SC-3 replay work  
- [ ] Export JSON downloads  
- [ ] Ethics note in README/UI  
- [ ] Video recorded  

Everything else is bonus.

---



## 9. Bonus Order (only after ship checklist)

1. Live LLM briefs for non-scenario captures
2. Scholarship decoy page wired to capture
3. Mini attack map
4. Discord decoy page
5. Leaderboard
6. Compare raw JSON vs brief toggle

---



## 10. Emergency Snippets (decisions pre-made)


| Question                       | Answer                               |
| ------------------------------ | ------------------------------------ |
| SSE broken?                    | Poll `/events` every 1s              |
| No OpenAI key?                 | Cached briefs only                   |
| Next.js slow?                  | FastAPI + Jinja monolith             |
| Deploy down?                   | Localhost video + GitHub README GIFs |
| Classifier unsure?             | Rules only; ignore ML                |
| Two decoys or one?             | **One live decoy + three replays**   |
| Pretty UI or working pipeline? | Working pipeline                     |


---



## 11. File Priority Order (create in this sequence)

1. `backend/app/main.py` — health + routers
2. `backend/app/models/db.py` — events table
3. `backend/app/services/redact.py`
4. `backend/app/api/routes_capture.py`
5. `frontend/.../decoy/portal/page.tsx`
6. `backend/app/pipeline/classify.py`
7. `backend/app/pipeline/runner.py`
8. `frontend/.../dashboard/page.tsx` + feed/pipeline components
9. `backend/app/scenarios/sc1..sc3.json`
10. `backend/app/api/routes_simulate.py`
11. `backend/app/pipeline/brief.py`
12. `backend/app/services/stix_export.py`
13. README + ethics

Do not create P1 decoy pages before item 12 works.

---



## 12. Now → First Command

Start the clock:

1. Scaffold backend health + frontend routes (B0)
2. Do not reread PRD end-to-end — only open this file + TRD API section when stuck
3. Next human message after setup should be: **“G-A status”** (pass/fail)

**Ship the spring. Everything else is decoration.**