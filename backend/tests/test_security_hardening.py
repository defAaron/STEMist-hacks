"""Regression tests for login/API hardening checklist items."""

from __future__ import annotations

import importlib
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parents[2]


def _clear_app_modules() -> None:
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


@pytest.fixture()
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    database = tmp_path / "security.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("EXPOSE_API_DOCS", "true")
    monkeypatch.setenv("REQUIRE_SIMULATE_TOKEN", "false")
    monkeypatch.delenv("SIMULATE_TOKEN", raising=False)
    monkeypatch.delenv("FORCE_HTTPS", raising=False)

    _clear_app_modules()
    from app.models import db as db_module

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()
    _clear_app_modules()


def _signup(client: TestClient, email: str) -> dict:
    response = client.post(
        "/auth/signup", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_env_secret_files_are_not_tracked() -> None:
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
    ).split(b"\0")
    forbidden_suffixes = (".env", ".env.local", ".pem", ".key")
    offenders: list[str] = []
    for raw in tracked:
        if not raw:
            continue
        path = raw.decode()
        name = Path(path).name
        if name.endswith(".example"):
            continue
        if name.startswith(".env") or name.endswith(forbidden_suffixes):
            offenders.append(path)
        if "credentials" in name.lower() and name.endswith((".json", ".txt")):
            offenders.append(path)
    assert offenders == []


def test_protected_routes_require_authentication(client: TestClient) -> None:
    protected = [
        ("GET", "/events"),
        ("GET", "/stats"),
        ("GET", "/auth/me"),
        ("GET", "/events/abcd1234abcd1234abcd1234abcd1234"),
        ("GET", "/export/stix/abcd1234abcd1234abcd1234abcd1234"),
        ("POST", "/capture"),
        ("POST", "/simulate"),
    ]
    for method, path in protected:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json={})
        assert response.status_code == 401, path
        body = response.json()
        assert "traceback" not in str(body).lower()
        assert "detail" in body


def test_error_responses_do_not_leak_stack_traces(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Force an unhandled error through a temporary route.
    database = tmp_path / "boom.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("REQUIRE_SIMULATE_TOKEN", "false")
    monkeypatch.delenv("SIMULATE_TOKEN", raising=False)

    _clear_app_modules()
    from app.models import db as db_module

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()

    from app.main import app

    @app.get("/__boom_test__")
    async def boom() -> None:
        raise RuntimeError("secret-internal-path:/tmp/leak")

    with TestClient(app, raise_server_exceptions=False) as isolated:
        response = isolated.get("/__boom_test__")

    assert response.status_code == 500
    payload = response.text
    assert "secret-internal-path" not in payload
    assert "Traceback" not in payload
    assert "RuntimeError" not in payload
    assert response.json() == {"detail": "Internal server error"}

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()
    _clear_app_modules()


def test_security_headers_present(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "no-store" in response.headers.get("Cache-Control", "")


def test_capture_input_is_validated_and_sanitized(client: TestClient) -> None:
    token = _signup(client, "safe@example.test")["token"]
    headers = {"Authorization": f"Bearer {token}"}

    rejected = client.post(
        "/capture",
        headers=headers,
        json={
            "decoy_id": "../etc/passwd",
            "fields_present": ["email"],
            "password": "plaintext-should-never-be-accepted",
        },
    )
    assert rejected.status_code == 400
    assert "plaintext-should-never-be-accepted" not in rejected.text

    xssish = client.post(
        "/capture",
        headers=headers,
        json={
            "decoy_id": "portal",
            "fields_present": ["<script>alert(1)</script>"],
        },
    )
    assert xssish.status_code == 400


def test_tenant_queries_never_list_all_events(tmp_path) -> None:
    from app.models.db import EventStore

    store = EventStore(tmp_path / "tenant.db")
    store.insert_event(decoy_id="portal", user_id="a")
    store.insert_event(decoy_id="portal", user_id="b")
    assert len(store.list_events(user_id="a")) == 1
    assert store.get_stats(user_id="b")["attacks_caught"] == 1
    with pytest.raises(TypeError):
        store.list_events()  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        store.get_stats()  # type: ignore[call-arg]


def test_debug_docs_disabled_in_production(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "prod-docs.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SIMULATE_TOKEN", "prod-simulate-token")
    monkeypatch.delenv("EXPOSE_API_DOCS", raising=False)
    monkeypatch.delenv("REQUIRE_SIMULATE_TOKEN", raising=False)

    _clear_app_modules()
    import app.config as config

    importlib.reload(config)
    assert config.EXPOSE_API_DOCS is False
    assert config.REQUIRE_SIMULATE_TOKEN is True

    from app.models import db as db_module

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()

    import app.main as main

    importlib.reload(main)
    with TestClient(main.app) as prod_client:
        assert prod_client.get("/docs").status_code == 404
        assert prod_client.get("/redoc").status_code == 404
        assert prod_client.get("/openapi.json").status_code == 404
        assert prod_client.get("/health").status_code == 200

    with db_module._STORE_CACHE_LOCK:
        db_module._STORE_CACHE.clear()
    _clear_app_modules()


def test_production_requires_simulate_token(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "prod-sim.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SIMULATE_TOKEN", raising=False)
    monkeypatch.delenv("REQUIRE_SIMULATE_TOKEN", raising=False)

    _clear_app_modules()
    import app.config as config

    importlib.reload(config)
    import app.main as main

    importlib.reload(main)
    with pytest.raises(RuntimeError, match="SIMULATE_TOKEN"):
        with TestClient(main.app):
            pass
    _clear_app_modules()
