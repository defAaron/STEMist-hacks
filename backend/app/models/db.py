"""SQLite-backed event store for HoneyDesk.

The module exposes a small synchronous API suitable for FastAPI route handlers
and the pipeline runner. Each operation uses a short-lived connection, so it is
safe to call through FastAPI's thread pool. Writes are serialized per store and
SQLite is configured for WAL mode and a busy timeout.
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import threading
import uuid
from collections.abc import Mapping, Sequence
from contextlib import closing
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any


TECHNIQUES = frozenset(
    {
        "credential_harvest",
        "urgency_pii_scam",
        "social_verify",
        "typosquat",
        "bot_probe",
        "unknown",
    }
)
SEVERITIES = frozenset({"low", "medium", "high", "critical"})
PIPELINE_STATUSES = frozenset({"running", "complete", "failed"})
SOURCES = frozenset({"live", "simulate", "replay"})

_JSON_FIELDS = frozenset(
    {
        "geo",
        "fields_present",
        "meta",
        "reasons",
        "data_targeted",
        "brief",
        "pipeline_steps",
        "metadata",
        "source_metadata",
        "scenario_metadata",
    }
)
_LIST_FIELDS = frozenset(
    {"fields_present", "reasons", "data_targeted", "pipeline_steps"}
)
_MAPPING_FIELDS = frozenset(
    {"geo", "meta", "brief", "metadata", "source_metadata", "scenario_metadata"}
)
_TEXT_FIELDS = frozenset(
    {
        "id",
        "created_at",
        "updated_at",
        "source",
        "scenario_id",
        "decoy_id",
        "ip",
        "user_agent",
        "path",
        "email_domain",
        "technique",
        "severity",
        "brief_victim",
        "brief_it",
        "brief_source",
        "pipeline_status",
    }
)
_EVENT_FIELDS = _JSON_FIELDS | _TEXT_FIELDS | frozenset(
    {"password_entered", "score"}
)

# Exact names and common suffixes are intentionally conservative. Values under
# these keys are dropped at every nesting level before serialization.
_SECRET_KEYS = frozenset(
    {
        "password",
        "passwd",
        "pass",
        "pwd",
        "token",
        "access_token",
        "refresh_token",
        "id_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "authorization",
        "auth",
        "cookie",
        "set_cookie",
        "ssn",
        "social_security_number",
        "routing",
        "routing_number",
        "bank_account",
        "bank_account_number",
        "credit_card",
        "card_number",
        "cvv",
        "cvc",
        "private_key",
    }
)
_SECRET_SUFFIXES = (
    "_password",
    "_passwd",
    "_token",
    "_api_key",
    "_secret",
    "_private_key",
)

_CREATE_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source TEXT NOT NULL,
    scenario_id TEXT,
    decoy_id TEXT NOT NULL,
    ip TEXT NOT NULL DEFAULT '',
    user_agent TEXT NOT NULL DEFAULT '',
    path TEXT,
    geo TEXT NOT NULL DEFAULT '{}',
    fields_present TEXT NOT NULL DEFAULT '[]',
    password_entered INTEGER NOT NULL DEFAULT 0 CHECK (password_entered IN (0, 1)),
    email_domain TEXT,
    meta TEXT NOT NULL DEFAULT '{}',
    technique TEXT NOT NULL DEFAULT 'unknown',
    severity TEXT NOT NULL DEFAULT 'medium',
    score INTEGER NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    reasons TEXT NOT NULL DEFAULT '[]',
    data_targeted TEXT NOT NULL DEFAULT '[]',
    brief TEXT NOT NULL DEFAULT '{}',
    brief_victim TEXT,
    brief_it TEXT,
    brief_source TEXT,
    pipeline_status TEXT NOT NULL DEFAULT 'running',
    pipeline_steps TEXT NOT NULL DEFAULT '[]',
    metadata TEXT NOT NULL DEFAULT '{}',
    source_metadata TEXT NOT NULL DEFAULT '{}',
    scenario_metadata TEXT NOT NULL DEFAULT '{}'
)
"""

_MIGRATION_COLUMNS = {
    "created_at": "TEXT NOT NULL DEFAULT ''",
    "updated_at": "TEXT NOT NULL DEFAULT ''",
    "source": "TEXT NOT NULL DEFAULT 'live'",
    "scenario_id": "TEXT",
    "decoy_id": "TEXT NOT NULL DEFAULT 'unknown'",
    "ip": "TEXT NOT NULL DEFAULT ''",
    "user_agent": "TEXT NOT NULL DEFAULT ''",
    "path": "TEXT",
    "geo": "TEXT NOT NULL DEFAULT '{}'",
    "fields_present": "TEXT NOT NULL DEFAULT '[]'",
    "password_entered": "INTEGER NOT NULL DEFAULT 0",
    "email_domain": "TEXT",
    "meta": "TEXT NOT NULL DEFAULT '{}'",
    "technique": "TEXT NOT NULL DEFAULT 'unknown'",
    "severity": "TEXT NOT NULL DEFAULT 'medium'",
    "score": "INTEGER NOT NULL DEFAULT 0",
    "reasons": "TEXT NOT NULL DEFAULT '[]'",
    "data_targeted": "TEXT NOT NULL DEFAULT '[]'",
    "brief": "TEXT NOT NULL DEFAULT '{}'",
    "brief_victim": "TEXT",
    "brief_it": "TEXT",
    "brief_source": "TEXT",
    "pipeline_status": "TEXT NOT NULL DEFAULT 'running'",
    "pipeline_steps": "TEXT NOT NULL DEFAULT '[]'",
    "metadata": "TEXT NOT NULL DEFAULT '{}'",
    "source_metadata": "TEXT NOT NULL DEFAULT '{}'",
    "scenario_metadata": "TEXT NOT NULL DEFAULT '{}'",
}

_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_events_technique ON events(technique)",
    "CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)",
    "CREATE INDEX IF NOT EXISTS idx_events_scenario_id ON events(scenario_id)",
)


def utc_now() -> str:
    """Return a canonical UTC timestamp with a ``Z`` suffix."""

    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _normalise_key(key: Any) -> str:
    return str(key).strip().lower().replace("-", "_").replace(" ", "_")


def _is_secret_key(key: Any) -> bool:
    normalised = _normalise_key(key)
    return normalised in _SECRET_KEYS or normalised.endswith(_SECRET_SUFFIXES)


def sanitize_for_storage(value: Any) -> Any:
    """Recursively remove values stored under obvious secret-bearing keys.

    The function deliberately preserves field *names* in lists such as
    ``fields_present=["password"]`` while removing a mapping entry such as
    ``{"password": "plaintext"}``.
    """

    if isinstance(value, Mapping):
        return {
            str(key): sanitize_for_storage(item)
            for key, item in value.items()
            if not _is_secret_key(key)
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_for_storage(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [sanitize_for_storage(item) for item in sorted(value, key=str)]
    return value


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return _normalise_timestamp(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (uuid.UUID, Path)):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("non-finite decimals cannot be stored as JSON")
        return number
    raise TypeError(f"{type(value).__name__} is not safely JSON serializable")


def safe_json_dumps(value: Any) -> str:
    """Serialize sanitized JSON deterministically, rejecting NaN/Infinity."""

    return json.dumps(
        sanitize_for_storage(value),
        default=_json_default,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _normalise_timestamp(value: Any) -> str:
    if value is None:
        return utc_now()
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"invalid timestamp: {value!r}") from exc
    if not isinstance(value, datetime):
        raise TypeError("timestamp must be an ISO string, date, or datetime")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _database_from_url(database: str | os.PathLike[str] | None) -> str:
    raw = str(database or os.getenv("DATABASE_URL") or "")
    if not raw:
        return str(Path(__file__).resolve().parents[2] / "data" / "honeydesk.db")
    if raw.startswith("sqlite:///"):
        raw = raw[len("sqlite:///") :]
    elif "://" in raw:
        raise ValueError("HoneyDesk event store only supports SQLite")
    return raw


class EventStore:
    """Thread-safe SQLite event store with one connection per operation."""

    def __init__(
        self,
        database: str | os.PathLike[str] | None = None,
        *,
        initialize: bool = True,
    ) -> None:
        requested = _database_from_url(database)
        self._lock = threading.RLock()
        self._keeper: sqlite3.Connection | None = None
        self._uri = False

        if requested == ":memory:":
            self.database = (
                f"file:honeydesk-{uuid.uuid4().hex}?mode=memory&cache=shared"
            )
            self._uri = True
            self._keeper = self._new_connection()
        else:
            path = Path(requested).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self.database = str(path)

        if initialize:
            self.initialize()

    def _new_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database,
            timeout=5.0,
            uri=self._uri,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def initialize(self) -> None:
        """Create the schema and add columns missing from an older MVP DB."""

        with self._lock, closing(self._new_connection()) as connection:
            if not self._uri:
                connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(_CREATE_EVENTS_SQL)
            existing = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(events)").fetchall()
            }
            if "id" not in existing:
                raise RuntimeError("existing events table has no id column")
            for column, definition in _MIGRATION_COLUMNS.items():
                if column not in existing:
                    connection.execute(
                        f"ALTER TABLE events ADD COLUMN {column} {definition}"
                    )
            now = utc_now()
            connection.execute(
                "UPDATE events SET created_at = ? WHERE created_at = ''", (now,)
            )
            connection.execute(
                "UPDATE events SET updated_at = created_at WHERE updated_at = ''"
            )
            for statement in _INDEX_SQL:
                connection.execute(statement)
            connection.commit()

    def close(self) -> None:
        """Release the keeper connection used by in-memory stores."""

        if self._keeper is not None:
            self._keeper.close()
            self._keeper = None

    def insert_event(
        self, event: Mapping[str, Any] | None = None, **fields: Any
    ) -> dict[str, Any]:
        """Insert and return a complete event.

        ``event`` and keyword fields may be combined; keyword fields win.
        Obvious secret-bearing mapping keys are removed before validation.
        """

        payload = dict(event or {})
        payload.update(fields)
        prepared = self._prepare_insert(payload)
        columns = tuple(prepared)
        placeholders = ", ".join("?" for _ in columns)
        sql = (
            f"INSERT INTO events ({', '.join(columns)}) "
            f"VALUES ({placeholders})"
        )
        values = [self._encode(column, prepared[column]) for column in columns]

        with self._lock, closing(self._new_connection()) as connection:
            connection.execute(sql, values)
            connection.commit()
        result = self.get_event(prepared["id"])
        assert result is not None
        return result

    def update_event(
        self,
        event_id: str,
        updates: Mapping[str, Any] | None = None,
        **fields: Any,
    ) -> dict[str, Any] | None:
        """Partially update an event, returning ``None`` when it is absent."""

        payload = dict(updates or {})
        payload.update(fields)
        prepared = self._prepare_update(payload)
        if not prepared:
            raise ValueError("update contains no persistable fields")
        prepared["updated_at"] = utc_now()
        assignments = ", ".join(f"{column} = ?" for column in prepared)
        values = [self._encode(column, value) for column, value in prepared.items()]
        values.append(str(event_id))

        with self._lock, closing(self._new_connection()) as connection:
            cursor = connection.execute(
                f"UPDATE events SET {assignments} WHERE id = ?", values
            )
            connection.commit()
            if cursor.rowcount == 0:
                return None
        return self.get_event(str(event_id))

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Return one event by ID, or ``None``."""

        with closing(self._new_connection()) as connection:
            row = connection.execute(
                "SELECT * FROM events WHERE id = ?", (str(event_id),)
            ).fetchone()
        return self._decode_row(row) if row is not None else None

    def list_events(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        source: str | None = None,
        technique: str | None = None,
        severity: str | None = None,
        scenario_id: str | None = None,
        pipeline_status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return newest events with optional exact-match filters."""

        if isinstance(limit, bool) or not 1 <= int(limit) <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        if isinstance(offset, bool) or int(offset) < 0:
            raise ValueError("offset must be non-negative")

        filters = {
            "source": source,
            "technique": technique,
            "severity": severity,
            "scenario_id": scenario_id,
            "pipeline_status": pipeline_status,
        }
        clauses: list[str] = []
        values: list[Any] = []
        for column, value in filters.items():
            if value is not None:
                clauses.append(f"{column} = ?")
                values.append(value)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        values.extend((int(limit), int(offset)))

        with closing(self._new_connection()) as connection:
            rows = connection.execute(
                f"SELECT * FROM events{where} "
                "ORDER BY created_at DESC, rowid DESC LIMIT ? OFFSET ?",
                values,
            ).fetchall()
        return [self._decode_row(row) for row in rows]

    def get_stats(self, *, source: str | None = None) -> dict[str, Any]:
        """Return aggregate counts, including the API contract's core fields."""

        where = " WHERE source = ?" if source is not None else ""
        params: tuple[Any, ...] = (source,) if source is not None else ()
        with closing(self._new_connection()) as connection:
            summary = connection.execute(
                f"SELECT COUNT(*) AS total, MAX(created_at) AS last FROM events{where}",
                params,
            ).fetchone()
            techniques = connection.execute(
                f"SELECT technique, COUNT(*) AS count FROM events{where} "
                "GROUP BY technique",
                params,
            ).fetchall()
            severities = connection.execute(
                f"SELECT severity, COUNT(*) AS count FROM events{where} "
                "GROUP BY severity",
                params,
            ).fetchall()
            sources = connection.execute(
                "SELECT source, COUNT(*) AS count FROM events GROUP BY source"
            ).fetchall()
        return {
            "attacks_caught": int(summary["total"]),
            "by_technique": {
                row["technique"]: int(row["count"]) for row in techniques
            },
            "by_severity": {
                row["severity"]: int(row["count"]) for row in severities
            },
            "by_source": {row["source"]: int(row["count"]) for row in sources},
            "last_event_at": summary["last"],
        }

    def append_pipeline_step(
        self,
        event_id: str,
        step: str,
        *,
        status: str = "ok",
        detail: str | None = None,
        ts: str | datetime | None = None,
    ) -> dict[str, Any] | None:
        """Append a sanitized pipeline step to an event."""

        with self._lock:
            event = self.get_event(event_id)
            if event is None:
                return None
            entry: dict[str, Any] = {
                "step": str(step),
                "status": str(status),
                "ts": _normalise_timestamp(ts),
            }
            if detail is not None:
                entry["detail"] = str(detail)
            steps = list(event["pipeline_steps"])
            steps.append(entry)
            return self.update_event(event_id, pipeline_steps=steps)

    def _prepare_insert(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        clean = self._prepare_common(payload)
        now = utc_now()
        defaults: dict[str, Any] = {
            "id": uuid.uuid4().hex,
            "created_at": now,
            "updated_at": now,
            "source": "live",
            "scenario_id": None,
            "ip": "",
            "user_agent": "",
            "path": None,
            "geo": {},
            "fields_present": [],
            "password_entered": False,
            "email_domain": None,
            "meta": {},
            "technique": "unknown",
            "severity": "medium",
            "score": 0,
            "reasons": [],
            "data_targeted": [],
            "brief": {},
            "brief_victim": None,
            "brief_it": None,
            "brief_source": None,
            "pipeline_status": "running",
            "pipeline_steps": [],
            "metadata": {},
            "source_metadata": {},
            "scenario_metadata": {},
        }
        defaults.update(clean)
        if not str(defaults.get("decoy_id") or "").strip():
            raise ValueError("decoy_id is required")
        defaults["decoy_id"] = str(defaults["decoy_id"])
        defaults["id"] = str(defaults["id"])
        defaults["created_at"] = _normalise_timestamp(defaults["created_at"])
        defaults["updated_at"] = _normalise_timestamp(defaults["updated_at"])
        self._validate(defaults)
        return defaults

    def _prepare_update(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        clean = self._prepare_common(payload)
        clean.pop("id", None)
        if "created_at" in clean:
            clean["created_at"] = _normalise_timestamp(clean["created_at"])
        if "updated_at" in clean:
            clean["updated_at"] = _normalise_timestamp(clean["updated_at"])
        self._validate(clean)
        return clean

    def _prepare_common(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        sanitized = sanitize_for_storage(dict(payload))
        clean = {
            key: value for key, value in sanitized.items() if key in _EVENT_FIELDS
        }

        brief = clean.get("brief")
        if not isinstance(brief, Mapping):
            brief = {}
        else:
            brief = dict(brief)
        # Pipeline brief adapters return these keys at the top level. Preserve
        # the complete structured result (especially actions), while also
        # maintaining the convenient brief_victim/brief_it columns.
        for key in ("victim", "it", "actions"):
            if key in sanitized and key not in brief:
                brief[key] = sanitized[key]
        if "brief_source" in sanitized and "source" not in brief:
            brief["source"] = sanitized["brief_source"]
        if brief:
            clean["brief"] = brief

        if isinstance(brief, Mapping):
            if "brief_victim" not in clean and "victim" in brief:
                clean["brief_victim"] = brief["victim"]
            if "brief_it" not in clean and "it" in brief:
                clean["brief_it"] = brief["it"]
            if "brief_source" not in clean and "source" in brief:
                clean["brief_source"] = brief["source"]

        for field in _LIST_FIELDS:
            if field in clean:
                value = clean[field]
                if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
                    raise TypeError(f"{field} must be a list")
                clean[field] = list(value)
        for field in _MAPPING_FIELDS:
            if field in clean:
                value = clean[field]
                if value is None:
                    clean[field] = {}
                elif not isinstance(value, Mapping):
                    raise TypeError(f"{field} must be an object")
                else:
                    clean[field] = dict(value)
        if "password_entered" in clean:
            clean["password_entered"] = bool(clean["password_entered"])
        if "score" in clean:
            if isinstance(clean["score"], bool):
                raise TypeError("score must be an integer")
            clean["score"] = int(clean["score"])
        return clean

    @staticmethod
    def _validate(payload: Mapping[str, Any]) -> None:
        if "source" in payload and payload["source"] not in SOURCES:
            raise ValueError(f"source must be one of {sorted(SOURCES)}")
        if "technique" in payload and payload["technique"] not in TECHNIQUES:
            raise ValueError(f"technique must be one of {sorted(TECHNIQUES)}")
        if "severity" in payload and payload["severity"] not in SEVERITIES:
            raise ValueError(f"severity must be one of {sorted(SEVERITIES)}")
        if (
            "pipeline_status" in payload
            and payload["pipeline_status"] not in PIPELINE_STATUSES
        ):
            raise ValueError(
                f"pipeline_status must be one of {sorted(PIPELINE_STATUSES)}"
            )
        if "score" in payload and not 0 <= payload["score"] <= 100:
            raise ValueError("score must be between 0 and 100")
        safe_json_dumps(payload)

    @staticmethod
    def _encode(column: str, value: Any) -> Any:
        if column in _JSON_FIELDS:
            return safe_json_dumps(value)
        if column == "password_entered":
            return int(bool(value))
        return value

    @staticmethod
    def _decode_row(row: sqlite3.Row) -> dict[str, Any]:
        event = dict(row)
        for field in _JSON_FIELDS:
            raw = event.get(field)
            try:
                event[field] = json.loads(raw) if raw is not None else None
            except (TypeError, json.JSONDecodeError):
                event[field] = [] if field in _LIST_FIELDS else {}
        event["password_entered"] = bool(event["password_entered"])
        return event


_STORE_CACHE: dict[str, EventStore] = {}
_STORE_CACHE_LOCK = threading.Lock()


def _get_store(database: str | os.PathLike[str] | None = None) -> EventStore:
    key = _database_from_url(database)
    with _STORE_CACHE_LOCK:
        store = _STORE_CACHE.get(key)
        if store is None:
            store = EventStore(key)
            _STORE_CACHE[key] = store
        return store


def init_db(database: str | os.PathLike[str] | None = None) -> EventStore:
    """Initialize a database and return its reusable :class:`EventStore`."""

    store = _get_store(database)
    store.initialize()
    return store


def insert_event(
    event: Mapping[str, Any] | None = None,
    *,
    database: str | os.PathLike[str] | None = None,
    **fields: Any,
) -> dict[str, Any]:
    return _get_store(database).insert_event(event, **fields)


def update_event(
    event_id: str,
    updates: Mapping[str, Any] | None = None,
    *,
    database: str | os.PathLike[str] | None = None,
    **fields: Any,
) -> dict[str, Any] | None:
    return _get_store(database).update_event(event_id, updates, **fields)


def get_event(
    event_id: str, *, database: str | os.PathLike[str] | None = None
) -> dict[str, Any] | None:
    return _get_store(database).get_event(event_id)


def list_events(
    *,
    database: str | os.PathLike[str] | None = None,
    limit: int = 50,
    offset: int = 0,
    source: str | None = None,
    technique: str | None = None,
    severity: str | None = None,
    scenario_id: str | None = None,
    pipeline_status: str | None = None,
) -> list[dict[str, Any]]:
    return _get_store(database).list_events(
        limit=limit,
        offset=offset,
        source=source,
        technique=technique,
        severity=severity,
        scenario_id=scenario_id,
        pipeline_status=pipeline_status,
    )


def get_stats(
    *, database: str | os.PathLike[str] | None = None, source: str | None = None
) -> dict[str, Any]:
    return _get_store(database).get_stats(source=source)


def append_pipeline_step(
    event_id: str,
    step: str,
    *,
    status: str = "ok",
    detail: str | None = None,
    ts: str | datetime | None = None,
    database: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    return _get_store(database).append_pipeline_step(
        event_id, step, status=status, detail=detail, ts=ts
    )


__all__ = [
    "EventStore",
    "PIPELINE_STATUSES",
    "SEVERITIES",
    "SOURCES",
    "TECHNIQUES",
    "append_pipeline_step",
    "get_event",
    "get_stats",
    "init_db",
    "insert_event",
    "list_events",
    "safe_json_dumps",
    "sanitize_for_storage",
    "update_event",
    "utc_now",
]
