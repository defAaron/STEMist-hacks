from __future__ import annotations

import asyncio
from typing import Any

from app.pipeline.enrich import derive_data_targeted, enrich_event
from app.pipeline.runner import PipelineExecutionError, run_pipeline


def test_runner_emits_ordered_steps_and_persists_complete_event() -> None:
    messages: list[dict[str, Any]] = []
    persisted: list[dict[str, Any]] = []

    def classify(event: dict[str, Any]) -> dict[str, Any]:
        assert event["pipeline_status"] == "running"
        return {
            "technique": "credential_harvest",
            "severity": "high",
            "score": 91,
            "reasons": ["Portal password field was submitted"],
        }

    async def brief(event: dict[str, Any]) -> dict[str, Any]:
        assert event["data_targeted"] == ["school_email", "password"]
        return {
            "victim": "This training page imitated a school login.",
            "actions": ["Change reused passwords", "Enable 2FA"],
            "brief_source": "cache",
        }

    async def persist(event: dict[str, Any]) -> None:
        persisted.append(event)

    result = asyncio.run(
        run_pipeline(
            {
                "decoy_id": "portal",
                "fields_present": ["email", "password"],
                "password_entered": True,
                "ip": "203.0.113.50",
                "user_agent": "Mozilla/5.0 Chrome/120.0 (Mac OS X)",
            },
            classifier=classify,
            brief_generator=brief,
            persister=persist,
            emit=messages.append,
            event_id="event-1",
        )
    )

    assert result["id"] == "event-1"
    assert result["pipeline_status"] == "complete"
    assert result["brief_victim"].startswith("This training page")
    assert [
        (step["step"], step["status"]) for step in result["pipeline_steps"]
    ] == [
        ("capture", "ok"),
        ("classify", "ok"),
        ("enrich", "ok"),
        ("brief", "ok"),
        ("persist", "ok"),
    ]
    assert persisted[0]["pipeline_status"] == "complete"
    assert [
        (message["type"], message.get("step"))
        for message in messages
    ] == [
        ("step_start", "capture"),
        ("step_end", "capture"),
        ("step_start", "classify"),
        ("step_end", "classify"),
        ("step_start", "enrich"),
        ("step_end", "enrich"),
        ("step_start", "brief"),
        ("step_end", "brief"),
        ("step_start", "persist"),
        ("step_end", "persist"),
        ("event_upsert", None),
        ("done", "end"),
    ]


def test_runner_redacts_secret_values_before_adapters_and_events() -> None:
    seen: list[dict[str, Any]] = []
    messages: list[dict[str, Any]] = []

    def inspect_and_classify(event: dict[str, Any]) -> dict[str, Any]:
        seen.append(event)
        return {"technique": "unknown", "severity": "medium", "score": 20}

    result = asyncio.run(
        run_pipeline(
            {
                "decoy_id": "portal",
                "fields_present": ["email", "password", "ssn"],
                "password_entered": True,
                "password": "hunter2",
                "email": "student@example.test",
                "email_domain": "example.test",
                "token": "token-value",
                "ssn": "123-45-6789",
                "routing_number": "000000000",
                "meta": {"authorization": "Bearer secret", "dwell_ms": 800},
            },
            classifier=inspect_and_classify,
            brief_generator=lambda event: {"victim": "Safe brief"},
            persister=lambda event: seen.append(event),
            emit=messages.append,
        )
    )

    combined = repr((seen, messages, result))
    assert "hunter2" not in combined
    assert "student@example.test" not in combined
    assert "token-value" not in combined
    assert "123-45-6789" not in combined
    assert "000000000" not in combined
    assert "Bearer secret" not in combined
    assert result["password_entered"] is True
    assert result["email_domain"] == "example.test"
    assert "password" in result["fields_present"]


def test_enrichment_is_deterministic_and_marks_geo_as_demo() -> None:
    event = {
        "scenario_id": "SC-2",
        "decoy_id": "scholarship",
        "ip": "198.51.100.20",
        "fields_present": ["email", "SSN", "routing-number"],
    }
    first = enrich_event(event)
    second = enrich_event(event)

    assert first == second
    assert first["data_targeted"] == [
        "school_email",
        "ssn",
        "bank_account",
    ]
    assert first["geo"]["label"].startswith("Demo location")


def test_discord_enrichment_includes_account_and_token_risk() -> None:
    assert derive_data_targeted(["verify"], "discord") == [
        "discord_account",
        "session_token_risk",
    ]


def test_runner_reports_failed_step_without_leaking_exception() -> None:
    messages: list[dict[str, Any]] = []

    def broken_classifier(event: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("sensitive upstream detail")

    try:
        asyncio.run(
            run_pipeline(
                {"decoy_id": "portal", "fields_present": []},
                classifier=broken_classifier,
                brief_generator=lambda event: {},
                persister=lambda event: None,
                emit=messages.append,
            )
        )
    except PipelineExecutionError as exc:
        assert exc.step == "classify"
        assert "sensitive upstream detail" not in str(exc)
    else:
        raise AssertionError("run_pipeline should raise PipelineExecutionError")

    assert messages[-1]["type"] == "error"
    assert messages[-1]["status"] == "failed"
    assert "sensitive upstream detail" not in repr(messages)
