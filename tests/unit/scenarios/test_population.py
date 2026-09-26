"""v0.2 Tasks 2.1-2.2: the population schema and its adapter to the v0.1
engines. Households are built from the golden households' own facts, so the
adapter is tested against records the engines already accept."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from poltika.scenarios.population import (
    HouseholdType,
    InvalidHouseholdFacts,
    dependent_children,
    household_type,
    scenario_record,
)
from poltika.scenarios.record import canonical_json, scenario_id
from poltika.semantics.population import (
    SYNTHETIC_LABEL,
    PersonRecord,
    PersonRole,
    PopulationDataset,
    PopulationHousehold,
)
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

GOLDEN = yaml.safe_load(GOLDEN_PATH.read_text())["households"]


def _facts(index: int = 0) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(canonical_json(record_from_yaml(GOLDEN[index])))
    return result


def _people(*roles: PersonRole) -> tuple[PersonRecord, ...]:
    return tuple(PersonRecord(person_id=f"p{i}", role=r) for i, r in enumerate(roles))


def _household(household_id: str = "h1", **overrides: Any) -> PopulationHousehold:
    fields: dict[str, Any] = {
        "household_id": household_id,
        "weight": Decimal("2.5"),
        "persons": _people(PersonRole.CLAIMANT, PersonRole.DEPENDENT_CHILD),
        "facts": _facts(),
    }
    fields.update(overrides)
    return PopulationHousehold(**fields)


def _dataset(*households: PopulationHousehold, **overrides: Any) -> PopulationDataset:
    fields: dict[str, Any] = {
        "population_id": "test_population",
        "version": 1,
        "synthetic": True,
        "label": SYNTHETIC_LABEL,
        "households": households or (_household(),),
    }
    fields.update(overrides)
    return PopulationDataset(**fields)


@pytest.mark.parametrize("index", range(len(GOLDEN)))
def test_adapter_rebuilds_the_same_scenario(index: int) -> None:
    original = record_from_yaml(GOLDEN[index])
    rebuilt = scenario_record(_household(facts=_facts(index)))
    assert rebuilt == original
    assert scenario_id(rebuilt) == scenario_id(original)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda f: f.pop("household"),
        lambda f: f["household"]["wff"].update(household_eligibility="maybe"),
        lambda f: f.update(wff_lookup_date="not a date"),
    ],
)
def test_malformed_facts_are_rejected(mutate: Any) -> None:
    facts = _facts()
    mutate(facts)
    with pytest.raises(InvalidHouseholdFacts, match="h1"):
        scenario_record(_household(facts=facts))


@pytest.mark.parametrize(
    ("roles", "expected"),
    [
        ((PersonRole.CLAIMANT, PersonRole.DEPENDENT_CHILD), HouseholdType.SOLE_PARENT),
        (
            (PersonRole.CLAIMANT, PersonRole.PARTNER, PersonRole.DEPENDENT_CHILD),
            HouseholdType.COUPLE_WITH_CHILDREN,
        ),
        ((PersonRole.CLAIMANT,), HouseholdType.SINGLE_WITHOUT_CHILDREN),
        ((PersonRole.CLAIMANT, PersonRole.PARTNER), HouseholdType.COUPLE_WITHOUT_CHILDREN),
        ((PersonRole.CLAIMANT, PersonRole.OTHER), HouseholdType.SINGLE_WITHOUT_CHILDREN),
        ((PersonRole.PARTNER, PersonRole.DEPENDENT_CHILD), HouseholdType.UNCLASSIFIED),
        ((PersonRole.CLAIMANT, PersonRole.CLAIMANT), HouseholdType.UNCLASSIFIED),
    ],
)
def test_household_type(roles: tuple[PersonRole, ...], expected: HouseholdType) -> None:
    household = _household(persons=_people(*roles))
    assert household_type(household) is expected
    assert dependent_children(household) == roles.count(PersonRole.DEPENDENT_CHILD)


@pytest.mark.parametrize(
    "overrides",
    [
        {"weight": Decimal(0)},
        {"weight": Decimal(-1)},
        {"persons": ()},
        {"household_id": "bad id"},
        {"persons": (PersonRecord(person_id="a", role=PersonRole.CLAIMANT),) * 2},
    ],
)
def test_invalid_households(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _household(**overrides)


def test_synthetic_population_must_carry_the_label() -> None:
    with pytest.raises(ValidationError, match="label"):
        _dataset(label="Looks official")
    assert _dataset(synthetic=False, label="Survey microdata").synthetic is False


def test_duplicate_household_ids_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate household"):
        _dataset(_household("h1"), _household("h1"))


def test_content_hash_is_stable_and_sensitive() -> None:
    a = _dataset(_household("h1"), _household("h2"))
    assert a.content_sha256() == _dataset(_household("h1"), _household("h2")).content_sha256()
    reweighted = _dataset(_household("h1"), _household("h2", weight=Decimal(3)))
    assert a.content_sha256() != reweighted.content_sha256()
