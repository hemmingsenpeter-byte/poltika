"""Task 21: FastAPI TestClient tests for the WFF calculation route.

Four cases, per BUILD_PLAN.md's Task 21 entry -- the fourth (a
loader-raised exception's HTTP status mapping) gets its own explicit test
rather than being left as prose-only documentation, since that's exactly
the failure mode (an exception silently becoming a 200) this task's
doctrine is most worried about.

Request payloads reuse `spec_cases.yaml`'s own scenario blocks via
`tests.conftest.load_wff_spec_case()` rather than hand-authoring a new
scenario -- the field names and FactStatus/BestStartCohort/PartnerStatus
string vocabulary are already identical between the YAML fixtures and the
API's request model (this module wraps `WffScenario`'s own fields
directly), so no separate translation is needed beyond adding
`modelled_date`/`requested_policy_version`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from fastapi.testclient import TestClient

from poltika.api.main import app
from tests.conftest import load_wff_spec_case

client = TestClient(app)


def _request_payload(case_id: str) -> dict[str, Any]:
    case = load_wff_spec_case(case_id)
    payload: dict[str, Any] = dict(case["scenario"])
    modelled_date = case["modelled_date"]
    if isinstance(modelled_date, date):
        modelled_date = modelled_date.isoformat()
    payload["modelled_date"] = modelled_date
    payload["requested_policy_version"] = case["policy_version"]
    return payload


def test_calculate_returns_calculated_result() -> None:
    """Case 1: a normal request producing a `calculated` result. Uses
    `single_ordinary_low_income`, an already-approved spec case, and
    checks the exact expected values from that case -- not just that the
    call succeeded.

    Compares by `Decimal` value, not raw string equality: `calculate_wff()`'s
    own Decimal arithmetic can legitimately produce trailing zeros (e.g.
    "7921.000" from a zero-abatement subtraction chain), which the API
    preserves rather than reformatting -- specification.md's "preserve the
    exact decimal annual result... do not introduce rounding" applies to
    the API response too, matching how every other test in this project
    compares `Decimal(actual) == Decimal(expected)`, never a literal string.
    """
    response = client.post("/wff/calculate", json=_request_payload("single_ordinary_low_income"))

    assert response.status_code == 200
    body = response.json()
    assert body["family_tax_credit"]["outcome"] == "calculated"
    assert Decimal(body["family_tax_credit"]["value"]) == Decimal(7921)
    assert body["family_tax_credit"]["reason"] is None
    assert body["minimum_family_tax_credit"]["outcome"] == "calculated"
    assert Decimal(body["minimum_family_tax_credit"]["value"]) == Decimal(6604)
    assert body["best_start"]["outcome"] == "calculated"
    assert Decimal(body["best_start"]["value"]) == Decimal(0)


def test_calculate_returns_needs_review_without_a_collapsed_value() -> None:
    """Case 2: the same request's in_work_tax_credit resolves
    needs_review under the real approved policy.yaml (in_work_base's live
    rate-status gate, Task 10.2) -- must serialize as `{"outcome":
    "needs_review", "value": null, "reason": <non-empty>}`, never a
    collapsed zero or omitted field."""
    response = client.post("/wff/calculate", json=_request_payload("single_ordinary_low_income"))

    assert response.status_code == 200
    component = response.json()["in_work_tax_credit"]
    assert component["outcome"] == "needs_review"
    assert component["value"] is None
    assert component["reason"]


def test_calculate_rejects_malformed_request_body() -> None:
    """Case 3: a malformed request body (missing a required field, and an
    invalid enum value for another) must return a 4xx with a clear
    validation error, not a 500 or an unhandled exception."""
    payload = _request_payload("single_ordinary_low_income")
    del payload["household_eligibility"]
    payload["partner_status"] = "not_a_real_status"

    response = client.post("/wff/calculate", json=payload)

    assert 400 <= response.status_code < 500
    detail = response.json()["detail"]
    fields_with_errors = {tuple(error["loc"]) for error in detail}
    assert ("body", "household_eligibility") in fields_with_errors
    assert ("body", "partner_status") in fields_with_errors


def test_calculate_maps_policy_version_mismatch_to_409_not_200() -> None:
    """Case 4: a requested_policy_version mismatch raises
    PolicyVersionMismatchError inside run_wff_module() -- this is the
    failure mode most worth testing explicitly, since a loader-raised
    exception silently collapsing into a 200 (or an unhandled 500) is
    exactly what Task 20/21's "caller-level structural errors stay
    distinguishable from calculation outcomes" discipline exists to
    prevent."""
    payload = _request_payload("single_ordinary_low_income")
    payload["requested_policy_version"] = "9.9.9"

    response = client.post("/wff/calculate", json=payload)

    assert response.status_code == 409
    assert "9.9.9" in response.json()["detail"]
