"""Read-only polling APIs for stored HoneyDesk events."""

from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser
from app.api.validators import validate_event_id
from app.models import db

router = APIRouter(tags=["events"])


@router.get("/events")
async def events(
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict[str, object]]:
    """Return newest events first for the authenticated user's dashboard."""

    return await asyncio.to_thread(
        db.list_events, limit=limit, offset=offset, user_id=user["id"]
    )


@router.get("/events/{event_id}")
async def event_detail(event_id: str, user: CurrentUser) -> dict[str, object]:
    """Return a complete event, including its brief and pipeline steps."""

    validate_event_id(event_id)
    event = await asyncio.to_thread(db.get_event, event_id, user_id=user["id"])
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/stats")
async def stats(user: CurrentUser) -> dict[str, object]:
    """Return aggregate counts derived from the authenticated user's events."""

    return await asyncio.to_thread(db.get_stats, user_id=user["id"])
