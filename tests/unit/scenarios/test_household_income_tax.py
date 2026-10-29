"""Task 7 (BUILD_PLAN_v0_3.md 2.3): income tax reads the shared household
model through a named mapping, `to_income_tax()`.

The engine is unchanged, so the proof is a round trip: every draft spec
case, held as a one-person household, maps back to the identical scenario
and gives the identical result, trace included. The other tests pin the
mapping's own rules: one person at a time, one whole-year spell (several
refused), no apportionment, no derivation from earnings, and the engine's order of
`unsupported` before `needs_review`."""

from __future__ import annotations

import shutil
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from poltika.common.errors import PolicyVersionMismatchError
from poltika.engines.simulator import income_tax as it
from poltika.engines.simulator.income_tax import run_income_tax_module
from poltika.policy.loader import load_policy_snapshot
from poltika.scenarios.household_mappings import (
    INCOME_TAX_YEAR_2026_27,
    AdapterRefused,
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


def _holds_at_year(scenario: it.IncomeTaxScenario) -> bool:
    """The adapter dates a known amount to `YEAR` unless the scenario asserts another year."""
    return scenario.annual_taxable_income is None or scenario.tax_year_basis not in (
        it.TaxYearBasis.OTHER_STANDARD_YEAR,
        it.TaxYearBasis.NON_STANDARD_YEAR,
    )


_AT_YEAR = [c for c in _CASES if _holds_at_year(scenario_from_yaml(c["scenario"]))]
_ANOTHER_YEAR = [c for c in _CASES if not _holds_at_year(scenario_from_yaml(c["scenario"]))]
_OWN_PERIOD = {
    it.TaxYearBasis.OTHER_STANDARD_YEAR: hh.DatePeriod(start=date(2025, 4, 1), end=date(2026, 4, 1)),
    it.TaxYearBasis.NON_STANDARD_YEAR: hh.DatePeriod(start=date(2026, 7, 1), end=date(2027, 7, 1)),
}


def test_the_round_trip_groups_cover_every_case() -> None:
    assert len(_AT_YEAR) + len(_ANOTHER_YEAR) == len(_CASES) == 47
    assert _AT_YEAR and _ANOTHER_YEAR


@pytest.mark.parametrize("case", _AT_YEAR, ids=[c["id"] for c in _AT_YEAR])
def test_every_spec_case_the_year_can_hold_round_trips_through_a_household(case: dict[str, Any]) -> None:
    scenario = scenario_from_yaml(case["scenario"])
    household = household_from_income_tax(scenario, household_id="it-case", tax_year=YEAR)
    assert to_income_tax(household, "taxpayer", YEAR) == scenario
    direct = run_income_tax_module(scenario)
    via_household = run_household_income_tax(household, "taxpayer", tax_year=YEAR)
    assert via_household == direct
    assert via_household.trace is not None and direct.trace is not None
    assert via_household.trace.scenario_sha256 == direct.trace.scenario_sha256


@pytest.mark.parametrize("case", _ANOTHER_YEAR, ids=[c["id"] for c in _ANOTHER_YEAR])
def test_every_spec_case_asserting_another_year_is_held_at_its_own_period(case: dict[str, Any]) -> None:
    scenario = scenario_from_yaml(case["scenario"])
    assert scenario.tax_year_basis is not None
    with pytest.raises(AdapterRefused, match="another tax year"):
        household_from_income_tax(scenario, household_id="it-case", tax_year=YEAR)
    own = _OWN_PERIOD[scenario.tax_year_basis]
    household = household_from_income_tax(scenario, household_id="it-case", tax_year=own)
    assert to_income_tax(household, "taxpayer", own) == scenario


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


def test_one_whole_year_spell_is_used_as_given_and_parts_are_never_summed() -> None:
    mid = date(2026, 10, 1)
    # Several spells are refused, not added: IT-02 gives no derivation.
    tiled = to_income_tax(_couple(_spell("a", YEAR.start, mid, "30000"), _spell("a", mid, YEAR.end, "20000")), "a", YEAR)
    assert isinstance(tiled, MappingRefusal)
    assert (tiled.outcome, tiled.code) == ("needs_review", "HOUSEHOLD_MAPPING_INVALID_FACTS")

    # A part-year spell alone is a gap: unknown, never zero.
    gap = to_income_tax(_couple(_spell("a", YEAR.start, mid, "30000")), "a", YEAR)
    assert isinstance(gap, it.IncomeTaxScenario) and gap.annual_taxable_income is None
    result = run_household_income_tax(_couple(_spell("a", YEAR.start, mid, "30000")), "a", tax_year=YEAR)
    assert (result.outcome, result.missing_facts) == ("needs_review", ("annual_taxable_income",))

    # The one whole-year amount passes through untouched: no rounding to the
    # Decimal context, and exponent and sign kept (Q17: never rounds).
    for amount in ("15600.0000000000000000000000000001", "1E+3", "-0"):
        mapped = to_income_tax(_couple(_whole_year("a", amount)), "a", YEAR)
        assert isinstance(mapped, it.IncomeTaxScenario)
        assert str(mapped.annual_taxable_income) == amount
    fractional = run_household_income_tax(_couple(_whole_year("a", "15600.0000000000000000000000000001")), "a", tax_year=YEAR)
    assert (fractional.outcome, fractional.code) == ("unsupported", "IT_FRACTIONAL_INCOME_NOT_MODELLED")


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
    # The refusal is traced: the policy, its reference period and the facts
    # run, with the income unknown rather than any part of the spell.
    assert result.trace is not None
    assert result.trace.policy_id == "income_tax"
    assert result.trace.assessment_period == (YEAR.start, YEAR.end)
    income_use = next(u for u in result.trace.inputs if u.name == "annual_taxable_income")
    assert income_use.value is None


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


def test_the_adapter_refuses_a_period_the_scenario_does_not_assert() -> None:
    scenario = scenario_from_yaml(_CASES[0]["scenario"])
    assert scenario.tax_year_basis is it.TaxYearBasis.STANDARD_2026_27
    with pytest.raises(AdapterRefused, match="standard 2026-27"):
        household_from_income_tax(
            scenario,
            household_id="it-case",
            tax_year=hh.DatePeriod(start=date(2025, 4, 1), end=date(2026, 4, 1)),
        )


# ------------------------------------------------------------ PR #232 review (R3, R4, R7)


def _straddler(person_id: str, amount: str = "1", **kw: Any) -> hh.IncomeSpell:
    return _spell(person_id, date(2026, 3, 1), date(2027, 4, 1), amount, **kw)


def _mapped(household: hh.Household, person_id: str = "a") -> it.IncomeTaxScenario:
    mapped = to_income_tax(household, person_id, YEAR)
    assert isinstance(mapped, it.IncomeTaxScenario)
    return mapped


def test_q10_ignores_a_straddler_of_another_basis() -> None:
    for basis in (hh.IncomeBasis.GROSS, hh.IncomeBasis.WFF_FAMILY_SCHEME):
        household = _couple(_whole_year("a", "60000"), _straddler("a", basis=basis))
        assert _mapped(household).annual_taxable_income == Decimal(60000)


def test_q10_reads_only_the_selected_person() -> None:
    household = _couple(_whole_year("a", "60000"), _straddler("b"))
    assert _mapped(household).annual_taxable_income == Decimal(60000)
    refused = to_income_tax(household, "b", YEAR)
    assert isinstance(refused, MappingRefusal) and refused.code == "HOUSEHOLD_SPELL_PERIOD_MISMATCH"


def test_q10_refuses_a_spell_ending_past_the_year() -> None:
    household = _couple(_spell("a", YEAR.start, date(2027, 5, 1), "60000"))
    refusal = to_income_tax(household, "a", YEAR)
    assert isinstance(refusal, MappingRefusal) and refusal.code == "HOUSEHOLD_SPELL_PERIOD_MISMATCH"


def test_a_disjoint_previous_year_spell_does_not_refuse_the_year() -> None:
    previous = _spell("a", date(2025, 4, 1), date(2026, 4, 1), "40000")
    assert _mapped(_couple(previous, _whole_year("a", "60000"))).annual_taxable_income == Decimal(60000)


def test_only_an_unsplit_total_is_taxable_income() -> None:
    typed = _spell("a", YEAR.start, YEAR.end, "60000", income_type=hh.IncomeType.EMPLOYMENT_EARNINGS)
    assert _mapped(_couple(typed)).annual_taxable_income is None


@pytest.mark.parametrize(
    ("amount", "code"),
    [("-1", "IT_NEGATIVE_INCOME_NOT_MODELLED"), ("15600.25", "IT_FRACTIONAL_INCOME_NOT_MODELLED")],
)
def test_a_typed_straddler_does_not_hide_a_known_numeric_exclusion(amount: str, code: str) -> None:
    typed = _straddler("a", income_type=hh.IncomeType.EMPLOYMENT_EARNINGS)
    for spells in ((_whole_year("a", amount),), (_whole_year("a", amount), typed)):
        result = run_household_income_tax(_couple(*spells), "a", tax_year=YEAR)
        assert (result.outcome, result.code) == ("unsupported", code)


def test_a_refusal_falls_back_on_the_selected_persons_facts() -> None:
    non_resident = _IN_SLICE.model_copy(update={"residence_scope": hh.TaxResidenceScope.NON_RESIDENT})
    household = _couple(_straddler("b"), claimant=non_resident, partner=_IN_SLICE)
    result = run_household_income_tax(household, "b", tax_year=YEAR)
    assert (result.outcome, result.code) == ("needs_review", "HOUSEHOLD_SPELL_PERIOD_MISMATCH")


def test_deductions_and_losses_map_each_to_its_own_field() -> None:
    facts = _IN_SLICE.model_copy(
        update={"no_deductions_status": hh.Assertion.VERIFIED, "no_available_losses_status": hh.Assertion.EXCLUDED}
    )
    mapped = _mapped(_couple(claimant=facts))
    assert mapped.no_deductions_status is it.FactStatus.VERIFIED
    assert mapped.no_available_losses_status is it.FactStatus.EXCLUDED
    swapped = _mapped(
        _couple(
            claimant=facts.model_copy(
                update={"no_deductions_status": hh.Assertion.EXCLUDED, "no_available_losses_status": hh.Assertion.VERIFIED}
            )
        )
    )
    assert swapped.no_deductions_status is it.FactStatus.EXCLUDED
    assert swapped.no_available_losses_status is it.FactStatus.VERIFIED


def _adapter_scenario(**kw: Any) -> it.IncomeTaxScenario:
    return it.IncomeTaxScenario(
        individual_status=it.FactStatus.VERIFIED,
        residence_scope=it.ResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT,
        tax_year_basis=kw.pop("tax_year_basis", it.TaxYearBasis.STANDARD_2026_27),
        income_composition=it.IncomeComposition.ORDINARY_SALARY_WAGES_ONLY,
        no_deductions_status=kw.pop("no_deductions_status", it.FactStatus.VERIFIED),
        no_available_losses_status=kw.pop("no_available_losses_status", it.FactStatus.EXCLUDED),
        general_basic_rate_status=it.FactStatus.VERIFIED,
        taxable_income_basis_attestation=True,
        annual_taxable_income=kw.pop("annual_taxable_income", Decimal(60000)),
    )


def test_the_adapter_sets_deductions_and_losses_each_to_its_own_field() -> None:
    person = household_from_income_tax(_adapter_scenario(), household_id="h", tax_year=YEAR).persons[0]
    facts = person.income_tax_facts
    assert facts is not None
    assert facts.no_deductions_status is hh.Assertion.VERIFIED
    assert facts.no_available_losses_status is hh.Assertion.EXCLUDED
    reverse = _adapter_scenario(
        no_deductions_status=it.FactStatus.EXCLUDED, no_available_losses_status=it.FactStatus.VERIFIED
    )
    facts = household_from_income_tax(reverse, household_id="h", tax_year=YEAR).persons[0].income_tax_facts
    assert facts is not None
    assert facts.no_deductions_status is hh.Assertion.EXCLUDED
    assert facts.no_available_losses_status is hh.Assertion.VERIFIED


def test_the_adapter_keeps_the_given_identities() -> None:
    household = household_from_income_tax(_adapter_scenario(), household_id="custom-h", tax_year=YEAR, person_id="p1")
    assert household.household_id == "custom-h"
    assert household.persons[0].person_id == "p1"
    assert household.families[0].claimant_id == "p1"
    assert [s.person_id for s in household.income_spells] == ["p1"]


def test_the_adapter_dates_the_spell_to_the_period_it_is_given() -> None:
    earlier = hh.DatePeriod(start=date(2025, 4, 1), end=date(2026, 4, 1))
    scenario = _adapter_scenario(tax_year_basis=it.TaxYearBasis.OTHER_STANDARD_YEAR)
    (spell,) = household_from_income_tax(scenario, household_id="h", tax_year=earlier).income_spells
    assert (spell.start, spell.end) == (earlier.start, earlier.end)


@pytest.mark.parametrize("basis", [it.TaxYearBasis.OTHER_STANDARD_YEAR, it.TaxYearBasis.NON_STANDARD_YEAR])
def test_the_adapter_refuses_another_years_amount_dated_2026_27(basis: it.TaxYearBasis) -> None:
    with pytest.raises(AdapterRefused, match="another tax year"):
        household_from_income_tax(_adapter_scenario(tax_year_basis=basis), household_id="h", tax_year=YEAR)
    # No amount, no spell, nothing to date.
    household = household_from_income_tax(
        _adapter_scenario(tax_year_basis=basis, annual_taxable_income=None), household_id="h", tax_year=YEAR
    )
    assert household.income_spells == ()


def test_the_adapter_infers_no_year_for_an_unknown_basis() -> None:
    unknown = replace(_adapter_scenario(), tax_year_basis=None)
    (spell,) = household_from_income_tax(unknown, household_id="h", tax_year=YEAR).income_spells
    assert (spell.start, spell.end) == (YEAR.start, YEAR.end)


def test_the_run_passes_the_policy_dir_the_modelled_date_and_the_requested_version(tmp_path: Path) -> None:
    household = _couple(_whole_year("a", "60000"))
    scenario = _mapped(household)
    # A copy whose specification differs binds a different snapshot into the trace.
    copy = tmp_path / "income_tax"
    shutil.copytree(it.POLICY_DIR, copy)
    with (copy / "specification.md").open("a") as handle:
        handle.write("\nprobe\n")
    result = run_household_income_tax(household, "a", tax_year=YEAR, policy_dir=copy)
    assert result.trace is not None
    assert dict(result.trace.artifact_sha256) == load_policy_snapshot(copy, expected_policy_id="income_tax").artifact_sha256
    assert result == run_income_tax_module(scenario, policy_dir=copy)
    default = run_household_income_tax(household, "a", tax_year=YEAR)
    assert default.trace is not None and default.trace.artifact_sha256 != result.trace.artifact_sha256

    late = date(2027, 4, 1)
    outside = run_household_income_tax(household, "a", tax_year=YEAR, modelled_date=late)
    assert outside.code == "IT_DATE_OUTSIDE_REFERENCE_PERIOD"
    assert outside == run_income_tax_module(scenario, modelled_date=late)
    assert outside.trace is not None and outside.trace.modelled_date == late

    with pytest.raises(PolicyVersionMismatchError):
        run_household_income_tax(household, "a", tax_year=YEAR, requested_policy_version="0.1.0")
