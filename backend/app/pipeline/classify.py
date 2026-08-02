"""Fast, deterministic classification for HoneyDesk capture events.

Only structural signals are inspected.  Values from untrusted events are never
interpolated into explanations, which keeps reasons safe to display and log.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from itertools import islice
import math
import re
from typing import Any, Literal, TypeAlias, TypedDict, cast

Technique: TypeAlias = Literal[
    "credential_harvest",
    "urgency_pii_scam",
    "social_verify",
    "typosquat",
    "bot_probe",
    "unknown",
]
Severity: TypeAlias = Literal["low", "medium", "high", "critical"]


class ClassificationDict(TypedDict):
    """JSON-ready classifier output consumed by the pipeline runner."""

    technique: Technique
    severity: Severity
    reasons: list[str]


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """Immutable typed result for callers that prefer attribute access."""

    technique: Technique
    severity: Severity
    reasons: tuple[str, ...]

    def as_dict(self) -> ClassificationDict:
        """Return a fresh JSON-serializable representation."""

        return {
            "technique": self.technique,
            "severity": self.severity,
            "reasons": list(self.reasons),
        }


_TOKEN_RE = re.compile(r"[^a-z0-9]+")
_MAX_COLLECTION_ITEMS = 128

_PORTAL_DECOYS = frozenset({"portal", "student_portal", "aid_portal", "login_portal"})
_SCHOLARSHIP_DECOYS = frozenset(
    {"scholarship", "scholarship_form", "aid_form", "financial_aid"}
)
_SOCIAL_DECOYS = frozenset(
    {"discord", "discord_verify", "social_verify", "verify_landing"}
)
_PASSWORD_FIELDS = frozenset(
    {"password", "passcode", "passwd", "school_password", "account_password"}
)
_HIGH_RISK_PII_FIELDS = frozenset(
    {
        "ssn",
        "social_security",
        "social_security_number",
        "bank",
        "bank_account",
        "account_number",
        "routing",
        "routing_number",
        "tax_id",
    }
)
_PII_FIELDS = _HIGH_RISK_PII_FIELDS | frozenset(
    {"dob", "date_of_birth", "government_id", "drivers_license"}
)
_TOKEN_FIELDS = frozenset(
    {"token", "session", "session_token", "auth_token", "discord_token", "cookie"}
)
_URGENCY_FLAGS = frozenset(
    {"urgent", "urgency", "deadline", "limited_time", "act_now", "immediate_action"}
)
_TYPOSQUAT_FLAGS = frozenset(
    {"typosquat", "lookalike_domain", "domain_mismatch", "homoglyph"}
)
_PROBE_FLAGS = frozenset(
    {"probe", "scanner", "automated", "automation", "headless", "bot"}
)
_BOT_UA_MARKERS = (
    "curl",
    "wget",
    "python_requests",
    "python_urllib",
    "httpx",
    "aiohttp",
    "scrapy",
    "go_http_client",
    "headless",
    "scanner",
    "bot",
)


def _token(value: object) -> str:
    """Normalize bounded text without invoking attacker-controlled ``__str__``."""

    if not isinstance(value, str):
        return ""
    return _TOKEN_RE.sub("_", value[:256].strip().casefold()).strip("_")


def _mapping(value: object) -> Mapping[str, Any]:
    return cast(Mapping[str, Any], value) if isinstance(value, Mapping) else {}


def _field_names(value: object) -> frozenset[str]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        return frozenset()
    return frozenset(
        token
        for item in islice(value, _MAX_COLLECTION_ITEMS)
        if (token := _token(item))
    )


def _flags(event: Mapping[str, Any], meta: Mapping[str, Any]) -> frozenset[str]:
    found: set[str] = set()
    for raw_flags in (event.get("flags"), meta.get("flags")):
        if isinstance(raw_flags, Mapping):
            for key, enabled in islice(
                raw_flags.items(), _MAX_COLLECTION_ITEMS
            ):
                if enabled is True and (token := _token(key)):
                    found.add(token)
        elif isinstance(raw_flags, (list, tuple, set, frozenset)):
            for item in islice(raw_flags, _MAX_COLLECTION_ITEMS):
                if token := _token(item):
                    found.add(token)
        elif token := _token(raw_flags):
            found.add(token)
    return frozenset(found)


def _first_token(*values: object) -> str:
    for value in values:
        if token := _token(value):
            return token
    return ""


def _dwell_ms(meta: Mapping[str, Any]) -> float | None:
    value = meta.get("dwell_ms")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number >= 0 else None


def classify_typed(raw_event: object) -> ClassificationResult:
    """Classify an untrusted event using deterministic, explainable rules.

    Invalid or non-mapping input is safely handled as an event with no supplied
    metadata. The function performs no I/O and never copies event values into
    its returned reasons.
    """

    event = _mapping(raw_event)
    meta = _mapping(event.get("meta"))
    headers = _mapping(event.get("headers"))

    decoy = _first_token(event.get("decoy_id"))
    path = _first_token(event.get("path"), meta.get("path"))
    source = _first_token(event.get("source"), meta.get("source"))
    user_agent = _first_token(
        event.get("user_agent"),
        event.get("user-agent"),
        meta.get("user_agent"),
        headers.get("user-agent"),
        headers.get("User-Agent"),
    )
    fields = _field_names(event.get("fields_present"))
    flags = _flags(event, meta)
    dwell_ms = _dwell_ms(meta)

    has_password = event.get("password_entered") is True or bool(
        fields & _PASSWORD_FIELDS
    )
    has_high_risk_pii = bool(fields & _HIGH_RISK_PII_FIELDS)
    has_pii = has_high_risk_pii or bool(fields & _PII_FIELDS)
    has_token = bool(fields & _TOKEN_FIELDS)
    is_urgent = bool(flags & _URGENCY_FLAGS) or any(
        marker in path for marker in ("urgent", "deadline", "confirm_now", "act_now")
    )
    is_verify = "verify" in path or "verification" in path or "verify" in flags
    is_typosquat = bool(flags & _TYPOSQUAT_FLAGS) or any(
        marker in decoy for marker in ("typosquat", "lookalike", "homoglyph")
    )
    bot_ua = not user_agent or any(marker in user_agent for marker in _BOT_UA_MARKERS)
    fast_submit = dwell_ms is not None and dwell_ms < 300
    automated_source = source in {"bot", "scanner", "automation", "probe"}
    is_bot = bot_ua or fast_submit or automated_source or bool(flags & _PROBE_FLAGS)

    if decoy in _SCHOLARSHIP_DECOYS or (has_pii and is_urgent):
        reasons = ["A scholarship or aid flow requested personal information."]
        if has_high_risk_pii:
            reasons.append("High-risk identity or financial fields were targeted.")
        elif is_urgent:
            reasons.append("Urgency indicators were present in the interaction.")
        if is_bot:
            reasons.append("Automation indicators were also observed.")
        return ClassificationResult(
            "urgency_pii_scam",
            "critical" if has_high_risk_pii else "high",
            tuple(reasons),
        )

    if decoy in _SOCIAL_DECOYS or (is_verify and has_token):
        reasons = ["A social-account verification flow was targeted."]
        if is_verify:
            reasons.append("The request path or flags indicated a verification action.")
        if has_token:
            reasons.append("Session or account-token fields were targeted.")
        if is_bot:
            reasons.append("Automation indicators were also observed.")
        return ClassificationResult(
            "social_verify", "critical" if has_token else "high", tuple(reasons)
        )

    if (decoy in _PORTAL_DECOYS and has_password) or (
        has_password and any(marker in path for marker in ("login", "signin", "sign_in"))
    ):
        reasons = [
            "A login flow recorded an attempted password submission.",
            "The interaction matched credential collection behavior.",
        ]
        if is_bot:
            reasons.append("Automation indicators were also observed.")
        return ClassificationResult("credential_harvest", "high", tuple(reasons))

    if is_typosquat:
        reasons = ["Lookalike-domain or typosquat indicators were present."]
        if has_password or has_pii:
            reasons.append("The lookalike flow also targeted sensitive field types.")
        return ClassificationResult(
            "typosquat", "high" if has_password or has_pii else "medium", tuple(reasons)
        )

    if is_bot:
        reasons = ["The interaction matched automated probing behavior."]
        if bot_ua:
            reasons.append("The user-agent was missing or matched an automation client.")
        if fast_submit:
            reasons.append("The form was submitted faster than typical human interaction.")
        return ClassificationResult(
            "bot_probe",
            "medium" if fast_submit or bool(flags & _PROBE_FLAGS) else "low",
            tuple(reasons),
        )

    return ClassificationResult(
        "unknown",
        "medium",
        ("No controlled technique rule matched the available metadata.",),
    )


def classify(raw_event: object) -> ClassificationDict:
    """Return the runner-facing JSON-ready classification dictionary."""

    return classify_typed(raw_event).as_dict()


def classify_event(raw_event: object) -> ClassificationDict:
    """Runner-friendly named alias for :func:`classify`."""

    return classify(raw_event)


__all__ = [
    "ClassificationDict",
    "ClassificationResult",
    "Severity",
    "Technique",
    "classify",
    "classify_event",
    "classify_typed",
]
