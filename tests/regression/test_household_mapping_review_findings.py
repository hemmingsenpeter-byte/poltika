"""Regressions for household-mapping review findings (ADR-0017 Task 6).

Each test reproduces a finding from an independent review under its own
durable, searchable name, independent of the unit tests' coverage.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import PartnerStatus
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.household_mappings import household_from_combined, to_wff
from poltika.semantics import household as hh
from poltika.semantics.household import BenefitKind, BenefitSpell, Family, Household, Person
from poltika.semantics.population import PersonRole
from tests.unit.scenarios.test_combined import WEEK as PAIR_WEEK
from tests.unit.scenarios.test_combined import _as, _wff
from tests.unit.scenarios.test_household_run import TAX_YEAR, _run, _with

WEEK = AssessmentWeek(date(2026, 6, 1), date(2026, 6, 8))


def test_map01_part_week_benefit_beside_whole_week_no_benefit_is_rejected() -> None:
    """MAP-01 (reviews/2026-10-12-task5-6-mapping-codex.md): a whole-week
    `NO_BENEFIT` spell and a one-day Jobseeker Support spell for the same
    claimant passed validation, and the AS mapping returned
    `NON_BENEFICIARY`. Contradictory benefit receipt is now refused."""
    with pytest.raises(ValidationError, match="benefit spells for claimant overlap"):
        Household(
            household_id="probe",
            persons=(Person(person_id="claimant", role=PersonRole.CLAIMANT),),
            families=(Family(claimant_id="claimant"),),
            benefit_spells=(
                BenefitSpell(person_id="claimant", benefit=BenefitKind.NO_BENEFIT, start=WEEK.start, end=WEEK.end),
                BenefitSpell(
                    person_id="claimant",
                    benefit=BenefitKind.JOBSEEKER_SUPPORT,
                    start=date(2026, 6, 3),
                    end=date(2026, 6, 4),
                ),
            ),
        )


def test_pr218_p3_income_spell_order_does_not_change_the_refusal() -> None:
    """#218 Codex recheck, inherited P3 (reviews/2026-10-15-pr218-independent.md
    in #222): two adults' straddling WFF income spells, listed in either
    order, gave one canonical household hash but refusals naming different
    spells. The refusal now names the canonically first spell."""
    base = household_from_combined(
        CombinedHouseholdScenario(
            wff=replace(_wff(), partner_status=PartnerStatus.PARTNERED),
            accommodation_supplement=_as(partner_status=None),
            as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
        ),
        household_id="probe",
        tax_year=TAX_YEAR,
        assessment_week=PAIR_WEEK,
    )
    spells = tuple(
        hh.IncomeSpell(
            person_id=person,
            income_type=hh.IncomeType.UNSPLIT_TOTAL,
            start=start,
            end=TAX_YEAR.end,
            amount=Decimal(100),
            basis=hh.IncomeBasis.WFF_FAMILY_SCHEME,
        )
        for person, start in (("claimant", date(2026, 3, 31)), ("partner", date(2026, 3, 30)))
    )
    a, b = _with(base, income_spells=spells), _with(base, income_spells=spells[::-1])
    assert a.content_sha256() == b.content_sha256()
    assert to_wff(a, TAX_YEAR) == to_wff(b, TAX_YEAR)
    assert _run(a) == _run(b)
    assert "[2026-03-30, 2027-04-01)" in str(to_wff(a, TAX_YEAR))


@pytest.mark.parametrize("reverse", [False, True])
def test_overlap_validation_names_the_same_group_in_any_order(reverse: bool) -> None:
    """Two people each with overlapping spells: the error names the
    canonically first group whatever order the spells were listed in."""
    def overlapping(person_id: str) -> tuple[hh.IncomeSpell, ...]:
        return tuple(
            hh.IncomeSpell(
                person_id=person_id,
                income_type=hh.IncomeType.EMPLOYMENT_EARNINGS,
                start=start,
                end=date(2026, 7, 1),
                amount=Decimal(1),
            )
            for start in (date(2026, 6, 1), date(2026, 6, 15))
        )

    income = (*overlapping("partner"), *overlapping("claimant"))
    benefits = tuple(
        BenefitSpell(person_id=p, benefit=BenefitKind.JOBSEEKER_SUPPORT, start=s, end=date(2026, 7, 1))
        for p in ("partner", "claimant")
        for s in (date(2026, 6, 1), date(2026, 6, 15))
    )
    persons = (Person(person_id="claimant", role=PersonRole.CLAIMANT), Person(person_id="partner", role=PersonRole.PARTNER))
    family = Family(claimant_id="claimant", partner_id="partner", partner_status=hh.FamilyPartnerStatus.PARTNERED)
    order = (lambda xs: xs[::-1]) if reverse else (lambda xs: xs)
    with pytest.raises(ValidationError, match="income spells for claimant/employment_earnings/gross overlap"):
        Household(household_id="probe", persons=persons, families=(family,), income_spells=order(income))
    with pytest.raises(ValidationError, match="benefit spells for claimant overlap"):
        Household(household_id="probe", persons=persons, families=(family,), benefit_spells=order(benefits))
