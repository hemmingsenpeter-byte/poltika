"""Programme Task 7 / v0.3 Phase 2.3: FastAPI TestClient tests for the
income-tax route.

The income-tax policy is draft, so no request is `calculated`. These tests
assert outcome, reason code, missing facts and the absence of any value --
and no monetary expected value of any kind. Case shapes follow
`tests/unit/engines/simulator/test_income_tax.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.income_tax import (
    IncomeTaxCalculationRequest,
    _income_tax_policy_dir,
    scenario_from_request,
)
from poltika.api.main import app
from poltika.engines.assurance.explanation import (
    EvidenceUsed,
    Explanation,
    ExplanationStep,
    explain,
    verify,
)
from poltika.engines.simulator.income_tax import REQUIRED_PARAMETER_IDS, run_income_tax_module
from poltika.policy.loader import load_policy_spec

client = TestClient(app)
URL = "/income-tax/calculate"

BASE: dict[str, Any] = {
    "modelled_date": "2026-10-29",
    "individual_status": "verified",
    "residence_scope": "whole_year_ordinary_nz_resident",
    "tax_year_basis": "standard_2026_27",
    "income_composition": "ordinary_salary_wages_only",
    "no_deductions_status": "verified",
    "no_available_losses_status": "verified",
    "general_basic_rate_status": "verified",
    "taxable_income_basis_attestation": True,
    "annual_taxable_income": "25",
}


def post(**overrides: Any) -> Any:
    payload = {**BASE, **overrides}
    return client.post(URL, json={k: v for k, v in payload.items() if v is not ...})


def component(response: Any) -> dict[str, Any]:
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()["basic_annual_income_tax"]
    assert body["value"] is None  # the policy is draft: never an amount
    return body


def test_policy_dir_env_var_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLTIKA_POLICY_SPECS_DIR", str(tmp_path))
    assert _income_tax_policy_dir() == tmp_path / "income_tax"


def test_policy_dir_defaults_without_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLTIKA_POLICY_SPECS_DIR", raising=False)
    resolved = _income_tax_policy_dir()
    assert (resolved.name, resolved.parent.name) == ("income_tax", "policy_specs")


def test_a_fully_verified_request_is_gated_by_the_draft_policy_with_no_value() -> None:
    body = component(post())
    assert (body["outcome"], body["code"]) == ("needs_review", "IT_POLICY_NOT_APPROVED")
    assert body["category"] is None and body["missing_facts"] == []


def test_the_response_carries_a_verified_explanation_and_the_parameter_evidence() -> None:
    response = post()
    explanation = response.json()["explanation"]
    assert explanation["component_id"] == "basic_annual_income_tax"
    assert explanation["outcome"] == "needs_review" and explanation["value"] is None
    assert explanation["steps"] == []
    assert [e["parameter_id"] for e in explanation["evidence"]] == list(REQUIRED_PARAMETER_IDS)
    assert all(
        e["value"] is None and e["review_status"] == "needs_review" for e in explanation["evidence"]
    )
    scenario = scenario_from_request(IncomeTaxCalculationRequest(**BASE))
    result = run_income_tax_module(scenario)
    rebuilt = Explanation(
        component_id=explanation["component_id"],
        outcome=explanation["outcome"],
        value=explanation["value"],
        summary=explanation["summary"],
        steps=tuple(ExplanationStep(**s) for s in explanation["steps"]),
        assumptions=tuple(explanation["assumptions"]),
        evidence=tuple(EvidenceUsed(**e) for e in explanation["evidence"]),
        code=explanation["code"],
        category=explanation["category"],
        missing_facts=tuple(explanation["missing_facts"]),
    )
    assert verify(rebuilt, result) == []
    assert explain("basic_annual_income_tax", result) == rebuilt


@pytest.mark.parametrize(
    ("override", "code"),
    [
        ({"individual_status": "excluded"}, "IT_NOT_NATURAL_PERSON"),
        ({"residence_scope": "non_resident"}, "IT_RESIDENCE_NOT_MODELLED"),
        ({"residence_scope": "changing_residence"}, "IT_RESIDENCE_NOT_MODELLED"),
        ({"residence_scope": "special_residence_regime"}, "IT_RESIDENCE_NOT_MODELLED"),
        ({"tax_year_basis": "non_standard_year"}, "IT_TAX_YEAR_NOT_MODELLED"),
        ({"tax_year_basis": "other_standard_year"}, "IT_TAX_YEAR_NOT_MODELLED"),
        ({"income_composition": "main_benefit"}, "IT_INCOME_COMPOSITION_NOT_MODELLED"),
        ({"income_composition": "other_or_mixed_income"}, "IT_INCOME_COMPOSITION_NOT_MODELLED"),
        ({"no_deductions_status": "excluded"}, "IT_DEDUCTIONS_NOT_MODELLED"),
        ({"no_available_losses_status": "excluded"}, "IT_LOSSES_NOT_MODELLED"),
        ({"general_basic_rate_status": "excluded"}, "IT_SPECIAL_BASIC_RATE_NOT_MODELLED"),
        ({"annual_taxable_income": "100.50"}, "IT_FRACTIONAL_INCOME_NOT_MODELLED"),
        ({"annual_taxable_income": "-1"}, "IT_NEGATIVE_INCOME_NOT_MODELLED"),
    ],
)
def test_each_exclusion_is_unsupported_with_its_reason_code(
    override: dict[str, Any], code: str
) -> None:
    body = component(post(**override))
    assert (body["outcome"], body["category"], body["code"]) == (
        "unsupported",
        "not_modelled",
        code,
    )
    assert body["missing_facts"] == []


@pytest.mark.parametrize(
    "field",
    [
        "individual_status",
        "residence_scope",
        "tax_year_basis",
        "income_composition",
        "no_deductions_status",
        "no_available_losses_status",
        "general_basic_rate_status",
        "taxable_income_basis_attestation",
        "annual_taxable_income",
    ],
)
def test_each_missing_fact_is_needs_review_naming_it(field: str) -> None:
    body = component(post(**{field: ...}))
    assert (body["outcome"], body["code"]) == ("needs_review", "IT_FACTS_UNVERIFIED")
    assert body["missing_facts"] == [field]


def test_an_unknown_status_is_a_missing_fact_not_a_pass() -> None:
    body = component(post(no_deductions_status="unknown", annual_taxable_income=...))
    assert body["missing_facts"] == ["no_deductions_status", "annual_taxable_income"]


def test_an_empty_request_body_beyond_the_date_names_every_missing_fact() -> None:
    body = component(client.post(URL, json={"modelled_date": "2026-10-29"}))
    assert body["code"] == "IT_FACTS_UNVERIFIED" and len(body["missing_facts"]) == 9


def test_zero_income_is_not_a_calculated_zero() -> None:
    body = component(post(annual_taxable_income="0"))
    assert body["outcome"] == "needs_review" and body["value"] is None


def test_a_false_attestation_is_needs_review_without_a_missing_fact() -> None:
    body = component(post(taxable_income_basis_attestation=False))
    assert (body["outcome"], body["code"], body["missing_facts"]) == (
        "needs_review",
        "IT_TAXABLE_INCOME_NOT_ATTESTED",
        [],
    )


def test_an_exclusion_outranks_a_missing_fact() -> None:
    body = component(post(residence_scope="non_resident", annual_taxable_income=...))
    assert body["code"] == "IT_RESIDENCE_NOT_MODELLED"


@pytest.mark.parametrize("modelled", ["2026-03-31", "2027-04-01", "2030-01-01"])
def test_a_date_outside_the_reference_period_is_unsupported(modelled: str) -> None:
    body = component(post(modelled_date=modelled))
    assert (body["outcome"], body["code"]) == ("unsupported", "IT_DATE_OUTSIDE_REFERENCE_PERIOD")


@pytest.mark.parametrize("modelled", ["2026-04-01", "2027-03-31"])
def test_both_reference_period_edges_are_inside(modelled: str) -> None:
    assert component(post(modelled_date=modelled))["code"] == "IT_POLICY_NOT_APPROVED"


def test_a_requested_version_other_than_the_draft_has_is_a_409() -> None:
    response = post(requested_policy_version="0.1.0")
    assert response.status_code == 409
    assert "0.1.0" in response.json()["detail"]
    assert "/" not in response.json()["detail"].replace("2026-27", "")  # no filesystem path


def test_omitting_the_requested_version_accepts_the_unversioned_draft() -> None:
    assert post(requested_policy_version=None).status_code == 200


def test_the_requested_version_becomes_required_once_the_policy_has_one() -> None:
    # WFF and AS require it. It is optional only while the draft has no
    # version; approving one must make this fail until the field is required.
    spec = load_policy_spec(_income_tax_policy_dir() / "policy.yaml")
    field = IncomeTaxCalculationRequest.model_fields["requested_policy_version"]
    assert spec.policy_version is not None or not field.is_required()
    assert spec.policy_version is None or field.is_required()


@pytest.mark.parametrize(
    "overrides",
    [
        {"surprise": 1},
        {"annual_taxable_income": 25000.5},
        {"annual_taxable_income": 25000},
        {"annual_taxable_income": True},
        {"annual_taxable_income": "NaN"},
        {"annual_taxable_income": "Infinity"},
        {"annual_taxable_income": "-Infinity"},
        {"annual_taxable_income": "not a number"},
        {"individual_status": "yes"},
        {"residence_scope": "resident"},
        {"tax_year_basis": "2026"},
        {"income_composition": "wages"},
        {"no_deductions_status": "maybe"},
        {"taxable_income_basis_attestation": "true"},
        {"taxable_income_basis_attestation": 1},
        {"modelled_date": "not-a-date"},
        {"modelled_date": ...},
    ],
)
def test_a_malformed_request_is_422(overrides: dict[str, Any]) -> None:
    assert post(**overrides).status_code == 422


def test_the_route_is_in_the_openapi_contract() -> None:
    schema = client.get("/openapi.json").json()
    assert "/income-tax/calculate" in schema["paths"]
    assert (
        schema["components"]["schemas"]["IncomeTaxCalculationRequest"]["additionalProperties"]
        is False
    )
