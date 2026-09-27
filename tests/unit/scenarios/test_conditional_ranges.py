"""v0.3 Tasks 1b.2b and 1b.3b-1b.3d (ADR-0016): numeric ranges, and the
properties every conditional answer must keep.

The monotone declarations here are test fixtures, added to copies of the
catalogue entries. The real declarations are specification content for
GPT/Codex to write from cited rules (BUILD_PLAN_v0_3 1b.2b). Each fixture
is checked against the engine below, so a wrong one fails."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from poltika.engines.simulator.outcome import FactStatus
from poltika.scenarios.conditional import (
    COMPONENTS,
    WFF_COMPONENTS,
    WFF_TOTAL,
    FactIndex,
    Resolution,
    Slot,
    assign,
    assign_number,
    component,
    resolve,
)
from poltika.scenarios.record import ScenarioRecord, result_payload
from poltika.semantics.schemas.fact_catalog import FactEntry, Monotone
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_conditional import FACTS, GOLDEN, _as, _run, _wff

G1 = GOLDEN[0]  # g1: a sole parent, non-beneficiary; FTC and AS both calculated
FSI = Slot("wff", "family_scheme_income")
AS_INCOME = Slot("accommodation_supplement", "weekly_income")
AS_COSTS = Slot("accommodation_supplement", "weekly_accommodation_costs")


def _declare(facts: FactIndex, slot: Slot, **monotone: tuple[str, str]) -> FactIndex:
    """A copy of the catalogue with test-fixture monotone declarations."""
    out = dict(facts)
    key = (slot.scope, slot.fact_id)
    out[key] = out[key].model_copy(
        update={"monotone": {c: Monotone(direction=d, rule=r) for c, (d, r) in monotone.items()}}
    )
    return out


DECLARED = _declare(
    _declare(
        _declare(FACTS, FSI, family_tax_credit=("decreasing", "WFF-03")),
        AS_INCOME,
        accommodation_supplement=("decreasing", "AS-07"),
    ),
    AS_COSTS,
    accommodation_supplement=("increasing", "AS-04"),
)


def _resolve(record: ScenarioRecord, facts: FactIndex = DECLARED, **kw: Any) -> Resolution:
    return resolve(record, WFF_POLICY_DIR, AS_POLICY_DIR, facts, **kw)


def _value(record: ScenarioRecord, name: str) -> Decimal | None:
    r = component(_run(record), name)
    return r.value if r.outcome == "calculated" else None


# --- 1b.2b: ranges ----------------------------------------------------------


def test_range_branches_at_both_endpoints_as_real_runs() -> None:
    record = _wff(G1, family_scheme_income=None)
    res = _resolve(record, ranges={FSI: (Decimal(20000), Decimal(90000))})
    assert [dict(b.assignment)[FSI] for b in res.branches] == ["20000", "90000"]
    for b in res.branches:
        direct = assign_number(record, FSI, Decimal(dict(b.assignment)[FSI]))
        assert result_payload(_run(direct)) == result_payload(b.result)
    ftc = res.bounds["family_tax_credit"]
    assert ftc.kind == "bounds" and ftc.complete
    assert ftc.low == _value(assign_number(record, FSI, Decimal(90000)), "family_tax_credit")
    assert ftc.high == _value(assign_number(record, FSI, Decimal(20000)), "family_tax_credit")
    # The base result is untouched: FTC still waits for the income.
    assert component(res.base, "family_tax_credit").outcome == "needs_review"


def test_undeclared_component_gives_points_not_bounds() -> None:
    record = _wff(G1, family_scheme_income=None)
    res = _resolve(record, FACTS, ranges={FSI: (Decimal(20000), Decimal(90000))})
    assert res.bounds["family_tax_credit"].kind == "points"
    assert res.bounds[WFF_TOTAL].kind == "points"


def test_ranges_combine_with_finite_facts_jointly() -> None:
    record = _as(_wff(G1, household_eligibility=FactStatus.UNKNOWN), weekly_income=None)
    res = _resolve(record, ranges={AS_INCOME: (Decimal(200), Decimal(900))})
    assert len(res.branches) == 4  # two endpoints x eligible or not
    for b in res.branches:
        direct = record
        for slot, value in b.assignment:
            direct = (
                assign_number(direct, slot, Decimal(value)) if slot == AS_INCOME
                else assign(direct, slot, value)
            )
        assert result_payload(_run(direct)) == result_payload(b.result)
    assert res.bounds["accommodation_supplement"].kind == "bounds"


def test_count_range_takes_whole_numbers() -> None:
    record = _as(G1, dependent_children_count=None)
    slot = Slot("accommodation_supplement", "dependent_children_count")
    res = _resolve(record, ranges={slot: (Decimal(1), Decimal(3))})
    assert [dict(b.assignment)[slot] for b in res.branches] == ["1", "3"]
    with pytest.raises(ValueError, match="whole numbers"):
        _resolve(record, ranges={slot: (Decimal("0.5"), Decimal(2))})


@pytest.mark.parametrize(
    ("ranges", "message"),
    [
        ({FSI: (Decimal(5), Decimal(1))}, "0 <= low <= high"),
        ({FSI: (Decimal(-1), Decimal(1))}, "0 <= low <= high"),
        ({FSI: (Decimal("NaN"), Decimal(1))}, "0 <= low <= high"),
        ({AS_INCOME: (Decimal(1), Decimal(2))}, "not a missing amount"),  # supplied, not missing
        ({Slot("wff", "household_eligibility"): (Decimal(0), Decimal(1))}, "not a missing amount"),
    ],
)
def test_bad_ranges_are_refused(ranges: dict[Slot, tuple[Decimal, Decimal]], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _resolve(_wff(G1, family_scheme_income=None), ranges=ranges)


def test_ranges_over_the_cap_are_refused() -> None:
    record = _as(_wff(G1, family_scheme_income=None), weekly_income=None)
    ranges = {FSI: (Decimal(1), Decimal(2)), AS_INCOME: (Decimal(1), Decimal(2))}
    with pytest.raises(ValueError, match="over the cap"):
        _resolve(record, ranges=ranges, max_branches=3)


def test_monotone_only_on_numeric_facts() -> None:
    entry = FACTS[("wff", "household_eligibility")]
    with pytest.raises(ValueError, match="only for money and count"):
        FactEntry.model_validate(
            {**entry.model_dump(), "monotone": {"family_tax_credit": {"direction": "increasing", "rule": "WFF-03"}}}
        )
    with pytest.raises(ValueError, match="not a rule id"):
        Monotone(direction="increasing", rule="because")


# --- 1b.3b: declarations hold, and values in a range stay in its bounds -----

_SETTINGS = settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
CASES = [
    (FSI, "family_tax_credit", _wff(G1, family_scheme_income=None), 0, 150000),
    (AS_INCOME, "accommodation_supplement", _as(G1, weekly_income=None), 0, 2000),
    (AS_COSTS, "accommodation_supplement", _as(G1, weekly_accommodation_costs=None), 0, 1500),
]


def _money(lo: int, hi: int) -> st.SearchStrategy[Decimal]:
    return st.decimals(min_value=lo, max_value=hi, places=2, allow_nan=False, allow_infinity=False)


@pytest.mark.parametrize(("slot", "name", "record", "lo", "hi"), CASES, ids=lambda x: getattr(x, "label", None))
@_SETTINGS
@given(data=st.data())
def test_declaration_holds_against_the_engine(
    slot: Slot, name: str, record: ScenarioRecord, lo: int, hi: int, data: st.DataObject
) -> None:
    a, b = sorted((data.draw(_money(lo, hi)), data.draw(_money(lo, hi))))
    fa, fb = (_value(assign_number(record, slot, v), name) for v in (a, b))
    if fa is None or fb is None:
        return
    direction = DECLARED[(slot.scope, slot.fact_id)].monotone[name].direction  # type: ignore[index]
    assert fa >= fb if direction == "decreasing" else fa <= fb


@pytest.mark.parametrize(("slot", "name", "record", "lo", "hi"), CASES, ids=lambda x: getattr(x, "label", None))
@_SETTINGS
@given(data=st.data())
def test_any_value_in_a_range_is_within_its_bounds(
    slot: Slot, name: str, record: ScenarioRecord, lo: int, hi: int, data: st.DataObject
) -> None:
    low, high = sorted((data.draw(_money(lo, hi)), data.draw(_money(lo, hi))))
    inside = data.draw(_money(0, 1).map(lambda t: low + (high - low) * t).map(lambda v: v.quantize(Decimal("0.01"))))
    bounds = _resolve(record, ranges={slot: (low, high)}).bounds[name]
    assert bounds.kind == "bounds"
    value = _value(assign_number(record, slot, inside), name)
    if value is not None and bounds.complete:
        assert bounds.low is not None and bounds.high is not None
        assert bounds.low <= value <= bounds.high


# --- 1b.3c: nothing conditional is ever calculated ---------------------------


def _clearable(record: ScenarioRecord) -> list[tuple[str, dict[str, Any]]]:
    wff, as_ = record.household.wff, record.household.accommodation_supplement
    out: list[tuple[str, dict[str, Any]]] = []
    for name in (
        "household_eligibility", "extra_instalment_status", "in_work_eligibility",
        "mc6a_veterans_payment", "mc6b_disqualifying_payment", "best_start_no_shared_care",
    ):
        if getattr(wff, name) is not FactStatus.UNKNOWN:
            out.append(("wff", {name: FactStatus.UNKNOWN}))
    if wff.family_scheme_income is not None:
        out.append(("wff", {"family_scheme_income": None}))
    for name in ("claimant_category", "statistical_area_unit", "weekly_income", "weekly_accommodation_costs"):
        if getattr(as_, name) is not None:
            out.append(("accommodation_supplement", {name: None}))
    return out


@pytest.mark.parametrize(
    ("index", "section", "change"),
    [(i, s, c) for i, g in enumerate(GOLDEN) for s, c in _clearable(g)],
    ids=lambda x: str(x) if not isinstance(x, dict) else next(iter(x)),
)
def test_a_removed_fact_never_leaves_a_blocked_component_calculated(
    index: int, section: str, change: dict[str, Any]
) -> None:
    golden = GOLDEN[index]
    record = _wff(golden, **change) if section == "wff" else _as(golden, **change)
    res = _resolve(record)
    for m in res.missing:
        for name in m.blocks:
            assert component(res.base, name).outcome != "calculated"
    for name in COMPONENTS:
        base = component(res.base, name)
        if base.outcome == "calculated":
            assert res.known[name] == base.value
        else:
            assert name not in res.known


# --- 1b.3d: totals are summed within one joint assignment --------------------


def test_total_bounds_come_from_joint_assignments_only() -> None:
    # The 2026-27 in-work tax credit is needs_review, so no v0.1 branch has
    # a WFF total yet; this holds the rule for when one does.
    record = _wff(G1, household_eligibility=FactStatus.UNKNOWN)
    res = _resolve(record)
    totals = [b.result.wff.total_annual_entitlement() for b in res.branches]
    calculated = [t for t in totals if t is not None]
    bounds = res.bounds[WFF_TOTAL]
    assert bounds.calculated == len(calculated)
    if calculated:
        assert (bounds.low, bounds.high) == (min(calculated), max(calculated))
    # The total's range is never the sum of the per-component extremes.
    per_component_high = sum(
        (res.bounds[c].high or Decimal(0)) for c in WFF_COMPONENTS
    )
    assert bounds.high is None or bounds.high <= per_component_high
