import asyncio
import json
from typing import Any

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.routes_capture import (
    CaptureRequest,
    _build_event,
    _validated_payload,
)


def _request(payload: Any, headers: dict[str, str] | None = None) -> Request:
    body = json.dumps(payload).encode()
    sent = False

    async def receive() -> dict[str, Any]:
        nonlocal sent
        if sent:
            return {"type": "http.disconnect"}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    raw_headers = [
        (key.lower().encode(), value.encode()) for key, value in (headers or {}).items()
    ]
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/capture",
            "headers": raw_headers,
            "client": ("198.51.100.8", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
            "query_string": b"",
        },
        receive,
    )


@pytest.mark.parametrize(
    "secret_payload,secret",
    [
        ({"password": "hunter2"}, "hunter2"),
        ({"meta": {"ssn": "111-22-3333"}}, "111-22-3333"),
        ({"meta": {"token": "abc.def"}}, "abc.def"),
        ({"bank_account": "12345678"}, "12345678"),
    ],
)
def test_capture_rejects_plaintext_secrets_without_echo(
    secret_payload: dict[str, Any], secret: str
) -> None:
    payload = {
        "decoy_id": "portal",
        "fields_present": ["email", "password"],
        **secret_payload,
    }

    with pytest.raises(HTTPException) as caught:
        asyncio.run(_validated_payload(_request(payload)))

    assert caught.value.status_code == 400
    assert secret not in str(caught.value.detail)


def test_capture_event_contains_only_safe_signals_and_metadata() -> None:
    payload = CaptureRequest.model_validate(
        {
            "decoy_id": "Scholarship",
            "path": "/aid/confirm",
            "fields_present": [
                "email",
                "password",
                "ssn",
                "routing_number",
                "token",
            ],
            "email_domain": "Student.Example",
            "meta": {
                "dwell_ms": 8400,
                "referrer": "https://example.test/start?token=do-not-store",
                "campaign": "demo-1",
            },
        }
    )
    request = _request(
        {},
        {
            "user-agent": "DemoBrowser/1.0",
            "x-forwarded-for": "203.0.113.4",
        },
    )

    event = _build_event(payload, request, "event-1")

    assert event["id"] == "event-1"
    assert event["source"] == "live"
    assert event["ip"] == "198.51.100.8"
    assert event["decoy_id"] == "scholarship"
    assert event["fields_present"] == [
        "email",
        "password",
        "ssn",
        "routing_number",
        "token",
    ]
    assert event["password_entered"] is True
    assert event["ssn_entered"] is True
    assert event["token_entered"] is True
    assert event["bank_data_entered"] is True
    assert event["email_domain"] == "student.example"
    assert event["meta"]["referrer"] == "https://example.test/start"
    assert event["meta"]["field_flags"] == {
        "password_entered": True,
        "ssn_entered": True,
        "token_entered": True,
        "bank_data_entered": True,
    }
    assert "do-not-store" not in repr(event)


def test_capture_schema_forbids_unknown_value_fields() -> None:
    with pytest.raises(Exception):
        CaptureRequest.model_validate(
            {
                "decoy_id": "portal",
                "fields_present": ["email"],
                "username": "student@example.test",
            }
        )
