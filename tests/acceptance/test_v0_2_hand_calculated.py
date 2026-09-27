"""v0.2 Task 9.3: hand-calculated population cases.

Small populations whose totals, winner counts and deciles are calculated
here, independently of the runner and analysis modules, from each
household's facts and the policy's own parameters (read from
`policy.yaml`, never restated). The family tax credit formula below is
written from the WFF specification's calculation sequence (step 2), not
taken from the engine:

    FTC = max(0, eldest + additional * (children - 1)
                 - rate * floor(max(0, family scheme income - threshold)))

Author: Claude Code. BUILD_PLAN_v0_2.md assigns 9.3 to GPT/Codex, so these
are an author's cases awaiting that independent check, not a substitute.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_FLOOR, Decimal
from typing import Any

import pytest

from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.microsim import analysis
from poltika.scenarios.microsim.analysis import ChangeClass
from poltika.scenarios.microsim.reform import Override, Reform
from poltika.scenarios.microsim.runner import AS_COMPONENT, PopulationRun, run_population
from poltika.scenarios.microsim.synthetic import generate
from poltika.scenarios.population import scenario_record
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_synthetic import TOY, _spec

CODE = CodeIdentity("hand", None, None, None)
FTC = ("family_tax_credit",)
NEW_THRESHOLD = Decimal(50000)
REFORM = Reform(
    reform_id="hand: FTC threshold to 50000",
    overrides=(
        Override(
            policy_id="working_for_families",
            parameter_id="family_tax_credit_abatement_threshold",
            operation="set",
            value=NEW_THRESHOLD,
        ),
    ),
)

_P = load_policy_parameters(
    WFF_POLICY_DIR, date(2026, 6, 1), requested_policy_version=TOY["requested_wff_policy_version"]
)


def _param(name: str) -> Decimal:
    value = _P.get(name).value
    assert value is not None
    return value


ELDEST = _param("family_tax_credit_eldest_child")
ADDITIONAL = _param("family_tax_credit_additional_child")
RATE = _param("family_tax_credit_abatement_rate")
THRESHOLD = _param("family_tax_credit_abatement_threshold")


def ftc(income: Decimal, children: int, threshold: Decimal = THRESHOLD) -> Decimal:
    excess = max(Decimal(0), income - threshold).to_integral_value(rounding=ROUND_FLOOR)
    return max(Decimal(0), ELDEST + ADDITIONAL * (children - 1) - RATE * excess)


def _run(population: PopulationDataset) -> PopulationRun:
    return run_population(population, REFORM, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)


def _one_band(amount: int) -> list[dict[str, Any]]:
    return [{"from": amount, "to": amount + 1, "share": "1"}]


def _homogeneous(**overrides: Any) -> tuple[PopulationDataset, PopulationRun]:
    population, _ = generate(_spec(households=3, represents="300", **overrides))
    return population, _run(population)


COUPLE_TWO_CHILDREN: dict[str, Any] = {
    "household_type": {"couple_with_children": "1"},
    "children_count": {"2": "1"},
    "best_start_cohort": {"outside_best_start_entitlement": "1"},
}


def test_three_identical_families_above_both_thresholds() -> None:
    income = Decimal(60000)
    population, run = _homogeneous(**COUPLE_TWO_CHILDREN, gross_income=_one_band(60000))
    base, reform = ftc(income, 2), ftc(income, 2, NEW_THRESHOLD)
    # 2026-27 values: 14,375 - 0.275 x 15,100 = 10,222.50, and 14,375 - 0.275 x 10,000 = 11,625.
    fiscal = analysis.fiscal(run)["family_tax_credit"]
    assert fiscal.baseline_total == 300 * base
    assert fiscal.reform_total == 300 * reform
    assert fiscal.delta_total == 300 * (reform - base)
    summary = analysis.overall(population, run, FTC).groups["all"]
    assert summary.by_class[ChangeClass.GAIN] == 300
    assert summary.by_class[ChangeClass.NO_CHANGE] == 0
    assert summary.mean_gain == reform - base


def test_families_below_both_thresholds_do_not_change() -> None:
    population, run = _homogeneous(**COUPLE_TWO_CHILDREN, gross_income=_one_band(40000))
    fiscal = analysis.fiscal(run)["family_tax_credit"]
    assert fiscal.baseline_total == fiscal.reform_total == 300 * (ELDEST + ADDITIONAL)
    assert (
        analysis.overall(population, run, FTC).groups["all"].by_class[ChangeClass.NO_CHANGE] == 300
    )


def test_households_without_children_are_outside_wff_and_counted_so() -> None:
    population, run = _homogeneous(
        household_type={"single_without_children": "1"}, gross_income=_one_band(60000)
    )
    fiscal = analysis.fiscal(run)["family_tax_credit"]
    assert fiscal.baseline_total == fiscal.reform_total == 0
    assert fiscal.coverage["unsupported"] == 300
    assert (
        analysis.overall(population, run, FTC).groups["all"].by_class[ChangeClass.UNSUPPORTED]
        == 300
    )


@pytest.fixture(scope="module")
def mixed() -> tuple[PopulationDataset, PopulationRun]:
    population, _ = generate(
        _spec(
            households=40,
            represents="4000",
            household_type={"sole_parent": "0.5", "couple_with_children": "0.5"},
            children_count={"1": "0.5", "3": "0.5"},
            best_start_cohort={"outside_best_start_entitlement": "1"},
            gross_income=[
                {"from": 30000, "to": 30001, "share": "0.3"},
                {"from": 60000, "to": 60001, "share": "0.4"},
                {"from": 90000, "to": 90001, "share": "0.3"},
            ],
        )
    )
    return population, _run(population)


def _facts(population: PopulationDataset) -> dict[str, tuple[Decimal, int, Decimal]]:
    """household id -> (family scheme income, children, weight), from the records."""
    out = {}
    for h in population.households:
        wff = scenario_record(h).household.wff
        assert wff.family_scheme_income is not None
        out[h.household_id] = (wff.family_scheme_income.combined, len(wff.children), h.weight)
    return out


def test_mixed_population_totals_and_winners_by_hand(
    mixed: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = mixed
    facts = _facts(population)
    base = sum((w * ftc(i, n) for i, n, w in facts.values()), Decimal(0))
    reform = sum((w * ftc(i, n, NEW_THRESHOLD) for i, n, w in facts.values()), Decimal(0))
    gainers = sum(
        (w for i, n, w in facts.values() if ftc(i, n, NEW_THRESHOLD) > ftc(i, n)), Decimal(0)
    )

    fiscal = analysis.fiscal(run)["family_tax_credit"]
    assert fiscal.coverage["calculated"] == 4000
    assert (fiscal.baseline_total, fiscal.reform_total, fiscal.delta_total) == (
        base,
        reform,
        reform - base,
    )
    summary = analysis.overall(population, run, FTC).groups["all"]
    assert summary.by_class[ChangeClass.GAIN] == gainers
    assert summary.by_class[ChangeClass.LOSS] == 0
    # A WFF-only reform leaves every household's Accommodation Supplement unchanged (R2).
    assert all(h.components[AS_COMPONENT].delta in (None, Decimal(0)) for h in run.households)


def test_mixed_population_deciles_by_hand(mixed: tuple[PopulationDataset, PopulationRun]) -> None:
    population, run = mixed
    facts = _facts(population)
    incomes = {
        h.household_id: h.characteristics.gross_household_income for h in population.households
    }
    ordered = sorted((incomes[k], w) for k, (_, _, w) in facts.items())
    total = sum(w for _, w in ordered)

    def cut(p: Decimal) -> Decimal:  # lower inverse of the weighted distribution
        running = Decimal(0)
        for income, w in ordered:
            running += w
            if running >= p * total:
                assert income is not None
                return income
        raise AssertionError("unreachable")

    cuts = [cut(Decimal(k) / 10) for k in range(1, 10)]
    expected: dict[str, Decimal] = {}
    for k, (i, n, w) in facts.items():
        income = incomes[k]
        assert income is not None
        decile = f"{1 + sum(income > c for c in cuts):02d}"
        expected[decile] = expected.get(decile, Decimal(0)) + w * (
            ftc(i, n, NEW_THRESHOLD) - ftc(i, n)
        )

    table = analysis.by_decile(population, run, FTC)
    assert {d: g.total_change for d, g in table.groups.items()} == expected
