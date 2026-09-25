"""Task 23: `calculate_accommodation_supplement()` against the accepted
Task 22 scoped calculation contract in `policy_specs/accommodation_supplement/
specification.md`. Expected values are hand-derived independently from that
contract's formulas (Schedule 4 Part 7 cl 1-3 area caps, r 18(2)'s DEC-001
unrounded income-excess reduction, s 423(3)'s complete-$100 asset
imputation, r 19's final round-up), not copied from an implementation.

Runs through Task 11's real loader throughout, but against two fixtures:
`parameters` is a synthetic policy.yaml carrying the real approved AS rates
(the 20 values Task 22 independently verified) plus test-only, clearly
non-authoritative `as_entry_threshold_*`/`as_income_level_non_beneficiary_*`
values (Task 26a repair, DEC-002) that isolate the calculated-outcome
arithmetic from the published values. The real policy.yaml declares the
published values for the supported rows only (Task 26a.2); `real_as_parameters`
is the actual approved `policy_specs/accommodation_supplement/policy.yaml`,
used to prove that an undeclared row's parameter propagates as
`needs_review`, not a crash and not a guessed number.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.wff import FactStatus
from poltika.policy.loader import load_policy_parameters
from tests.conftest import real_as_parameters_without

AS_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "accommodation_supplement"
MODELLED_DATE = date(2026, 6, 1)


@pytest.fixture()
def real_as_parameters():
    """The real, approved AS policy.yaml -- used to prove that an
    undeclared row's entry threshold or r 18(3) income level reaches the
    calculator as `needs_review`, never a crash and never a guessed
    number (see `calculate_accommodation_supplement._param_value`'s
    docstring for why an undeclared parameter is the normal v0.1 state
    here, unlike WFF's PR #21 bug)."""
    return load_policy_parameters(AS_POLICY_DIR, MODELLED_DATE)


def _param(param_id: str, value_type: str, unit: str, value: str) -> dict[str, Any]:
    return {
        "id": param_id,
        "value_type": value_type,
        "unit": unit,
        "values": [
            {
                "effective_from": "2026-03-02",
                "effective_to": "2027-04-01",
                "value": value,
                "source_id": "test-source",
                "locator": "s 1",
                "review_status": "approved",
            }
        ],
    }


_RATE_HOUSEHOLDS = (
    "single_no_dependent_children",
    "sole_parent",
    "couple_no_dependent_children",
    "couple_with_dependent_children",
)


@pytest.fixture()
def parameters(tmp_path: Path):
    """The real 20 Task-22-verified AS values, plus test-only
    `as_entry_threshold_*`/`as_income_level_non_beneficiary_*` figures that do NOT exist in the
    real policy.yaml -- these are not statutory values, just round numbers
    for exercising the arithmetic (documented inline, never to be confused
    with a real MSD-sourced rate)."""
    policy_dir = tmp_path / "policy"
    policy_dir.mkdir()
    policy = {
        "schema_version": "0.1",
        "policy_id": "accommodation_supplement",
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": "2026-03-02", "to": "2027-04-01"},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            _param("area_cap_with_dependent_children_area1", "money", "NZD_per_week", "305"),
            _param("area_cap_with_dependent_children_area2", "money", "NZD_per_week", "220"),
            _param("area_cap_with_dependent_children_area3", "money", "NZD_per_week", "160"),
            _param("area_cap_with_dependent_children_area4", "money", "NZD_per_week", "120"),
            _param(
                "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area1",
                "money",
                "NZD_per_week",
                "235",
            ),
            _param(
                "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area2",
                "money",
                "NZD_per_week",
                "155",
            ),
            _param(
                "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area3",
                "money",
                "NZD_per_week",
                "105",
            ),
            _param(
                "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area4",
                "money",
                "NZD_per_week",
                "80",
            ),
            _param("area_cap_single_no_dependent_children_area1", "money", "NZD_per_week", "165"),
            _param("area_cap_single_no_dependent_children_area2", "money", "NZD_per_week", "105"),
            _param("area_cap_single_no_dependent_children_area3", "money", "NZD_per_week", "80"),
            _param("area_cap_single_no_dependent_children_area4", "money", "NZD_per_week", "70"),
            _param("rent_board_subsidy_rate", "fraction", "fraction", "0.7"),
            _param("entry_threshold_rent_board_fraction", "fraction", "fraction", "0.25"),
            _param("asset_ceiling_relationship_or_dependent_children", "money", "NZD", "16200"),
            _param("asset_ceiling_other", "money", "NZD", "8100"),
            _param(
                "asset_imputation_threshold_relationship_or_dependent_children",
                "money",
                "NZD",
                "5400",
            ),
            _param("asset_imputation_threshold_other", "money", "NZD", "2700"),
            _param("asset_imputation_step_size", "money", "NZD", "100"),
            _param("asset_imputation_amount_per_step", "money", "NZD_per_week", "1"),
            _param("income_reduction_rate", "fraction", "fraction", "0.25"),
            # Test-only figures, NOT statutory values -- see module docstring.
            # Task 26a repair: the entry threshold is keyed by claimant
            # category and the published-table rate household. Every
            # combination is declared at $75 -- the same threshold these
            # tests previously reached as 25% of an assumed $300 base -- so
            # every hand calculation below is unchanged.
            *(
                _param(f"as_entry_threshold_{claimant_category}_{rate_household}", "money", "NZD_per_week", "75")
                for claimant_category in (
                    "jobseeker_support",
                    "sole_parent_support",
                    "supported_living_payment",
                    "non_beneficiary",
                )
                for rate_household in _RATE_HOUSEHOLDS
            ),
            *(
                _param(f"as_income_level_non_beneficiary_{rate_household}", "money", "NZD_per_week", "200")
                for rate_household in _RATE_HOUSEHOLDS
            ),
        ],
        "components": [],
        "outputs": {},
    }
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    return load_policy_parameters(policy_dir, MODELLED_DATE)


def _ordinary_scenario(**overrides: object) -> AsScenario:
    base: dict[str, object] = {
        "household_eligibility": FactStatus.VERIFIED,
        "claimant_category": ClaimantCategory.JOBSEEKER_SUPPORT,
        "tenure_type": TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
        "partner_status": PartnerType.SINGLE,
        "statistical_area_unit": Area.AREA_1,
        "weekly_accommodation_costs": Decimal(200),
        "dependent_children_count": 0,
        "cash_assets": Decimal(1000),
        "exempt_cash_asset_status": FactStatus.VERIFIED,
        "ordinary_rate_status": FactStatus.VERIFIED,
        "eldest_dependent_child_under_16": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return AsScenario(**base)  # type: ignore[arg-type]


def test_ordinary_jobseeker_case_no_income_test(parameters) -> None:
    """Single, no dependent children, Jobseeker Support, Area 1: entry
    threshold (test assumption) = 75; excess = 200 - 75 = 125; cost-based =
    min(0.7 * 125, 165) = 87.5; Jobseeker Support has no AS income test
    (AS-08), so pre-rounding = 87.5; rounded up (r 19) = 88."""
    result = calculate_accommodation_supplement(_ordinary_scenario(), parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(88)


def test_non_beneficiary_income_reduction_unrounded_excess(parameters) -> None:
    """Same household, but non-beneficiary with weekly_income=250 and
    cash_assets=3000. Imputation threshold (single, no children) = 2700;
    asset excess = 300 -> 3 complete $100 steps -> $3/week imputed.
    total_income = 253; income_level (test fixture) = 200; excess = 53,
    NOT floored (DEC-001); reduction = 0.25 * 53 = 13.25; cost-based
    (unchanged from the ordinary case) = 87.5; pre-rounding =
    87.5 - 13.25 = 74.25; rounded up = 75."""
    scenario = _ordinary_scenario(
        claimant_category=ClaimantCategory.NON_BENEFICIARY,
        weekly_income=Decimal(250),
        cash_assets=Decimal(3000),
    )

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(75)


def test_income_reduction_exceeding_cost_based_amount_floors_to_zero(parameters) -> None:
    """Self-review probe: a very high weekly_income must floor the result
    at zero, not go negative. weekly_accommodation_costs=100 -> excess=25
    -> cost-based=min(0.7*25,165)=17.5; weekly_income=1000,
    cash_assets=1000 (below the 2700 imputation threshold, so no imputed
    income) -> income_excess=1000-200=800 -> reduction=0.25*800=200;
    pre-rounding=max(0,17.5-200)=0 -> final=0, not a negative amount."""
    scenario = _ordinary_scenario(
        claimant_category=ClaimantCategory.NON_BENEFICIARY,
        weekly_accommodation_costs=Decimal(100),
        weekly_income=Decimal(1000),
        cash_assets=Decimal(1000),
    )

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(0)


def test_cost_based_amount_at_entry_threshold_is_a_genuine_zero(parameters) -> None:
    """weekly_accommodation_costs exactly at the entry threshold (75) ->
    excess = 0 -> cost-based = 0, a genuine calculated zero (not
    unsupported), per specification.md's "at the exact entry threshold,
    the cost-based amount is zero"."""
    scenario = _ordinary_scenario(weekly_accommodation_costs=Decimal(75))

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(0)


def test_area_cap_binds_before_income_reduction(parameters) -> None:
    """A very high weekly_accommodation_costs is capped at the Area 1
    single-no-children maximum (165) before any income reduction --
    excess = 2000 - 75 = 1925; 0.7 * 1925 = 1347.5, capped to 165;
    Jobseeker Support has no income test, so final = ceil(165) = 165."""
    scenario = _ordinary_scenario(weekly_accommodation_costs=Decimal(2000))

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(165)


@pytest.mark.parametrize(
    ("overrides", "expected_reason_fragment"),
    [
        ({"household_eligibility": FactStatus.EXCLUDED}, "household_eligibility_facts verified outside"),
        (
            {"claimant_category": ClaimantCategory.PENSION_OR_VETERANS},
            "outside the v0.1 supported categories",
        ),
        ({"tenure_type": TenureType.HOMEOWNER}, "homeowner accommodation costs"),
        ({"partner_status": PartnerType.JOINT_TENANCY}, "needs its own specification"),
        ({"exempt_cash_asset_status": FactStatus.UNKNOWN}, "exempt cash asset"),
        ({"exempt_cash_asset_status": FactStatus.EXCLUDED}, "exempt cash asset"),
    ],
)
def test_unsupported_household_gate_triggers(
    parameters, overrides: dict[str, object], expected_reason_fragment: str
) -> None:
    scenario = _ordinary_scenario(**overrides)

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "unsupported"
    assert result.value is None
    assert expected_reason_fragment in (result.reason or "")


def test_asset_ceiling_exceeded_is_unsupported_not_zero(parameters) -> None:
    """cash_assets at/above the r 15 ceiling ($8,100 for a single claimant
    with no dependent children) fails the assets requirement (r 15) -- a
    genuine, evidenced exclusion, not a calculated zero."""
    scenario = _ordinary_scenario(cash_assets=Decimal(8100))

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "unsupported"
    assert result.value is None
    assert "assets requirement" in (result.reason or "")


@pytest.mark.parametrize(
    "overrides",
    [
        {"household_eligibility": FactStatus.UNKNOWN},
        {"claimant_category": None},
        {"tenure_type": None},
        {"partner_status": None},
        {"statistical_area_unit": None},
        {"weekly_accommodation_costs": None},
        {"dependent_children_count": None},
        {"cash_assets": None},
    ],
)
def test_unverified_facts_are_needs_review_not_a_silent_default(
    parameters, overrides: dict[str, object]
) -> None:
    scenario = _ordinary_scenario(**overrides)

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "needs_review"
    assert result.value is None


def test_non_beneficiary_missing_weekly_income_is_needs_review(parameters) -> None:
    scenario = _ordinary_scenario(claimant_category=ClaimantCategory.NON_BENEFICIARY)

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "needs_review"
    assert "weekly_income" in (result.reason or "")


def test_real_policy_undeclared_base_rate_is_needs_review_not_a_crash(real_as_parameters) -> None:
    """A policy that does not declare
    as_entry_threshold_jobseeker_support_single_no_dependent_children (the
    real policy with that id removed) -- this must resolve needs_review, not raise
    KeyError. `_ordinary_scenario()`'s default (single, no dependent
    children) maps to the `single_no_dependent_children` rate row."""
    # Task 26a.2 declares the real thresholds; remove the one exercised here.
    result = calculate_accommodation_supplement(
        _ordinary_scenario(),
        real_as_parameters_without("as_entry_threshold_jobseeker_support_single_no_dependent_children"),
    )

    assert result.outcome == "needs_review"
    assert result.value is None
    assert "as_entry_threshold_jobseeker_support_single_no_dependent_children" in (result.reason or "")
    assert "not yet declared" in (result.reason or "")
