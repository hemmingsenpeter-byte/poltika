"""Task B0.1.7: a stored scenario and run outlive the application process.

A hosted deployment restarts (a deploy, a platform restart). The scenario store
is PostgreSQL only (`scenarios/store.py`), so a run's deep link must resolve
after the app is torn down and started again against the same database. The
lifespan cycle below stands in for that restart; the database is the throwaway
PostgreSQL server from `tests/conftest.py`, so the test skips when no server
binaries are installed and fails under `POLTIKA_REQUIRE_POSTGRES=1`.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from tests.unit.api.test_workbench_api import _reform, configured  # noqa: F401 (fixture)


@pytest.fixture
def stored(
    database_url: str, monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    request.getfixturevalue("configured")  # the Workbench tests' synthetic population
    monkeypatch.setenv("POLTIKA_DATABASE_URL", database_url)


@pytest.mark.postgres
def test_a_stored_run_and_its_deep_link_survive_an_app_restart(stored: None) -> None:
    # A value no other test uses: scenarios are stored once per content, and the
    # database is shared across the session.
    body = {"title": "Restart check", "options": [{"label": "Option A", "reform": _reform("52500")}]}

    with TestClient(app) as before:  # first process
        created = before.post("/api/v1/scenarios", json=body)
        assert created.status_code == 201, created.text
        scenario_id = created.json()["scenario_id"]
        run = before.post(f"/api/v1/scenarios/{scenario_id}/runs")
        assert run.status_code == 201, run.text
        run_id = run.json()["run_id"]
        workspace_before: dict[str, Any] = before.get(
            f"/api/v1/scenarios/{scenario_id}/runs/{run_id}"
        ).json()

    with TestClient(app) as after:  # second process, same database
        listed = after.get("/api/v1/scenarios").json()
        assert scenario_id in {item["scenario_id"] for item in listed["items"]}
        deep_link = after.get(f"/api/v1/scenarios/{scenario_id}/runs/{run_id}")
        assert deep_link.status_code == 200, deep_link.text
        assert deep_link.json() == workspace_before
        assert after.get(f"/api/v1/scenarios/{scenario_id}").json() == workspace_before
