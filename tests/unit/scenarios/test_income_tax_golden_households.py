"""Income-tax golden households: thin runner for
policy_specs/income_tax/golden_households.yaml (v0.3 Phase 2.5, new-policy PR 3).

Expectations live in the protected YAML file, not here. Each household runs
through the shared household model, one `run_household_income_tax` call per
person (IT-01), against the real draft policy. Every income-tax value is
draft, so every result is `needs_review` or `unsupported` and the expectations
are non-numeric: outcome, reason code, category, missing facts and policy
identity. The bracket-boundary goldens are listed in the file as waiting on
the protected-value process and are never run here.
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.scenarios.household_mappings import INCOME_TAX_YEAR_2026_27, run_household_income_tax
from poltika.semantics import household as hh

ROOT = Path(__file__).resolve().parents[3]
GOLDEN_PATH = ROOT / "policy_specs" / "income_tax" / "golden_households.yaml"
POLICY_PATH = ROOT / "policy_specs" / "income_tax" / "policy.yaml"

# Reason codes the engine emits for a known fact outside the slice (IT-01 to
# IT-05, Q17), each reachable from household facts and spells.
EXCLUSION_CODES = {
    "IT_NOT_NATURAL_PERSON",
    "IT_RESIDENCE_NOT_MODELLED",
    "IT_TAX_YEAR_NOT_MODELLED",
    "IT_INCOME_COMPOSITION_NOT_MODELLED",
    "IT_DEDUCTIONS_NOT_MODELLED",
    "IT_LOSSES_NOT_MODELLED",
    "IT_SPECIAL_BASIC_RATE_NOT_MODELLED",
    "IT_NEGATIVE_INCOME_NOT_MODELLED",
    "IT_FRACTIONAL_INCOME_NOT_MODELLED",
}
# Fixed allow-list of synthetic spell amounts. -1 is the negative-income sentinel
# (g43): it exercises the sign check only, so it is exempt from the proximity check.
NEGATIVE_SENTINEL = Decimal(-1)
SYNTHETIC_AMOUNTS = {
    Decimal(v) for v in ("52000", "38000", "30000", "20000", "65000", "41000", "1000.5", "-1")
}
_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
_MONEY = re.compile(r"\$|(?<![-\w])\d{3,}")


def _file() -> dict[str, Any]:
    loaded: dict[str, Any] = yaml.safe_load(GOLDEN_PATH.read_text())
    return loaded


def _households() -> list[dict[str, Any]]:
    households: list[dict[str, Any]] = _file()["households"]
    return households


def _numbers(node: Any) -> set[Decimal]:
    """Every number in a parsed policy file, including those inside strings."""
    found: set[Decimal] = set()
    if isinstance(node, bool):
        return found
    if isinstance(node, (int, float)):
        found.add(Decimal(str(node)))
    elif isinstance(node, str):
        found.update(Decimal(m.replace(",", "")) for m in _NUMBER.findall(node))
    elif isinstance(node, dict):
        for value in node.values():
            found |= _numbers(value)
    elif isinstance(node, list):
        for value in node:
            found |= _numbers(value)
    return found


def _expected_keys(run: dict[str, Any]) -> set[str]:
    return set(run) - {"person"}


def test_golden_file_is_complete_and_assumption_free() -> None:
    golden = _file()
    households = _households()
    assert len(households) >= 20
    ids = [h["id"] for h in households]
    assert len(ids) == len(set(ids))
    assert len({h["household"]["household_id"] for h in households}) == len(households)
    assert "parameter_assumptions" not in golden
    candidate_numbers = _numbers(yaml.safe_load(POLICY_PATH.read_text()))
    codes: set[str] = set()
    for household in households:
        assert household["why"], household["id"]
        assert "parameter_assumptions" not in household, household["id"]
        persons = {p["person_id"] for p in household["household"]["persons"]}
        assert household["runs"], household["id"]
        assert {r["person"] for r in household["runs"]} <= persons, household["id"]
        for run in household["runs"]:
            # Non-numeric only: no key may carry an amount or a tax figure.
            assert _expected_keys(run) == {"outcome", "code", "category", "missing_facts"}, (
                household["id"]
            )
            assert run["outcome"] in {"needs_review", "unsupported"}, household["id"]
            codes.add(run["code"])
        for spell in household["household"].get("income_spells", []):
            # Synthetic inputs, never near a parameter value from the draft policy.
            amount = Decimal(spell["amount"])
            assert amount in SYNTHETIC_AMOUNTS, (household["id"], spell["amount"])
            if amount != NEGATIVE_SENTINEL:
                nearest = min(abs(amount - number) for number in candidate_numbers)
                assert nearest >= 2, (household["id"], spell["amount"])
    assert EXCLUSION_CODES <= codes


def test_every_slice_boundary_member_of_each_enum_has_a_golden() -> None:
    # A new out-of-slice enum member must get a golden, not fall through.
    facts: dict[str, set[str]] = {
        "residence_scope": set(),
        "tax_year_basis": set(),
        "income_composition": set(),
    }
    for household in _households():
        for person in household["household"]["persons"]:
            for name, seen in facts.items():
                value = (person.get("income_tax_facts") or {}).get(name)
                if value is not None:
                    seen.add(value)
    for name, enum_type, slice_member in (
        (
            "residence_scope",
            hh.TaxResidenceScope,
            hh.TaxResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT,
        ),
        ("tax_year_basis", hh.TaxYearBasis, hh.TaxYearBasis.STANDARD_2026_27),
        (
            "income_composition",
            hh.TaxIncomeComposition,
            hh.TaxIncomeComposition.ORDINARY_SALARY_WAGES_ONLY,
        ),
    ):
        wanted = {m.value for m in enum_type if m.value != "unknown"}
        assert wanted <= facts[name], (name, wanted - facts[name])
        assert slice_member.value in facts[name]


def test_the_bracket_boundaries_wait_on_the_protected_value_process_and_hold_no_amount() -> None:
    waiting = _file()["waiting_on_protected_value_process"]
    assert any("bracket" in w["covers"] for w in waiting)
    for entry in waiting:
        assert set(entry) == {"id", "covers", "waiting_on"}
        # Prose only: nothing here may be a statutory or candidate value.
        assert not _MONEY.search(entry["covers"] + entry["waiting_on"]), entry
    assert not {h["id"] for h in _households()} & {w["id"] for w in waiting}


@pytest.mark.parametrize("household", _households(), ids=lambda h: h["id"])
def test_golden_household(household: dict[str, Any]) -> None:
    policy = _file()["policy"]
    year = INCOME_TAX_YEAR_2026_27
    assert (policy["tax_year"]["start"], policy["tax_year"]["end"]) == (year.start, year.end)
    model = hh.Household.model_validate(household["household"])
    for run in household["runs"]:
        label = f"{household['id']} {run['person']}"
        result = run_household_income_tax(model, run["person"], tax_year=year)
        assert (result.outcome, result.code, result.category, list(result.missing_facts)) == (
            run["outcome"],
            run["code"],
            run["category"],
            run["missing_facts"],
        ), f"{label}: {result.reason}"
        assert result.value is None, label
        assert result.trace is not None, label
        assert (result.trace.policy_id, result.trace.component_id, result.trace.policy_version) == (
            policy["policy_id"],
            policy["component_id"],
            policy["policy_version"],
        ), label
        assert result.trace.assessment_period == (date(2026, 4, 1), date(2027, 4, 1)), label
