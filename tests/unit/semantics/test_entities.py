"""Programme Task 2.4: entities, identifier schemes and populations."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from poltika.common.errors import (
    InvalidIdentifierError,
    UnassignedIdentifierSchemeError,
    UnknownEntityTypeError,
    UnknownIdentifierSchemeError,
)
from poltika.scenarios.microsim.synthetic import SyntheticSpec, generate
from poltika.semantics import population as population_module
from poltika.semantics.entities import (
    IDENTIFIER_SCHEMES,
    EntityType,
    IdentifierScheme,
    Population,
    get_entity_type,
    get_identifier_scheme,
    validate_identifier,
)
from poltika.semantics.population import PersonRecord, PersonRole, PopulationHousehold

REPO_ROOT = Path(__file__).resolve().parents[3]


def _household(household_id: str) -> PopulationHousehold:
    return PopulationHousehold(
        household_id=household_id,
        weight=Decimal(1),
        persons=(PersonRecord(person_id="p0", role=PersonRole.CLAIMANT),),
        facts={},
    )


def test_entity_types_are_the_programme_set() -> None:
    assert {e.value for e in EntityType} == {
        "person",
        "family",
        "household",
        "firm",
        "sector",
        "crown",
        "new_zealand",
    }
    assert get_entity_type("household") is EntityType.HOUSEHOLD
    with pytest.raises(UnknownEntityTypeError):
        get_entity_type("company")


def test_every_entity_type_has_a_scheme_and_ids_are_unique() -> None:
    assert {s.entity_type for s in IDENTIFIER_SCHEMES.values()} == set(EntityType)
    for key, scheme in IDENTIFIER_SCHEMES.items():
        assert key == scheme.id


def test_registry_is_read_only() -> None:
    with pytest.raises(TypeError):
        IDENTIFIER_SCHEMES["x"] = IDENTIFIER_SCHEMES["household_id"]  # type: ignore[index]


def test_scheme_needs_exactly_one_of_pattern_and_reason() -> None:
    with pytest.raises(ValidationError):
        IdentifierScheme(id="x", entity_type=EntityType.FIRM, issuer="i")
    with pytest.raises(ValidationError):
        IdentifierScheme(
            id="x", entity_type=EntityType.FIRM, issuer="i", pattern="^a$", unassigned_reason="r"
        )


def test_unknown_scheme_is_refused() -> None:
    with pytest.raises(UnknownIdentifierSchemeError):
        get_identifier_scheme("nope")
    with pytest.raises(UnknownIdentifierSchemeError):
        validate_identifier("nope", "x")


def test_household_scheme_accepts_real_generated_ids() -> None:
    spec_path = REPO_ROOT / "data/metadata/populations/nz_synthetic_development.v1.yaml"
    spec = SyntheticSpec.model_validate(yaml.safe_load(spec_path.read_text()))
    population, _ = generate(spec.model_copy(update={"households": 20}))
    assert population.households
    for household in population.households:
        assert validate_identifier("household_id", household.household_id) == household.household_id
        # The generator's person ids are a convention, not a rule: unassigned.
        for person in household.persons:
            with pytest.raises(UnassignedIdentifierSchemeError):
                validate_identifier("person_id", person.person_id)


@pytest.mark.parametrize("bad", ["", " ", "_a", "-a", ".a", "a b", "a/b", "é1"])
def test_household_scheme_rejects_malformed(bad: str) -> None:
    with pytest.raises(InvalidIdentifierError):
        validate_identifier("household_id", bad)


@pytest.mark.parametrize("unassigned", ["person_id", "family_id", "firm_id", "sector_id"])
def test_unassigned_schemes_refuse_with_reason(unassigned: str) -> None:
    scheme = get_identifier_scheme(unassigned)
    assert scheme.pattern is None and scheme.unassigned_reason
    with pytest.raises(UnassignedIdentifierSchemeError, match="unassigned"):
        validate_identifier(unassigned, "anything")


def test_firm_and_sector_name_no_external_scheme() -> None:
    for sid in ("firm_id", "sector_id"):
        assert get_identifier_scheme(sid).unassigned_reason == "no cited source yet"


def test_singletons_have_one_fixed_id() -> None:
    assert validate_identifier("crown_id", "crown") == "crown"
    assert validate_identifier("new_zealand_id", "new_zealand") == "new_zealand"
    for sid, other in (("crown_id", "Crown"), ("crown_id", "crown2"), ("crown_id", "crown\n"), ("new_zealand_id", "nz"), ("new_zealand_id", "new_zealand\n")):
        with pytest.raises(InvalidIdentifierError):
            validate_identifier(sid, other)


def test_household_scheme_pattern_is_the_populations_own() -> None:
    scheme = get_identifier_scheme("household_id")
    assert scheme.pattern == population_module._ID.pattern


@pytest.mark.parametrize(
    "value",
    ["a", "A1", "s0000001", "h-1.x_y", "0", "", " ", "_a", "a b", "é", "a\n", "-1", "a/b"],
)
def test_household_scheme_agrees_with_population_validator(value: str) -> None:
    try:
        _household(value)
        population_accepts = True
    except ValidationError:
        population_accepts = False
    try:
        validate_identifier("household_id", value)
        scheme_accepts = True
    except InvalidIdentifierError:
        scheme_accepts = False
    assert population_accepts == scheme_accepts


def test_population_definition() -> None:
    pop = Population(
        id="nz_households",
        entity_type=EntityType.HOUSEHOLD,
        geography="New Zealand",
        description="Private households in New Zealand",
    )
    assert pop.entity_type is EntityType.HOUSEHOLD
    with pytest.raises(ValidationError):
        Population(
            id="x",
            entity_type="company",
            geography="g",
            description="d",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", ["a\n", "s0000001\n"])
def test_household_id_with_a_trailing_newline_is_refused(value: str) -> None:
    # `$` also matches before a final newline; `\Z` does not.
    with pytest.raises(ValidationError):
        _household(value)
    with pytest.raises(InvalidIdentifierError):
        validate_identifier("household_id", value)
