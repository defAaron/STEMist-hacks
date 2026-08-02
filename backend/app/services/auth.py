"""Password hashing and session helpers for HoneyDesk accounts."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import PASSWORD_MIN_LENGTH, SESSION_TTL_DAYS
from app.models import db

_EMAIL_RE = re.compile(
    r"^(?=.{3,254}$)[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
_PBKDF2_ITERATIONS = 210_000
_SALT_BYTES = 16
_TOKEN_BYTES = 32


def normalise_email(email: str) -> str:
    return str(email).strip().lower()


def validate_email(email: str) -> str:
    normalised = normalise_email(email)
    if not _EMAIL_RE.fullmatch(normalised):
        raise ValueError("invalid email")
    return normalised


def validate_password(password: str) -> str:
    if not isinstance(password, str) or len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"password must be at least {PASSWORD_MIN_LENGTH} characters")
    if len(password) > 256:
        raise ValueError("password is too long")
    return password


def hash_password(password: str) -> str:
    """Return ``pbkdf2$iterations$salt_hex$hash_hex``."""

    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return f"pbkdf2${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt_hex, digest_hex = password_hash.split("$", 3)
        if scheme != "pbkdf2":
            return False
        iterations = int(iterations_raw)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (AttributeError, TypeError, ValueError):
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(candidate, expected)


def _expires_at(*, days: int | None = None) -> str:
    ttl = SESSION_TTL_DAYS if days is None else days
    expiry = datetime.now(timezone.utc) + timedelta(days=max(ttl, 1))
    return expiry.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def create_session_token(user_id: str) -> str:
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    db.create_session(user_id, token, expires_at=_expires_at())
    return token


def public_user(user: dict[str, Any]) -> dict[str, str]:
    return {
        "id": str(user["id"]),
        "email": str(user["email"]),
        "created_at": str(user["created_at"]),
    }


def signup(email: str, password: str) -> dict[str, Any]:
    """Create a user and session. Raises ``ValueError`` for bad input."""

    normalised = validate_email(email)
    validate_password(password)
    if db.get_user_by_email(normalised) is not None:
        raise LookupError("email already registered")
    user = db.create_user(normalised, hash_password(password))
    token = create_session_token(user["id"])
    return {"token": token, "user": public_user(user)}


def login(email: str, password: str) -> dict[str, Any]:
    """Authenticate and return a new session. Raises ``PermissionError`` on failure."""

    normalised = normalise_email(email)
    user = db.get_user_by_email(normalised)
    if user is None or not verify_password(password, str(user["password_hash"])):
        raise PermissionError("invalid credentials")
    token = create_session_token(str(user["id"]))
    return {
        "token": token,
        "user": {
            "id": str(user["id"]),
            "email": str(user["email"]),
            "created_at": str(user["created_at"]),
        },
    }


def logout(token: str) -> None:
    db.delete_session(token)


def resolve_user_from_token(token: str | None) -> dict[str, str] | None:
    """Validate a bearer token and return the public user, or ``None``."""

    if not token or not token.strip():
        return None
    session = db.get_session(token.strip())
    if session is None:
        return None
    expires_at = str(session["expires_at"])
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )
    if expires_at <= now:
        db.delete_session(token.strip())
        return None
    user = db.get_user_by_id(str(session["user_id"]))
    if user is None:
        db.delete_session(token.strip())
        return None
    return public_user(user)


def extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        return None
    return value.strip()
