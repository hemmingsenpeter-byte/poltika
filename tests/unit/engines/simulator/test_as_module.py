"""Task 24.7: the AS module's integration entry point, `run_as_module()`.

Mirrors `test_wff_module.py`'s Task 20 scope, adapted for AS's
single-component result shape: the module-boundary invariants
`_as_module_validation_failure()` enforces (policy_id match, modelled_date
within the reference_period, and every declared parameter rate-covered for
the complete reference period), plus a behaviour-preservation smoke test
and confirmation the pre-existing policy_version-mismatch raise is
untouched.

Unlike WFF, there is no "missing required parameter" invariant test here --
`calculate_accommodation_supplement()`'s own `_param_value()` already
handles an undeclared parameter as `needs_review` one layer down (Task 23's
documented design), so `run_as_module()` deliberately does not duplicate
that check (see `_as_module_validation_failure()`'s own docstring).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.common.errors import PolicyVersionMismatchError
from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
    run_as_module,
)
from poltika.engines.simulator.wff import FactStatus
from poltika.policy.loader import load_policy_parameters

AS_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "accommodation_supplement"
MODELLED_DATE = date(2026, 6, 1)


def _ordinary_scenario() -> AsScenario:
    return AsScenario(
        household_eligibility=FactStatus.VERIFIED,
        claimant_category=ClaimantCategory.JOBSEEKER_SUPPORT,
        tenure_type=TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
        partner_status=PartnerType.SINGLE,
        statistical_area_unit=Area.AREA_1,
        weekly_accommodation_costs=Decimal(400),
        dependent_children_count=0,
        cash_assets=Decimal(500),
        exempt_cash_asset_status=FactStatus.VERIFIED,
    )


# Every parameter id the real, approved policy.yaml declares -- mirrors
# test_as_spec_cases.py's own `_INDEPENDENTLY_VERIFIED_PARAMETER_IDS`. A
# synthetic fixture used here only needs one declared parameter to exercise
# invariant (3); it does not need to match the real set, since (unlike
# WFF) there is no missing-required-parameter invariant to accidentally trip.
def _param(param_id: str, effective_from: str, effective_to: str | None) -> dict[str, Any]:
    return {
        "id": param_id,
        "value_type": "fraction",
        "unit": "fraction",
        "values": [
            {
                "effective_from": effective_from,
                "effective_to": effective_to,
                "value": "0.25",
                "source_id": "test-source",
                "locator": "test",
                "review_status": "approved",
            }
        ],
    }


def _write_policy_dir(
    tmp_path: Path,
    *,
    policy_id: str = "accommodation_supplement",
    reference_from: str = "2026-04-01",
    reference_to: str = "2027-04-01",
    param_effective_from: str = "2026-04-01",
    param_effective_to: str | None = "2027-04-01",
    parameter_ids: tuple[str, ...] = ("entry_threshold_rent_board_fraction",),
) -> Path:
    policy_dir = tmp_path / "policy"
    policy_dir.mkdir()
    policy = {
        "schema_version": "0.1",
        "policy_id": policy_id,
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": reference_from, "to": reference_to},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            _param(param_id, param_effective_from, param_effective_to) for param_id in parameter_ids
        ],
        "components": [],
        "outputs": {},
    }
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    return policy_dir


def test_modelled_date_outside_reference_period_is_needs_review(tmp_path: Path) -> None:
    """Invariant (1). An open-ended parameter interval legitimately resolves
    under Task 11's loader alone for a date years outside the reviewed
    reference_period -- `run_as_module()` must catch that at the
    integration boundary."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to=None)

    result = run_as_module(
        policy_dir, date(2030, 1, 1), _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.outcome == "needs_review"
    assert "reference_period" in (result.reason or "")


def test_mismatched_policy_id_is_needs_review(tmp_path: Path) -> None:
    """Invariant (2). A `policy_dir` resolving to a different policy_id
    (e.g. an accidental WFF directory) must not silently run AS arithmetic
    against a foreign parameter set."""
    policy_dir = _write_policy_dir(tmp_path, policy_id="working_for_families")

    result = run_as_module(
        policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.outcome == "needs_review"
    assert "policy_id" in (result.reason or "")
    assert "working_for_families" in (result.reason or "")


def test_parameter_interval_not_spanning_full_period_is_needs_review(tmp_path: Path) -> None:
    """Invariant (3). A parameter interval that covers `modelled_date` but
    ends before the reference period's own end must not be treated as a
    verified full-year rate."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to="2027-01-01")

    result = run_as_module(
        policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.outcome == "needs_review"
    assert "does not span the complete reference period" in (result.reason or "")


def test_parameter_interval_starting_after_reference_period_is_needs_review(tmp_path: Path) -> None:
    """Invariant (3), mirror direction -- a parameter interval starting
    after the reference period's own start, even though it still covers
    `modelled_date`."""
    policy_dir = _write_policy_dir(
        tmp_path, param_effective_from="2026-07-01", param_effective_to="2027-04-01"
    )

    result = run_as_module(
        policy_dir, date(2026, 8, 1), _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.outcome == "needs_review"
    assert "does not span the complete reference period" in (result.reason or "")


def test_valid_full_year_case_matches_calculate_accommodation_supplement_directly() -> None:
    """When every module-boundary invariant holds, `run_as_module()` must
    be behaviour-preserving: identical to calling `load_policy_parameters()`
    then `calculate_accommodation_supplement()` directly, against the real
    approved AS policy and its own scenario."""
    scenario = _ordinary_scenario()

    direct_parameters = load_policy_parameters(
        AS_POLICY_DIR, MODELLED_DATE, requested_policy_version="0.1.0"
    )
    expected = calculate_accommodation_supplement(scenario, direct_parameters)

    actual = run_as_module(
        AS_POLICY_DIR, MODELLED_DATE, scenario, requested_policy_version="0.1.0"
    )

    assert actual == expected


def test_requested_policy_version_mismatch_still_raises() -> None:
    """A schema-version/approval-status/policy_version mismatch is a
    caller-level structural error `load_policy_parameters()` already
    raises for (Task 11) -- `run_as_module()` does not swallow or convert
    that into a needs_review result, it is unchanged, existing behaviour."""
    with pytest.raises(PolicyVersionMismatchError):
        run_as_module(
            AS_POLICY_DIR, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="9.9.9"
        )
