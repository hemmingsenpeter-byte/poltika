"""Phase C Task 12: conformance tests for the WFF and AS routes.

Each test cites the specification section or rule it covers
(`policy_specs/working_for_families/specification.md`,
`policy_specs/accommodation_supplement/specification.md`) and the matrix row
in `reviews/2026-10-11-wff-as-conformance-matrix.md`. They assert statuses,
reason codes, missing-fact lists and the absence of amounts. None asserts a
statutory dollar figure, and none changes a protected expected value
(`doctrine/test-doctrine.md`).
"""

from __future__ import annotations

import copy
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from tests.unit.api.test_as_api import _request_payload as as_payload
from tests.unit.api.test_wff_api import _request_payload as wff_payload

client = TestClient(app)
WFF = "/wff/calculate"
AS = "/accommodation-supplement/calculate"
WFF_COMPONENTS = ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start")


def _wff(**overrides: Any) -> dict[str, Any]:
    payload = wff_payload("single_ordinary_low_income")
    payload.update(overrides)
    return payload


def _components(body: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {k: v for k, v in body.items() if isinstance(v, dict) and "outcome" in v}


# --- unknown fields are rejected (BUILD_PLAN 33; v0.1 API contract) ----------


def test_wff_route_rejects_an_unknown_top_level_field() -> None:
    """Matrix X-01: an unknown request field is a 422, not silently ignored."""
    response = client.post(WFF, json=_wff(bogus_field=1))
    assert response.status_code == 422
    assert {tuple(e["loc"]) for e in response.json()["detail"]} == {("body", "bogus_field")}


def test_wff_route_rejects_an_unknown_child_field() -> None:
    """Matrix X-01: the rejection reaches nested child facts."""
    payload = _wff()
    payload["children"] = copy.deepcopy(payload["children"])
    payload["children"][0]["bogus_field"] = 1
    response = client.post(WFF, json=payload)
    assert response.status_code == 422
    assert ("body", "children", 0, "bogus_field") in {tuple(e["loc"]) for e in response.json()["detail"]}


def test_as_route_rejects_an_unknown_field() -> None:
    """Matrix X-01: the AS route also forbids extra fields, including the
    ones a caller might expect to exist (an age, a date of birth)."""
    for field in ("bogus_field", "date_of_birth", "age"):
        response = client.post(AS, json=as_payload(**{field: "x"}))
        assert response.status_code == 422, field
        assert {tuple(e["loc"]) for e in response.json()["detail"]} == {("body", field)}


# --- IWTC is never calculated against the real policy (WFF Task 10.2) ---------


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"family_scheme_income": None},
    ],
)
def test_in_work_tax_credit_is_never_calculated_with_the_real_policy(overrides: dict[str, Any]) -> None:
    """Matrix W-IWTC: 'Temporary in-work base: Task 10.2 rate-status contract'.
    The in-work base is gated, so the component has no amount whatever the
    other facts say, and no response field totals the WFF components."""
    payload = _wff(**overrides)
    response = client.post(WFF, json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    iwtc = body["in_work_tax_credit"]
    assert iwtc["outcome"] in {"needs_review", "unsupported"}
    assert iwtc["value"] is None
    assert not any("total" in key for key in body)


def test_wff_components_are_reported_separately_never_as_a_sum() -> None:
    """Matrix W-TOTAL: 'Do not sum a partial result and present it as total
    WFF entitlement'. Four named components, nothing else numeric at top level."""
    body = client.post(WFF, json=_wff()).json()
    assert set(_components(body)) == set(WFF_COMPONENTS)
    assert set(body) - set(WFF_COMPONENTS) <= {"explanations"}


# --- WFF scope boundaries: unsupported, not zero (supported domain) -----------


def test_part_year_child_makes_every_wff_component_unsupported() -> None:
    """Matrix W-SCOPE-1: 'Children are fully in the claimant's care ... for the
    whole 2026-27 tax year'; a child not qualifying all year is out of scope."""
    payload = _wff()
    payload["children"] = copy.deepcopy(payload["children"])
    payload["children"][0]["qualifies_whole_year"] = "excluded"
    body = client.post(WFF, json=payload).json()
    for name, component in _components(body).items():
        assert component["outcome"] == "unsupported", name
        assert component["value"] is None, name
        assert component["category"], name


def test_extra_instalment_year_is_unsupported_not_the_ordinary_amount() -> None:
    """Matrix W-SCOPE-2: TAA s 80KW cases 'return unsupported in this first
    branch'; unknown applicability is needs_review."""
    applies = client.post(WFF, json=_wff(extra_instalment_status="excluded")).json()
    unknown = client.post(WFF, json=_wff(extra_instalment_status="unknown")).json()
    for name, component in _components(applies).items():
        assert component["outcome"] == "unsupported" and component["value"] is None, name
    for name, component in _components(unknown).items():
        assert component["outcome"] == "needs_review" and component["value"] is None, name
        assert "extra_instalment_status" in component["missing_facts"], name


# --- AS: unsupported / needs_review table (AS supported domain) ---------------


@pytest.mark.parametrize(
    ("overrides", "outcome", "code", "missing"),
    [
        ({"partner_status": "community_spouse_or_partner"}, "unsupported", "AS_PARTNER_TYPE_NOT_MODELLED", []),
        ({"partner_status": "joint_tenancy"}, "unsupported", None, []),
        ({"claimant_category": "mixed_benefit_couple"}, "unsupported", "AS_CLAIMANT_CATEGORY_NOT_MODELLED", []),
        ({"claimant_category": "pension_or_veterans"}, "unsupported", "AS_CLAIMANT_CATEGORY_NOT_MODELLED", []),
        ({"tenure_type": "homeowner"}, "unsupported", None, []),
        ({"weekly_accommodation_costs": "0"}, "unsupported", "AS_NO_ACCOMMODATION_COSTS", []),
        ({"household_eligibility": "excluded"}, "unsupported", None, []),
        ({"household_eligibility": "unknown"}, "needs_review", "AS_HOUSEHOLD_ELIGIBILITY_UNVERIFIED", ["household_eligibility"]),
        ({"statistical_area_unit": None}, "needs_review", "AS_AREA_UNVERIFIED", ["statistical_area_unit"]),
        ({"dependent_children_count": None}, "needs_review", "AS_DEPENDENT_CHILDREN_UNVERIFIED", ["dependent_children_count"]),
        ({"claimant_category": None}, "needs_review", "AS_CLAIMANT_CATEGORY_UNVERIFIED", ["claimant_category"]),
        ({"weekly_accommodation_costs": None}, "needs_review", "AS_COSTS_UNVERIFIED", ["weekly_accommodation_costs"]),
        ({"cash_assets": None}, "needs_review", "AS_CASH_ASSETS_UNVERIFIED", ["cash_assets"]),
        (
            {"claimant_category": "non_beneficiary"},
            "needs_review",
            "AS_WEEKLY_INCOME_UNVERIFIED",
            ["weekly_income"],
        ),
    ],
)
def test_as_scope_and_missing_fact_outcomes(
    overrides: dict[str, Any], outcome: str, code: str | None, missing: list[str]
) -> None:
    """Matrix A-GATE-*: 'Unsupported ... must resolve to unsupported or
    needs_review, never a false zero or a silent default' (AS supported
    domain). Includes: an unverified Statistical Area Unit never defaults to
    Area 4; a verified $0 cost is unsupported; a missing non-beneficiary
    income is needs_review. The value is absent in every case."""
    response = client.post(AS, json=as_payload(**overrides))
    assert response.status_code == 200, response.text
    component = response.json()["accommodation_supplement"]
    assert component["outcome"] == outcome
    assert component["value"] is None
    assert component["reason"]
    if code is not None:
        assert component["code"] == code
    if outcome == "needs_review":
        assert component["missing_facts"] == missing
    else:
        assert component["category"]


def test_as_unsupported_outranks_needs_review_through_the_api() -> None:
    """Matrix A-PREC: 'unsupported outranks needs_review'. A community
    spouse (unsupported) with a missing area (needs_review) is unsupported."""
    body = client.post(
        AS, json=as_payload(partner_status="community_spouse_or_partner", statistical_area_unit=None)
    ).json()
    assert body["accommodation_supplement"]["outcome"] == "unsupported"


# --- AS: one rounding, at the end (calculation sequence step 6, r 19) ---------


@pytest.mark.parametrize("cost", ["200", "199.99", "233.33", "350.5"])
def test_a_calculated_as_amount_is_a_whole_dollar_amount(cost: str) -> None:
    """Matrix A-ROUND: 'Round the final positive amount up to the complete
    dollar (r 19)'. Structural check only: whatever the amount is, it has no
    fractional dollars; and a fractional input is accepted, not truncated."""
    response = client.post(AS, json=as_payload(weekly_accommodation_costs=cost))
    component = response.json()["accommodation_supplement"]
    assert component["outcome"] == "calculated"
    amount = Decimal(component["value"])
    assert amount == amount.to_integral_value()
