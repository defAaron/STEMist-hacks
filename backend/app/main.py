"""HoneyDesk FastAPI application."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_auth import router as auth_router
from app.api.routes_capture import router as capture_router
from app.api.routes_events import router as events_router
from app.api.routes_export import router as export_router
from app.api.routes_simulate import router as simulate_router
from app.config import (
    FORCE_HTTPS,
    RATE_LIMIT_AUTH_PER_MINUTE,
    RATE_LIMIT_CAPTURE_PER_MINUTE,
    RATE_LIMIT_SIMULATE_PER_MINUTE,
    RATE_LIMIT_WINDOW_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    TRUST_PROXY,
)
from app.middleware.security import (
    HttpsRedirectMiddleware,
    RateLimitMiddleware,
    RequestTimeoutMiddleware,
)
from app.models.db import init_db
from app.pipeline.runner import PipelineExecutionError

logger = logging.getLogger(__name__)

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


@app.exception_handler(PipelineExecutionError)
async def pipeline_execution_error_handler(
    _: Request, __: PipelineExecutionError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "Event processing is temporarily unavailable"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if FORCE_HTTPS:
    app.add_middleware(HttpsRedirectMiddleware)

app.add_middleware(
    RequestTimeoutMiddleware,
    timeout_seconds=REQUEST_TIMEOUT_SECONDS,
)
app.add_middleware(
    RateLimitMiddleware,
    limits={
        "/capture": RATE_LIMIT_CAPTURE_PER_MINUTE,
        "/simulate": RATE_LIMIT_SIMULATE_PER_MINUTE,
        "/auth/login": RATE_LIMIT_AUTH_PER_MINUTE,
        "/auth/signup": RATE_LIMIT_AUTH_PER_MINUTE,
    },
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    trust_proxy=TRUST_PROXY,
)

origins = _cors_origins(os.getenv("CORS_ORIGINS"))
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization", "X-Simulate-Token"],
    )

app.include_router(auth_router)
app.include_router(capture_router)
app.include_router(simulate_router)
app.include_router(events_router)
app.include_router(export_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, object]:
    return {"ok": True, "version": VERSION}
