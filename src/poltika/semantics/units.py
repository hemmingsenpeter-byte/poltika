"""v0.2 Task 2.2: units and price bases.

A unit has a dimension, a scale, a price basis and, for money, a currency.
"Per household" and "per week" are not part of a unit: they belong to a
variable's entity and period (Tasks 2.4, 2.3, 2.1).

Only a pure change of scale (thousands of people to people) is done
implicitly, and only between units that share dimension, price basis and
currency. Any other conversion (nominal to real, for example) exists only as
a named `UnitConversion` rule with a deflator variable and a cited source.
No such rule has a source in the repository yet, so the conversion registry
starts empty and `convert` refuses.
"""

from __future__ import annotations

import re
import types
from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from poltika.common.errors import (
    IncompatibleUnitsError,
    MissingConversionRuleError,
    UnitConversionError,
    UnknownUnitError,
)

_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_VARIABLE_ID = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


class PriceBasis(str, Enum):
    NOMINAL = "nominal"
    REAL = "real"
    NOT_APPLICABLE = "not_applicable"  # counts, indices, ratios


class Dimension(str, Enum):
    MONEY = "money"
    PERSONS = "persons"
    CHILDREN = "children"  # dictionary: "thousands of children"
    HOUSEHOLDS = "households"
    FAMILIES = "families"  # dictionary: "thousands of families"
    EVENTS = "events"  # dictionary: "live births registered"
    RECIPIENTS = "recipients"  # dictionary: AS "recipients" (open question)
    RATIO = "ratio"
    PERCENT = "percent"


class Unit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    dimension: Dimension
    scale: Decimal
    price_basis: PriceBasis
    currency: str | None = None
    label: str

    @field_validator("id")
    @classmethod
    def _id_shape(cls, value: str) -> str:
        if not _ID.match(value):
            raise ValueError(f"'{value}' is not a snake-case unit id")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> Unit:
        if self.scale <= 0:
            raise ValueError(f"'{self.id}': scale must be positive")
        if self.dimension is Dimension.MONEY:
            if self.currency is None:
                raise ValueError(f"'{self.id}': a money unit needs a currency")
            if self.price_basis is PriceBasis.NOT_APPLICABLE:
                raise ValueError(f"'{self.id}': a money unit needs a price basis")
        else:
            if self.currency is not None:
                raise ValueError(f"'{self.id}': only a money unit has a currency")
            if self.price_basis is not PriceBasis.NOT_APPLICABLE:
                raise ValueError(f"'{self.id}': only a money unit has a price basis")
        return self


def _unit(
    id: str,
    dimension: Dimension,
    scale: int,
    label: str,
    *,
    currency: str | None = None,
) -> Unit:
    basis = PriceBasis.NOMINAL if dimension is Dimension.MONEY else PriceBasis.NOT_APPLICABLE
    return Unit(
        id=id,
        dimension=dimension,
        scale=Decimal(scale),
        price_basis=basis,
        currency=currency,
        label=label,
    )


_UNITS: tuple[Unit, ...] = (
    _unit("nzd", Dimension.MONEY, 1, "NZD", currency="NZD"),
    _unit("nzd_thousand", Dimension.MONEY, 1_000, "NZD thousands", currency="NZD"),
    _unit("nzd_million", Dimension.MONEY, 1_000_000, "NZD million", currency="NZD"),
    _unit("persons", Dimension.PERSONS, 1, "people"),
    _unit("persons_thousand", Dimension.PERSONS, 1_000, "thousands of people"),
    _unit("children", Dimension.CHILDREN, 1, "children"),
    _unit("children_thousand", Dimension.CHILDREN, 1_000, "thousands of children"),
    _unit("households", Dimension.HOUSEHOLDS, 1, "households"),
    _unit("households_thousand", Dimension.HOUSEHOLDS, 1_000, "thousands of households"),
    _unit("families", Dimension.FAMILIES, 1, "families"),
    _unit("families_thousand", Dimension.FAMILIES, 1_000, "thousands of families"),
    _unit("live_births", Dimension.EVENTS, 1, "live births registered"),
    _unit("recipients", Dimension.RECIPIENTS, 1, "recipients"),
    _unit("ratio", Dimension.RATIO, 1, "ratio"),
    _unit("percent", Dimension.PERCENT, 1, "percent"),
)


def _build(units: tuple[Unit, ...]) -> Mapping[str, Unit]:
    ids = [u.id for u in units]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate unit id(s): {duplicates}")
    return types.MappingProxyType({u.id: u for u in units})


UNITS: Mapping[str, Unit] = _build(_UNITS)


def get_unit(unit_id: str) -> Unit:
    try:
        return UNITS[unit_id]
    except KeyError:
        raise UnknownUnitError(f"unknown unit id '{unit_id}'") from None


def rescale(value: Decimal, from_unit: Unit, to_unit: Unit) -> Decimal:
    """A pure change of scale. Refused unless the units share dimension,
    price basis and currency."""
    if (
        from_unit.dimension is not to_unit.dimension
        or from_unit.price_basis is not to_unit.price_basis
        or from_unit.currency != to_unit.currency
    ):
        raise IncompatibleUnitsError(
            f"cannot rescale '{from_unit.id}' to '{to_unit.id}': they differ in "
            "dimension, price basis or currency; only a named conversion rule "
            "may do that"
        )
    return value * from_unit.scale / to_unit.scale


class UnitConversion(BaseModel):
    """A named, sourced rule changing a unit's price basis. It is useless
    without its deflator variable and a source citation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    from_unit: str
    to_unit: str
    deflator_variable_id: str
    method: str = Field(min_length=1)
    source: str = Field(min_length=1)  # a citation already in the repository, file:line
    valid_from: date
    valid_to: date | None = None  # exclusive

    @field_validator("deflator_variable_id")
    @classmethod
    def _deflator(cls, value: str) -> str:
        if not _VARIABLE_ID.match(value):
            raise ValueError(f"'{value}' is not a dotted canonical variable id")
        return value

    @field_validator("source", "method")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> UnitConversion:
        if self.from_unit == self.to_unit:
            raise ValueError(f"'{self.id}': from_unit and to_unit are the same")
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError(f"'{self.id}': valid period is empty")
        return self


class ConversionRegistry:
    def __init__(self, rules: tuple[UnitConversion, ...] = ()) -> None:
        self._rules: dict[str, UnitConversion] = {}
        for rule in rules:
            self.register(rule)

    def register(self, rule: UnitConversion) -> None:
        if rule.id in self._rules:
            raise ValueError(f"duplicate conversion rule id '{rule.id}'")
        get_unit(rule.from_unit)
        get_unit(rule.to_unit)
        self._rules[rule.id] = rule

    def find(self, from_unit: str, to_unit: str, on: date) -> UnitConversion | None:
        for rule in self._rules.values():
            if (
                rule.from_unit == from_unit
                and rule.to_unit == to_unit
                and rule.valid_from <= on
                and (rule.valid_to is None or on < rule.valid_to)
            ):
                return rule
        return None


# No conversion rule has a source in this repository today.
CONVERSIONS = ConversionRegistry()


def convert(
    value: Decimal,
    from_unit: Unit,
    to_unit: Unit,
    on: date,
    registry: ConversionRegistry | None = None,
) -> Decimal:
    """Convert across price bases by a named rule. Refuses when no rule
    exists; never implicit."""
    del value
    rule = (registry or CONVERSIONS).find(from_unit.id, to_unit.id, on)
    if rule is None:
        raise MissingConversionRuleError(
            f"no sourced conversion rule from '{from_unit.id}' to '{to_unit.id}' "
            f"on {on.isoformat()}; conversion is never implicit"
        )
    raise UnitConversionError(
        f"rule '{rule.id}' (method '{rule.method}') has no implemented method"
    )
