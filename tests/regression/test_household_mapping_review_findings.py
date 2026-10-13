"""Regressions for household-mapping review findings (ADR-0017 Task 6).

Each test reproduces a finding from an independent review under its own
durable, searchable name, independent of the unit tests' coverage.
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.semantics.household import BenefitKind, BenefitSpell, Family, Household, Person
from poltika.semantics.population import PersonRole

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
