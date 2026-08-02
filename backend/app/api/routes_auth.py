"""Signup, login, logout, and session introspection."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import CurrentUser
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthCredentials(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class AuthUser(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    user: AuthUser


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: AuthCredentials) -> AuthResponse:
    try:
        result = auth_service.signup(body.email, body.password)
    except ValueError as exc:
        message = str(exc)
        # Only return known validation copy — never raw internal exceptions.
        if message.startswith("password must be at least") or message in {
            "invalid email",
            "password is too long",
        }:
            detail = message
        else:
            detail = "Invalid signup details"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from None
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None
    return AuthResponse.model_validate(result)


@router.post("/login", response_model=AuthResponse)
async def login(body: AuthCredentials) -> AuthResponse:
    try:
        result = auth_service.login(body.email, body.password)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None
    return AuthResponse.model_validate(result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    token = auth_service.extract_bearer_token(authorization)
    if token:
        auth_service.logout(token)


@router.get("/me", response_model=AuthUser)
async def me(user: CurrentUser) -> AuthUser:
    return AuthUser.model_validate(user)
