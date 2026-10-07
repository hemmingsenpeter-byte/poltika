"""v0.2 Task 2.1: the canonical population schema.

A `PopulationDataset` is a set of weighted households. Each carries:

- `persons`: who lives there (role and age), used for household types and
  record checks, never by the policy engines;
- `characteristics`: what analysis groups by (region, the decile income
  basis). Also never read by the engines;
- `facts`: the household's policy facts, in exactly the plain form a
  stored scenario record takes (`scenarios/record.py`). The runner turns
  them into a `ScenarioRecord` (`scenarios/population.py`), so a
  population household goes through the same path as a single household.

v0.2 models one WFF family and one Accommodation Supplement unit per
household, so the family is the household's facts rather than a separate
record. A multi-family household can't be represented and is left out by
the generator or adapter, and counted in its report.

This module sits in `semantics/` because both sides of the data boundary
use it. The data layer builds populations, and the runner reads them,
without either importing the other.
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SYNTHETIC_LABEL = "Synthetic development population, not an estimate for New Zealand."

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


class PersonRole(str, Enum):
    CLAIMANT = "claimant"
    PARTNER = "partner"
    DEPENDENT_CHILD = "dependent_child"
    OTHER = "other"


class PersonRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    person_id: str
    role: PersonRole
    age: int | None = Field(default=None, ge=0, le=120)


class HouseholdCharacteristics(BaseModel):
    """Grouping dimensions. `None` means unknown, and the household is left
    out of that grouping (and counted as left out), never put in a default
    group."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    region: str | None = None
    # The decile basis (BUILD_PLAN_v0_2.md D3): gross annual household income
    # as the population records it.
    gross_household_income: Decimal | None = Field(default=None, ge=0)


class PopulationHousehold(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    weight: Decimal = Field(gt=0)
    persons: tuple[PersonRecord, ...] = Field(min_length=1)
    characteristics: HouseholdCharacteristics = HouseholdCharacteristics()
    facts: dict[str, Any]

    @field_validator("household_id")
    @classmethod
    def _id(cls, value: str) -> str:
        if not _ID.match(value):
            raise ValueError(f"'{value}' is not a valid household id")
        return value

    @model_validator(mode="after")
    def _unique_people(self) -> PopulationHousehold:
        ids = [p.person_id for p in self.persons]
        if len(set(ids)) != len(ids):
            raise ValueError(f"household '{self.household_id}' lists a person twice")
        return self


class PopulationDataset(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    population_id: str
    version: int = Field(ge=1)
    synthetic: bool
    label: str
    households: tuple[PopulationHousehold, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> PopulationDataset:
        if self.synthetic and self.label != SYNTHETIC_LABEL:
            raise ValueError(f"a synthetic population must carry the label {SYNTHETIC_LABEL!r}")
        ids = [h.household_id for h in self.households]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate household id(s): {duplicates[:5]}")
        return self

    def content_sha256(self) -> str:
        """The population's identity, recorded in every run that uses it."""
        content = self.model_dump(mode="json")
        content["households"].sort(key=lambda h: h["household_id"])
        canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
