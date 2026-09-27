"""v0.3 Task 1b.6 (ADR-0016): population ranges for needs_review households.

Built from golden household g1 with facts removed. The expected ranges are
recomputed independently here, by running each branch's household directly
under the baseline and reform parameters."""

from __future__ import annotations

import copy
from decimal import Decimal
from typing import Any

import pytest

from poltika.policy.facts import fact_index, load_fact_catalog
from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.combined import run_combined_household
from poltika.scenarios.conditional import Slot, assign, component
from poltika.scenarios.microsim import analysis
from poltika.scenarios.microsim.ranges import population_ranges
from poltika.scenarios.microsim.reform import Override, Reform, apply_reform
from poltika.scenarios.microsim.runner import COMPONENTS, PopulationRun, run_population
from poltika.scenarios.population import scenario_record
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_validation import KNOWN, _persons_for
from tests.unit.scenarios.test_population import _dataset, _facts, _household

CODE = CodeIdentity("test", None, None, None)
FACTS = fact_index(
    load_fact_catalog(WFF_POLICY_DIR),
    load_fact_catalog(AS_POLICY_DIR),
    load_fact_catalog(WFF_POLICY_DIR.parent / "wff_as_interaction"),
)
AREA = Slot("accommodation_supplement", "statistical_area_unit")
# An Accommodation Supplement reform, so the area branches' changes differ.
AS_REFORM = Reform(
    reform_id="as subsidy rate",
    overrides=(
        Override(
            policy_id="accommodation_supplement",
            parameter_id="rent_board_subsidy_rate",
            operation="set",
            value=Decimal("0.8"),
        ),
    ),
)


def _g1(hid: str, weight: str, change: tuple[str, str, Any] | None = None) -> Any:
    facts = copy.deepcopy(_facts(0))
    if change is not None:
        section, name, value = change
        facts["household"][section][name] = value
    return _household(
        household_id=hid,
        weight=Decimal(weight),
        facts=facts,
        persons=_persons_for(facts),
        characteristics=KNOWN,
    )


@pytest.fixture(scope="module")
def population() -> PopulationDataset:
    return _dataset(
        _g1("full", "2"),
        _g1("area", "3", ("accommodation_supplement", "statistical_area_unit", None)),
        _g1("eligibility", "5", ("wff", "household_eligibility", "unknown")),
        _g1("income", "7", ("wff", "family_scheme_income", None)),
    )


@pytest.fixture(scope="module")
def run(population: PopulationDataset) -> PopulationRun:
    return run_population(population, AS_REFORM, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)


def _direct_area_changes(population: PopulationDataset) -> list[tuple[Decimal, Decimal]]:
    """(baseline, reform) AS for each area, run directly."""
    household = next(h for h in population.households if h.household_id == "area")
    record = scenario_record(household)
    base = load_policy_parameters(
        AS_POLICY_DIR, record.as_lookup_date, requested_policy_version=record.requested_as_policy_version
    )
    reformed = apply_reform(base, AS_REFORM)
    out = []
    for value in FACTS[("accommodation_supplement", "statistical_area_unit")].domain():
        branch = assign(record, AREA, value)
        amounts = []
        for params in (base, reformed):
            result = run_combined_household(
                WFF_POLICY_DIR,
                AS_POLICY_DIR,
                branch.household,
                wff_lookup_date=branch.wff_lookup_date,
                as_lookup_date=branch.as_lookup_date,
                assessment_week=branch.assessment_week,
                requested_wff_policy_version=branch.requested_wff_policy_version,
                requested_as_policy_version=branch.requested_as_policy_version,
                as_parameters=params,
            )
            r = component(result, "accommodation_supplement")
            assert r.outcome == "calculated" and r.value is not None
            amounts.append(r.value)
        out.append((amounts[0], amounts[1]))
    return out


def test_bounded_household_range_matches_direct_runs(
    population: PopulationDataset, run: PopulationRun
) -> None:
    ranges = population_ranges(run, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS)["accommodation_supplement"]
    direct = _direct_area_changes(population)
    changes = [after - before for before, after in direct]
    weight = Decimal(3)
    assert ranges.bounded_households == 1 and ranges.bounded_weight == weight
    assert (ranges.delta_low, ranges.delta_high) == (min(changes) * weight, max(changes) * weight)
    baselines = [before for before, _ in direct]
    assert (ranges.baseline_low, ranges.baseline_high) == (min(baselines) * weight, max(baselines) * weight)
    assert ranges.delta_low < ranges.delta_high  # the areas really differ


def test_unsupported_branch_or_missing_amount_is_unboundable(run: PopulationRun) -> None:
    ftc = population_ranges(run, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS)["family_tax_credit"]
    # eligibility unknown: its "excluded" branch is unsupported; income missing: no branches.
    assert ftc.bounded_households == 0
    assert ftc.unboundable_weight == Decimal(5) + Decimal(7)


def test_calculated_totals_are_unchanged_and_weights_reconcile(run: PopulationRun) -> None:
    before = (run.run_id, run.results_sha256)
    ranges = population_ranges(run, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS)
    assert (run.run_id, run.results_sha256) == before
    fiscal = analysis.fiscal(run)
    total = sum((h.weight for h in run.households), Decimal(0))
    for c in COMPONENTS:
        r = ranges[c]
        assert r.calculated_delta == fiscal[c].delta_total
        assert r.calculated_weight == fiscal[c].coverage["calculated"]
        assert r.unsupported_weight == fiscal[c].coverage["unsupported"]
        assert r.calculated_weight + r.bounded_weight + r.unboundable_weight + r.unsupported_weight == total
        assert r.bounded_weight + r.unboundable_weight == fiscal[c].coverage["needs_review"]


def test_in_work_tax_credit_is_unboundable_while_its_rate_needs_review(run: PopulationRun) -> None:
    iwtc = population_ranges(run, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS)["in_work_tax_credit"]
    assert iwtc.bounded_weight == 0 and iwtc.calculated_weight == 0
    assert iwtc.delta_low == iwtc.delta_high == 0
