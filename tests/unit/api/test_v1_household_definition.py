"""Copy stored household facts without filling unknowns or changing periods."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from poltika.api import v1_scenarios
from poltika.api.household import HouseholdCalculationRequest, record_from_request
from poltika.api.main import app
from poltika.common.errors import StoredRunNotFoundError
from tests.unit.api.test_household_api import _payload

client = TestClient(app)
SID = "a" * 64
RID = "b" * 64


@pytest.mark.parametrize("unknown", [False, True])
def test_copied_household_request_roundtrips_all_retained_facts(
    monkeypatch: pytest.MonkeyPatch, unknown: bool
) -> None:
    payload = _payload()
    if unknown:
        payload["wff"].update(
            household_eligibility="unknown",
            family_scheme_income=None,
            best_start_protected_credit="unknown",
            requested_policy_version="retained-wff",
        )
        payload["accommodation_supplement"].update(
            weekly_income=None,
            ordinary_rate_status="unknown",
            requested_policy_version="retained-as",
        )
        payload["as_claimant_is_wff_claimant_or_partner"] = "unknown"
    request = HouseholdCalculationRequest.model_validate(payload)
    record = record_from_request(request)
    stored = SimpleNamespace(scenario_id=SID, record=record)
    monkeypatch.setattr(v1_scenarios, "_store", lambda: SimpleNamespace(get_run=lambda _: stored))
    response = client.get(f"/api/v1/scenarios/{SID}/runs/{RID}/definition")
    assert response.status_code == 200
    copied = HouseholdCalculationRequest.model_validate(response.json())
    assert record_from_request(copied) == record
    assert copied.model_dump(mode="json") == request.model_dump(mode="json")


def test_household_copy_rejects_a_run_of_another_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    stored = SimpleNamespace(scenario_id="c" * 64)
    monkeypatch.setattr(v1_scenarios, "_store", lambda: SimpleNamespace(get_run=lambda _: stored))
    response = client.get(f"/api/v1/scenarios/{SID}/runs/{RID}/definition")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "run_not_found"


def test_household_copy_reports_a_missing_run(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(_: str) -> None:
        raise StoredRunNotFoundError("missing")

    monkeypatch.setattr(v1_scenarios, "_store", lambda: SimpleNamespace(get_run=missing))
    response = client.get(f"/api/v1/scenarios/{SID}/runs/{RID}/definition")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "run_not_found"
