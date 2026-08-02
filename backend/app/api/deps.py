"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.services import auth as auth_service


async def require_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    """Require a valid Bearer session token and return the public user."""

    token = auth_service.extract_bearer_token(authorization)
    user = auth_service.resolve_user_from_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[dict[str, str], Depends(require_user)]
