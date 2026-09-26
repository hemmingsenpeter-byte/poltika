"""v0.2 Phase 8: analysis tables, on hand-built runs whose answers are known
exactly, plus a smoke run on the golden-household population."""

from __future__ import annotations

from decimal import Decimal as D
from typing import Any

import pytest

from poltika.scenarios.microsim.analysis import (
    ChangeClass,
    by_as_area,
    by_children,
    by_decile,
    by_household_type,
    by_region,
    component_set_unit,
    fiscal,
    household_change,
    overall,
)
from poltika.scenarios.microsim.reform import Override, Reform
from poltika.scenarios.microsim.runner import (
    COMPONENTS,
    ComponentDelta,
    ComponentOutcomeValue,
    HouseholdResult,
    PopulationRun,
    run_population,
)
from poltika.scenarios.microsim.validation import RecordStatus, validate_population
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import HouseholdCharacteristics, PersonRole
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_population import _dataset, _household, _people

FTC = ("family_tax_credit",)


def _cov(outcome: str, value: str | None) -> ComponentOutcomeValue:
    return ComponentOutcomeValue(outcome, None if value is None else D(value), None)  # type: ignore[arg-type]


def _delta(base: str | None, new: str | None, outcome: str = "calculated") -> ComponentDelta:
    if outcome != "calculated":
        return ComponentDelta(outcome, _cov(outcome, None), _cov(outcome, None), None)  # type: ignore[arg-type]
    assert base is not None and new is not None
    return ComponentDelta(
        "calculated", _cov("calculated", base), _cov("calculated", new), D(new) - D(base)
    )


def _result(
    hid: str, weight: str, ftc: ComponentDelta, **others: ComponentDelta
) -> HouseholdResult:
    components = {c: _delta("0", "0") for c in COMPONENTS}
    components["family_tax_credit"] = ftc
    components.update(others)
    return HouseholdResult(hid, D(weight), RecordStatus.VALID, components)


# Five households: gains of 100 (w1) and 300 (w3), a loss of 50 (w2),
# no change (w4), and one needs_review (w5).
RESULTS = (
    _result("a", "1", _delta("1000", "1100")),
    _result("b", "3", _delta("500", "800")),
    _result("c", "2", _delta("200", "150")),
    _result("d", "4", _delta("0", "0")),
    _result("e", "5", _delta(None, None, "needs_review")),
)
INCOMES = {"a": "10000", "b": "20000", "c": "30000", "d": None, "e": "50000"}
REGIONS = {"a": "North", "b": "North", "c": "South", "d": None, "e": "South"}


def _population() -> Any:
    households = []
    for r in RESULTS:
        income = INCOMES[r.household_id]
        roles = (
            (PersonRole.CLAIMANT, PersonRole.DEPENDENT_CHILD)
            if r.household_id in "ab"
            else (PersonRole.CLAIMANT,)
        )
        households.append(
            _household(
                household_id=r.household_id,
                weight=r.weight,
                persons=_people(*roles),
                characteristics=HouseholdCharacteristics(
                    region=REGIONS[r.household_id],
                    gross_household_income=None if income is None else D(income),
                ),
            )
        )
    return _dataset(*households)


def _run(results: tuple[HouseholdResult, ...] = RESULTS) -> PopulationRun:
    population = _population()
    return PopulationRun(
        run_id="x",
        results_sha256="y",
        population_id=population.population_id,
        population_version=1,
        population_sha256="z",
        synthetic=True,
        label=population.label,
        reform=Reform(
            reform_id="r",
            overrides=(
                Override(
                    policy_id="working_for_families", parameter_id="p", operation="set", value=D(1)
                ),
            ),
        ),
        code=CodeIdentity("t", None, None, None),
        policy_artifacts=(),
        validation=validate_population(population),
        households=results,
    )


def test_winners_and_losers_by_hand() -> None:
    s = overall(_population(), _run(), FTC).groups["all"]
    assert s.households == 5 and s.weight == D(15)
    assert s.by_class == {
        ChangeClass.GAIN: D(4),
        ChangeClass.LOSS: D(2),
        ChangeClass.NO_CHANGE: D(4),
        ChangeClass.NEEDS_REVIEW: D(5),
        ChangeClass.UNSUPPORTED: D(0),
    }
    assert s.mean_gain == D(250)  # (100*1 + 300*3) / 4
    assert s.median_gain == D(300)  # cumulative weight 1 then 4, half is 2
    assert (s.mean_loss, s.median_loss) == (D(-50), D(-50))
    assert (s.largest_gain, s.largest_loss) == (D(300), D(-50))
    assert s.total_change == D(900)  # 100 + 900 - 100 + 0; needs_review excluded
    assert s.calculated_weight == D(10)


def test_needs_review_is_never_counted_as_zero() -> None:
    change = household_change(RESULTS[4], FTC)
    assert change.change_class is ChangeClass.NEEDS_REVIEW and change.change is None


def test_component_set_must_share_a_unit() -> None:
    assert component_set_unit(("family_tax_credit", "best_start")) == "NZD per tax year"
    with pytest.raises(ValueError, match="mix units"):
        component_set_unit(("family_tax_credit", "accommodation_supplement"))
    with pytest.raises(ValueError, match="unknown"):
        component_set_unit(("nope",))


def test_a_set_is_calculated_only_if_every_member_is() -> None:
    mixed = _result(
        "m", "1", _delta("0", "10"), in_work_tax_credit=_delta(None, None, "needs_review")
    )
    assert household_change(mixed, FTC).change == D(10)
    assert (
        household_change(mixed, ("family_tax_credit", "in_work_tax_credit")).change_class
        is ChangeClass.NEEDS_REVIEW
    )


def test_deciles_leave_out_unknown_income() -> None:
    table = by_decile(_population(), _run(), FTC)
    assert table.left_out == {"income unknown": D(4)}
    # Known incomes 10k (w1), 20k (w3), 30k (w2), 50k (w5): total weight 11.
    assert sum(g.weight for g in table.groups.values()) == D(11)
    # Cuts at k/10 of 11: 1.1, 2.2, 3.3 -> 20k (cumulative 4); 4.4, 5.5 -> 30k
    # (cumulative 6); 6.6 and above -> 50k. So 10k and 20k are decile 1 (at or
    # below the first cut), 30k is decile 4 and 50k decile 6. With so few
    # households, deciles are lumpy by construction.
    assert sorted(table.groups) == ["01", "04", "06"]
    assert table.groups["01"].households == 2 and table.groups["01"].total_change == D(1000)
    assert table.groups["04"].total_change == D(-100)
    assert table.groups["06"].by_class[ChangeClass.NEEDS_REVIEW] == D(5)


def test_region_type_children_and_area_groupings() -> None:
    regions = by_region(_population(), _run(), FTC)
    assert regions.left_out == {"region unknown": D(4)}
    assert regions.groups["North"].total_change == D(1000)
    assert regions.groups["South"].total_change == D(-100)
    types = by_household_type(_population(), _run(), FTC)
    assert set(types.groups) == {"sole_parent", "single_without_children"}
    children = by_children(_population(), _run(), FTC)
    assert children.groups["1"].weight == D(4) and children.groups["0"].weight == D(11)
    areas = by_as_area(_population(), _run(), FTC)
    assert sum(g.weight for g in areas.groups.values()) + sum(areas.left_out.values()) == D(15)


def test_fiscal_totals_and_coverage_by_hand() -> None:
    table = fiscal(_run())
    ftc = table["family_tax_credit"]
    assert ftc.unit == "NZD per tax year"
    assert ftc.baseline_total == D(1000 * 1 + 500 * 3 + 200 * 2)
    assert ftc.reform_total == D(1100 * 1 + 800 * 3 + 150 * 2)
    assert ftc.delta_total == ftc.reform_total - ftc.baseline_total == D(900)
    assert ftc.coverage == {"calculated": D(10), "needs_review": D(5), "unsupported": D(0)}
    assert table["accommodation_supplement"].unit == "NZD per week"


def test_smoke_on_the_golden_population() -> None:
    from tests.unit.scenarios.microsim.test_runner import THRESHOLD
    from tests.unit.scenarios.microsim.test_runner import _population as golden

    population = golden()
    run = run_population(
        population,
        THRESHOLD,
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("t", None, None, None),
    )
    s = overall(population, run, FTC).groups["all"]
    assert s.weight == sum(h.weight for h in run.households)
    assert s.by_class[ChangeClass.LOSS] == 0
    assert s.by_class[ChangeClass.GAIN] > 0
    assert fiscal(run)["accommodation_supplement"].delta_total == 0
