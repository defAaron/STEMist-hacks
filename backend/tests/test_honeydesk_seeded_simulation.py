from __future__ import annotations

import asyncio
import json
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from app.api import routes_simulate
from app.pipeline.classify import classify


SCENARIO_DIR = Path(__file__).parents[1] / "app" / "scenarios"
EXPECTED = {
    "SC-1": "credential_harvest",
    "SC-2": "urgency_pii_scam",
    "SC-3": "social_verify",
}
DOCUMENTATION_NETWORKS = (
    ip_network("192.0.2.0/24"),
    ip_network("198.51.100.0/24"),
    ip_network("203.0.113.0/24"),
)


def test_seeded_scenarios_are_safe_stable_and_classify_as_expected() -> None:
    loaded_ids: set[str] = set()

    for fixture_path in sorted(SCENARIO_DIR.glob("sc*.json")):
        scenario = json.loads(fixture_path.read_text(encoding="utf-8"))
        scenario_id = scenario["scenario_id"]
        loaded_ids.add(scenario_id)

        assert scenario["expected_technique"] == EXPECTED[scenario_id]
        assert classify(scenario)["technique"] == EXPECTED[scenario_id]
        assert scenario["cached_brief_victim"]
        assert len(scenario["cached_brief_victim"].split()) <= 120
        assert any(
            ip_address(scenario["ip"]) in network
            for network in DOCUMENTATION_NETWORKS
        )
        assert "password" not in scenario
        assert "token" not in scenario
        assert "ssn_value" not in scenario
        assert "routing_number" not in scenario

    assert loaded_ids == set(EXPECTED)


def test_scenario_loader_is_allowlisted_and_returns_defensive_copies() -> None:
    first = routes_simulate.load_scenario("SC-1")
    first["scenario_id"] = "changed"

    assert routes_simulate.load_scenario("SC-1")["scenario_id"] == "SC-1"

    for invalid_id in ("../../etc/passwd", "sc1.json", "SC-4"):
        try:
            routes_simulate.load_scenario(invalid_id)
        except KeyError:
            pass
        else:
            raise AssertionError(f"{invalid_id!r} bypassed the scenario allowlist")


def test_post_simulate_runs_shared_pipeline_as_replay(monkeypatch: Any) -> None:
    calls: list[tuple[dict[str, Any], str]] = []

    async def fake_run_pipeline(
        scenario: dict[str, Any], *, source: str
    ) -> dict[str, Any]:
        calls.append((scenario, source))
        return {
            "id": "event-test",
            "scenario_id": scenario["scenario_id"],
            "source": source,
            "technique": "urgency_pii_scam",
            "brief_victim": "Cached safe brief.",
        }

    monkeypatch.setattr(routes_simulate, "run_pipeline", fake_run_pipeline)

    response = asyncio.run(
        routes_simulate.simulate(
            routes_simulate.SimulateRequest(scenario_id="SC-2")
        )
    )

    assert response["scenario_id"] == "SC-2"
    assert response["source"] == "replay"
    assert response["technique"] == "urgency_pii_scam"
    assert calls[0][0]["scenario_id"] == "SC-2"
    assert "expected_technique" not in calls[0][0]
    assert "cached_brief_victim" not in calls[0][0]
    assert calls[0][1] == "replay"


def test_post_simulate_rejects_unknown_and_malformed_ids(monkeypatch: Any) -> None:
    async def should_not_run(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("pipeline must not run for invalid scenario IDs")

    monkeypatch.setattr(routes_simulate, "run_pipeline", should_not_run)

    try:
        asyncio.run(
            routes_simulate.simulate(
                routes_simulate.SimulateRequest(
                    scenario_id="../../etc/passwd"
                )
            )
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("unknown scenario ID was accepted")

    for invalid_payload in (
        {"scenario_id": ""},
        {"scenario_id": "SC-1", "extra": True},
    ):
        try:
            routes_simulate.SimulateRequest(**invalid_payload)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"malformed payload was accepted: {invalid_payload}")

    simulate_route = next(
        route for route in routes_simulate.router.routes if route.path == "/simulate"
    )
    assert simulate_route.methods == {"POST"}
