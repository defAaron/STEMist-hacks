# HoneyDesk

**Trap the scammer. Teach the student. Brief the school.**

HoneyDesk is a student-threat deception platform for [STEMist Hacks IV](https://stemist.io): fake student surfaces (portal login, scholarship form, Discord verify) that capture scam behavior, classify attacks in real time, and generate plain-English briefs plus STIX exports for school IT.

> **Ethics:** Authorized deception / training only. Never stores plaintext passwords. Demo uses seeded replay scenarios — not unsolicited phishing.

---

## Quick start

### Prerequisites

- Python 3.12+
- Node.js 20+

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit as needed
mkdir -p data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Create an account at `/signup`, then use `/dashboard` and `/decoy/portal` — each tester’s captures stay private.

---

## Repository structure

| Path | Purpose |
|------|---------|
| [`backend/`](backend/) | FastAPI API, capture pipeline, SQLite store, tests |
| [`frontend/`](frontend/) | Next.js App Router UI (landing, dashboard, decoys) |
| [`docs/`](docs/) | PRD, TRD, architecture, feature tracker, error log |
| [`render.yaml`](render.yaml) | Render.com Blueprint (API + frontend) |

See [docs/architecture.md](docs/architecture.md) for the full layout and data-flow diagram.

---

## Deploy (Render)

1. Push this repo to GitHub (if not already).
2. In [Render](https://dashboard.render.com): **New → Blueprint** → select the repo.
3. Apply the Blueprint (`honeydesk-api` + `honeydesk-web`, both `starter`).
4. Wait for both services to go live, then open `https://honeydesk-web.onrender.com`.
5. Smoke path: **Signup → Dashboard → Decoy portal submit → Replay SC-1 → Export STIX**.

```bash
curl --fail https://honeydesk-api.onrender.com/health
```

If you rename services, update `CORS_ORIGINS` / `NEXT_PUBLIC_API_URL` in
`render.yaml` (or the dashboard) and redeploy the web service so the new API
URL is baked into the client. Optional LLM: set `OPENAI_API_KEY` on the API
service; cached briefs work without it.

---

## 90-second demo path

1. Open `/dashboard`
2. Submit fake login at `/decoy/portal`
3. Watch the dashboard row detonate and pipeline steps animate
4. Read the victim brief
5. Click Replay SC-2 / SC-3
6. Download “Share with school IT” JSON

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/PRD.md](docs/PRD.md) | Product requirements |
| [docs/TRD.md](docs/TRD.md) | Technical requirements |
| [docs/architecture.md](docs/architecture.md) | Repo layout and system overview |
| [backend/README.md](backend/README.md) | API setup, env vars, Docker |
| [frontend/README.md](frontend/README.md) | Routes, design system, frontend env |

---

## License

Built for STEMist Hacks IV (Aug 2026). See event rules for submission and attribution requirements.
