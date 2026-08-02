"""Download route for sanitized STIX exports."""

from __future__ import annotations

import inspect
import json
import re
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.stix_export import event_to_stix_bundle

router = APIRouter(tags=["export"])


async def _get_event(event_id: str) -> Any:
    # Import lazily so this router remains testable while the DB module initializes.
    from app.models import db

    getter = getattr(db, "get_event", None)
    if not callable(getter):
        raise RuntimeError("app.models.db.get_event(event_id) is required")
    event = getter(event_id)
    return await event if inspect.isawaitable(event) else event


@router.get("/export/stix/{event_id}")
async def export_stix(event_id: str) -> Response:
    """Return a STIX 2.1 JSON attachment for one stored event."""
    event = await _get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    bundle = event_to_stix_bundle(event)
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", event_id)[:80] or "event"
    return Response(
        content=json.dumps(bundle, indent=2, sort_keys=True),
        media_type="application/stix+json",
        headers={
            "Content-Disposition": f'attachment; filename="honeydesk-{safe_id}.stix.json"'
        },
    )
