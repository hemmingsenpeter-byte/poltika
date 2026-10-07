"""Task B0.1.2 (ADR-0023): durable reform scenarios and the workspace view,
against a throwaway real PostgreSQL server."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from tests.unit.api.test_household_api import _payload
from tests.unit.api.test_workbench_api import _reform, configured  # noqa: F401 (fixture)

client = TestClient(app)
TABS = ["overview", "fiscal", "distribution", "evidence", "assumptions", "technical", "audit"]


@pytest.fixture
def stored(
    database_url: str, monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    request.getfixturevalue("configured")  # the Workbench tests' synthetic population
    monkeypatch.setenv("POLTIKA_DATABASE_URL", database_url)


def _create(title: str = "Higher threshold", value: str = "50000") -> dict[str, Any]:
    body = {"title": title, "options": [{"label": "Option A", "reform": _reform(value)}]}
    response = client.post("/api/v1/scenarios", json=body)
    assert response.status_code == 201, response.text
    return dict(response.json())


def _blocks(workspace: dict[str, Any], tab: str) -> dict[str, dict[str, Any]]:
    found = next(t for t in workspace["tabs"] if t["id"] == tab)
    return {b["id"]: b for b in found["blocks"]}


def _all_cells(workspace: dict[str, Any]) -> list[Any]:
    return [
        cell
        for tab in workspace["tabs"]
        for block in tab["blocks"]
        if block["type"] == "table"
        for row in block["rows"]
        for cell in row
    ]


@pytest.mark.postgres
def test_a_reform_scenario_is_stored_once_with_its_first_title(stored: None) -> None:
    first = _create("First title")
    again = _create("Another title")
    assert again["scenario_id"] == first["scenario_id"]
    assert again["title"] == "First title"
    assert first["runs"] == 0


@pytest.mark.postgres
def test_an_invalid_option_is_refused_before_anything_is_stored(stored: None) -> None:
    before = client.get("/api/v1/scenarios").json()["total"]
    body = {"title": "Bad", "options": [{"label": "A", "reform": _reform("-5")}]}
    response = client.post("/api/v1/scenarios", json=body)
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_scenario"
    assert client.get("/api/v1/scenarios").json()["total"] == before


@pytest.mark.postgres
def test_a_run_is_durable_reproducible_and_shown_in_seven_tabs(stored: None) -> None:
    scenario = _create()
    sid = scenario["scenario_id"]
    unrun = client.get(f"/api/v1/scenarios/{sid}").json()
    assert unrun["run"] is None
    assert {t["status"] for t in unrun["tabs"]} == {"unavailable"}

    run = client.post(f"/api/v1/scenarios/{sid}/runs")
    assert run.status_code == 201, run.text
    run_id = run.json()["run_id"]
    # Same deployment, same inputs: the same run, stored once.
    assert client.post(f"/api/v1/scenarios/{sid}/runs").json()["run_id"] == run_id

    workspace = client.get(f"/api/v1/scenarios/{sid}/runs/{run_id}").json()
    assert [t["id"] for t in workspace["tabs"]] == TABS
    assert workspace["run"]["run_id"] == run_id
    assert workspace["context"]["synthetic"] is True
    assert client.get(f"/api/v1/scenarios/{sid}").json() == workspace  # latest run

    overview = _blocks(workspace, "overview")
    ftc = overview["headline_family_tax_credit"]
    assert ftc["type"] == "metric" and ftc["precision"] == "population_estimate"
    assert ftc["unit"]["period"] == "tax_year" and ftc["unit"]["currency"] == "NZD"
    assert overview["headline_accommodation_supplement"]["unit"]["period"] == "week"
    assert overview["parameters_changed"]["title"] == "What was tested"

    fiscal = _blocks(workspace, "fiscal")
    assert fiscal["net_crown_impact"]["tone"] == "unavailable"
    # Never a combined total across WFF and the Accommodation Supplement.
    assert all("total" not in str(r[0]).lower() for r in fiscal["fiscal_components"]["rows"])

    distribution = _blocks(workspace, "distribution")
    assert "distribution_family_tax_credit_decile" in distribution
    assert "winners_losers_family_tax_credit" in distribution
    assert _blocks(workspace, "evidence")["sources_working_for_families"]["sources"]
    assert _blocks(workspace, "technical")["models"]["models"][0]["id"] == "population_runner"
    assert _blocks(workspace, "audit")["identity"]["fields"][1]["value"] == run_id

    # Every table cell is a string or null; nothing not calculated reads as 0.
    assert all(c is None or isinstance(c, str) for c in _all_cells(workspace))


@pytest.mark.postgres
def test_the_list_shows_reform_and_household_scenarios(stored: None) -> None:
    scenario = _create()
    household = client.post("/scenarios", json=_payload())
    assert household.status_code == 201
    listing = client.get("/api/v1/scenarios").json()
    kinds = {i["scenario_id"]: i["kind"] for i in listing["items"]}
    assert kinds[scenario["scenario_id"]] == "reform"
    assert kinds[household.json()["scenario_id"]] == "household"
    reforms = client.get("/api/v1/scenarios", params={"kind": "reform"}).json()["items"]
    assert {i["kind"] for i in reforms} == {"reform"}


@pytest.mark.postgres
def test_a_household_scenario_has_a_workspace(stored: None) -> None:
    created = client.post("/scenarios", json=_payload()).json()
    sid, rid = created["scenario_id"], created["result_id"]
    workspace = client.get(f"/api/v1/scenarios/{sid}/runs/{rid}").json()
    assert workspace["scenario"]["kind"] == "household"
    overview = _blocks(workspace, "overview")
    as_metric = overview["component_accommodation_supplement"]
    assert as_metric["values"][0]["value"] == "220"
    assert as_metric["precision"] == "household_rule"
    iwtc = overview["component_in_work_tax_credit"]["values"][0]
    assert iwtc["value"] is None and iwtc["outcome"] == "needs_review"
    assert next(t for t in workspace["tabs"] if t["id"] == "fiscal")["status"] == "unavailable"


@pytest.mark.postgres
def test_unknown_ids_are_coded_404s(stored: None) -> None:
    unknown = "0" * 64
    assert client.get(f"/api/v1/scenarios/{unknown}").json()["detail"]["code"] == "scenario_not_found"
    sid = _create()["scenario_id"]
    response = client.get(f"/api/v1/scenarios/{sid}/runs/{unknown}")
    assert response.json()["detail"]["code"] == "run_not_found"
    assert client.post(f"/api/v1/scenarios/{unknown}/runs").status_code == 404


def test_without_a_database_storage_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLTIKA_DATABASE_URL", raising=False)
    response = client.get("/api/v1/scenarios")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"


def test_an_unreachable_database_is_a_coded_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLTIKA_DATABASE_URL", "postgresql+psycopg://nobody@127.0.0.1:1/none")
    response = client.get("/api/v1/scenarios")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"


def test_a_group_mean_distinguishes_none_from_not_calculated() -> None:
    from decimal import Decimal

    from poltika.api.workbench_tables import NONE_IN_GROUP, NOT_CALCULATED, _mean_or

    assert _mean_or(Decimal("12.345"), Decimal(3)) == "12.35"
    assert _mean_or(None, Decimal(3)) == NONE_IN_GROUP
    assert _mean_or(None, Decimal(0)) == NOT_CALCULATED
