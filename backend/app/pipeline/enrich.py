"""Deterministic, network-free enrichment for HoneyDesk events.

This module deliberately has no imports from the runner, database, or API
layers, so it can be reused by live captures and replay fixtures.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import Any


_DEMO_GEOS: tuple[dict[str, Any], ...] = (
    {"lat": 40.7128, "lon": -74.0060, "label": "Demo location — New York, US"},
    {"lat": 34.0522, "lon": -118.2437, "label": "Demo location — Los Angeles, US"},
    {"lat": 41.8781, "lon": -87.6298, "label": "Demo location — Chicago, US"},
    {"lat": 29.7604, "lon": -95.3698, "label": "Demo location — Houston, US"},
    {"lat": 43.6532, "lon": -79.3832, "label": "Demo location — Toronto, CA"},
)


def derive_data_targeted(
    fields_present: object, decoy_id: object = ""
) -> list[str]:
    """Map field names and decoy context to non-secret data categories."""

    fields = {
        _normalise_field(field)
        for field in fields_present
        if isinstance(field, str)
    } if isinstance(fields_present, (list, tuple, set, frozenset)) else set()
    decoy = str(decoy_id or "").strip().lower()
    targeted: list[str] = []

    if fields & {"email", "email_address", "school_email", "username", "user"}:
        targeted.append("school_email")
    if fields & {"password", "pass", "passwd"}:
        targeted.append("password")
    if fields & {"ssn", "social_security", "social_security_number"}:
        targeted.append("ssn")
    if fields & {
        "bank",
        "bank_account",
        "account_number",
        "routing",
        "routing_number",
    }:
        targeted.append("bank_account")

    discord_signal = decoy == "discord" or bool(
        fields & {"discord", "discord_username", "verify", "verification_code", "token"}
    )
    if discord_signal:
        targeted.extend(("discord_account", "session_token_risk"))

    return list(dict.fromkeys(targeted))


def demo_geo_for(event: Mapping[str, Any]) -> dict[str, Any]:
    """Return a stable, explicitly demo-labelled location without an API call."""

    seed = "|".join(
        str(event.get(key) or "") for key in ("scenario_id", "ip", "decoy_id")
    )
    digest = hashlib.sha256(seed.encode("utf-8", errors="replace")).digest()
    return dict(_DEMO_GEOS[int.from_bytes(digest[:2], "big") % len(_DEMO_GEOS)])


def enrich_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Return enrichment fields to merge into an event.

    The input is not mutated. Scenario-provided coordinates are retained for a
    reliable replay, but their label is marked as demo data.
    """

    supplied_geo = event.get("geo")
    geo = _safe_scenario_geo(supplied_geo) or demo_geo_for(event)
    return {
        "data_targeted": derive_data_targeted(
            event.get("fields_present", ()), event.get("decoy_id", "")
        ),
        "geo": geo,
        "ua_family": _ua_family(str(event.get("user_agent") or "")),
    }


def _normalise_field(field: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", field.strip().lower())).strip("_")


def _safe_scenario_geo(value: object) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    lat, lon = value.get("lat"), value.get("lon")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None
    if isinstance(lat, bool) or isinstance(lon, bool):
        return None
    if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
        return None
    raw_label = str(value.get("label") or "Scenario location")
    label = re.sub(r"[\x00-\x1f\x7f]", "", raw_label).strip()[:80]
    if not label.lower().startswith("demo location"):
        label = f"Demo location — {label or 'Scenario location'}"
    return {"lat": float(lat), "lon": float(lon), "label": label}


def _ua_family(user_agent: str) -> str:
    ua = user_agent.lower()
    browser = next(
        (
            name
            for marker, name in (
                ("edg/", "Edge"),
                ("chrome/", "Chrome"),
                ("firefox/", "Firefox"),
                ("safari/", "Safari"),
                ("curl/", "curl"),
                ("python-requests", "Python requests"),
            )
            if marker in ua
        ),
        "Unknown browser",
    )
    os_name = next(
        (
            name
            for marker, name in (
                ("windows", "Windows"),
                ("android", "Android"),
                ("iphone", "iOS"),
                ("ipad", "iPadOS"),
                ("mac os x", "macOS"),
                ("linux", "Linux"),
            )
            if marker in ua
        ),
        "Unknown OS",
    )
    return f"{browser} on {os_name}"
