"""Best-effort STIX 2.1 export for sanitized HoneyDesk events."""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid5

_NAMESPACE = UUID("ce08ccb8-46ca-4dc9-a7e7-381dfb6c9ef7")
_EPOCH = "1970-01-01T00:00:00.000Z"

_TECHNIQUES = {
    "credential_harvest": (
        "Credential Harvest via Fake Student Portal",
        "A deceptive student portal attempted to collect account credentials.",
    ),
    "urgency_pii_scam": (
        "Urgent Scholarship Personal Data Scam",
        "A deceptive scholarship flow used urgency to request sensitive personal data.",
    ),
    "social_verify": (
        "Fake Social Account Verification",
        "A deceptive verification flow attempted to gain access to a social account.",
    ),
    "typosquat": (
        "Student Service Typosquat",
        "A lookalike student-service location was used as part of a deceptive flow.",
    ),
    "bot_probe": (
        "Automated Honeypot Probe",
        "Automated traffic probed a student-facing honeypot surface.",
    ),
    "unknown": (
        "Suspicious Student-Facing Interaction",
        "HoneyDesk observed suspicious behavior that did not match a known technique.",
    ),
}
_SAFE_TARGETS = {
    "school_email",
    "email",
    "password",
    "personal_information",
    "ssn",
    "bank_account",
    "discord_account",
    "session_token_risk",
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return vars(value) if hasattr(value, "__dict__") else {}


def _timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return _EPOCH
    else:
        return _EPOCH
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed = parsed.astimezone(timezone.utc)
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _stable_id(object_type: str, event_key: str, suffix: str = "") -> str:
    return f"{object_type}--{uuid5(_NAMESPACE, f'{object_type}|{event_key}|{suffix}')}"


def _event_key(event: Mapping[str, Any]) -> str:
    event_id = str(event.get("id") or event.get("event_id") or "")
    if event_id:
        return event_id[:200]
    safe_parts = (
        str(event.get("created_at") or ""),
        str(event.get("scenario_id") or ""),
        str(event.get("decoy_id") or ""),
        str(event.get("technique") or ""),
    )
    return "|".join(safe_parts)[:500] or "unknown-event"


def _indicator_pattern(event: Mapping[str, Any]) -> tuple[str, str]:
    raw_ip = str(event.get("ip") or "").strip()
    try:
        address = ipaddress.ip_address(raw_ip)
    except ValueError:
        return "[url:value = 'https://invalid.local/honeydesk-decoy']", "decoy URL"
    object_type = "ipv4-addr" if address.version == 4 else "ipv6-addr"
    return f"[{object_type}:value = '{address.compressed}']", "source IP address"


def _safe_targets(event: Mapping[str, Any]) -> list[str]:
    values = event.get("data_targeted")
    if not isinstance(values, (list, tuple, set)):
        return []
    # These are category labels only; no captured values are exported.
    return sorted({str(value) for value in values if str(value) in _SAFE_TARGETS})


def event_to_stix_bundle(event: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Build a deterministic STIX 2.1 bundle without raw captured fields.

    Only controlled labels, a validated source IP, and generated descriptions
    enter the bundle. Passwords, tokens, SSN values, form values, reasons, user
    agents, and arbitrary metadata are intentionally excluded.
    """
    data = _as_mapping(event)
    key = _event_key(data)
    created = _timestamp(data.get("created_at"))
    technique = str(data.get("technique") or "unknown")
    technique_name, technique_description = _TECHNIQUES.get(
        technique, _TECHNIQUES["unknown"]
    )
    severity = str(data.get("severity") or "unknown").lower()
    if severity not in {"low", "medium", "high", "critical"}:
        severity = "unknown"
    scenario_id = str(data.get("scenario_id") or "")
    if not (scenario_id.startswith("SC-") and scenario_id[3:].isdigit()):
        scenario_id = ""
    targets = _safe_targets(data)

    indicator_id = _stable_id("indicator", key)
    attack_pattern_id = _stable_id("attack-pattern", key, technique)
    incident_id = _stable_id("incident", key)
    note_id = _stable_id("note", key)
    pattern, indicator_kind = _indicator_pattern(data)

    indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": indicator_id,
        "created": created,
        "modified": created,
        "name": f"HoneyDesk {indicator_kind} indicator",
        "description": "A sanitized indicator observed by an authorized defensive honeypot.",
        "indicator_types": ["malicious-activity"],
        "pattern": pattern,
        "pattern_type": "stix",
        "valid_from": created,
    }
    attack_pattern = {
        "type": "attack-pattern",
        "spec_version": "2.1",
        "id": attack_pattern_id,
        "created": created,
        "modified": created,
        "name": technique_name,
        "description": technique_description,
    }
    incident = {
        "type": "incident",
        "spec_version": "2.1",
        "id": incident_id,
        "created": created,
        "modified": created,
        "name": f"HoneyDesk defensive catch: {technique_name}",
        "description": (
            f"An authorized honeypot recorded a sanitized {severity}-severity interaction. "
            "No captured credentials or sensitive form values are included."
        ),
    }
    summary_parts = [
        f"Technique: {technique_name}.",
        f"Severity: {severity}.",
        "This export contains category labels only, not captured secret values.",
    ]
    if scenario_id:
        summary_parts.append(f"Training scenario: {scenario_id}.")
    if targets:
        summary_parts.append("Data categories targeted: " + ", ".join(targets) + ".")
    note = {
        "type": "note",
        "spec_version": "2.1",
        "id": note_id,
        "created": created,
        "modified": created,
        "abstract": "Sanitized HoneyDesk incident summary",
        "content": " ".join(summary_parts),
        "object_refs": [indicator_id, attack_pattern_id, incident_id],
    }
    relationship = {
        "type": "relationship",
        "spec_version": "2.1",
        "id": _stable_id("relationship", key, "indicates"),
        "created": created,
        "modified": created,
        "relationship_type": "indicates",
        "source_ref": indicator_id,
        "target_ref": attack_pattern_id,
    }
    return {
        "type": "bundle",
        "id": _stable_id("bundle", key),
        "objects": [indicator, attack_pattern, incident, note, relationship],
    }


build_stix_bundle = event_to_stix_bundle
export_event = event_to_stix_bundle
