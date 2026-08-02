from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

import pytest

from app.models.db import (
    EventStore,
    append_pipeline_step,
    get_event,
    get_stats,
    init_db,
    insert_event,
    list_events,
    safe_json_dumps,
    update_event,
)


def test_event_lifecycle_and_pipeline_metadata(tmp_path):
    database = tmp_path / "events.db"
    store = EventStore(database)

    created = store.insert_event(
        {
            "decoy_id": "portal",
            "source": "replay",
            "scenario_id": "SC-1",
            "fields_present": ["email", "password"],
            "password_entered": True,
            "meta": {"dwell_ms": 8400},
            "source_metadata": {"transport": "simulate-route"},
            "scenario_metadata": {"name": "Aid Portal Login"},
        }
    )
    assert created["id"]
    assert created["technique"] == "unknown"
    assert created["pipeline_status"] == "running"
    assert created["fields_present"] == ["email", "password"]
    assert created["created_at"].endswith("Z")

    updated = store.update_event(
        created["id"],
        technique="credential_harvest",
        severity="high",
        score=91,
        reasons=["Portal requested a password"],
        data_targeted=["school_email", "password"],
        brief={
            "victim": "This page tried to collect school credentials.",
            "it": "Credential collection was observed.",
            "source": "cache",
            "actions": ["Change reused passwords", "Enable MFA"],
        },
        pipeline_status="complete",
    )
    assert updated is not None
    assert updated["brief_victim"].startswith("This page")
    assert updated["brief_it"].startswith("Credential")
    assert updated["brief_source"] == "cache"
    assert updated["brief"]["actions"][0] == "Change reused passwords"

    stepped = store.append_pipeline_step(
        created["id"], "classify", status="ok", detail="score=91"
    )
    assert stepped is not None
    assert stepped["pipeline_steps"][0]["step"] == "classify"
    assert store.get_event(created["id"]) == stepped
    assert store.get_event("missing") is None


def test_secret_keys_are_never_persisted(tmp_path):
    database = tmp_path / "secrets.db"
    store = EventStore(database)
    event = store.insert_event(
        {
            "decoy_id": "portal",
            "password": "SUPER-SECRET-PASSWORD",
            "meta": {
                "campaign": "demo",
                "api_key": "sk-obvious-secret",
                "nested": {
                    "access_token": "bearer-obvious-secret",
                    "safe": "kept",
                },
            },
            "metadata": {
                "client_secret": "client-obvious-secret",
                "note": "safe",
            },
            "fields_present": ["email", "password", "ssn"],
        }
    )

    assert event["meta"] == {"campaign": "demo", "nested": {"safe": "kept"}}
    assert event["metadata"] == {"note": "safe"}
    assert event["fields_present"] == ["email", "password", "ssn"]

    with sqlite3.connect(database) as connection:
        row_text = repr(connection.execute("SELECT * FROM events").fetchone())
    assert "SUPER-SECRET-PASSWORD" not in row_text
    assert "sk-obvious-secret" not in row_text
    assert "bearer-obvious-secret" not in row_text
    assert "client-obvious-secret" not in row_text

    with pytest.raises(ValueError, match="no persistable fields"):
        store.update_event(event["id"], {"refresh_token": "do-not-store"})


def test_list_filters_ordering_and_stats(tmp_path):
    store = EventStore(tmp_path / "stats.db")
    tenant = "user-alice"
    first = store.insert_event(
        decoy_id="portal",
        user_id=tenant,
        created_at="2026-08-02T12:00:00Z",
        source="live",
        technique="credential_harvest",
        severity="high",
    )
    second = store.insert_event(
        decoy_id="scholarship",
        user_id=tenant,
        created_at="2026-08-02T13:00:00Z",
        source="replay",
        scenario_id="SC-2",
        technique="urgency_pii_scam",
        severity="critical",
    )
    store.insert_event(
        decoy_id="portal",
        user_id="user-bob",
        created_at="2026-08-02T14:00:00Z",
        source="live",
        technique="bot_probe",
        severity="low",
    )

    assert [item["id"] for item in store.list_events(user_id=tenant)] == [
        second["id"],
        first["id"],
    ]
    assert store.list_events(user_id=tenant, source="live")[0]["id"] == first["id"]
    assert store.list_events(user_id=tenant, scenario_id="SC-2")[0]["id"] == second["id"]

    stats = store.get_stats(user_id=tenant)
    assert stats["attacks_caught"] == 2
    assert stats["by_technique"] == {
        "credential_harvest": 1,
        "urgency_pii_scam": 1,
    }
    assert stats["by_severity"] == {"critical": 1, "high": 1}
    assert stats["by_source"] == {"live": 1, "replay": 1}
    assert stats["last_event_at"] == second["created_at"]
    assert store.get_stats(user_id=tenant, source="live")["attacks_caught"] == 1
    with pytest.raises(ValueError, match="user_id is required"):
        store.list_events(user_id=" ")
    with pytest.raises(ValueError, match="user_id is required"):
        store.get_stats(user_id="")


def test_module_api_and_safe_json_types(tmp_path):
    database = tmp_path / "module.db"
    assert init_db(database).database == str(database)
    tenant = "user-module"
    event = insert_event(
        {
            "id": uuid.uuid4(),
            "decoy_id": "discord",
            "user_id": tenant,
            "geo": {
                "observed": datetime(2026, 8, 2, tzinfo=timezone.utc),
            },
        },
        database=database,
    )
    assert get_event(event["id"], database=database) == event

    updated = update_event(
        event["id"],
        database=database,
        technique="social_verify",
        pipeline_status="complete",
    )
    assert updated is not None
    append_pipeline_step(event["id"], "brief", database=database)
    assert list_events(
        database=database, user_id=tenant, technique="social_verify"
    )[0]["id"] == event["id"]
    assert get_stats(database=database, user_id=tenant)["attacks_caught"] == 1
    assert '"values":[1,2,3]' in safe_json_dumps({"values": {3, 1, 2}})


def test_validation_and_in_memory_store():
    store = EventStore(":memory:")
    with pytest.raises(ValueError, match="decoy_id"):
        store.insert_event(source="live")
    with pytest.raises(ValueError, match="score"):
        store.insert_event(decoy_id="portal", score=101)
    with pytest.raises(ValueError, match="source"):
        store.insert_event(decoy_id="portal", source="external")
    with pytest.raises(ValueError, match="limit"):
        store.list_events(user_id="user-1", limit=0)

    created = store.insert_event(decoy_id="portal", user_id="user-1")
    assert store.get_event(created["id"]) is not None
    store.close()


def test_initialization_upgrades_a_minimal_legacy_table(tmp_path):
    database = tmp_path / "legacy.db"
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE events (id TEXT PRIMARY KEY, decoy_id TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO events (id, decoy_id) VALUES (?, ?)", ("legacy-1", "portal")
        )

    store = EventStore(database)
    legacy = store.get_event("legacy-1")
    assert legacy is not None
    assert legacy["technique"] == "unknown"
    assert legacy["pipeline_steps"] == []
    assert legacy["created_at"].endswith("Z")

    fresh = store.insert_event(decoy_id="discord")
    assert store.get_event(fresh["id"]) == fresh
