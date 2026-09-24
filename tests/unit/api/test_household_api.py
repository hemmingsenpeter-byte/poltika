"""Task 33.1: POST /household/calculate end to end (FastAPI TestClient),
using golden household g2's facts and the Task 28.2 dates."""

from __future__ import annotations

from typing import Any

import yaml
from fastapi.testclient import TestClient

from poltika.api.main import app
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH

client = TestClient(app)


def _payload(household_id: str = "g2_couple_two_children_income_abated_both", **as_overrides: Any) -> dict[str, Any]:
    h = next(x for x in yaml.safe_load(GOLDEN_PATH.read_text())["households"] if x["id"] == household_id)
    return {
        "wff": {**h["wff"], "modelled_date": "2026-06-01", "requested_policy_version": "0.1.0"},
        "accommodation_supplement": {
            **h["accommodation_supplement"],
            "modelled_date": "2026-06-01",
            "assessment_week_start": "2026-06-01",
            "assessment_week_end": "2026-06-08",
            "requested_policy_version": "0.1.1",
            **as_overrides,
        },
        "as_claimant_is_wff_claimant_or_partner": h["precondition"],
    }


def test_household_route_returns_both_policies_in_native_periods() -> None:
    response = client.post("/household/calculate", json=_payload())
    assert response.status_code == 200
    body = response.json()
    # Golden g2's protected expectations.
    assert body["wff"]["family_tax_credit"] == {"outcome": "calculated", "value": "7472.500", "reason": None}
    assert body["wff"]["in_work_tax_credit"]["outcome"] == "needs_review"
    assert body["accommodation_supplement"]["value"] == "220"
    assert body["wff_period"] == ["2026-04-01", "2027-04-01"]
    assert body["accommodation_supplement_period"] == ["2026-06-01", "2026-06-08"]
    assert body["contradictions"] == []
    assert "total" not in body
    assert body["provenance"]["result_id"] == body["result_id"]
    assert body["provenance"]["accommodation_supplement"]["components"][0]["value"] == "220"


def test_household_route_reports_a_disagreement() -> None:
    response = client.post("/household/calculate", json=_payload(dependent_children_count=5))
    body = response.json()
    assert any("dependent children" in c for c in body["contradictions"])
    assert body["wff"]["family_tax_credit"]["outcome"] == "needs_review"
    assert body["accommodation_supplement"]["value"] is None


def test_household_route_rejects_a_malformed_week() -> None:
    response = client.post("/household/calculate", json=_payload(assessment_week_end="2026-06-10"))
    assert response.status_code == 422


def test_household_route_maps_a_version_mismatch_to_409() -> None:
    response = client.post("/household/calculate", json=_payload(requested_policy_version="0.1.0"))
    assert response.status_code == 409


def test_household_route_is_deterministic() -> None:
    first = client.post("/household/calculate", json=_payload()).json()
    second = client.post("/household/calculate", json=_payload()).json()
    assert (first["scenario_id"], first["result_id"]) == (second["scenario_id"], second["result_id"])
