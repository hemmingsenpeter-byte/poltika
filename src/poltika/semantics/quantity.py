"""Step 2.6 (ADR-0018): the quantity, X = (x̂, D_x, E_x).

`doctrine/epistemic-constitution.md` section 2: every number Poltika shows
or stores carries its value x̂, its uncertainty D_x and the evidence E_x for
it, in eleven fields: value, unit, reference period, geography, population,
source, method, evidence class, uncertainty, model version, dependencies.

This module is the typed record and the precision rule (P3). It depends on
nothing outside `semantics/`, so the adapters that build a quantity from an
engine result live downstream (`engines/assurance/quantities.py`). The
engines themselves don't change.

The uncertainty type accepts intervals and distributions now, although
nothing propagates them until Step 11, so later models aren't built on an
implicit assumption of point values.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from poltika.semantics.variables import Observation


class EvidenceClass(str, Enum):
    """The constitution's eight classes (section 1)."""

    FACT = "fact"
    RULE = "rule"
    ESTIMATE = "estimate"
    TRANSFERRED_ESTIMATE = "transferred_estimate"
    ASSUMPTION = "assumption"
    SCENARIO = "scenario"
    MODEL_OUTPUT = "model_output"
    AI_HYPOTHESIS = "ai_hypothesis"


class Method(str, Enum):
    STATUTE = "statute"
    OBSERVATION = "observation"
    CALCULATION = "calculation"
    ESTIMATION = "estimation"
    STATED = "stated"


# How each class may be obtained. An AI hypothesis may come from anywhere,
# which is why it can never be a dependency (`Dependency`).
_METHODS: dict[EvidenceClass, frozenset[Method]] = {
    EvidenceClass.FACT: frozenset({Method.OBSERVATION}),
    EvidenceClass.RULE: frozenset({Method.STATUTE}),
    EvidenceClass.ESTIMATE: frozenset({Method.ESTIMATION}),
    EvidenceClass.TRANSFERRED_ESTIMATE: frozenset({Method.ESTIMATION}),
    EvidenceClass.ASSUMPTION: frozenset({Method.STATED}),
    EvidenceClass.SCENARIO: frozenset({Method.STATED}),
    EvidenceClass.MODEL_OUTPUT: frozenset({Method.CALCULATION}),
    EvidenceClass.AI_HYPOTHESIS: frozenset(Method),
}

# A figure resting only on these may be exact: a Rule, or a Rule applied to
# scenario inputs (constitution section 2).
_EXACT_BASIS = frozenset({EvidenceClass.RULE, EvidenceClass.SCENARIO})

# Classes a shown figure must name when it rests on them (section 1).
CAVEAT_CLASSES = frozenset(
    {
        EvidenceClass.ASSUMPTION,
        EvidenceClass.SCENARIO,
        EvidenceClass.ESTIMATE,
        EvidenceClass.TRANSFERRED_ESTIMATE,
    }
)


class UncertaintyKind(str, Enum):
    EXACT = "exact"
    INTERVAL = "interval"
    DISTRIBUTION = "distribution"
    UNQUANTIFIED = "unquantified"


class Uncertainty(BaseModel):
    """D_x. `interval_kind` is `bounds` for true bounds, or `points` for
    values at chosen points that are not bounds (ADR-0016's `Bounds.kind`).
    A distribution is given by its quantiles, so any later method can
    report into it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: UncertaintyKind
    low: Decimal | None = None
    high: Decimal | None = None
    interval_kind: Literal["bounds", "points"] | None = None
    # (probability, value) pairs, probabilities strictly increasing in (0, 1).
    quantiles: tuple[tuple[Decimal, Decimal], ...] = ()
    reason: str | None = None

    @model_validator(mode="after")
    def _consistent(self) -> Uncertainty:
        interval = (self.low, self.high, self.interval_kind)
        if self.kind is UncertaintyKind.INTERVAL:
            if self.low is None or self.high is None or self.interval_kind is None:
                raise ValueError("an interval needs low, high and interval_kind")
            if self.low > self.high:
                raise ValueError(f"interval low {self.low} is above high {self.high}")
        elif interval != (None, None, None):
            raise ValueError(f"low, high and interval_kind belong to an interval, not {self.kind.value}")
        if self.kind is UncertaintyKind.DISTRIBUTION:
            if len(self.quantiles) < 2:
                raise ValueError("a distribution needs at least two quantiles")
            probabilities = [p for p, _ in self.quantiles]
            values = [v for _, v in self.quantiles]
            if not all(Decimal(0) < p < Decimal(1) for p in probabilities):
                raise ValueError("quantile probabilities must lie strictly between 0 and 1")
            if any(a >= b for a, b in zip(probabilities, probabilities[1:], strict=False)):
                raise ValueError("quantile probabilities must be strictly increasing")
            if any(a > b for a, b in zip(values, values[1:], strict=False)):
                raise ValueError("quantile values must not decrease")
        elif self.quantiles:
            raise ValueError(f"quantiles belong to a distribution, not {self.kind.value}")
        if self.kind is UncertaintyKind.UNQUANTIFIED:
            if not self.reason:
                raise ValueError("unquantified uncertainty must say why")
        elif self.reason is not None:
            raise ValueError(f"a reason belongs to unquantified uncertainty, not {self.kind.value}")
        return self

    @classmethod
    def exact(cls) -> Uncertainty:
        return cls(kind=UncertaintyKind.EXACT)

    @classmethod
    def interval(
        cls, low: Decimal, high: Decimal, interval_kind: Literal["bounds", "points"]
    ) -> Uncertainty:
        return cls(kind=UncertaintyKind.INTERVAL, low=low, high=high, interval_kind=interval_kind)

    @classmethod
    def unquantified(cls, reason: str) -> Uncertainty:
        return cls(kind=UncertaintyKind.UNQUANTIFIED, reason=reason)


class PopulationKind(str, Enum):
    HOUSEHOLD = "household"  # one caller-described household
    WEIGHTED_POPULATION = "weighted_population"
    PUBLISHED_STATISTIC = "published_statistic"
    NOT_APPLICABLE = "not_applicable"  # e.g. a statutory rate; the description says why


class PopulationGrade(str, Enum):
    """P4's names. The criteria for each come with Step 7.2."""

    DEVELOPMENT = "development"
    PUBLIC_DATA = "public_data"
    IDI_CALIBRATED = "idi_calibrated"


class Population(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: PopulationKind
    description: str = Field(min_length=1)
    # Required for a weighted population, and only then: no synthetic
    # population is presented as reality (constitution section 5).
    grade: PopulationGrade | None = None

    @model_validator(mode="after")
    def _grade(self) -> Population:
        if (self.kind is PopulationKind.WEIGHTED_POPULATION) != (self.grade is not None):
            raise ValueError("a weighted population needs its grade, and only it has one")
        return self


class Period(BaseModel):
    """`[start, end)`. `start == end` is a point in time (a stock's date)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    start: date
    end: date

    @model_validator(mode="after")
    def _ordered(self) -> Period:
        if self.end < self.start:
            raise ValueError(f"period ends ({self.end}) before it starts ({self.start})")
        return self


class Dependency(BaseModel):
    """Something a quantity rests on, flattened to its evidence: a parameter,
    a fact, a dataset, an assumption. Intermediate model outputs are the
    evidence graph's to chain (Step 4), and an AI hypothesis never enters a
    calculation (constitution section 7)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    evidence_class: EvidenceClass

    @model_validator(mode="after")
    def _flattened(self) -> Dependency:
        if self.evidence_class is EvidenceClass.AI_HYPOTHESIS:
            raise ValueError(f"'{self.id}': an AI hypothesis can't be a dependency until it is promoted")
        if self.evidence_class is EvidenceClass.MODEL_OUTPUT:
            raise ValueError(f"'{self.id}': list what the model output rests on, not the output itself")
        return self


class Quantity(BaseModel):
    """X = (x̂, D_x, E_x). `value` is None only for a range with no central
    figure (an interval of bounds across conditional branches)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    value: Decimal | None
    unit: str = Field(min_length=1)
    reference_period: Period
    geography: str = Field(min_length=1)
    population: Population
    source: tuple[str, ...] = Field(min_length=1)
    method: Method
    evidence_class: EvidenceClass
    uncertainty: Uncertainty
    model_version: str = Field(min_length=1)
    dependencies: tuple[Dependency, ...] = ()

    @model_validator(mode="after")
    def _consistent(self) -> Quantity:
        if any(not s for s in self.source):
            raise ValueError("an empty source entry is not provenance")
        if self.method not in _METHODS[self.evidence_class]:
            raise ValueError(
                f"a {self.evidence_class.value} is not obtained by {self.method.value}"
            )
        ids = [d.id for d in self.dependencies]
        if len(ids) != len(set(ids)):
            raise ValueError("a dependency is listed twice")
        if self.evidence_class is EvidenceClass.MODEL_OUTPUT and not self.dependencies:
            raise ValueError("a model output must list what it rests on")
        kind = self.uncertainty.kind
        if self.value is None and kind is not UncertaintyKind.INTERVAL:
            raise ValueError("only an interval may have no central value")
        if self.value is not None and kind is UncertaintyKind.INTERVAL:
            low, high = self.uncertainty.low, self.uncertainty.high
            assert low is not None and high is not None
            if not low <= self.value <= high:
                raise ValueError(f"value {self.value} lies outside its interval [{low}, {high}]")
        if kind is UncertaintyKind.EXACT and not self.rests_on <= _EXACT_BASIS:
            raise ValueError(
                "only a Rule, a Scenario, or a model output resting on nothing else, is exact"
            )
        return self

    @property
    def rests_on(self) -> frozenset[EvidenceClass]:
        """The classes this figure ultimately depends on, itself included
        unless it is a model output."""
        own = set() if self.evidence_class is EvidenceClass.MODEL_OUTPUT else {self.evidence_class}
        return frozenset(own | {d.evidence_class for d in self.dependencies})

    @property
    def caveats(self) -> tuple[EvidenceClass, ...]:
        """The classes a shown figure must name (constitution section 1)."""
        return tuple(sorted(self.rests_on & CAVEAT_CLASSES, key=lambda c: c.value))


def observation_quantity(
    observation: Observation, *, geography: str, population: Population, uncertainty: Uncertainty
) -> Quantity:
    """A Fact read through the data layer. The caller states its geography,
    population and uncertainty from the publication; none is defaulted."""
    lineage = observation.lineage
    return Quantity(
        value=observation.value,
        unit=observation.unit,
        reference_period=Period(start=observation.period_start, end=observation.period_end),
        geography=geography,
        population=population,
        source=(
            f"{lineage.source_organisation}: {lineage.publication} ({lineage.vintage})",
            lineage.source_url_or_identifier,
            f"dataset {lineage.dataset_id} v{lineage.raw_snapshot_version}",
        ),
        method=Method.OBSERVATION,
        evidence_class=EvidenceClass.FACT,
        uncertainty=uncertainty,
        model_version=(
            f"transformation {lineage.transformation_id} v{lineage.transformation_version}; "
            f"raw sha256 {lineage.raw_sha256}"
        ),
    )


# P3: figures that aren't a single household's exact result are shown to
# three significant figures.
SHOWN_SIGNIFICANT_FIGURES = 3


def round_significant(value: Decimal, figures: int = SHOWN_SIGNIFICANT_FIGURES) -> Decimal:
    """`value` to `figures` significant figures, half away from zero."""
    if value == 0:
        return Decimal(0)
    exponent = value.adjusted() - figures + 1
    return value.quantize(Decimal(1).scaleb(exponent), rounding=ROUND_HALF_UP)


def _grouped(value: Decimal) -> str:
    places = max(0, -value.as_tuple().exponent) if isinstance(value.as_tuple().exponent, int) else 0
    return f"{value:,.{places}f}"


def keeps_legal_precision(quantity: Quantity) -> bool:
    """P3: a single household's exact result keeps the precision the law
    sets. Everything else is shown to three significant figures."""
    return quantity.uncertainty.kind is UncertaintyKind.EXACT and quantity.population.kind in {
        PopulationKind.HOUSEHOLD,
        PopulationKind.NOT_APPLICABLE,
    }


def shown(quantity: Quantity) -> str:
    """The figure as it may be shown (constitution section 3). Stored values
    keep full precision; only this rendering rounds. An interval is shown as
    its range, never as a point alone."""
    if keeps_legal_precision(quantity):
        assert quantity.value is not None
        return _grouped(quantity.value)
    uncertainty = quantity.uncertainty
    if uncertainty.kind is UncertaintyKind.INTERVAL:
        assert uncertainty.low is not None and uncertainty.high is not None
        low = _grouped(round_significant(uncertainty.low))
        high = _grouped(round_significant(uncertainty.high))
        span = f"{low} to {high}" if low != high else low
        if quantity.value is None:
            return span
        return f"{_grouped(round_significant(quantity.value))} ({span})"
    assert quantity.value is not None
    return _grouped(round_significant(quantity.value))
