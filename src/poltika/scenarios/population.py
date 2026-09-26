"""v0.2 Task 2.2: from a population household to the v0.1 engines' input.

`scenario_record()` rebuilds a household's `facts` into the same
`ScenarioRecord` a stored single-household scenario uses
(`record_from_plain`). There is no second path into the engines.
Malformed facts raise `InvalidHouseholdFacts`. Population validation
(Phase 4) reports that household as `invalid` rather than running it.

`household_type()` classifies from `persons` alone. It is a grouping label
for analysis, not a policy fact. Eligibility is decided only by the engines
from `facts`.
"""

from __future__ import annotations

from enum import Enum

from poltika.common.errors import PoltikaError
from poltika.scenarios.record import ScenarioRecord, record_from_plain
from poltika.semantics.population import PersonRole, PopulationHousehold


class InvalidHouseholdFacts(PoltikaError):
    """A household's `facts` don't form a valid scenario record."""


class HouseholdType(str, Enum):
    SOLE_PARENT = "sole_parent"
    COUPLE_WITH_CHILDREN = "couple_with_children"
    SINGLE_WITHOUT_CHILDREN = "single_without_children"
    COUPLE_WITHOUT_CHILDREN = "couple_without_children"
    UNCLASSIFIED = "unclassified"


def scenario_record(household: PopulationHousehold) -> ScenarioRecord:
    try:
        record = record_from_plain(household.facts)
        wff = record.household.wff
        as_ = record.household.accommodation_supplement
        # The stored-record decoder assumes canonical types; external
        # population facts have not passed the API's input validation.
        if type(wff.net_family_scheme_income_me3_attested) is not bool:
            raise ValueError("net_family_scheme_income_me3_attested must be a boolean")
        count = as_.dependent_children_count
        if count is not None and type(count) is not int:
            raise ValueError("dependent_children_count must be an integer or null")
        amounts = [
            wff.net_family_scheme_income, as_.weekly_accommodation_costs,
            as_.cash_assets, as_.weekly_income,
        ]
        if wff.family_scheme_income is not None:
            amounts.extend([
                wff.family_scheme_income.claimant_amount,
                wff.family_scheme_income.partner_amount,
            ])
        if any(amount is not None and not amount.is_finite() for amount in amounts):
            raise ValueError("income, costs and assets must be finite")
        return record
    except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
        raise InvalidHouseholdFacts(
            f"household '{household.household_id}': facts are not a valid scenario record ({exc!r})"
        ) from exc


def household_type(household: PopulationHousehold) -> HouseholdType:
    roles = [p.role for p in household.persons]
    claimants = roles.count(PersonRole.CLAIMANT)
    partners = roles.count(PersonRole.PARTNER)
    children = roles.count(PersonRole.DEPENDENT_CHILD)
    if claimants != 1 or partners > 1:
        return HouseholdType.UNCLASSIFIED
    if partners:
        return (
            HouseholdType.COUPLE_WITH_CHILDREN
            if children
            else HouseholdType.COUPLE_WITHOUT_CHILDREN
        )
    return HouseholdType.SOLE_PARENT if children else HouseholdType.SINGLE_WITHOUT_CHILDREN


def dependent_children(household: PopulationHousehold) -> int:
    return sum(p.role is PersonRole.DEPENDENT_CHILD for p in household.persons)
