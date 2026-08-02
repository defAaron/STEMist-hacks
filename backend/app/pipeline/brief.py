"""Deterministic, age-appropriate victim brief generation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping
from urllib import request
from urllib.parse import urlsplit

from app.config import BRIEF_FAILOVER_CACHE, LLM_TIMEOUT_SECONDS

MAX_VICTIM_WORDS = 120
_SCENARIO_DIR = Path(__file__).resolve().parents[1] / "scenarios"
_SAFE_TECHNIQUES = {
    "credential_harvest",
    "urgency_pii_scam",
    "social_verify",
    "typosquat",
    "bot_probe",
    "unknown",
}
_SAFE_SEVERITIES = {"low", "medium", "high", "critical"}
_SAFE_DECOYS = {"portal", "scholarship", "discord"}
_SAFE_SOURCES = {"live", "simulate", "replay"}
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

_FALLBACKS: dict[str, tuple[str, list[str]]] = {
    "credential_harvest": (
        "This page tried to collect a school login so someone could access email or other accounts. "
        "That is risky because reused passwords can unlock more than one service. "
        "If you entered a real password on a page like this, change it on the real school website, "
        "turn on two-step verification, and report the link to school IT or a trusted adult.",
        [
            "Change the password on the real school website.",
            "Turn on two-step verification.",
            "Report the link to school IT or a trusted adult.",
        ],
    ),
    "urgency_pii_scam": (
        "This page used scholarship urgency to ask for sensitive personal or banking details. "
        "That information could be used for identity theft or unauthorized payments. "
        "Stop using the page, contact the school or scholarship through an official website, "
        "and tell a trusted adult or school IT what information may have been entered.",
        [
            "Stop using the page.",
            "Verify the offer through an official website.",
            "Tell a trusted adult or school IT what may have been entered.",
        ],
    ),
    "social_verify": (
        "This verification page tried to take control of a social or chat account. "
        "Fake verification links are risky because they can capture sign-in access and message friends as you. "
        "Close the page, review active sessions and security settings in the real app, "
        "and report the link to the platform or a trusted adult.",
        [
            "Close the page.",
            "Review active sessions in the real app.",
            "Report the link to the platform or a trusted adult.",
        ],
    ),
    "unknown": (
        "This page showed behavior that may be unsafe, but there is not enough information to identify the exact scam. "
        "Unexpected forms and links can put accounts or personal information at risk. "
        "Do not enter more information, verify the request using an official contact method, "
        "and ask a trusted adult or school IT to review it.",
        [
            "Do not enter more information.",
            "Verify the request through an official contact.",
            "Ask a trusted adult or school IT to review it.",
        ],
    ),
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return vars(value) if hasattr(value, "__dict__") else {}


def _word_count(text: str) -> int:
    return len(text.split())


def _safe_victim(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    compact = " ".join(text.split()).strip()
    if not compact:
        return None
    words = compact.split()
    return " ".join(words[:MAX_VICTIM_WORDS])


def _safe_actions(actions: Any) -> list[str] | None:
    if not isinstance(actions, list) or not 2 <= len(actions) <= 3:
        return None
    cleaned = [" ".join(str(action).split()) for action in actions]
    if any(not action or len(action) > 180 for action in cleaned):
        return None
    return cleaned


def _load_scenario(scenario_id: str) -> Mapping[str, Any] | None:
    normalized = scenario_id.upper()
    for path in sorted(_SCENARIO_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if str(payload.get("scenario_id", "")).upper() == normalized:
            return payload
    return None


def _cached_brief(
    event: Mapping[str, Any], scenario: Mapping[str, Any] | None
) -> dict[str, Any] | None:
    scenario_id = str(event.get("scenario_id") or "").upper()
    source = scenario or (_load_scenario(scenario_id) if scenario_id.startswith("SC-") else None)
    if source is None:
        return None
    victim = _safe_victim(source.get("cached_brief_victim"))
    if victim is None:
        return None
    actions = _safe_actions(source.get("cached_brief_actions"))
    if actions is None:
        technique = str(event.get("technique") or source.get("expected_technique") or "unknown")
        actions = list(_FALLBACKS.get(technique, _FALLBACKS["unknown"])[1])
    return {"victim": victim, "it": None, "actions": actions, "brief_source": "cache"}


def _network_allowed(explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    if BRIEF_FAILOVER_CACHE:
        return False
    return bool(os.getenv("OPENAI_API_KEY"))


def _https_base_url(base_url: str) -> str | None:
    parts = urlsplit(base_url.strip())
    if parts.scheme != "https" or not parts.netloc:
        return None
    return base_url.rstrip("/")


def _llm_brief(
    event: Mapping[str, Any], api_key: str, model: str, base_url: str
) -> dict[str, Any] | None:
    """Call an OpenAI-compatible endpoint only after explicit opt-in."""
    safe_base = _https_base_url(base_url)
    if safe_base is None:
        return None
    technique = str(event.get("technique") or "unknown")
    severity = str(event.get("severity") or "medium")
    decoy_id = str(event.get("decoy_id") or "unknown")
    source = str(event.get("source") or "live")
    raw_targets = event.get("data_targeted")
    targets = (
        sorted({str(value) for value in raw_targets if str(value) in _SAFE_TARGETS})
        if isinstance(raw_targets, (list, tuple, set))
        else []
    )
    safe_input = {
        "technique": technique if technique in _SAFE_TECHNIQUES else "unknown",
        "severity": severity if severity in _SAFE_SEVERITIES else "medium",
        "data_targeted": targets,
        "decoy_id": decoy_id if decoy_id in _SAFE_DECOYS else "unknown",
        "source": source if source in _SAFE_SOURCES else "live",
    }
    prompt = (
        "You are a calm security coach for ages 13-19. Return JSON with victim and actions. "
        "The victim text must explain what happened, why it is risky, and include 2-3 concrete "
        "next steps in no more than 120 words. Do not claim the student is already hacked. Event: "
        + json.dumps(safe_input, sort_keys=True)
    )
    body = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode()
    endpoint = safe_base + "/chat/completions"
    req = request.Request(
        endpoint,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as response:
            envelope = json.loads(response.read())
        content = envelope["choices"][0]["message"]["content"]
        result = json.loads(content)
    except (OSError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        return None
    victim = _safe_victim(result.get("victim"))
    actions = _safe_actions(result.get("actions"))
    if victim is None or actions is None or _word_count(victim) > MAX_VICTIM_WORDS:
        return None
    return {"victim": victim, "it": None, "actions": actions, "brief_source": "llm"}


def generate_brief(
    event: Mapping[str, Any] | Any,
    scenario: Mapping[str, Any] | Any | None = None,
    *,
    allow_network: bool | None = None,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Return a stable cached/fallback brief; network use requires explicit opt-in.

    Seeded scenarios always use their checked-in cached brief, even when an API key
    is available. This keeps replay behavior deterministic.
    """
    event_data = _as_mapping(event)
    scenario_data = _as_mapping(scenario) if scenario is not None else None
    cached = _cached_brief(event_data, scenario_data)
    if cached is not None:
        return cached

    key = api_key or os.getenv("OPENAI_API_KEY")
    if _network_allowed(allow_network) and key:
        generated = _llm_brief(
            event_data,
            key,
            model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        if generated is not None:
            return generated

    technique = str(event_data.get("technique") or "unknown")
    victim, actions = _FALLBACKS.get(technique, _FALLBACKS["unknown"])
    return {
        "victim": victim,
        "it": None,
        "actions": list(actions),
        "brief_source": "fallback",
    }


async def generate_brief_async(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Async adapter for pipeline runners with an async step contract."""
    return generate_brief(*args, **kwargs)


build_brief = generate_brief
