"""Task 7: the draft income-tax spec cases (`policy_specs/income_tax/spec_cases.yaml`).

Every case's `expected` is non-numeric while the review gates are open, so
each runs against the real draft policy through the module entry point. The
`conditional_arithmetic` values are hand calculations the specification keeps
apart from `expected`; they check only `basic_tax_band_sum()`, with the draft's
candidate values, and never become a result."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.income_tax import (
    COMPONENT_ID,
    IncomeComposition,
    IncomeTaxScenario,
    ResidenceScope,
    TaxYearBasis,
    basic_tax_band_sum,
    run_income_tax_module,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.policy.loader import ParameterResolution, PolicyParameterSet, load_policy_spec

POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "income_tax"
_DOC = yaml.safe_load((POLICY_DIR / "spec_cases.yaml").read_text())
_CASES: list[dict[str, Any]] = _DOC["spec_cases"]
_ARITHMETIC = [c for c in _CASES if "conditional_arithmetic" in c]


def scenario_from_yaml(facts: dict[str, Any]) -> IncomeTaxScenario:
    def optional(enum: Any, value: str | None) -> Any:
        return None if value is None else enum(value)

    income = facts["annual_taxable_income"]
    return IncomeTaxScenario(
        individual_status=FactStatus(facts["individual_status"]),
        residence_scope=optional(ResidenceScope, facts["residence_scope"]),
        tax_year_basis=optional(TaxYearBasis, facts["tax_year_basis"]),
        income_composition=optional(IncomeComposition, facts["income_composition"]),
        no_deductions_status=FactStatus(facts["no_deductions_status"]),
        no_available_losses_status=FactStatus(facts["no_available_losses_status"]),
        general_basic_rate_status=FactStatus(facts["general_basic_rate_status"]),
        taxable_income_basis_attestation=facts["taxable_income_basis_attestation"],
        annual_taxable_income=None if income is None else Decimal(income),
    )


def test_the_cases_are_complete_unique_and_all_non_numeric() -> None:
    ids = [c["id"] for c in _CASES]
    assert len(ids) == 47 and len(set(ids)) == 47
    assert len(_ARITHMETIC) == 17
    for case in _CASES:
        assert set(case["expected"]) == {COMPONENT_ID}
        assert "value" not in case["expected"][COMPONENT_ID], case["id"]


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_spec_case(case: dict[str, Any]) -> None:
    expected = case["expected"][COMPONENT_ID]
    result = run_income_tax_module(scenario_from_yaml(case["scenario"]), policy_dir=POLICY_DIR)
    assert result.outcome == expected["outcome"]
    assert result.value is None
    if "category" in expected:
        assert result.category == expected["category"]
    if "missing_facts" in expected:
        assert result.missing_facts == tuple(expected["missing_facts"])
    if expected["outcome"] == "needs_review" and "missing_facts" not in expected:
        # A fully asserted, in-slice case stops at a server gate a caller cannot clear.
        assert result.code in {"IT_POLICY_NOT_APPROVED", "IT_TAXABLE_INCOME_NOT_ATTESTED"}


def _candidate_parameters() -> PolicyParameterSet:
    """The draft's candidate values as a hand-built set, for arithmetic only."""
    spec = load_policy_spec(POLICY_DIR / "policy.yaml")
    resolutions = {
        p.id: ParameterResolution(parameter_id=p.id, outcome="resolved", value=Decimal(str(p.values[0].value)))
        for p in spec.parameters
    }
    return PolicyParameterSet("income_tax", "conditional", "0.1", date(2026, 4, 1), resolutions)


@pytest.mark.parametrize("case", _ARITHMETIC, ids=[c["id"] for c in _ARITHMETIC])
def test_conditional_arithmetic_matches_the_band_sum(case: dict[str, Any]) -> None:
    income = Decimal(case["scenario"]["annual_taxable_income"])
    expected = Decimal(case["conditional_arithmetic"]["value"])
    assert basic_tax_band_sum(income, _candidate_parameters()) == expected
