"""Task 9.3: Codex's fixed, hand-calculated population cases.

Derivation and primary-source checks: reviews/2026-09-27-pr117.md.
Expected values are literal arithmetic results, independent of the policy
loader, generator, calculator and weighted-quantile implementation.
The shared golden helper supplies input facts only, never expected values.
"""

from __future__ import annotations

from decimal import Decimal as D

import pytest

from poltika.scenarios.microsim import analysis
from poltika.scenarios.microsim.analysis import ChangeClass
from poltika.scenarios.microsim.reform import Override, Reform
from poltika.scenarios.microsim.runner import PopulationRun, run_population
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import HouseholdCharacteristics, PersonRole, PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_population import _dataset, _facts, _household, _people

FTC = ("family_tax_credit",)


@pytest.fixture(scope="module")
def population() -> PopulationDataset:
    # id, weight, gross income, qualifying children. f has unverified WFF income.
    rows = (
        ("a", "1", "40000", 1),
        ("b", "2", "44901.99", 1),
        ("c", "3", "60000", 2),
        ("d", "1", "60000", 1),
        ("e", "1", "100000", 1),
        ("f", "1", "70000", 1),
        ("g", "1", "80000", 0),
    )
    households = []
    for hid, weight, income, children in rows:
        facts = _facts()
        wff = facts["household"]["wff"]
        wff["children"] = [dict(wff["children"][0]) for _ in range(children)]
        wff["family_scheme_income"] = (
            None if hid == "f" else {"claimant_amount": income, "partner_amount": None}
        )
        wff["net_family_scheme_income"] = None
        wff["net_family_scheme_income_me3_attested"] = False
        as_ = facts["household"]["accommodation_supplement"]
        as_["dependent_children_count"] = children
        as_["weekly_income"] = str((D(income) / 52).quantize(D("0.01")))
        households.append(
            _household(
                hid,
                weight=D(weight),
                persons=_people(
                    PersonRole.CLAIMANT, *([PersonRole.DEPENDENT_CHILD] * children)
                ),
                characteristics=HouseholdCharacteristics(gross_household_income=D(income)),
                facts=facts,
            )
        )
    return _dataset(*households, population_id="codex_hand_population")


def _run(population: PopulationDataset, threshold: str) -> PopulationRun:
    return run_population(
        population,
        Reform(
            reform_id=f"hand FTC threshold {threshold}",
            overrides=(
                Override(
                    policy_id="working_for_families",
                    parameter_id="family_tax_credit_abatement_threshold",
                    operation="set",
                    value=D(threshold),
                ),
            ),
        ),
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("codex-hand-cases", None, None, None),
    )


@pytest.fixture(scope="module")
def raised(population: PopulationDataset) -> PopulationRun:
    return _run(population, "50000")


def test_fixed_entitlements_and_weighted_totals(raised: PopulationRun) -> None:
    expected = {
        "a": ("calculated", D(7921), D(7921)),
        "b": ("calculated", D("7920.725"), D(7921)),
        "c": ("calculated", D("10222.5"), D(11625)),
        "d": ("calculated", D("3768.5"), D(5171)),
        "e": ("calculated", D(0), D(0)),
        "f": ("needs_review", None, None),
        "g": ("unsupported", None, None),
    }
    for h in raised.households:
        delta = h.components["family_tax_credit"]
        assert (delta.outcome, delta.baseline.value, delta.reform.value) == expected[h.household_id]
    fiscal = analysis.fiscal(raised)["family_tax_credit"]
    assert (fiscal.baseline_total, fiscal.reform_total, fiscal.delta_total) == (
        D("58198.45"), D(63809), D("5610.55")
    )
    assert fiscal.coverage == {"calculated": D(8), "needs_review": D(1), "unsupported": D(1)}


def test_fixed_winners_and_tied_weighted_deciles(
    population: PopulationDataset, raised: PopulationRun
) -> None:
    summary = analysis.overall(population, raised, FTC).groups["all"]
    assert summary.by_class == {
        ChangeClass.GAIN: D(6),
        ChangeClass.LOSS: D(0),
        ChangeClass.NO_CHANGE: D(2),
        ChangeClass.NEEDS_REVIEW: D(1),
        ChangeClass.UNSUPPORTED: D(1),
    }
    assert summary.median_gain == D("1402.5")
    table = analysis.by_decile(population, raised, FTC)
    # Cumulative weights are 1, 3, 7, 8, 9, 10. Both 60k households stay together.
    assert {k: (g.weight, g.total_change) for k, g in table.groups.items()} == {
        "01": (D(1), D(0)),
        "02": (D(2), D("0.55")),
        "04": (D(4), D(5610)),
        "08": (D(1), D(0)),
        "09": (D(1), D(0)),
        "10": (D(1), D(0)),
    }
    assert table.groups["08"].by_class[ChangeClass.NEEDS_REVIEW] == 1
    assert table.groups["09"].by_class[ChangeClass.UNSUPPORTED] == 1
    assert table.groups["08"].calculated_weight == table.groups["09"].calculated_weight == 0
    assert table.left_out == {}


def test_lower_threshold_losses_by_hand(population: PopulationDataset) -> None:
    run = _run(population, "40000")
    fiscal = analysis.fiscal(run)["family_tax_credit"]
    assert (fiscal.baseline_total, fiscal.reform_total, fiscal.delta_total) == (
        D("58198.45"), D("50113.45"), D(-8085)
    )
    summary = analysis.overall(population, run, FTC).groups["all"]
    assert summary.by_class == {
        ChangeClass.GAIN: D(0),
        ChangeClass.LOSS: D(6),
        ChangeClass.NO_CHANGE: D(2),
        ChangeClass.NEEDS_REVIEW: D(1),
        ChangeClass.UNSUPPORTED: D(1),
    }
    assert summary.mean_loss == summary.median_loss == D("-1347.5")
