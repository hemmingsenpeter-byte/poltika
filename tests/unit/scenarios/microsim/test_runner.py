"""v0.2 Tasks 7.1-7.3: the population runner, on a population built from
the golden households' own facts. Expected values are invariants, not
numbers: no figure here is a claim about New Zealand."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.microsim.reform import Override, Reform, UnsupportedReformError
from poltika.scenarios.microsim.runner import (
    AS_COMPONENT,
    COMPONENTS,
    UNITS,
    WFF_COMPONENTS,
    PopulationRun,
    run_population,
)
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import PersonRecord, PersonRole
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_validation import KNOWN, _persons_for
from tests.unit.scenarios.test_population import GOLDEN as GOLDEN_YAML
from tests.unit.scenarios.test_population import _dataset, _facts, _household
from tests.unit.scenarios.test_scenario_record import record_from_yaml

CODE = CodeIdentity("test", None, None, None)
WFF = "working_for_families"


def _population(extra: tuple[Any, ...] = ()) -> Any:
    households = []
    for i in range(len(GOLDEN_YAML)):
        facts = _facts(i)
        households.append(
            _household(
                household_id=f"g{i}",
                weight=Decimal(i + 1),
                facts=facts,
                persons=_persons_for(facts),
                characteristics=KNOWN,
            )
        )
    return _dataset(*households, *extra)


def _reform(*overrides: tuple[str, str, str, str], reform_id: str = "test") -> Reform:
    return Reform(
        reform_id=reform_id,
        overrides=tuple(
            Override(policy_id=p, parameter_id=k, operation=op, value=Decimal(v))
            for p, k, op, v in overrides
        ),
    )


IDENTITY = _reform((WFF, "family_tax_credit_abatement_threshold", "add", "0"), reform_id="identity")
THRESHOLD = _reform(
    (WFF, "family_tax_credit_abatement_threshold", "set", "50000"), reform_id="threshold"
)


@pytest.fixture(scope="module")
def threshold_run() -> PopulationRun:
    return run_population(_population(), THRESHOLD, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)


def test_every_household_runs_every_component(threshold_run: PopulationRun) -> None:
    assert len(threshold_run.households) == len(GOLDEN_YAML)
    assert all(set(h.components) == set(COMPONENTS) for h in threshold_run.households)
    assert threshold_run.synthetic and threshold_run.label
    assert set(UNITS) == set(COMPONENTS)


def test_identity_reform_has_zero_deltas() -> None:
    run = run_population(_population(), IDENTITY, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    for h in run.households:
        for c in h.components.values():
            assert c.baseline == c.reform
            if c.outcome == "calculated":
                assert c.delta == 0


def test_raising_the_threshold_never_lowers_family_tax_credit(threshold_run: PopulationRun) -> None:
    for h in threshold_run.households:
        ftc = h.components["family_tax_credit"]
        if ftc.outcome == "calculated":
            assert ftc.delta is not None and ftc.delta >= 0


def test_a_wff_reform_leaves_accommodation_supplement_unchanged(
    threshold_run: PopulationRun,
) -> None:
    # AS-10 and WFF DEC-003: WFF tax credits are not AS chargeable income.
    for h in threshold_run.households:
        a = h.components[AS_COMPONENT]
        assert a.baseline == a.reform
        assert a.outcome != "calculated" or a.delta == 0


def test_deltas_exist_only_when_both_runs_calculated(threshold_run: PopulationRun) -> None:
    for h in threshold_run.households:
        for c in h.components.values():
            both = c.baseline.outcome == "calculated" and c.reform.outcome == "calculated"
            assert (c.outcome == "calculated") == both
            assert (c.delta is not None) == both
            if not both:
                expected = (
                    "needs_review"
                    if "needs_review" in (c.baseline.outcome, c.reform.outcome)
                    else "unsupported"
                )
                assert c.outcome == expected


def test_reproducible_identity(threshold_run: PopulationRun) -> None:
    again = run_population(_population(), THRESHOLD, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    assert (again.run_id, again.results_sha256) == (
        threshold_run.run_id,
        threshold_run.results_sha256,
    )
    other = run_population(_population(), IDENTITY, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    assert other.run_id != threshold_run.run_id
    assert {p for p, _ in threshold_run.policy_artifacts} >= {
        "working_for_families/policy.yaml",
        "accommodation_supplement/policy.yaml",
    }


def test_invalid_households_are_not_run_and_review_households_are_flagged() -> None:
    bad = _facts(0)
    bad["household"]["wff"]["household_eligibility"] = "maybe"
    single = _facts(0)
    single["household"]["wff"]["partner_status"] = "single"
    contradictory_persons = (
        *_persons_for(single),
        PersonRecord(person_id="px", role=PersonRole.PARTNER),
    )
    population = _population(
        (
            _household(household_id="bad", facts=bad, characteristics=KNOWN),
            _household(
                household_id="review",
                facts=single,
                persons=contradictory_persons,
                characteristics=KNOWN,
            ),
        )
    )
    run = run_population(population, THRESHOLD, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    ids = {h.household_id for h in run.households}
    assert "bad" not in ids and "review" in ids
    review = next(h for h in run.households if h.household_id == "review")
    assert review.record_status is RecordStatus.NEEDS_REVIEW
    assert all(c.outcome == "needs_review" for c in review.components.values())


def test_unmodelled_policy_reform_is_refused_before_running() -> None:
    with pytest.raises(UnsupportedReformError):
        run_population(
            _population(),
            _reform(("childcare_subsidy", "rate", "set", "1")),
            WFF_POLICY_DIR,
            AS_POLICY_DIR,
            code=CODE,
        )


def test_wff_components_and_as_have_separate_units() -> None:
    assert {UNITS[c] for c in WFF_COMPONENTS} == {"NZD per tax year"}
    assert UNITS[AS_COMPONENT] == "NZD per week"


def test_threshold_gain_is_bounded_by_the_policy_values(threshold_run: PopulationRun) -> None:
    """No family tax credit gain exceeds (new threshold - old threshold) x
    abatement rate, both read from policy.yaml. At least one household
    gains, so the invariant tests above are not vacuous."""
    record = record_from_yaml(GOLDEN_YAML[0])
    params = load_policy_parameters(
        WFF_POLICY_DIR,
        record.wff_lookup_date,
        requested_policy_version=record.requested_wff_policy_version,
    )
    threshold = params.get("family_tax_credit_abatement_threshold").value
    rate = params.get("family_tax_credit_abatement_rate").value
    assert threshold is not None and rate is not None
    bound = (Decimal(50000) - threshold) * rate
    gains = [
        h.components["family_tax_credit"].delta
        for h in threshold_run.households
        if h.components["family_tax_credit"].outcome == "calculated"
    ]
    assert all(g is not None and g <= bound for g in gains)
    assert any(g is not None and g > 0 for g in gains)
