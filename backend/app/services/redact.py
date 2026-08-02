"""Secret-safe normalization for all capture ingress.

The redactor deliberately discards secret values instead of hashing them. Hashes
of low-entropy data such as passwords, SSNs, and bank details are still unsafe
to retain and are unnecessary for HoneyDesk's defensive analytics.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

REDACTED = "[REDACTED]"

_SAFE_FLAG_KEYS = {
    "password_entered",
    "ssn_entered",
    "token_entered",
    "bank_data_entered",
}

_PASSWORD_KEYS = {
    "pass",
    "passwd",
    "password",
    "password_confirmation",
    "password_confirm",
    "pwd",
}
_SSN_KEYS = {
    "national_id",
    "social_security",
    "social_security_number",
    "ssn",
    "tax_id",
}
_TOKEN_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "bearer",
    "cookie",
    "id_token",
    "jwt",
    "refresh_token",
    "secret",
    "session",
    "session_id",
    "session_token",
    "token",
}
_BANK_KEYS = {
    "account_number",
    "bank",
    "bank_account",
    "bank_data",
    "card",
    "card_number",
    "credit_card",
    "cvv",
    "iban",
    "pin",
    "routing",
    "routing_number",
}

_SECRET_KEY_TO_FLAG = {
    **{key: "password_entered" for key in _PASSWORD_KEYS},
    **{key: "ssn_entered" for key in _SSN_KEYS},
    **{key: "token_entered" for key in _TOKEN_KEYS},
    **{key: "bank_data_entered" for key in _BANK_KEYS},
}

_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|pwd|ssn|token|authorization|api[_-]?key|"
    r"routing(?:_number)?|account(?:_number)?|card(?:_number)?|cvv|pin)"
    r"\b(\s*[:=]\s*)([^\s,;&]+)"
)
_BEARER_VALUE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")


def normalize_field_name(name: str) -> str:
    """Return a bounded canonical field name, never a submitted field value."""

    normalized = re.sub(r"[^a-z0-9_.-]+", "_", name.strip().lower())
    return normalized.strip("_.-")[:64]


def secret_flag_for_field(name: str) -> str | None:
    """Map a sensitive field name to its safe boolean signal."""

    normalized = normalize_field_name(name).replace("-", "_").replace(".", "_")
    if normalized in _SAFE_FLAG_KEYS:
        return None
    exact = _SECRET_KEY_TO_FLAG.get(normalized)
    if exact is not None:
        return exact

    parts = frozenset(part for part in normalized.split("_") if part)
    if parts & {"password", "passwd", "pwd"}:
        return "password_entered"
    if "ssn" in parts or {"social", "security"}.issubset(parts):
        return "ssn_entered"
    if parts & {"token", "jwt", "secret"} or normalized.endswith("_api_key"):
        return "token_entered"
    if parts & {"routing", "iban", "cvv"} or "bank" in parts:
        return "bank_data_entered"
    if "card" in parts and parts & {"number", "credit", "debit"}:
        return "bank_data_entered"
    if "account" in parts and "number" in parts:
        return "bank_data_entered"
    return None


def redact_secrets(value: Any) -> Any:
    """Recursively copy *value*, dropping secret-bearing mapping entries.

    A removed secret is represented only by a category boolean in the same
    mapping. Lists and tuples are traversed so dictionaries nested at any depth
    receive identical treatment. The input object is never mutated.
    """

    if isinstance(value, Mapping):
        clean: dict[Any, Any] = {}
        inferred_flags: set[str] = set()

        for key, item in value.items():
            if isinstance(key, str):
                flag = secret_flag_for_field(key)
                if flag is not None:
                    inferred_flags.add(flag)
                    continue
            clean[key] = redact_secrets(item)

        for flag in inferred_flags:
            clean[flag] = True
        return clean

    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secrets(item) for item in value)
    if isinstance(value, set):
        return {redact_secrets(item) for item in value}
    return value


def scrub_secret_text(text: str) -> str:
    """Remove common accidental secret assignments from log-safe text."""

    scrubbed = _BEARER_VALUE.sub(f"Bearer {REDACTED}", text)
    return _SENSITIVE_ASSIGNMENT.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{REDACTED}", scrubbed
    )
