"""Read-only polling APIs for stored HoneyDesk events."""

from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.validators import validate_event_id
from app.models import db

router = APIRouter(tags=["events"])


@router.get("/events")
async def events(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict[str, object]]:
    """Return newest events first for dashboard polling."""

    return await asyncio.to_thread(db.list_events, limit=limit, offset=offset)


@router.get("/events/{event_id}")
async def event_detail(event_id: str) -> dict[str, object]:
    """Return a complete event, including its brief and pipeline steps."""

    validate_event_id(event_id)
    event = await asyncio.to_thread(db.get_event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/stats")
async def stats() -> dict[str, object]:
    """Return aggregate counts derived from all stored events."""

    return await asyncio.to_thread(db.get_stats)
