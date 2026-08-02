"""Secret-safe capture API boundary."""

from __future__ import annotations

import asyncio
import copy
import inspect
import json
import re
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Literal
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.api.deps import CurrentUser
from app.config import TRUST_PROXY
from app.services.redact import (
    normalize_field_name,
    redact_secrets,
    scrub_secret_text,
    secret_flag_for_field,
)

router = APIRouter(tags=["capture"])

_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")
_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)
_MAX_BODY_BYTES = 64 * 1024


class CaptureMeta(BaseModel):
    """Non-secret interaction metadata accepted from a decoy."""

    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    dwell_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    referrer: str | None = Field(default=None, max_length=512)
    campaign: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("referrer")
    @classmethod
    def remove_referrer_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parts = urlsplit(value)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))[:512]

    @field_validator("campaign")
    @classmethod
    def validate_campaign(cls, value: str | None) -> str | None:
        if value is not None and not _IDENTIFIER_RE.fullmatch(value):
            raise ValueError("campaign must be an identifier, not user data")
        return value


class CaptureRequest(BaseModel):
    """Allowlisted capture signals; there are intentionally no value fields."""

    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    decoy_id: str = Field(min_length=1, max_length=64)
    path: str | None = Field(default=None, max_length=256)
    fields_present: list[str] = Field(min_length=1, max_length=32)
    password_entered: bool = False
    ssn_entered: bool = False
    token_entered: bool = False
    bank_data_entered: bool = False
    email_domain: str | None = Field(default=None, max_length=253)
    meta: CaptureMeta = Field(default_factory=CaptureMeta)

    @field_validator("decoy_id")
    @classmethod
    def validate_decoy_id(cls, value: str) -> str:
        if not _IDENTIFIER_RE.fullmatch(value):
            raise ValueError("decoy_id must be a safe identifier")
        return value.lower()

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.startswith("/") or "?" in value or "#" in value:
            raise ValueError("path must be an absolute path without query or fragment")
        return value

    @field_validator("fields_present")
    @classmethod
    def validate_field_names(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            if not _IDENTIFIER_RE.fullmatch(value):
                raise ValueError("fields_present may contain field names only")
            field_name = normalize_field_name(value)
            if field_name and field_name not in normalized:
                normalized.append(field_name)
        if not normalized:
            raise ValueError("at least one field name is required")
        return normalized

    @field_validator("email_domain")
    @classmethod
    def validate_email_domain(cls, value: str | None) -> str | None:
        if value is None:
            return None
        domain = value.lower().rstrip(".")
        if not _DOMAIN_RE.fullmatch(domain):
            raise ValueError("email_domain must contain a domain only")
        return domain


class CaptureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    status: Literal["accepted"] = "accepted"


def _contains_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and secret_flag_for_field(key) is not None:
                return True
            if _contains_secret_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_secret_key(item) for item in value)
    return False


async def _validated_payload(request: Request) -> CaptureRequest:
    body = await request.body()
    if not body or len(body) > _MAX_BODY_BYTES:
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if body else status.HTTP_400_BAD_REQUEST
        raise HTTPException(code, "Capture payload is empty or too large")

    try:
        raw = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid capture payload") from None

    if not isinstance(raw, dict) or _contains_secret_key(raw):
        # Keep this error generic: validation responses must never reflect a secret.
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Secret values are not accepted; send field names and boolean flags only",
        )

    try:
        return CaptureRequest.model_validate(raw)
    except ValidationError:
        # Pydantic errors include rejected input by default, so do not return them.
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid capture payload") from None


def _client_ip(request: Request) -> str:
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()[:64]
    return (request.client.host if request.client else "unknown")[:64]


def _build_event(
    payload: CaptureRequest,
    request: Request,
    event_id: str,
    *,
    user_id: str,
) -> dict[str, Any]:
    capture = payload.model_dump(mode="json")
    for field_name in capture["fields_present"]:
        flag = secret_flag_for_field(field_name)
        if flag is not None:
            capture[flag] = True
    capture["meta"]["field_flags"] = {
        "password_entered": capture["password_entered"],
        "ssn_entered": capture["ssn_entered"],
        "token_entered": capture["token_entered"],
        "bank_data_entered": capture["bank_data_entered"],
    }

    event = {
        "id": event_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "live",
        "user_id": user_id,
        "ip": _client_ip(request),
        "user_agent": scrub_secret_text(request.headers.get("user-agent", ""))[:512],
        **capture,
    }
    return redact_secrets(event)


async def _call(candidate: Any, event: dict[str, Any]) -> None:
    if inspect.iscoroutinefunction(candidate):
        result = await candidate(event)
    else:
        result = await asyncio.to_thread(candidate, event)
    if inspect.isawaitable(result):
        await result


async def _persist_directly(event: dict[str, Any]) -> None:
    """Use the DB module only when no pipeline entry point is available."""

    try:
        db = import_module("app.models.db")
    except ModuleNotFoundError as exc:
        raise RuntimeError("Capture requires app.pipeline.runner or app.models.db") from exc

    for name in ("insert_event", "create_event", "save_event"):
        candidate = getattr(db, name, None)
        if callable(candidate):
            await _call(candidate, event)
            return
    raise RuntimeError("app.models.db has no supported event persistence function")


async def dispatch_capture(event: dict[str, Any]) -> None:
    """Send a sanitized event through the shared pipeline, if available."""

    try:
        runner = import_module("app.pipeline.runner")
    except ModuleNotFoundError:
        await _persist_directly(event)
        return

    for name in ("run_pipeline", "run_capture", "process_capture"):
        candidate = getattr(runner, name, None)
        if callable(candidate):
            await _call(candidate, event)
            return

    await _persist_directly(event)


def _inline_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Flatten Pydantic `$defs` so Swagger/OpenAPI can resolve nested models."""

    defs = schema.pop("$defs", None) or schema.pop("definitions", {}) or {}

    def resolve(node: Any) -> Any:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith(("#/$defs/", "#/definitions/")):
                name = ref.rsplit("/", 1)[-1]
                if name in defs:
                    return resolve(copy.deepcopy(defs[name]))
            return {key: resolve(value) for key, value in node.items()}
        if isinstance(node, list):
            return [resolve(item) for item in node]
        return node

    return resolve(schema)


_CAPTURE_REQUEST_SCHEMA = _inline_json_schema(CaptureRequest.model_json_schema())


@router.post(
    "/capture",
    response_model=CaptureResponse,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": _CAPTURE_REQUEST_SCHEMA}},
        }
    },
)
async def capture(
    request: Request,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
) -> CaptureResponse:
    payload = await _validated_payload(request)
    event_id = str(uuid4())
    event = _build_event(payload, request, event_id, user_id=user["id"])
    background_tasks.add_task(dispatch_capture, event)
    return CaptureResponse(event_id=event_id)
