"""HoneyDesk FastAPI application."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_capture import router as capture_router
from app.api.routes_events import router as events_router
from app.api.routes_export import router as export_router
from app.api.routes_simulate import router as simulate_router
from app.models.db import init_db

VERSION = "0.1.0"
_LOCAL_ORIGINS = ("http://localhost:3000", "http://127.0.0.1:3000")


def _cors_origins(raw: str | None) -> list[str]:
    """Parse exact HTTP(S) origins and reject unsafe wildcard configuration."""

    values = raw.split(",") if raw is not None else list(_LOCAL_ORIGINS)
    origins: list[str] = []
    for candidate in values:
        origin = candidate.strip().rstrip("/")
        if not origin:
            continue
        parts = urlsplit(origin)
        if (
            origin == "*"
            or parts.scheme not in {"http", "https"}
            or not parts.netloc
            or parts.username is not None
            or parts.password is not None
            or parts.path
            or parts.query
            or parts.fragment
        ):
            raise RuntimeError("CORS_ORIGINS must contain exact HTTP(S) origins")
        normalized = f"{parts.scheme}://{parts.netloc}"
        if normalized not in origins:
            origins.append(normalized)
    return origins


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize the configured SQLite store before accepting traffic."""

    store = await asyncio.to_thread(init_db)
    try:
        yield
    finally:
        # File-backed stores open short-lived connections. This only releases
        # the keeper connection used by an explicitly configured memory store.
        store.close()


app = FastAPI(
    title="HoneyDesk API",
    version=VERSION,
    lifespan=lifespan,
)

origins = _cors_origins(os.getenv("CORS_ORIGINS"))
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Simulate-Token"],
    )

app.include_router(capture_router)
app.include_router(simulate_router)
app.include_router(events_router)
app.include_router(export_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, object]:
    return {"ok": True, "version": VERSION}
