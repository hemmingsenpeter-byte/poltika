"""v0.2 Tasks 3.3-3.4: the synthetic population generator, on a toy spec.
Every share and band below is made up for the test; none describes New
Zealand (the real spec comes from Task 3.1's tables)."""

from __future__ import annotations

from decimal import Decimal as D
from typing import Any

import pytest
from pydantic import ValidationError

from poltika.scenarios.microsim.runner import run_population
from poltika.scenarios.microsim.synthetic import SyntheticSpec, generate
from poltika.scenarios.microsim.validation import RecordStatus, validate_population
from poltika.scenarios.population import HouseholdType, household_type
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import SYNTHETIC_LABEL
from tests.conftest import AS_POLICY_DIR, AS_POLICY_VERSION, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_runner import THRESHOLD

V = "verified"
TOY: dict[str, Any] = {
    "population_id": "toy_population",
    "version": 1,
    "seed": 7,
    "households": 400,
    "represents": "1000",
    "sources": ["toy: made up for tests"],
    "household_type": {
        "sole_parent": "0.25",
        "couple_with_children": "0.25",
        "single_without_children": "0.25",
        "couple_without_children": "0.25",
    },
    "children_count": {"1": "0.5", "2": "0.3", "3": "0.2"},
    "best_start_cohort": {"outside_best_start_entitlement": "1"},
    "gross_income": [
        {"from": 20000, "to": 60000, "share": "0.5"},
        {"from": 60000, "to": 120000, "share": "0.5"},
    ],
    "partner_income_share": "0.4",
    "weekly_income_divisor": "52",
    "tenure": {"rent_contributions_or_board": "0.7", "homeowner": "0.3"},
    "weekly_housing_cost": [{"from": 200, "to": 700, "share": "1"}],
    "as_area": {"area1": "0.25", "area2": "0.25", "area3": "0.25", "area4": "0.25"},
    "region": {"Toy North": "0.5", "Toy South": "0.5"},
    "claimant_category": {"non_beneficiary": "1"},
    "cash_assets": [{"from": 0, "to": 5000, "share": "1"}],
    "assumed": {
        "wff_household_eligibility": V,
        "extra_instalment_status": V,
        "in_work_eligibility": V,
        "ftc_iwtc_protected_or_direct_abatement": V,
        "mc6a_veterans_payment": V,
        "mc6b_disqualifying_payment": V,
        "minimum_family_full_time_earner_weeks": V,
        "best_start_no_shared_care": V,
        "best_start_protected_credit": V,
        "child_qualifies_whole_year": V,
        "child_best_start_no_disqualifying_payment": V,
        "as_household_eligibility": V,
        "exempt_cash_asset_status": V,
        "ordinary_rate_status": V,
        "eldest_dependent_child_under_16": V,
        "as_claimant_is_wff_claimant_or_partner": V,
    },
    "wff_lookup_date": "2026-06-01",
    "as_lookup_date": "2026-06-01",
    "assessment_week_start": "2026-06-01",
    "assessment_week_end": "2026-06-08",
    "requested_wff_policy_version": "0.1.0",
    "requested_as_policy_version": AS_POLICY_VERSION,
}


def _spec(**overrides: Any) -> SyntheticSpec:
    return SyntheticSpec.model_validate({**TOY, **overrides})


@pytest.fixture(scope="module")
def generated() -> Any:
    return generate(_spec())


def test_population_is_labelled_weighted_and_valid(generated: Any) -> None:
    population, _ = generated
    assert population.synthetic and population.label == SYNTHETIC_LABEL
    assert len(population.households) == 400
    assert sum(h.weight for h in population.households) == D(1000)
    statuses = {h.status for h in validate_population(population).households}
    assert statuses == {RecordStatus.VALID}


def test_same_spec_same_population_and_seed_matters(generated: Any) -> None:
    population, _ = generated
    assert generate(_spec())[0].content_sha256() == population.content_sha256()
    assert generate(_spec(seed=8))[0].content_sha256() != population.content_sha256()


def test_generator_rules_hold_for_every_household(generated: Any) -> None:
    population, _ = generated
    for h in population.households:
        wff = h.facts["household"]["wff"]
        as_ = h.facts["household"]["accommodation_supplement"]
        gross = h.characteristics.gross_household_income
        income = wff["family_scheme_income"]
        partner = D(income["partner_amount"]) if income["partner_amount"] is not None else D(0)
        assert D(income["claimant_amount"]) + partner == gross
        assert D(as_["weekly_income"]) == (gross / 52).quantize(D("0.01"))
        assert wff["net_family_scheme_income"] is None
        kind = household_type(h)
        couple = kind in (HouseholdType.COUPLE_WITH_CHILDREN, HouseholdType.COUPLE_WITHOUT_CHILDREN)
        assert (wff["partner_status"] == "partnered") == couple
        assert len(wff["children"]) == as_["dependent_children_count"]
        assert (len(wff["children"]) > 0) == (
            kind in (HouseholdType.SOLE_PARENT, HouseholdType.COUPLE_WITH_CHILDREN)
        )


def test_calibration_report_tracks_the_targets(generated: Any) -> None:
    _, calibration = generated
    rows = {(r.dimension, r.key): r for r in calibration}
    assert rows[("household_type", "sole_parent")].target == D("0.25")
    # 400 draws: each generated share within 0.1 of its target
    assert all(abs(r.generated - r.target) < D("0.1") for r in calibration)
    for dimension in {r.dimension for r in calibration}:
        assert sum(r.generated for r in calibration if r.dimension == dimension) == 1


def test_generated_population_runs(generated: Any) -> None:
    population, _ = generated
    run = run_population(
        population,
        THRESHOLD,
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("t", None, None, None),
    )
    assert len(run.households) == 400
    assert any(h.components["family_tax_credit"].outcome == "calculated" for h in run.households)


@pytest.mark.parametrize(
    "overrides",
    [
        {"household_type": {"sole_parent": "0.5"}},
        {"household_type": {"sole_parent": "0.5", "unclassified": "0.5"}},
        {"tenure": {"castle": "1"}},
        {"children_count": {"0": "1"}},
        {"gross_income": [{"from": 10, "to": 10, "share": "1"}]},
        {"gross_income": [{"from": 0, "to": 10, "share": "0.5"}]},
        {"sources": []},
        {"partner_income_share": "1.5"},
    ],
)
def test_invalid_specs_are_rejected(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _spec(**overrides)


def test_every_assumed_fact_is_required() -> None:
    assumed = dict(TOY["assumed"])
    assumed.pop("in_work_eligibility")
    with pytest.raises(ValidationError):
        _spec(assumed=assumed)


def test_cli_writes_a_loadable_population(tmp_path: Any, capsys: Any) -> None:
    import json

    import yaml

    from poltika.scenarios.microsim.synthetic import main
    from poltika.semantics.population import PopulationDataset

    spec_path, out = tmp_path / "spec.yaml", tmp_path / "population.json"
    spec_path.write_text(yaml.safe_dump({**TOY, "households": 20}))
    assert main([str(spec_path), str(out)]) == 0
    loaded = PopulationDataset.model_validate(json.loads(out.read_text()))
    assert loaded.content_sha256() == generate(_spec(households=20))[0].content_sha256()
    printed = capsys.readouterr().out
    assert (
        SYNTHETIC_LABEL in printed and "calibration" not in printed.lower() or "target" in printed
    )
    assert main([]) == 2


@pytest.mark.parametrize(("represents", "households"), [("1000", 300), ("1", 3), ("1234567.89", 7)])
def test_weights_sum_exactly_and_are_nearly_equal(represents: str, households: int) -> None:
    population, _ = generate(_spec(households=households, represents=represents))
    weights = [h.weight for h in population.households]
    assert sum(weights) == D(represents)
    assert max(weights) - min(weights) <= D("0.000001")


def test_sub_millionth_population_weight_is_rejected() -> None:
    with pytest.raises(ValueError, match="decimal places"):
        generate(_spec(households=3, represents="1.0000001"))


def test_calibration_uses_the_actual_rounded_weights() -> None:
    population, calibration = generate(_spec(seed=0, households=3, represents="0.000004"))
    for row in calibration:
        if row.dimension == "region":
            weight = sum((h.weight for h in population.households
                          if h.characteristics.region == row.key), D(0))
            assert row.generated == weight / D("0.000004")
