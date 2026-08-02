"""Replay safe, bundled HoneyDesk scenarios through the shared pipeline."""

from __future__ import annotations

import json
import os
import secrets
from copy import deepcopy
from functools import lru_cache
from importlib import resources
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import CurrentUser, require_user
from app.pipeline.runner import PipelineExecutionError, run_pipeline


async def require_simulate_token(
    x_simulate_token: str | None = Header(default=None),
) -> None:
    """Require the configured replay token without exposing it in errors."""

    expected = os.getenv("SIMULATE_TOKEN")
    if expected and (
        x_simulate_token is None
        or not secrets.compare_digest(x_simulate_token, expected)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid simulate token",
        )


router = APIRouter(
    tags=["simulate"],
    dependencies=[Depends(require_user), Depends(require_simulate_token)],
)

_SCENARIO_FILES = {
    "SC-1": "sc1.json",
    "SC-2": "sc2.json",
    "SC-3": "sc3.json",
}
_REQUIRED_FIXTURE_KEYS = {
    "scenario_id",
    "decoy_id",
    "fields_present",
    "password_entered",
    "expected_technique",
    "cached_brief_victim",
}
_RUNNER_FIELDS = {
    "scenario_id",
    "decoy_id",
    "path",
    "ip",
    "user_agent",
    "geo",
    "fields_present",
    "password_entered",
    "email_domain",
    "meta",
}
_FORBIDDEN_SECRET_KEYS = {
    "password",
    "pass",
    "token",
    "access_token",
    "session_token",
    "ssn_value",
    "routing_number",
}


class SimulateRequest(BaseModel):
    """A request to replay one stable, allowlisted scenario."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str = Field(min_length=1, max_length=16)


def _contains_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            str(key).lower() in _FORBIDDEN_SECRET_KEYS
            or _contains_secret_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_secret_key(child) for child in value)
    return False


@lru_cache(maxsize=len(_SCENARIO_FILES))
def _load_scenario_cached(scenario_id: str) -> dict[str, Any]:
    """Load only a known package resource; request data never becomes a path."""
    filename = _SCENARIO_FILES.get(scenario_id)
    if filename is None:
        raise KeyError(scenario_id)

    scenario_resource = resources.files("app.scenarios").joinpath(filename)
    with scenario_resource.open("r", encoding="utf-8") as fixture:
        scenario = json.load(fixture)

    if not isinstance(scenario, dict):
        raise RuntimeError(f"Scenario {scenario_id} must be a JSON object")
    missing = _REQUIRED_FIXTURE_KEYS.difference(scenario)
    if missing:
        raise RuntimeError(
            f"Scenario {scenario_id} is missing required fields: {sorted(missing)}"
        )
    if scenario["scenario_id"] != scenario_id:
        raise RuntimeError(f"Scenario {scenario_id} has a mismatched scenario_id")
    if _contains_secret_key(scenario):
        raise RuntimeError(f"Scenario {scenario_id} contains a forbidden secret field")

    return scenario


def load_scenario(scenario_id: str) -> dict[str, Any]:
    """Return a defensive copy so pipeline mutation cannot alter the cache."""
    return deepcopy(_load_scenario_cached(scenario_id))


@router.post("/simulate")
async def simulate(request: SimulateRequest, user: CurrentUser) -> dict[str, Any]:
    """Run one seeded scenario through the same pipeline as live captures."""
    try:
        scenario = load_scenario(request.scenario_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown scenario_id",
        ) from exc

    capture = {
        key: value for key, value in scenario.items() if key in _RUNNER_FIELDS
    }
    capture["user_id"] = user["id"]
    try:
        event = await run_pipeline(capture, source="replay")
    except PipelineExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scenario replay failed",
        ) from exc
    return event
