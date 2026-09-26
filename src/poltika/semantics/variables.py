"""v0.2 Tasks 2.1 and 2.3: canonical variables and the read interface.

Downstream code (the future baseline module, engines) sees data only
through these types. It asks a `CanonicalContext` for a canonical variable
on a date and gets an `Observation` with its lineage. It never sees a file,
a column or a source format (`REPOSITORY_STRUCTURE.md`, the dependency
boundary). The implementation lives in `poltika.data.context`.

The dictionary itself is data-layer metadata
(`data/metadata/variables/dictionary.yaml`). Its entries record a
publication's own definitions, so they are added with the dataset that
feeds them (Task 3.1), never from memory.
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_VARIABLE_ID = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


class Frequency(str, Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"


class PriceBasis(str, Enum):
    NOMINAL = "nominal"
    REAL = "real"
    NOT_APPLICABLE = "not_applicable"  # counts, indices, ratios


class Measure(str, Enum):
    STOCK = "stock"  # a level at a point in time (debt, population)
    FLOW = "flow"  # an amount over a period (revenue, GDP)


class CanonicalVariable(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    meaning: str
    unit: str
    frequency: Frequency
    price_basis: PriceBasis
    # The price base of a real series, as the publication states it.
    price_base: str | None = None
    measure: Measure
    geography_population: str
    valid_from: date
    valid_to: date | None = None  # exclusive; None while the series continues

    @field_validator("id")
    @classmethod
    def _dotted_id(cls, value: str) -> str:
        if not _VARIABLE_ID.match(value):
            raise ValueError(f"'{value}' is not a dotted canonical variable id")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> CanonicalVariable:
        if (self.price_basis is PriceBasis.REAL) != (self.price_base is not None):
            raise ValueError(
                f"'{self.id}': price_base is required for a real series, and only then"
            )
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError(f"'{self.id}': valid period is empty")
        return self


class DataDictionary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variables: list[CanonicalVariable] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_ids(self) -> DataDictionary:
        ids = [v.id for v in self.variables]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate canonical variable id(s): {duplicates}")
        return self

    def by_id(self) -> dict[str, CanonicalVariable]:
        return {v.id: v for v in self.variables}


class Lineage(BaseModel):
    """value → transformation → dataset → source → publication → vintage →
    retrieval date (`ROADMAP.md`, v0.2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transformation_id: str
    transformation_version: int
    dataset_id: str
    raw_snapshot_version: int
    raw_sha256: str
    source_organisation: str
    publication: str
    source_url_or_identifier: str
    vintage: str
    retrieval_date: date


class Observation(BaseModel):
    """One value of a canonical variable for the period `[period_start,
    period_end)`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    variable_id: str
    period_start: date
    period_end: date
    value: Decimal
    unit: str
    lineage: Lineage


class CanonicalContext(Protocol):
    def get(self, variable_id: str, on: date, vintage: str | None = None) -> Observation:
        """The observation of `variable_id` whose period covers `on`, from
        `vintage` or the latest one."""
        ...
