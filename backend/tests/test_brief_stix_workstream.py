import asyncio
import json

from app.api import routes_export
from app.pipeline.brief import generate_brief
from app.services.stix_export import event_to_stix_bundle


def test_seeded_brief_always_uses_cached_copy():
    scenario = {
        "scenario_id": "SC-1",
        "expected_technique": "credential_harvest",
        "cached_brief_victim": (
            "A fake portal tried to collect a school login. That is risky because an attacker "
            "could access school services. Change the password on the official site, enable "
            "two-step verification, and report the link to school IT."
        ),
        "cached_brief_actions": ["Change the password.", "Enable 2FA.", "Report the link."],
    }
    result = generate_brief(
        {"scenario_id": "SC-1", "technique": "credential_harvest"},
        scenario,
        allow_network=True,
        api_key="must-not-be-used",
    )

    assert result["brief_source"] == "cache"
    assert result["victim"] == scenario["cached_brief_victim"]
    assert len(result["actions"]) == 3


def test_fallback_briefs_are_safe_actionable_and_short():
    for technique in (
        "credential_harvest",
        "urgency_pii_scam",
        "social_verify",
        "unknown",
    ):
        result = generate_brief({"technique": technique})
        assert result["brief_source"] == "fallback"
        assert len(result["victim"].split()) <= 120
        assert 2 <= len(result["actions"]) <= 3


def test_stix_bundle_is_stable_structured_and_sanitized():
    event = {
        "id": "evt-123",
        "created_at": "2026-08-02T15:30:00Z",
        "scenario_id": "SC-2",
        "technique": "urgency_pii_scam",
        "severity": "critical",
        "ip": "203.0.113.12",
        "user_agent": "secret-agent token=raw-token-value",
        "password": "raw-password-value",
        "ssn": "123-45-6789",
        "data_targeted": ["ssn", "bank_account"],
        "reasons": ["Captured password raw-password-value"],
    }

    first = event_to_stix_bundle(event)
    second = event_to_stix_bundle(dict(reversed(list(event.items()))))
    encoded = json.dumps(first, sort_keys=True)

    assert first == second
    assert first["type"] == "bundle"
    assert {obj["type"] for obj in first["objects"]} >= {
        "indicator",
        "attack-pattern",
        "incident",
        "note",
    }
    assert "raw-password-value" not in encoded
    assert "raw-token-value" not in encoded
    assert "123-45-6789" not in encoded


def test_export_route_returns_download(monkeypatch):
    async def fake_get_event(event_id, *, user_id):
        assert user_id == "user-test-1"
        return {
            "id": event_id,
            "created_at": "2026-08-02T15:30:00Z",
            "technique": "credential_harvest",
            "severity": "high",
            "ip": "203.0.113.50",
        }

    monkeypatch.setattr(routes_export, "_get_event", fake_get_event)
    user = {
        "id": "user-test-1",
        "email": "tester@example.test",
        "created_at": "2026-08-02T00:00:00.000Z",
    }
    response = asyncio.run(routes_export.export_stix("evt-1", user))
    payload = json.loads(response.body)

    assert payload["type"] == "bundle"
    assert response.media_type == "application/stix+json"
    assert "attachment;" in response.headers["content-disposition"]
