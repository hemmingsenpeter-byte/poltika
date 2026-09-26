"""v0.2 Task 4.1: population record checks."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from poltika.scenarios.microsim.validation import (
    RecordStatus,
    validate_household,
    validate_population,
)
from poltika.semantics.population import HouseholdCharacteristics, PersonRecord, PersonRole
from tests.unit.scenarios.test_population import _dataset, _facts, _household, _people

KNOWN = HouseholdCharacteristics(region="Test region", gross_household_income=Decimal(50000))


def _golden_consistent() -> dict[str, Any]:
    """Golden household 0's facts with persons matching them."""
    return _facts(0)


def _persons_for(facts: dict[str, Any]) -> tuple[Any, ...]:
    wff = facts["household"]["wff"]
    roles = [PersonRole.CLAIMANT]
    if wff["partner_status"] == "partnered":
        roles.append(PersonRole.PARTNER)
    roles += [PersonRole.DEPENDENT_CHILD] * len(wff["children"])
    return _people(*roles)


def _consistent(**overrides: Any) -> Any:
    facts = _golden_consistent()
    as_facts = facts["household"]["accommodation_supplement"]
    as_facts["dependent_children_count"] = len(facts["household"]["wff"]["children"])
    fields: dict[str, Any] = {
        "facts": facts,
        "persons": _persons_for(facts),
        "characteristics": KNOWN,
    }
    fields.update(overrides)
    return _household(**fields)


def test_consistent_household_is_valid() -> None:
    result = validate_household(_consistent())
    assert result.status is RecordStatus.VALID, result.findings
    assert result.record is not None


def test_bad_facts_are_invalid_and_have_no_record() -> None:
    facts = _golden_consistent()
    facts["household"]["wff"]["household_eligibility"] = "maybe"
    result = validate_household(_consistent(facts=facts))
    assert result.status is RecordStatus.INVALID
    assert result.record is None


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("wff", "net_family_scheme_income_me3_attested", "false"),
        ("wff", "net_family_scheme_income_me3_attested", 1),
        ("wff", "net_family_scheme_income", "Infinity"),
        ("accommodation_supplement", "dependent_children_count", 1.5),
        ("accommodation_supplement", "dependent_children_count", True),
        ("accommodation_supplement", "weekly_income", "Infinity"),
    ],
)
def test_malformed_primitive_facts_are_invalid(section: str, field: str, value: Any) -> None:
    facts = _golden_consistent()
    facts["household"][section][field] = value
    result = validate_household(_consistent(facts=facts))
    assert result.status is RecordStatus.INVALID
    assert result.record is None


def test_claimant_and_partner_counts() -> None:
    no_claimant = validate_household(_consistent(persons=_people(PersonRole.PARTNER)))
    two_partners = validate_household(
        _consistent(persons=_people(PersonRole.CLAIMANT, PersonRole.PARTNER, PersonRole.PARTNER))
    )
    assert no_claimant.status is RecordStatus.INVALID and no_claimant.record is None
    assert two_partners.status is RecordStatus.INVALID


def test_partner_contradiction_needs_review() -> None:
    facts = _golden_consistent()
    facts["household"]["wff"]["partner_status"] = "single"
    with_partner = (*_persons_for(facts), PersonRecord(person_id="px", role=PersonRole.PARTNER))
    result = validate_household(_consistent(facts=facts, persons=with_partner))
    assert result.status is RecordStatus.NEEDS_REVIEW
    assert result.record is not None
    facts["household"]["wff"]["partner_status"] = "partnered"
    result = validate_household(_consistent(facts=facts, persons=_people(PersonRole.CLAIMANT)))
    assert any("persons list no partner" in text for _, text in result.findings)


def test_child_count_mismatch_and_unknown_grouping_are_warnings() -> None:
    facts = _golden_consistent()
    extra = PersonRecord(person_id="extra", role=PersonRole.DEPENDENT_CHILD)
    persons = (*_persons_for(facts), extra)
    result = validate_household(
        _consistent(persons=persons, characteristics=HouseholdCharacteristics())
    )
    assert result.status is RecordStatus.WARNING
    texts = " | ".join(text for _, text in result.findings)
    assert "WFF facts list" in texts and "region unknown" in texts and "income unknown" in texts


def test_population_summary_counts_and_weights() -> None:
    facts = _golden_consistent()
    facts["household"]["wff"]["household_eligibility"] = "maybe"
    population = _dataset(
        _consistent(household_id="a", weight=Decimal(2)),
        _consistent(
            household_id="b", weight=Decimal(3), characteristics=HouseholdCharacteristics()
        ),
        _consistent(household_id="c", weight=Decimal(5), facts=facts),
    )
    summary = validate_population(population).by_status()
    assert summary[RecordStatus.VALID] == (1, Decimal(2))
    assert summary[RecordStatus.WARNING] == (1, Decimal(3))
    assert summary[RecordStatus.INVALID] == (1, Decimal(5))
    assert summary[RecordStatus.NEEDS_REVIEW] == (0, Decimal(0))
