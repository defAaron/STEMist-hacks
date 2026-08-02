# HoneyDesk API

FastAPI deployment scaffold for the HoneyDesk defensive honeypot API.

## Runtime contract

- Python 3.12, FastAPI, and Uvicorn
- ASGI application: `app.main:app`
- Health check: `GET /health` must return HTTP 200 (the intended body is
  `{"ok": true, "version": "0.1.0"}`)
- Uvicorn listens on `0.0.0.0` and uses the platform-provided `PORT` (default
  `8000` locally)
- The image runs as an unprivileged `app` user

## Configuration

| Variable | Required | Example / purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes in deployed environments | `sqlite:////var/data/honeydesk.db`; the parent directory must exist and be writable |
| `CORS_ORIGINS` | Yes when the frontend is separate | Comma-separated exact origins, for example `https://honeydesk-web.onrender.com,http://localhost:3000` |
| `SIMULATE_TOKEN` | Yes on a public deployment | Secret checked by the replay/simulate endpoint |
| `TRUST_PROXY` | Recommended on Render | `true`, so trusted forwarded client information can be used |
| `BRIEF_FAILOVER_CACHE` | Recommended | `true`, so seeded scenarios do not depend on an LLM |
| `OPENAI_API_KEY` | No | Enables live LLM briefs when the application supports them |
| `OPENAI_MODEL` | No | Model selected by the briefing module |
| `PORT` | Platform-provided | Render injects this; local default is `8000` |

Do not use `CORS_ORIGINS=*` for the public deployment. Add every exact
frontend/decoy origin that calls the API, with no trailing slash. The
application configuration must parse `CORS_ORIGINS` and `DATABASE_URL`; the
deployment scaffold does not override application-level defaults.

SQLite is persisted on Render at `/var/data`. Do not use a relative production
database path: files elsewhere in the service filesystem are ephemeral.

## Run locally

With Python:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data
DATABASE_URL=sqlite:///./data/honeydesk.db \
CORS_ORIGINS=http://localhost:3000 \
SIMULATE_TOKEN=dev-only-token \
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

With Docker:

```bash
docker build -t honeydesk-api ./backend
docker volume create honeydesk-data
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=sqlite:////var/data/honeydesk.db \
  -e CORS_ORIGINS=http://localhost:3000 \
  -e SIMULATE_TOKEN=dev-only-token \
  -v honeydesk-data:/var/data \
  honeydesk-api
curl --fail http://localhost:8000/health
```

If a host bind mount is used instead of a named volume, make that directory
writable by the image's non-root user.

## Deploy to Render

The repository-root `render.yaml` Blueprint defines:

1. **honeydesk-api** — Docker FastAPI service + 1 GB disk at `/var/data`
2. **honeydesk-web** — Node Next.js service (`frontend/`) wired to the API

In Render: **New → Blueprint →** select this repo. Both services use the paid
`starter` plan (persistent disk for SQLite; avoids free-tier spin-down during
demo). Render generates `SIMULATE_TOKEN` on the API and injects the same value
into the web service as `NEXT_PUBLIC_SIMULATE_TOKEN`.

Default hostnames assumed by the Blueprint:

| Service | URL |
| --- | --- |
| API | `https://honeydesk-api.onrender.com` |
| Web | `https://honeydesk-web.onrender.com` |

If you rename a service, update `CORS_ORIGINS` (API) and `NEXT_PUBLIC_API_URL`
(web) to match, then redeploy the web service so the public URL is rebuilt into
the client bundle. Optional: add `OPENAI_API_KEY` on the API service for live
briefs (cached failover remains on by default).

After deployment:

```bash
export API_URL=https://honeydesk-api.onrender.com
export WEB_URL=https://honeydesk-web.onrender.com
curl --fail "$API_URL/health"
curl --fail -o /dev/null -w "%{http_code}\n" "$WEB_URL/"
```

Expected readiness is HTTP 200 from `/health` and the web root. Render should
not route API traffic until the health check succeeds. A failing check usually
means `app.main:app` could not import, the process did not bind to `PORT`, or
the database directory is not writable. Unauthenticated `GET /events` returning
401 is expected (auth required).

## Acceptable use

HoneyDesk is for authorized defensive training. Never collect real passwords,
tokens, SSNs, or banking details; ingress must discard secrets and persist only
safe flags or field names. Do not use this project for unsolicited targeting,
bulk messaging, or impersonation outside project-controlled demo surfaces.
