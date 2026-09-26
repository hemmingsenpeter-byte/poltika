"""v0.2 Tasks 8.6-8.7: withdrawal paths and sweeps. Rates are checked against
the rates in policy.yaml, never restated."""

from __future__ import annotations

from decimal import Decimal as D

import pytest

from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.microsim.analysis import fiscal
from poltika.scenarios.microsim.withdrawal import sweep, withdrawal_path
from poltika.scenarios.record import CodeIdentity, ScenarioRecord
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_population import GOLDEN
from tests.unit.scenarios.test_scenario_record import record_from_yaml


def _rate(policy_dir: object, record: ScenarioRecord, parameter: str, wff: bool) -> D:
    params = load_policy_parameters(
        WFF_POLICY_DIR if wff else AS_POLICY_DIR,
        record.wff_lookup_date if wff else record.as_lookup_date,
        requested_policy_version=record.requested_wff_policy_version
        if wff
        else record.requested_as_policy_version,
    )
    value = params.get(parameter).value
    assert value is not None
    return value


def test_ftc_withdrawal_above_the_threshold_is_the_policy_abatement_rate() -> None:
    record = record_from_yaml(GOLDEN[1])
    rate = _rate(WFF_POLICY_DIR, record, "family_tax_credit_abatement_rate", wff=True)
    threshold = _rate(WFF_POLICY_DIR, record, "family_tax_credit_abatement_threshold", wff=True)
    assert record.household.wff.family_scheme_income is not None
    partner = record.household.wff.family_scheme_income.partner_amount or D(0)
    start = threshold - partner + 1000  # combined income above the threshold
    path = withdrawal_path(
        record,
        "working_for_families",
        [start, start + 5000, start + 10000],
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
    )
    assert path.unit == "NZD per tax year"
    for step in path.steps:
        assert step.rates["family_tax_credit"] == rate
    # net family scheme income can't follow the path, so MFTC is not calculated
    assert all(p.values["minimum_family_tax_credit"] is None for p in path.points)


def test_as_withdrawal_never_exceeds_the_reduction_rate_plus_rounding() -> None:
    record = record_from_yaml(GOLDEN[0])
    rate = _rate(AS_POLICY_DIR, record, "income_reduction_rate", wff=False)
    incomes = [D(v) for v in range(0, 2001, 100)]
    path = withdrawal_path(
        record, "accommodation_supplement", incomes, WFF_POLICY_DIR, AS_POLICY_DIR
    )
    assert path.unit == "NZD per week"
    rates = [s.rates["accommodation_supplement"] for s in path.steps]
    calculated = [r for r in rates if r is not None]
    assert calculated, "the path should cross calculated points"
    # AS rounds the final amount up to a whole dollar (AS-07): each step can
    # differ from the rate by at most $1 over its $100 width.
    assert all(D(0) <= r <= rate + D("0.01") for r in calculated)
    assert any(r > 0 for r in calculated)


def test_path_needs_two_distinct_non_negative_incomes() -> None:
    record = record_from_yaml(GOLDEN[0])
    with pytest.raises(ValueError):
        withdrawal_path(
            record, "accommodation_supplement", [D(1), D(1)], WFF_POLICY_DIR, AS_POLICY_DIR
        )
    with pytest.raises(ValueError):
        withdrawal_path(
            record, "accommodation_supplement", [D(-1), D(1)], WFF_POLICY_DIR, AS_POLICY_DIR
        )


def test_sweep_is_monotone_in_the_threshold() -> None:
    from tests.unit.scenarios.microsim.test_runner import _population

    runs = sweep(
        _population(),
        "working_for_families",
        "family_tax_credit_abatement_threshold",
        [D(46000), D(48000), D(50000)],
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("t", None, None, None),
    )
    assert len({run.run_id for _, run in runs}) == 3
    deltas = [fiscal(run)["family_tax_credit"].delta_total for _, run in runs]
    assert deltas == sorted(deltas) and deltas[-1] > 0
