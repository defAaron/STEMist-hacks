"""Shared API input validators."""

from __future__ import annotations

import re

from fastapi import HTTPException, status

_EVENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{3,79}$")


def validate_event_id(event_id: str) -> str:
    """Reject malformed or path-like event IDs before they reach the database."""

    if ".." in event_id or "/" in event_id or "\\" in event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID",
        )
    if not _EVENT_ID_RE.fullmatch(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID",
        )
    return event_id
