"""Environment-backed runtime settings for HoneyDesk."""

from __future__ import annotations

import os


def env_bool(name: str, *, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_float(name: str, *, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def env_int(name: str, *, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


# Request and dependency timeouts (seconds)
REQUEST_TIMEOUT_SECONDS = env_float("REQUEST_TIMEOUT_SECONDS", default=30.0)
LLM_TIMEOUT_SECONDS = env_float("LLM_TIMEOUT_SECONDS", default=4.0)
SQLITE_TIMEOUT_SECONDS = env_float("SQLITE_TIMEOUT_SECONDS", default=5.0)
SQLITE_BUSY_RETRIES = env_int("SQLITE_BUSY_RETRIES", default=3)

# Rate limiting (in-memory; per client IP per route)
RATE_LIMIT_CAPTURE_PER_MINUTE = env_int("RATE_LIMIT_CAPTURE_PER_MINUTE", default=30)
RATE_LIMIT_SIMULATE_PER_MINUTE = env_int("RATE_LIMIT_SIMULATE_PER_MINUTE", default=10)
RATE_LIMIT_AUTH_PER_MINUTE = env_int("RATE_LIMIT_AUTH_PER_MINUTE", default=20)
RATE_LIMIT_WINDOW_SECONDS = env_int("RATE_LIMIT_WINDOW_SECONDS", default=60)

# Auth sessions
SESSION_TTL_DAYS = env_int("SESSION_TTL_DAYS", default=7)
PASSWORD_MIN_LENGTH = env_int("PASSWORD_MIN_LENGTH", default=8)

# Security and failover
FORCE_HTTPS = env_bool("FORCE_HTTPS", default=False)
TRUST_PROXY = env_bool("TRUST_PROXY", default=False)
BRIEF_FAILOVER_CACHE = env_bool("BRIEF_FAILOVER_CACHE", default=True)

# Deployment posture: production disables OpenAPI UIs and requires SIMULATE_TOKEN.
APP_ENV = (os.getenv("APP_ENV") or "development").strip().lower()
IS_PRODUCTION = APP_ENV in {"production", "prod"}
EXPOSE_API_DOCS = env_bool("EXPOSE_API_DOCS", default=not IS_PRODUCTION)
REQUIRE_SIMULATE_TOKEN = env_bool(
    "REQUIRE_SIMULATE_TOKEN", default=IS_PRODUCTION
)
