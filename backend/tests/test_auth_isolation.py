"""Per-user auth and event isolation contracts."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# Point the store at a private temp DB before the app lifespan initializes.
@pytest.fixture()
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    database = tmp_path / "auth-isolation.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    monkeypatch.delenv("SIMULATE_TOKEN", raising=False)

    # Drop cached stores so each test gets a fresh file-backed DB.
    from app.models import db as db_module

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()


def _signup(client: TestClient, email: str, password: str = "password123") -> dict:
    response = client.post(
        "/auth/signup", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response.json()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_signup_login_me_and_logout(client: TestClient) -> None:
    created = _signup(client, "alice@example.test")
    assert created["user"]["email"] == "alice@example.test"
    assert created["token"]

    me = client.get("/auth/me", headers=_auth_headers(created["token"]))
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.test"

    login = client.post(
        "/auth/login",
        json={"email": "alice@example.test", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["token"]

    logout = client.post("/auth/logout", headers=_auth_headers(token))
    assert logout.status_code == 204
    assert client.get("/auth/me", headers=_auth_headers(token)).status_code == 401


def test_unauthenticated_apis_return_401(client: TestClient) -> None:
    assert client.get("/events").status_code == 401
    assert client.get("/stats").status_code == 401
    assert client.post(
        "/capture",
        json={
            "decoy_id": "portal",
            "fields_present": ["email", "password"],
            "password_entered": True,
        },
    ).status_code == 401
    assert client.post("/simulate", json={"scenario_id": "SC-1"}).status_code == 401
    assert client.get("/export/stix/deadbeefdeadbeefdeadbeefdeadbeef").status_code == 401


def test_events_are_isolated_between_users(client: TestClient) -> None:
    alice = _signup(client, "alice@example.test")
    bob = _signup(client, "bob@example.test")

    capture = client.post(
        "/capture",
        headers=_auth_headers(alice["token"]),
        json={
            "decoy_id": "portal",
            "fields_present": ["email", "password"],
            "password_entered": True,
            "email_domain": "school.edu",
        },
    )
    assert capture.status_code == 201
    event_id = capture.json()["event_id"]

    # BackgroundTasks run inside TestClient before the response returns.
    alice_events = client.get("/events", headers=_auth_headers(alice["token"]))
    assert alice_events.status_code == 200
    alice_ids = {item["id"] for item in alice_events.json()}
    assert event_id in alice_ids

    bob_events = client.get("/events", headers=_auth_headers(bob["token"]))
    assert bob_events.status_code == 200
    assert bob_events.json() == []

    alice_stats = client.get("/stats", headers=_auth_headers(alice["token"]))
    bob_stats = client.get("/stats", headers=_auth_headers(bob["token"]))
    assert alice_stats.json()["attacks_caught"] >= 1
    assert bob_stats.json()["attacks_caught"] == 0

    assert (
        client.get(
            f"/events/{event_id}", headers=_auth_headers(bob["token"])
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/export/stix/{event_id}", headers=_auth_headers(bob["token"])
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/export/stix/{event_id}", headers=_auth_headers(alice["token"])
        ).status_code
        == 200
    )


def test_simulate_is_scoped_to_user(client: TestClient) -> None:
    alice = _signup(client, "alice@example.test")
    bob = _signup(client, "bob@example.test")

    simulated = client.post(
        "/simulate",
        headers=_auth_headers(alice["token"]),
        json={"scenario_id": "SC-1"},
    )
    assert simulated.status_code == 200
    event = simulated.json()
    assert event["user_id"] == alice["user"]["id"]
    assert event["scenario_id"] == "SC-1"

    bob_events = client.get("/events", headers=_auth_headers(bob["token"]))
    assert bob_events.json() == []

    alice_events = client.get("/events", headers=_auth_headers(alice["token"]))
    assert any(item["id"] == event["id"] for item in alice_events.json())


def test_duplicate_signup_conflicts(client: TestClient) -> None:
    _signup(client, "same@example.test")
    again = client.post(
        "/auth/signup",
        json={"email": "same@example.test", "password": "password123"},
    )
    assert again.status_code == 409
