"""Linear async HoneyDesk pipeline orchestration.

Adapters are intentionally plain callables that receive one event mapping.
They may be synchronous or asynchronous and must return a mapping (the
persister may also return ``None``). This keeps API routes, DB code, and the
pipeline independent and avoids circular imports.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime, timezone
from typing import Any, Protocol, TypeAlias
from uuid import uuid4

from .enrich import enrich_event


Event: TypeAlias = dict[str, Any]
StepEvent: TypeAlias = dict[str, Any]
AdapterResult: TypeAlias = Mapping[str, Any] | None


class PipelineAdapter(Protocol):
    def __call__(
        self, event: Mapping[str, Any]
    ) -> AdapterResult | Awaitable[AdapterResult]: ...


class EventSink(Protocol):
    def __call__(self, event: StepEvent) -> Any | Awaitable[Any]: ...


class PipelineExecutionError(RuntimeError):
    """A safely worded pipeline failure with no capture values attached."""

    def __init__(self, step: str) -> None:
        self.step = step
        super().__init__(f"pipeline step failed: {step}")


_STEPS = ("capture", "classify", "enrich", "brief", "persist")
_SAFE_SECRET_FLAGS = {
    "bank_data_entered",
    "email_domain",
    "password_entered",
    "ssn_entered",
    "token_entered",
}
_SECRET_KEY_PARTS = (
    "password",
    "passwd",
    "pass",
    "credential",
    "secret",
    "token",
    "ssn",
    "email",
    "username",
    "authorization",
    "cookie",
    "api_key",
    "apikey",
    "routing",
    "bank_account",
    "credit_card",
    "card_number",
    "cvv",
    "cvc",
    "private_key",
    "social_security",
)


async def run_pipeline(
    capture: Mapping[str, Any],
    *,
    classifier: PipelineAdapter | None = None,
    enricher: PipelineAdapter = enrich_event,
    brief_generator: PipelineAdapter | None = None,
    persister: PipelineAdapter | None = None,
    emit: EventSink | None = None,
    event_id: str | None = None,
    source: str | None = None,
    demo_delay: float = 0.0,
) -> Event:
    """Run Capture → Classify → Enrich → Brief → Persist and return the event.

    ``classifier``, ``brief_generator``, and ``persister`` are optional only
    when the corresponding default project modules are available. ``emit`` is
    best-effort so an unavailable SSE subscriber cannot prevent persistence.
    Delays are clamped to one second per step and default to disabled.
    """

    if not isinstance(capture, Mapping):
        raise TypeError("capture must be a mapping")

    adapters = _default_adapters(
        classifier=classifier,
        brief_generator=brief_generator,
        persister=persister,
    )
    delay = _normalise_delay(demo_delay)
    resolved_id = str(event_id or capture.get("id") or uuid4())
    event: Event = {}
    current_step = "capture"

    try:
        await _announce(emit, "step_start", resolved_id, current_step, "running")
        await _pause(delay)
        event = _capture_boundary(capture, event_id=resolved_id, source=source)
        _mark_step(event, current_step, "ok")
        await _announce(
            emit, "step_end", resolved_id, current_step, "ok", "capture_redacted"
        )

        for current_step, adapter in (
            ("classify", adapters["classifier"]),
            ("enrich", enricher),
            ("brief", adapters["brief_generator"]),
        ):
            await _announce(
                emit, "step_start", resolved_id, current_step, "running"
            )
            await _pause(delay)
            result = await _invoke(adapter, event, current_step)
            event.update(_sanitise_mapping(result))
            if current_step == "classify" and "score" not in event:
                event["score"] = {
                    "low": 25,
                    "medium": 50,
                    "high": 80,
                    "critical": 95,
                }.get(str(event.get("severity")), 50)
            if current_step == "brief":
                _normalise_brief(event, result)
            _mark_step(event, current_step, "ok")
            await _announce(
                emit,
                "step_end",
                resolved_id,
                current_step,
                "ok",
                _step_detail(current_step, event),
            )

        current_step = "persist"
        await _announce(emit, "step_start", resolved_id, current_step, "running")
        await _pause(delay)
        event["pipeline_status"] = "complete"
        _mark_step(event, current_step, "ok")
        persisted = await _invoke(adapters["persister"], event, current_step)
        event.update(_sanitise_mapping(persisted))
        await _announce(
            emit, "step_end", resolved_id, current_step, "ok", "event_persisted"
        )
        await _announce(
            emit,
            "event_upsert",
            resolved_id,
            status="ok",
            payload=_sanitise_mapping(event),
        )
        await _announce(emit, "done", resolved_id, step="end", status="ok")
        return event
    except PipelineExecutionError:
        if event:
            event["pipeline_status"] = "failed"
            _mark_step(event, current_step, "failed")
        await _announce(
            emit, "step_end", resolved_id, current_step, "failed", "step_failed"
        )
        await _announce(
            emit, "error", resolved_id, current_step, "failed", "pipeline_failed"
        )
        raise
    except Exception as exc:
        if event:
            event["pipeline_status"] = "failed"
            _mark_step(event, current_step, "failed")
        await _announce(
            emit, "step_end", resolved_id, current_step, "failed", "step_failed"
        )
        await _announce(
            emit, "error", resolved_id, current_step, "failed", "pipeline_failed"
        )
        raise PipelineExecutionError(current_step) from exc


def _default_adapters(
    *,
    classifier: PipelineAdapter | None,
    brief_generator: PipelineAdapter | None,
    persister: PipelineAdapter | None,
) -> dict[str, PipelineAdapter]:
    return {
        "classifier": classifier
        or _load_adapter("app.pipeline.classify", ("classify_event", "classify")),
        "brief_generator": brief_generator
        or _load_adapter(
            "app.pipeline.brief",
            ("generate_brief", "build_brief", "create_brief"),
        ),
        "persister": persister
        or _load_adapter(
            "app.models.db",
            ("persist_event", "save_event", "create_event", "insert_event"),
        ),
    }


def _load_adapter(module_name: str, names: tuple[str, ...]) -> PipelineAdapter:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f"no adapter supplied and {module_name} is unavailable"
        ) from exc
    for name in names:
        adapter = getattr(module, name, None)
        if callable(adapter):
            return adapter
    raise RuntimeError(
        f"{module_name} must expose one of these callables: {', '.join(names)}"
    )


async def _invoke(
    adapter: PipelineAdapter, event: Mapping[str, Any], step: str
) -> Mapping[str, Any]:
    try:
        if inspect.iscoroutinefunction(adapter):
            result = await adapter(dict(event))
        else:
            result = await asyncio.to_thread(adapter, dict(event))
        if inspect.isawaitable(result):
            result = await result
    except Exception as exc:
        raise PipelineExecutionError(step) from exc
    if result is None:
        return {}
    if not isinstance(result, Mapping):
        model_dump = getattr(result, "model_dump", None)
        if callable(model_dump):
            result = model_dump(mode="json")
    if not isinstance(result, Mapping):
        raise PipelineExecutionError(step)
    return result


def _capture_boundary(
    capture: Mapping[str, Any], *, event_id: str, source: str | None
) -> Event:
    event = _sanitise_mapping(capture)
    event["id"] = event_id
    event["created_at"] = str(
        event.get("created_at") or datetime.now(timezone.utc).isoformat()
    )
    chosen_source = str(source or event.get("source") or "live").lower()
    event["source"] = (
        chosen_source
        if chosen_source in {"live", "simulate", "replay"}
        else "live"
    )
    event["fields_present"] = [
        str(field)[:80]
        for field in event.get("fields_present", ())
        if isinstance(field, str)
    ] if isinstance(event.get("fields_present"), (list, tuple, set)) else []
    event["password_entered"] = bool(event.get("password_entered", False))
    event["pipeline_status"] = "running"
    event["pipeline_steps"] = [
        {"step": step, "status": "pending"} for step in _STEPS
    ]
    return event


def _sanitise_mapping(value: Mapping[str, Any] | None) -> Event:
    if value is None:
        return {}
    clean: Event = {}
    for raw_key, item in value.items():
        key = str(raw_key)
        lowered = key.lower()
        if lowered not in _SAFE_SECRET_FLAGS and any(
            part in lowered for part in _SECRET_KEY_PARTS
        ):
            continue
        clean[key] = _sanitise_value(item)
    return clean


def _sanitise_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _sanitise_mapping(value)
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_sanitise_value(item) for item in value]
    return value


def _normalise_brief(event: Event, result: Mapping[str, Any]) -> None:
    if "victim" in result and "brief_victim" not in event:
        event["brief_victim"] = str(result["victim"])
    if "it" in result and "brief_it" not in event and result["it"] is not None:
        event["brief_it"] = str(result["it"])


def _mark_step(event: Event, step: str, status: str) -> None:
    steps = event.setdefault("pipeline_steps", [])
    if not isinstance(steps, list):
        return
    for entry in steps:
        if isinstance(entry, dict) and entry.get("step") == step:
            entry["status"] = status
            entry["ts"] = datetime.now(timezone.utc).isoformat()
            return
    steps.append(
        {
            "step": step,
            "status": status,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    )


def _step_detail(step: str, event: Mapping[str, Any]) -> str:
    if step == "classify":
        technique = str(event.get("technique") or "unknown")[:40]
        score = event.get("score")
        return f"{technique} score={score}" if isinstance(score, (int, float)) else technique
    if step == "enrich":
        geo = event.get("geo")
        label = geo.get("label") if isinstance(geo, Mapping) else "demo geo ready"
        return str(label)[:100]
    return "victim_brief_ready"


async def _announce(
    sink: EventSink | None,
    event_type: str,
    event_id: str,
    step: str | None = None,
    status: str | None = None,
    detail: str | None = None,
    payload: Any = None,
) -> None:
    if sink is None:
        return
    message: StepEvent = {
        "type": event_type,
        "event_id": event_id,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if step is not None:
        message["step"] = step
    if status is not None:
        message["status"] = status
    if detail is not None:
        message["detail"] = detail
    if payload is not None:
        message["payload"] = _sanitise_value(payload)
    try:
        emitted = sink(message)
        if inspect.isawaitable(emitted):
            await emitted
    except Exception:
        # Streaming is observability, not a prerequisite for safe persistence.
        return


def _normalise_delay(value: float) -> float:
    try:
        return min(max(float(value), 0.0), 1.0)
    except (TypeError, ValueError):
        return 0.0


async def _pause(delay: float) -> None:
    if delay:
        await asyncio.sleep(delay)
