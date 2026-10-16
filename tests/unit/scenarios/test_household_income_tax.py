"""Task 7 (BUILD_PLAN_v0_3.md 2.3): income tax reads the shared household
model through a named mapping, `to_income_tax()`.

The engine is unchanged, so the proof is a round trip: every draft spec
case, held as a one-person household, maps back to the identical scenario
and gives the identical result, trace included. The other tests pin the
mapping's own rules: one person at a time, spells that tile the year,
no apportionment, no derivation from earnings, and the engine's order of
`unsupported` before `needs_review`."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from poltika.engines.simulator import income_tax as it
from poltika.engines.simulator.income_tax import run_income_tax_module
from poltika.scenarios.household_mappings import (
    INCOME_TAX_YEAR_2026_27,
    MappingRefusal,
    household_from_income_tax,
    run_household_income_tax,
    to_income_tax,
)
from poltika.semantics import household as hh
from poltika.semantics.population import PersonRole
from tests.unit.engines.simulator.test_income_tax_spec_cases import _CASES, scenario_from_yaml

YEAR = INCOME_TAX_YEAR_2026_27

# Every fact verified inside the slice: the engine's draft-policy gate is the
# only thing between this person and an amount.
_IN_SLICE = hh.IncomeTaxFacts(
    individual_status=hh.Assertion.VERIFIED,
    residence_scope=hh.TaxResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT,
    tax_year_basis=hh.TaxYearBasis.STANDARD_2026_27,
    income_composition=hh.TaxIncomeComposition.ORDINARY_SALARY_WAGES_ONLY,
    no_deductions_status=hh.Assertion.VERIFIED,
    no_available_losses_status=hh.Assertion.VERIFIED,
    general_basic_rate_status=hh.Assertion.VERIFIED,
    taxable_income_basis_attestation=True,
)


def _spell(person_id: str, start: date, end: date, amount: str, **kw: Any) -> hh.IncomeSpell:
    return hh.IncomeSpell(
        person_id=person_id,
        income_type=kw.pop("income_type", hh.IncomeType.UNSPLIT_TOTAL),
        start=start,
        end=end,
        amount=Decimal(amount),
        basis=kw.pop("basis", hh.IncomeBasis.IT_ANNUAL_TAXABLE),
    )


def _couple(
    *spells: hh.IncomeSpell,
    claimant: hh.IncomeTaxFacts | None = _IN_SLICE,
    partner: hh.IncomeTaxFacts | None = None,
) -> hh.Household:
    return hh.Household(
        household_id="it-couple",
        persons=(
            hh.Person(person_id="a", role=PersonRole.CLAIMANT, income_tax_facts=claimant),
            hh.Person(person_id="b", role=PersonRole.PARTNER, income_tax_facts=partner),
        ),
        families=(hh.Family(claimant_id="a", partner_status=hh.FamilyPartnerStatus.PARTNERED, partner_id="b"),),
        income_spells=spells,
    )


def _whole_year(person_id: str, amount: str) -> hh.IncomeSpell:
    return _spell(person_id, YEAR.start, YEAR.end, amount)


# ------------------------------------------------------------ round trip


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_every_spec_case_round_trips_through_a_household(case: dict[str, Any]) -> None:
    scenario = scenario_from_yaml(case["scenario"])
    household = household_from_income_tax(scenario, household_id="it-case", tax_year=YEAR)
    assert to_income_tax(household, "taxpayer", YEAR) == scenario
    direct = run_income_tax_module(scenario)
    via_household = run_household_income_tax(household, "taxpayer", tax_year=YEAR)
    assert via_household == direct
    assert via_household.trace is not None and direct.trace is not None
    assert via_household.trace.scenario_sha256 == direct.trace.scenario_sha256


def test_the_household_enums_carry_the_engine_values_plus_unknown() -> None:
    for household_enum, engine_enum in (
        (hh.TaxResidenceScope, it.ResidenceScope),
        (hh.TaxYearBasis, it.TaxYearBasis),
        (hh.TaxIncomeComposition, it.IncomeComposition),
    ):
        assert {m.value for m in household_enum} == {m.value for m in engine_enum} | {"unknown"}


def test_a_household_without_tax_facts_keeps_its_identity() -> None:
    # Computed on `origin/main` at 352c288, before `income_tax_facts` existed.
    household = hh.Household(
        household_id="hash-pin",
        persons=(
            hh.Person(person_id="a", role=PersonRole.CLAIMANT),
            hh.Person(person_id="b", role=PersonRole.PARTNER),
        ),
        families=(hh.Family(claimant_id="a", partner_status=hh.FamilyPartnerStatus.PARTNERED, partner_id="b"),),
        income_spells=(
            _spell("a", YEAR.start, YEAR.end, "52000", income_type=hh.IncomeType.EMPLOYMENT_EARNINGS,
                   basis=hh.IncomeBasis.GROSS),
        ),
    )
    assert household.content_sha256() == "b2125ca6c0948d4596e7c4c736f5cc254fd9053a70f60ded6d4f828f649cccac"
    with_facts = household.model_copy(
        update={"persons": (household.persons[0].model_copy(update={"income_tax_facts": _IN_SLICE}),
                            household.persons[1])}
    )
    assert with_facts.content_sha256() != household.content_sha256()


# ------------------------------------------------------------ the mapping's rules


def test_each_person_maps_on_their_own_facts_and_spells() -> None:
    household = _couple(_whole_year("a", "60000"), _whole_year("b", "45000"), partner=None)
    claimant = to_income_tax(household, "a", YEAR)
    partner = to_income_tax(household, "b", YEAR)
    assert isinstance(claimant, it.IncomeTaxScenario) and isinstance(partner, it.IncomeTaxScenario)
    assert claimant.annual_taxable_income == Decimal(60000)
    assert claimant.residence_scope is it.ResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT
    # The partner asserted nothing: every fact unknown, never the claimant's.
    assert partner.annual_taxable_income == Decimal(45000)
    assert partner.individual_status is it.FactStatus.UNKNOWN
    assert (partner.residence_scope, partner.tax_year_basis, partner.income_composition) == (None, None, None)
    assert partner.taxable_income_basis_attestation is None
    result = run_household_income_tax(household, "b", tax_year=YEAR)
    assert (result.outcome, result.code, result.value) == ("needs_review", "IT_FACTS_UNVERIFIED", None)
    assert set(result.missing_facts) == {
        "individual_status",
        "residence_scope",
        "tax_year_basis",
        "income_composition",
        "no_deductions_status",
        "no_available_losses_status",
        "general_basic_rate_status",
        "taxable_income_basis_attestation",
    }


def test_spells_that_tile_the_year_add_and_a_gap_is_unknown_never_zero() -> None:
    mid = date(2026, 10, 1)
    tiled = _couple(_spell("a", YEAR.start, mid, "30000"), _spell("a", mid, YEAR.end, "20000"))
    mapped = to_income_tax(tiled, "a", YEAR)
    assert isinstance(mapped, it.IncomeTaxScenario) and mapped.annual_taxable_income == Decimal(50000)

    gap = to_income_tax(_couple(_spell("a", YEAR.start, mid, "30000")), "a", YEAR)
    assert isinstance(gap, it.IncomeTaxScenario) and gap.annual_taxable_income is None
    result = run_household_income_tax(_couple(_spell("a", YEAR.start, mid, "30000")), "a", tax_year=YEAR)
    assert (result.outcome, result.missing_facts) == ("needs_review", ("annual_taxable_income",))


def test_taxable_income_is_never_derived_from_earnings_or_another_basis() -> None:
    household = _couple(
        _spell("a", YEAR.start, YEAR.end, "60000", income_type=hh.IncomeType.EMPLOYMENT_EARNINGS,
               basis=hh.IncomeBasis.GROSS),
        _spell("a", YEAR.start, YEAR.end, "60000", basis=hh.IncomeBasis.WFF_FAMILY_SCHEME),
    )
    mapped = to_income_tax(household, "a", YEAR)
    assert isinstance(mapped, it.IncomeTaxScenario) and mapped.annual_taxable_income is None


def test_a_spell_past_the_year_is_refused_never_apportioned() -> None:
    household = _couple(_spell("a", date(2026, 3, 1), YEAR.end, "65000"))
    refusal = to_income_tax(household, "a", YEAR)
    assert isinstance(refusal, MappingRefusal)
    assert (refusal.outcome, refusal.code) == ("needs_review", "HOUSEHOLD_SPELL_PERIOD_MISMATCH")
    result = run_household_income_tax(household, "a", tax_year=YEAR)
    assert (result.outcome, result.code, result.value) == ("needs_review", "HOUSEHOLD_SPELL_PERIOD_MISMATCH", None)


def test_a_known_exclusion_outranks_a_mapping_refusal() -> None:
    non_resident = _IN_SLICE.model_copy(update={"residence_scope": hh.TaxResidenceScope.NON_RESIDENT})
    household = _couple(_spell("a", date(2026, 3, 1), YEAR.end, "65000"), claimant=non_resident)
    assert isinstance(to_income_tax(household, "a", YEAR), MappingRefusal)
    result = run_household_income_tax(household, "a", tax_year=YEAR)
    assert (result.outcome, result.code, result.category) == (
        "unsupported",
        "IT_RESIDENCE_NOT_MODELLED",
        "not_modelled",
    )


def test_the_asserted_year_and_the_mapped_period_must_agree() -> None:
    earlier = hh.DatePeriod(start=date(2025, 4, 1), end=date(2026, 4, 1))
    household = _couple(_spell("a", earlier.start, earlier.end, "60000"))
    refusal = to_income_tax(household, "a", earlier)
    assert isinstance(refusal, MappingRefusal)
    assert (refusal.outcome, refusal.code) == ("needs_review", "HOUSEHOLD_MAPPING_INVALID_FACTS")
    other = _IN_SLICE.model_copy(update={"tax_year_basis": hh.TaxYearBasis.OTHER_STANDARD_YEAR})
    mapped = to_income_tax(_couple(_spell("a", earlier.start, earlier.end, "60000"), claimant=other), "a", earlier)
    assert isinstance(mapped, it.IncomeTaxScenario) and mapped.tax_year_basis is it.TaxYearBasis.OTHER_STANDARD_YEAR


def test_the_run_takes_only_the_policy_reference_period_and_a_held_person() -> None:
    household = _couple(_whole_year("a", "60000"))
    with pytest.raises(ValueError, match="reference period"):
        run_household_income_tax(
            household, "a", tax_year=hh.DatePeriod(start=date(2025, 4, 1), end=date(2026, 4, 1))
        )
    with pytest.raises(ValueError, match="holds no person 'c'"):
        to_income_tax(household, "c", YEAR)


def test_an_in_slice_person_stops_at_the_draft_policy_gate_with_no_amount() -> None:
    result = run_household_income_tax(_couple(_whole_year("a", "60000")), "a", tax_year=YEAR)
    assert (result.outcome, result.code, result.value) == ("needs_review", "IT_POLICY_NOT_APPROVED", None)


@pytest.mark.parametrize("value", ["true", 1, "no", 0])
def test_an_attestation_is_a_strict_boolean(value: object) -> None:
    with pytest.raises(ValueError, match="valid boolean"):
        hh.IncomeTaxFacts(taxable_income_basis_attestation=value)
