"""Rate limiting, request timeouts, and HTTPS enforcement middleware."""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

logger = logging.getLogger(__name__)


def _client_ip(request: Request, *, trust_proxy: bool) -> str:
    if trust_proxy:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()[:64]
    if request.client is not None:
        return request.client.host[:64]
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter for abuse-prone routes."""

    def __init__(
        self,
        app: Any,
        *,
        limits: dict[str, int],
        window_seconds: int,
        trust_proxy: bool = False,
    ) -> None:
        super().__init__(app)
        self._limits = limits
        self._window = max(window_seconds, 1)
        self._trust_proxy = trust_proxy
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _allow(self, key: str, limit: int) -> bool:
        now = time.monotonic()
        cutoff = now - self._window
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        path = request.url.path
        limit = self._limits.get(path)
        if request.method == "POST" and limit is not None:
            client = _client_ip(request, trust_proxy=self._trust_proxy)
            key = f"{client}:{path}"
            if not self._allow(key, limit):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests; try again later"},
                    headers={"Retry-After": str(self._window)},
                )
        return await call_next(request)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Abort requests that exceed a configured wall-clock budget."""

    def __init__(self, app: Any, *, timeout_seconds: float) -> None:
        super().__init__(app)
        self._timeout = max(timeout_seconds, 1.0)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        try:
            return await asyncio.wait_for(call_next(request), timeout=self._timeout)
        except asyncio.TimeoutError:
            logger.warning(
                "Request timed out after %.1fs: %s %s",
                self._timeout,
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=504,
                content={"detail": "Request timed out"},
            )


class HttpsRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS when deployed behind a TLS-terminating proxy."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        forwarded = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
        if forwarded == "http":
            target = str(request.url.replace(scheme="https"))
            return RedirectResponse(target, status_code=308)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach conservative security headers to every API response."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
        response.headers.setdefault("Cache-Control", "no-store")
        return response
