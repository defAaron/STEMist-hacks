from __future__ import annotations

import json
from pathlib import Path

from app.pipeline.classify import (
    ClassificationResult,
    classify,
    classify_event,
    classify_typed,
)


def test_repository_seeded_scenarios_match_expected_contract() -> None:
    scenario_dir = Path(__file__).parents[1] / "app" / "scenarios"

    for scenario_id in ("sc1", "sc2", "sc3"):
        scenario = json.loads((scenario_dir / f"{scenario_id}.json").read_text())
        result = classify_event(scenario)

        assert result["technique"] == scenario["expected_technique"]
        assert result["severity"] == scenario["expected_severity"]


def test_seeded_sc1_credential_harvest() -> None:
    result = classify(
        {
            "scenario_id": "SC-1",
            "decoy_id": " Student Portal ",
            "path": "/aid/LOGIN",
            "fields_present": ["EMAIL", "Password"],
            "password_entered": True,
            "user_agent": "Mozilla/5.0",
            "source": "replay",
        }
    )

    assert result["technique"] == "credential_harvest"
    assert result["severity"] == "high"
    assert result["reasons"]


def test_seeded_sc2_urgency_pii_is_critical() -> None:
    result = classify(
        {
            "scenario_id": "SC-2",
            "decoy_id": "SCHOLARSHIP-FORM",
            "path": "/confirm-now",
            "fields_present": ["full_name", "SSN", "routing-number"],
            "flags": {"urgent": True},
            "user_agent": "Mozilla/5.0",
            "source": "replay",
        }
    )

    assert result["technique"] == "urgency_pii_scam"
    assert result["severity"] == "critical"


def test_seeded_sc3_social_verify() -> None:
    result = classify(
        {
            "scenario_id": "SC-3",
            "decoy_id": "Discord Verify",
            "path": "/VERIFY/account",
            "fields_present": ["username"],
            "user_agent": "Mozilla/5.0",
            "source": "replay",
        }
    )

    assert result["technique"] == "social_verify"
    assert result["severity"] == "high"


def test_typosquat_flags_and_sensitive_fields_raise_severity() -> None:
    result = classify(
        {
            "decoy_id": "landing",
            "fields_present": ["password"],
            "flags": ["LOOKALIKE DOMAIN"],
            "user_agent": "Mozilla/5.0",
        }
    )

    assert result["technique"] == "typosquat"
    assert result["severity"] == "high"


def test_bot_probe_uses_user_agent_dwell_and_source_metadata() -> None:
    result = classify(
        {
            "decoy_id": "unrecognized",
            "fields_present": [],
            "meta": {
                "dwell_ms": 42,
                "source": "scanner",
                "user_agent": "python-requests/2.32",
            },
        }
    )

    assert result["technique"] == "bot_probe"
    assert result["severity"] == "medium"
    assert len(result["reasons"]) == 3


def test_unknown_decoy_defaults_to_medium() -> None:
    result = classify(
        {
            "decoy_id": "other",
            "fields_present": ["nickname"],
            "user_agent": "Mozilla/5.0",
            "source": "live",
        }
    )

    assert result == {
        "technique": "unknown",
        "severity": "medium",
        "reasons": ["No controlled technique rule matched the available metadata."],
    }


def test_typed_interface_is_immutable_and_dict_conversion_is_fresh() -> None:
    typed = classify_typed(
        {
            "decoy_id": "portal",
            "fields_present": ["password"],
            "password_entered": True,
            "user_agent": "Mozilla/5.0",
        }
    )
    first = typed.as_dict()
    first["reasons"].append("mutated by caller")

    assert isinstance(typed, ClassificationResult)
    assert typed.technique == "credential_harvest"
    assert "mutated by caller" not in typed.as_dict()["reasons"]


def test_untrusted_values_are_not_exposed_in_reasons() -> None:
    secret = "SUPER-SECRET-VALUE-9381"
    result = classify(
        {
            "decoy_id": "portal",
            "path": f"/login/{secret}",
            "fields_present": ["password", secret],
            "password_entered": True,
            "user_agent": f"Mozilla/5.0 {secret}",
            "flags": [secret],
            "meta": {"campaign": secret},
        }
    )

    assert secret.casefold() not in " ".join(result["reasons"]).casefold()


def test_non_string_objects_are_not_stringified() -> None:
    class MustNotStringify:
        def __str__(self) -> str:
            raise AssertionError("untrusted objects must not be stringified")

    result = classify(
        {
            "decoy_id": MustNotStringify(),
            "path": MustNotStringify(),
            "fields_present": [MustNotStringify()],
            "flags": [MustNotStringify()],
            "user_agent": "Mozilla/5.0",
        }
    )

    assert result["technique"] == "unknown"
