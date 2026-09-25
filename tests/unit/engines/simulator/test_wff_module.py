"""Task 20: the WFF module's integration entry point, `run_wff_module()`.

These are the three blocking acceptance tests `BUILD_PLAN.md`'s Task 20
entry requires before the Task 17 ARCHITECTURE_ISSUE finding (full-year
rate binding) can be considered resolved, plus a smoke test proving the
integration wrapper is behaviour-preserving for the ordinary case. Per
Pete's decision (22 September 2026, `BUILD_PLAN.md` Task 19): these checks
belong here, at the module integration boundary, not inside Task 11's
`loader.py` -- `tests/unit/policy/test_loader.py` already establishes that
the loader deliberately has no hardcoded assessment-period assumption, and
this file must not conflict with that.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.common.errors import ArtifactHashMismatchError, PolicyVersionMismatchError
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    calculate_wff,
    run_wff_module,
)
from poltika.policy.loader import load_policy_parameters
from tests.conftest import WFF_POLICY_DIR, load_wff_spec_case, wff_scenario_from_yaml

MODELLED_DATE = date(2026, 6, 1)


def _ordinary_scenario() -> WffScenario:
    return WffScenario(
        household_eligibility=FactStatus.VERIFIED,
        extra_instalment_status=FactStatus.VERIFIED,
        partner_status=PartnerStatus.SINGLE,
        children=[
            ChildFacts(
                qualifies_whole_year=FactStatus.VERIFIED,
                best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
                best_start_no_disqualifying_payment=FactStatus.VERIFIED,
            )
        ],
        family_scheme_income=VerifiedIncome(claimant_amount=Decimal(30000)),
        net_family_scheme_income=Decimal(30000),
        net_family_scheme_income_me3_attested=True,
        in_work_eligibility=FactStatus.VERIFIED,
        ftc_iwtc_protected_or_direct_abatement=FactStatus.VERIFIED,
        mc6a_veterans_payment=FactStatus.VERIFIED,
        mc6b_disqualifying_payment=FactStatus.VERIFIED,
        minimum_family_full_time_earner_weeks=FactStatus.VERIFIED,
        best_start_no_shared_care=FactStatus.VERIFIED,
        best_start_protected_credit=FactStatus.VERIFIED,
    )


# Mirrors wff.py's own _WFF_REQUIRED_PARAMETER_IDS -- every id
# calculate_wff() looks up. A synthetic fixture that omits one would trip
# the new missing-required-parameter invariant instead of isolating
# whichever invariant a given test actually targets, so every test fixture
# here declares the complete set.
_ALL_REQUIRED_PARAMETER_IDS = (
    "family_tax_credit_eldest_child",
    "family_tax_credit_additional_child",
    "family_tax_credit_abatement_threshold",
    "family_tax_credit_abatement_rate",
    "in_work_base",
    "in_work_additional_child",
    "minimum_family_prescribed_amount",
    "best_start_annual_amount",
    "best_start_abatement_threshold",
    "best_start_abatement_rate",
)


def _param(param_id: str, effective_from: str, effective_to: str | None) -> dict[str, Any]:
    return {
        "id": param_id,
        "value_type": "money",
        "unit": "NZD_per_tax_year",
        "values": [
            {
                "effective_from": effective_from,
                "effective_to": effective_to,
                "value": "100",
                "source_id": "test-source",
                "locator": "s 1",
                "review_status": "approved",
            }
        ],
    }


def _write_policy_dir(
    tmp_path: Path,
    *,
    policy_id: str = "working_for_families",
    reference_from: str = "2026-04-01",
    reference_to: str = "2027-04-01",
    param_effective_from: str = "2026-04-01",
    param_effective_to: str | None = "2027-04-01",
    parameter_ids: tuple[str, ...] = _ALL_REQUIRED_PARAMETER_IDS,
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
    under Task 11's loader alone (by design -- see
    `test_open_ended_final_interval_resolves`) for a date years outside the
    reviewed reference_period. `run_wff_module()` must catch that at the
    integration boundary."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to=None)

    result = run_wff_module(
        policy_dir, date(2030, 1, 1), _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.in_work_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.best_start.outcome == "needs_review"
    assert "reference_period" in (result.family_tax_credit.reason or "")


def test_mismatched_policy_id_is_needs_review(tmp_path: Path) -> None:
    """Invariant (2). A `policy_dir` resolving to a different policy_id
    (e.g. an accidental Accommodation Supplement directory) must not
    silently run WFF arithmetic against a foreign parameter set."""
    policy_dir = _write_policy_dir(tmp_path, policy_id="accommodation_supplement")

    result = run_wff_module(
        policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.best_start.outcome == "needs_review"
    assert "policy_id" in (result.family_tax_credit.reason or "")
    assert "accommodation_supplement" in (result.family_tax_credit.reason or "")


def test_missing_required_parameter_is_needs_review_not_keyerror(tmp_path: Path) -> None:
    """Historical issue: PR #21's review finding. A policy.yaml that omits
    one of calculate_wff()'s required parameter ids passed all three
    module-boundary invariants as originally implemented, then reached
    calculate_wff() and raised a bare KeyError partway through a
    component calculation -- reproduced directly against this file's own
    synthetic policy helper with only one parameter ('rate') declared.
    `run_wff_module()` must catch a policy that doesn't declare every
    parameter it will need before calling calculate_wff() at all."""
    policy_dir = _write_policy_dir(tmp_path, parameter_ids=("rate",))

    result = run_wff_module(
        policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.in_work_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.best_start.outcome == "needs_review"
    assert "does not declare required parameter" in (result.family_tax_credit.reason or "")


def test_parameter_interval_not_spanning_full_period_is_needs_review(tmp_path: Path) -> None:
    """Invariant (3). A parameter interval that covers `modelled_date` but
    ends before the reference period's own end must not be treated as a
    verified full-year rate -- the same gap PR #20 removed from the
    generic loader, now re-implemented at the module boundary instead
    (Task 19 decision, 22 September 2026)."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to="2027-01-01")

    result = run_wff_module(
        policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.best_start.outcome == "needs_review"
    assert "does not span the complete reference period" in (result.family_tax_credit.reason or "")


def test_parameter_interval_starting_after_reference_period_is_needs_review(tmp_path: Path) -> None:
    """Invariant (3), mirror direction -- a parameter interval starting
    after the reference period's own start, even though it still covers
    `modelled_date`."""
    policy_dir = _write_policy_dir(
        tmp_path, param_effective_from="2026-07-01", param_effective_to="2027-04-01"
    )

    result = run_wff_module(
        policy_dir, date(2026, 8, 1), _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert "does not span the complete reference period" in (result.minimum_family_tax_credit.reason or "")


def test_valid_full_year_case_matches_calculate_wff_directly() -> None:
    """When every module-boundary invariant holds, `run_wff_module()` must
    be behaviour-preserving: identical to calling `load_policy_parameters()`
    then `calculate_wff()` directly, against the real approved WFF policy
    and an existing spec case."""
    case = load_wff_spec_case("single_ordinary_low_income")
    scenario = wff_scenario_from_yaml(case["scenario"])
    modelled_date = case["modelled_date"]
    if isinstance(modelled_date, str):
        modelled_date = date.fromisoformat(modelled_date)

    direct_parameters = load_policy_parameters(
        WFF_POLICY_DIR, modelled_date, requested_policy_version=case["policy_version"]
    )
    expected = calculate_wff(scenario, direct_parameters)

    actual = run_wff_module(
        WFF_POLICY_DIR, modelled_date, scenario, requested_policy_version=case["policy_version"]
    )

    assert actual == expected


def test_requested_policy_version_mismatch_still_raises() -> None:
    """A schema-version/approval-status/policy_version mismatch is a
    caller-level structural error `load_policy_parameters()` already
    raises for (Task 11) -- `run_wff_module()` does not swallow or convert
    that into a needs_review result, it is unchanged, existing behaviour."""
    with pytest.raises(PolicyVersionMismatchError):
        run_wff_module(
            WFF_POLICY_DIR, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="9.9.9"
        )


def test_open_ended_parameter_value_is_needs_review(tmp_path: Path) -> None:
    """v0.1 question set QS-2: SCHEMA.md permits an open-ended final interval,
    but a calculation must not rely on one -- a legislative replacement that
    has not been loaded would otherwise be applied silently."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to=None)

    result = run_wff_module(
        policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0"
    )

    assert result.family_tax_credit.outcome == "needs_review"
    assert "has no effective_to" in (result.family_tax_credit.reason or "")


def test_policy_file_replaced_after_its_parameters_loaded_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The module's own checks must read the same policy.yaml the parameters
    (and every trace's hash) came from, not a file replaced in between."""
    import shutil

    import poltika.engines.simulator.wff as wff_module

    policy_dir = tmp_path / "working_for_families"
    shutil.copytree(WFF_POLICY_DIR, policy_dir)

    def load_then_replace(*args: Any, **kwargs: Any) -> Any:
        parameters = load_policy_parameters(*args, **kwargs)
        with (policy_dir / "policy.yaml").open("a") as f:
            f.write("\n# replaced after loading\n")
        return parameters

    monkeypatch.setattr(wff_module, "load_policy_parameters", load_then_replace)
    with pytest.raises(ArtifactHashMismatchError):
        run_wff_module(policy_dir, MODELLED_DATE, _ordinary_scenario(), requested_policy_version="0.1.0")
