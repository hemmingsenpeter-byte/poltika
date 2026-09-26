"""v0.2 Task 10.1: the microsimulation routes, on a toy synthetic
population written to a temporary file."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.scenarios.microsim.synthetic import generate
from poltika.semantics.population import SYNTHETIC_LABEL
from tests.unit.scenarios.microsim.test_synthetic import _spec

client = TestClient(app)
THRESHOLD: dict[str, Any] = {
    "reform_id": "threshold",
    "overrides": [
        {
            "policy_id": "working_for_families",
            "parameter_id": "family_tax_credit_abatement_threshold",
            "operation": "set",
            "value": "50000",
        }
    ],
}


@pytest.fixture
def configured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    population, _ = generate(_spec(households=40))
    path = tmp_path / "population.json"
    path.write_text(population.model_dump_json())
    monkeypatch.setenv("POLTIKA_POPULATION_PATH", str(path))
    return path


def test_unconfigured_population_is_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLTIKA_POPULATION_PATH", raising=False)
    assert client.get("/microsim/population").status_code == 503
    assert client.post("/microsim/runs", json={"reform": THRESHOLD}).status_code == 503


def test_population_and_parameters(configured: Path) -> None:
    described = client.get("/microsim/population").json()
    assert described["synthetic"] is True and described["label"] == SYNTHETIC_LABEL
    assert described["households"] == 40
    params = client.get("/microsim/parameters").json()
    threshold = next(
        p for p in params if p["parameter_id"] == "family_tax_credit_abatement_threshold"
    )
    assert threshold["outcome"] == "resolved" and threshold["source_id"]


def test_run_returns_tables_explanation_and_identity(configured: Path) -> None:
    response = client.post("/microsim/runs", json={"reform": THRESHOLD})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["label"] == SYNTHETIC_LABEL and body["synthetic"] is True
    assert body["explanation"].startswith(SYNTHETIC_LABEL)
    assert body["explanation_problems"] == []
    assert body["component_set"] == ["family_tax_credit"]
    assert body["units"]["accommodation_supplement"] == "NZD per week"
    assert set(body["tables"]) == {
        "overall",
        "decile",
        "household_type",
        "children",
        "region",
        "as_area",
    }
    assert set(body["tables"]["overall"]["groups"]["all"]["by_class"]) == {
        "gain",
        "loss",
        "no_change",
        "needs_review",
        "unsupported",
    }
    assert body["overridden"][0]["reform_value"] == "50000"
    assert Decimal(body["fiscal"]["accommodation_supplement"]["delta_total"]) == 0
    again = client.post("/microsim/runs", json={"reform": THRESHOLD}).json()
    assert (again["run_id"], again["results_sha256"]) == (body["run_id"], body["results_sha256"])
    assert client.get(f"/microsim/runs/{body['run_id']}").json() == body


@pytest.mark.parametrize(
    ("request_body", "status"),
    [
        (
            {
                "reform": {
                    **THRESHOLD,
                    "overrides": [{**THRESHOLD["overrides"][0], "policy_id": "childcare"}],
                }
            },
            422,
        ),
        (
            {"reform": {**THRESHOLD, "overrides": [{**THRESHOLD["overrides"][0], "value": "-1"}]}},
            422,
        ),
        (
            {
                "reform": THRESHOLD,
                "component_set": ["family_tax_credit", "accommodation_supplement"],
            },
            422,
        ),
        ({"reform": THRESHOLD, "population_path": "/etc/passwd"}, 422),
    ],
)
def test_bad_requests(configured: Path, request_body: dict[str, Any], status: int) -> None:
    assert client.post("/microsim/runs", json=request_body).status_code == status


def test_unknown_run_is_404(configured: Path) -> None:
    assert client.get("/microsim/runs/" + "0" * 64).status_code == 404
    assert client.get("/microsim/runs/not-a-hash").status_code == 422


def test_fetch_measure_is_explicit_and_not_overwritten_by_another_request(configured: Path) -> None:
    first = client.post("/microsim/runs", json={"reform": THRESHOLD}).json()
    other = client.post("/microsim/runs", json={
        "reform": THRESHOLD, "component_set": ["accommodation_supplement"],
    }).json()
    assert first["run_id"] == other["run_id"]
    url = f"/microsim/runs/{first['run_id']}"
    assert client.get(url).json() == first
    assert client.get(url, params={"component_set": "accommodation_supplement"}).json() == other
    assert client.get(url, params={"component_set": "unknown"}).status_code == 422


def test_page_is_self_contained_and_shows_every_tab() -> None:
    response = client.get("/analyst/microsim")
    assert response.status_code == 200 and response.headers["content-type"].startswith("text/html")
    html = response.text
    for tab in ("Overview", "Distribution", "Households", "Areas", "Fiscal", "Evidence", "Methodology"):
        assert f'"{tab}"' in html
    assert "src=" not in html and "<link rel=\"stylesheet\"" not in html
    assert "full take-up" in html and "never counted as zero" in html
