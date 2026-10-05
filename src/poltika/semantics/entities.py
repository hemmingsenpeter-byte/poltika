"""Programme Task 2.4: entities, identifier schemes and populations.

The entities are person, family, household, firm, sector, the Crown and New
Zealand (BUILD_PLAN_PROGRAMME.md Task 2.1). Each has an identifier scheme.
A scheme is registered with a rule only where this repository already has
one, quoted from its validator below. Where no cited source exists the
scheme is registered as unassigned, with the reason, and refuses to
validate: an identifier is never accepted on a guessed rule.

v0.3 keeps one family per household (ADR-0017 section 1). ADR-0017 holds
families "by person id" and does not define a family identifier or tie it
to the household id, so the family scheme is unassigned.

A `Population` names the set of entities a figure counts and where. The
geography is a plain string until Task 2.5 types it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, model_validator

from poltika.common.errors import (
    InvalidIdentifierError,
    UnassignedIdentifierSchemeError,
    UnknownEntityTypeError,
    UnknownIdentifierSchemeError,
)


class EntityType(str, Enum):
    PERSON = "person"
    FAMILY = "family"
    HOUSEHOLD = "household"
    FIRM = "firm"
    SECTOR = "sector"
    CROWN = "crown"
    NEW_ZEALAND = "new_zealand"


class IdentifierScheme(BaseModel):
    """How one kind of entity is identified.

    Exactly one of `pattern` and `unassigned_reason` is set. A pattern is
    applied with `re.match`, as the repository's own validators do."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    entity_type: EntityType
    pattern: str | None = None
    issuer: str
    unassigned_reason: str | None = None

    @model_validator(mode="after")
    def _rule_xor_reason(self) -> IdentifierScheme:
        if (self.pattern is None) == (self.unassigned_reason is None):
            raise ValueError(
                f"scheme '{self.id}' needs exactly one of a pattern and an unassigned_reason"
            )
        if self.pattern is not None:
            re.compile(self.pattern)
        return self


class Population(BaseModel):
    """A set of entities of one type in one place, which a figure counts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    entity_type: EntityType
    geography: str  # plain string until Task 2.5
    description: str


_NO_SOURCE = "no cited source yet"

_SCHEMES: tuple[IdentifierScheme, ...] = (
    IdentifierScheme(
        id="household_id",
        entity_type=EntityType.HOUSEHOLD,
        # src/poltika/semantics/population.py:37 `_ID`, applied by the
        # PopulationHousehold.household_id validator at :78-82.
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$",
        issuer="PopulationHousehold in a PopulationDataset (semantics/population.py); "
        "unique within one population (population.py:104-108)",
    ),
    IdentifierScheme(
        id="person_id",
        entity_type=EntityType.PERSON,
        issuer="PersonRecord in a PopulationHousehold (semantics/population.py)",
        unassigned_reason=(
            "PersonRecord.person_id is an unvalidated str, only required to be unique "
            "within its household (population.py:52, :84-89); the synthetic generator's "
            "form s{n:07d}p{i} (scenarios/microsim/synthetic.py:277) is its own "
            "convention, not a rule"
        ),
    ),
    IdentifierScheme(
        id="family_id",
        entity_type=EntityType.FAMILY,
        issuer="none",
        unassigned_reason=(
            "ADR-0017 section 1 keeps one family per household and records families "
            "'by person id', but defines no family identifier and does not say how one "
            "relates to the household id"
        ),
    ),
    IdentifierScheme(
        id="firm_id",
        entity_type=EntityType.FIRM,
        issuer="none",
        unassigned_reason=_NO_SOURCE,
    ),
    IdentifierScheme(
        id="sector_id",
        entity_type=EntityType.SECTOR,
        issuer="none",
        unassigned_reason=_NO_SOURCE,
    ),
    # Singletons: a fixed id each, chosen here (an orchestrator decision of
    # Task 2.4), not taken from an external scheme.
    IdentifierScheme(
        id="crown_id",
        entity_type=EntityType.CROWN,
        pattern=r"^crown\Z",
        issuer="Poltika: the one Crown entity",
    ),
    IdentifierScheme(
        id="new_zealand_id",
        entity_type=EntityType.NEW_ZEALAND,
        pattern=r"^new_zealand\Z",
        issuer="Poltika: the one New Zealand entity",
    ),
)


def _registry() -> Mapping[str, IdentifierScheme]:
    ids = [s.id for s in _SCHEMES]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate identifier scheme id(s): {duplicates}")
    return MappingProxyType({s.id: s for s in _SCHEMES})


IDENTIFIER_SCHEMES: Mapping[str, IdentifierScheme] = _registry()


def get_entity_type(value: str) -> EntityType:
    try:
        return EntityType(value)
    except ValueError:
        raise UnknownEntityTypeError(
            f"'{value}' is not an entity type; expected one of {[e.value for e in EntityType]}"
        ) from None


def get_identifier_scheme(scheme_id: str) -> IdentifierScheme:
    try:
        return IDENTIFIER_SCHEMES[scheme_id]
    except KeyError:
        raise UnknownIdentifierSchemeError(
            f"no identifier scheme '{scheme_id}'; registered: {sorted(IDENTIFIER_SCHEMES)}"
        ) from None


def validate_identifier(scheme_id: str, value: str) -> str:
    """Return `value` if it matches the scheme. An unassigned scheme refuses
    with its reason; a malformed value is an error, never repaired."""
    scheme = get_identifier_scheme(scheme_id)
    if scheme.pattern is None:
        raise UnassignedIdentifierSchemeError(
            f"identifier scheme '{scheme_id}' is unassigned: {scheme.unassigned_reason}"
        )
    if not re.match(scheme.pattern, value):
        raise InvalidIdentifierError(
            f"'{value}' is not a valid {scheme_id} (pattern {scheme.pattern})"
        )
    return value
