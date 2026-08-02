# HoneyDesk — Agent Guidelines

Project-wide notes for AI-assisted development in this monorepo.

## Context files (read at session start)

- [docs/features.md](docs/features.md) — what's built, in progress, planned
- [docs/errors.md](docs/errors.md) — past bugs and approaches that failed
- [docs/architecture.md](docs/architecture.md) — repo layout and data flow
- [docs/PRD.md](docs/PRD.md) / [docs/TRD.md](docs/TRD.md) — product and technical requirements

## Repository layout

- `backend/` — FastAPI API (Python). Entry: `app.main:app`
- `frontend/` — Next.js App Router (TypeScript). Entry: `src/app/`
- `docs/` — All documentation and dev-context markdown

## Frontend (Next.js)

<!-- BEGIN:nextjs-agent-rules -->
This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `frontend/node_modules/next/dist/docs/` before writing Next.js code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

- shadcn/ui components live in `frontend/src/components/ui/`
- API client: `frontend/src/lib/api.ts`
- Env: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SIMULATE_TOKEN`

## Backend (FastAPI)

- Never store plaintext passwords — redact in `app/services/redact.py`
- Pipeline: capture → classify (rules) → enrich → brief (LLM/cache)
- Tests: `cd backend && pytest`

## Conventions

- Minimize scope; match existing patterns in each package
- Demo path first: portal → dashboard → brief → replay → export
- Do not commit secrets, `.env` files, or local databases
