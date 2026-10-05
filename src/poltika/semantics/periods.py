"""Programme Task 2.3: time periods and the named rules that relate them.

A `Period` carries explicit dates, half-open `[start, end)` as
`Observation` does in `semantics/variables.py`. A point in time has a
start and no end.

Structure is validated only where the repository states the rule with a
source. The assessment week is exactly 7 days with an explicit start and
no weekday convention (BUILD_PLAN.md:1511, Task 28.2;
`AssessmentWeek.__post_init__` in
`engines/simulator/accommodation_supplement.py:812`). No anchor date is
enforced for the tax year, quarter, calendar year or year ended June: the
repository records the 2026-27 WFF year's dates as a choice for that year
(AS specification.md:463-465), not as a calendar convention, so the type
carries its dates and nothing is inferred.

A conversion between period types is a named `PeriodRelation` with a
source. A value conversion between annual and weekly amounts has no
stated rule (v0.2 D9, BUILD_PLAN_v0_2.md:329-333; BUILD_PLAN.md:1700-1706),
so none is registered and `convert_amount` refuses.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, model_validator

from poltika.common.errors import (
    PeriodConversionRefusedError,
    PeriodRelationMismatchError,
    UnknownPeriodRelationError,
    UnknownPeriodTypeError,
)


class PeriodType(str, Enum):
    TAX_YEAR = "tax_year"
    ASSESSMENT_WEEK = "assessment_week"
    QUARTER = "quarter"
    CALENDAR_YEAR = "calendar_year"
    POINT_IN_TIME = "point_in_time"
    YEAR_ENDED_JUNE = "year_ended_june"


ASSESSMENT_WEEK_DAYS = 7


class Period(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: PeriodType
    start: date
    end: date | None = None  # exclusive; None only for a point in time

    @model_validator(mode="after")
    def _structure(self) -> Period:
        if self.type is PeriodType.POINT_IN_TIME:
            if self.end is not None:
                raise ValueError("a point_in_time has a start and no end")
            return self
        if self.end is None:
            raise ValueError(f"a {self.type.value} needs an explicit end (exclusive)")
        if self.end <= self.start:
            raise ValueError(f"end must be after start, got [{self.start}, {self.end})")
        if self.type is PeriodType.ASSESSMENT_WEEK and self.end - self.start != timedelta(
            days=ASSESSMENT_WEEK_DAYS
        ):
            raise ValueError(
                f"an assessment_week spans exactly {ASSESSMENT_WEEK_DAYS} days [start, end), "
                f"got {self.start} to {self.end}"
            )
        return self


class PeriodTypeDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: PeriodType
    meaning: str
    # Where the repository uses or states this type, as file:line.
    source: str


class RelationKind(str, Enum):
    CONTAINMENT = "containment"
    VALUE_CONVERSION = "value_conversion"


class PeriodRelation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    from_type: PeriodType  # the inner period (containment) or the source amount's period
    to_type: PeriodType  # the outer period (containment) or the target amount's period
    kind: RelationKind
    source: str  # file:line citation
    statement: str


_PERIOD_TYPES: tuple[PeriodTypeDefinition, ...] = (
    PeriodTypeDefinition(
        id=PeriodType.TAX_YEAR,
        meaning="A WFF assessment year, with explicit dates (2026-27 is [2026-04-01, 2027-04-01)).",
        source="policy_specs/accommodation_supplement/specification.md:463",
    ),
    PeriodTypeDefinition(
        id=PeriodType.ASSESSMENT_WEEK,
        meaning="An AS assessment week: exactly 7 days, [start, end), explicit start, no weekday convention.",
        source="BUILD_PLAN.md:1511",
    ),
    PeriodTypeDefinition(
        id=PeriodType.QUARTER,
        meaning="A quarterly series period, with explicit dates (MSD recipients table).",
        source="data/metadata/variables/dictionary.yaml:566",
    ),
    PeriodTypeDefinition(
        id=PeriodType.CALENDAR_YEAR,
        meaning="A calendar year, with explicit dates. Named in Programme Task 2.3; no repository use yet.",
        source="BUILD_PLAN_PROGRAMME.md (Task 2.3)",
    ),
    PeriodTypeDefinition(
        id=PeriodType.POINT_IN_TIME,
        meaning="An instant (a lookup date, a census night). Start only.",
        source="data/metadata/variables/dictionary.yaml:234",
    ),
    PeriodTypeDefinition(
        id=PeriodType.YEAR_ENDED_JUNE,
        meaning="A Household Economic Survey 'year ended June' annual series period, with explicit dates.",
        source="data/metadata/variables/dictionary.yaml:9",
    ),
)

_RELATIONS: tuple[PeriodRelation, ...] = (
    PeriodRelation(
        id="as_week_within_wff_year",
        from_type=PeriodType.ASSESSMENT_WEEK,
        to_type=PeriodType.TAX_YEAR,
        kind=RelationKind.CONTAINMENT,
        source="policy_specs/accommodation_supplement/specification.md:468",
        statement="The AS assessment week must lie wholly inside the WFF year, or every component is needs_review.",
    ),
)


def _index[T](items: tuple[T, ...], key: str, what: str) -> Mapping[str, T]:
    out: dict[str, T] = {}
    for item in items:
        raw = getattr(item, key)
        k = raw.value if isinstance(raw, Enum) else raw
        if k in out:
            raise ValueError(f"duplicate {what} id: {k}")
        out[k] = item
    return MappingProxyType(out)


PERIOD_TYPES: Mapping[str, PeriodTypeDefinition] = _index(_PERIOD_TYPES, "id", "period type")
PERIOD_RELATIONS: Mapping[str, PeriodRelation] = _index(_RELATIONS, "id", "period relation")


def get_period_type(period_type_id: str) -> PeriodTypeDefinition:
    try:
        return PERIOD_TYPES[period_type_id]
    except KeyError:
        raise UnknownPeriodTypeError(f"unknown period type: {period_type_id!r}") from None


def get_period_relation(relation_id: str) -> PeriodRelation:
    try:
        return PERIOD_RELATIONS[relation_id]
    except KeyError:
        raise UnknownPeriodRelationError(f"unknown period relation: {relation_id!r}") from None


def contains(outer: Period, inner: Period) -> bool:
    """Whether `inner` lies wholly inside `outer`, both half-open.

    A point in time is inside when `outer.start <= instant < outer.end`.
    A point-in-time `outer` has no extent and contains nothing.
    """
    if outer.end is None:
        return False
    if inner.end is None:
        return outer.start <= inner.start < outer.end
    return outer.start <= inner.start and inner.end <= outer.end


def check_containment(relation_id: str, outer: Period, inner: Period) -> bool:
    """Apply a registered containment relation to two periods of its types."""
    relation = get_period_relation(relation_id)
    if relation.kind is not RelationKind.CONTAINMENT:
        raise PeriodRelationMismatchError(f"relation {relation_id!r} is not a containment rule")
    if inner.type is not relation.from_type or outer.type is not relation.to_type:
        raise PeriodRelationMismatchError(
            f"relation {relation_id!r} relates {relation.from_type.value} inside {relation.to_type.value}, "
            f"got {inner.type.value} inside {outer.type.value}"
        )
    return contains(outer, inner)


def convert_amount(amount: Decimal, from_type: PeriodType, to_type: PeriodType) -> Decimal:
    """Refuse: no value conversion between period types has a stated rule.

    v0.2 D9 (BUILD_PLAN_v0_2.md:329-333) and Task 28.2 (BUILD_PLAN.md:1700-1706)
    record that no annual/weekly conversion exists without one. The registry
    holds none, so this always raises.
    """
    registered = [
        r
        for r in PERIOD_RELATIONS.values()
        if r.kind is RelationKind.VALUE_CONVERSION and r.from_type is from_type and r.to_type is to_type
    ]
    raise PeriodConversionRefusedError(
        f"no named value-conversion rule from {from_type.value} to {to_type.value} "
        f"({len(registered)} registered); v0.2 D9 allows none without a stated, sourced rule "
        f"(amount {amount} not converted)"
    )
