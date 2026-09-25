"""Task 24.7: the AS module's integration entry point, `run_as_module()`.

Mirrors `test_wff_module.py`'s Task 20 scope, adapted for AS's
single-component result shape: the module-boundary invariants
`_as_module_validation_failure()` enforces (policy_id match, the assessment
week within the reference_period, the lookup date within the week, and every
declared parameter's value covering the whole week), plus a
behaviour-preservation smoke test and confirmation the pre-existing
policy_version-mismatch raise is untouched.

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
    AssessmentWeek,
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
        "policy_version": "0.1.2",
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


# A test week containing MODELLED_DATE -- not Task 28.2's selected week,
# which Pete has not chosen yet.
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))


def _run(policy_dir: Path, *, week: AssessmentWeek = WEEK, modelled_date: date = MODELLED_DATE) -> Any:
    return run_as_module(
        policy_dir, modelled_date, _ordinary_scenario(), requested_policy_version="0.1.2", assessment_week=week
    )


def _passes_module_validation(policy_dir: Path, week: AssessmentWeek, modelled_date: date = MODELLED_DATE) -> bool:
    """True when run_as_module() reaches the calculator: its result then
    equals calling the calculator directly on the same parameters."""
    direct = calculate_accommodation_supplement(
        _ordinary_scenario(), load_policy_parameters(policy_dir, modelled_date, requested_policy_version="0.1.2")
    )
    return bool(_run(policy_dir, week=week, modelled_date=modelled_date) == direct)


def test_week_outside_reference_period_is_needs_review(tmp_path: Path) -> None:
    """An open-ended parameter interval legitimately resolves under Task
    11's loader for a date years outside the reviewed reference_period --
    `run_as_module()` must catch that at the integration boundary."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to=None)

    result = _run(
        policy_dir, week=AssessmentWeek(start=date(2030, 1, 1), end=date(2030, 1, 8)), modelled_date=date(2030, 1, 1)
    )

    assert result.outcome == "needs_review"
    assert "reference_period" in (result.reason or "")


def test_week_straddling_the_reference_period_end_is_needs_review(tmp_path: Path) -> None:
    policy_dir = _write_policy_dir(tmp_path, param_effective_to=None)

    result = _run(
        policy_dir, week=AssessmentWeek(start=date(2027, 3, 29), end=date(2027, 4, 5)), modelled_date=date(2027, 3, 29)
    )

    assert result.outcome == "needs_review"
    assert "not wholly within" in (result.reason or "")


def test_mismatched_policy_id_is_needs_review(tmp_path: Path) -> None:
    """A `policy_dir` resolving to a different policy_id (e.g. an accidental
    WFF directory) must not silently run AS arithmetic against a foreign
    parameter set."""
    policy_dir = _write_policy_dir(tmp_path, policy_id="working_for_families")

    result = _run(policy_dir)

    assert result.outcome == "needs_review"
    assert "policy_id" in (result.reason or "")
    assert "working_for_families" in (result.reason or "")


def test_lookup_date_outside_the_week_is_needs_review(tmp_path: Path) -> None:
    policy_dir = _write_policy_dir(tmp_path)

    result = _run(policy_dir, modelled_date=date(2026, 6, 8))  # the week's exclusive end

    assert result.outcome == "needs_review"
    assert "outside the assessment week" in (result.reason or "")


def test_value_covering_the_week_but_not_the_whole_reference_period_is_usable(tmp_path: Path) -> None:
    """Replaces the Task 24.7 test that required each value to span the
    whole reference period. That rule was WFF's annual one, copied in error:
    AS is assessed per week (CODE_ERROR, Task 28.2 research, PR #41). A value
    that ends after the week but before the reference period ends is that
    week's rate."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to="2027-01-01")

    assert _passes_module_validation(policy_dir, WEEK)


def test_value_starting_after_the_reference_period_start_is_usable_for_a_later_week(tmp_path: Path) -> None:
    """Replaces the Task 24.7 mirror-direction test, which expected
    `needs_review` here. A value starting 1 July covers an August week."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_from="2026-07-01", param_effective_to="2027-04-01")

    assert _passes_module_validation(
        policy_dir, AssessmentWeek(start=date(2026, 8, 1), end=date(2026, 8, 8)), modelled_date=date(2026, 8, 1)
    )


@pytest.mark.parametrize(
    ("effective_from", "effective_to"),
    [
        ("2026-06-03", "2027-04-01"),  # starts inside the week
        ("2026-04-01", "2026-06-05"),  # ends inside the week
    ],
)
def test_value_changing_inside_the_week_is_needs_review(
    tmp_path: Path, effective_from: str, effective_to: str
) -> None:
    """A value covering only part of the week is not that week's rate, and
    the module must not silently pick one side of the change."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_from=effective_from, param_effective_to=effective_to)

    result = _run(policy_dir, modelled_date=date(2026, 6, 4))

    assert result.outcome == "needs_review"
    assert "changes inside the assessment week" in (result.reason or "")


@pytest.mark.parametrize(
    ("effective_from", "effective_to"),
    [
        ("2026-06-01", "2027-04-01"),  # starts exactly at the week's start
        ("2026-04-01", "2026-06-08"),  # ends exactly at the week's exclusive end
    ],
)
def test_value_meeting_the_week_boundary_exactly_is_usable(
    tmp_path: Path, effective_from: str, effective_to: str
) -> None:
    policy_dir = _write_policy_dir(tmp_path, param_effective_from=effective_from, param_effective_to=effective_to)

    assert _passes_module_validation(policy_dir, WEEK)


def test_assessment_week_must_be_seven_days() -> None:
    with pytest.raises(ValueError, match="exactly 7 days"):
        AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 9))


def test_valid_case_matches_calculate_accommodation_supplement_directly() -> None:
    """When every module-boundary invariant holds, `run_as_module()` must
    be behaviour-preserving: identical to calling `load_policy_parameters()`
    then `calculate_accommodation_supplement()` directly, against the real
    approved AS policy and its own scenario."""
    assert _passes_module_validation(AS_POLICY_DIR, WEEK)


def test_result_trace_records_the_assessment_week() -> None:
    result = _run(AS_POLICY_DIR)
    assert result.trace is not None
    assert result.trace.assessment_period == (WEEK.start, WEEK.end)


def test_requested_policy_version_mismatch_still_raises() -> None:
    """A schema-version/approval-status/policy_version mismatch is a
    caller-level structural error `load_policy_parameters()` already
    raises for (Task 11) -- `run_as_module()` does not swallow or convert
    that into a needs_review result, it is unchanged, existing behaviour."""
    with pytest.raises(PolicyVersionMismatchError):
        run_as_module(
            AS_POLICY_DIR,
            MODELLED_DATE,
            _ordinary_scenario(),
            requested_policy_version="9.9.9",
            assessment_week=WEEK,
        )


# --- Boundary coverage added after the fresh-context review of PR #43,
# which found these mutations survived: dropping or loosening the
# reference-period start check, flipping either reference edge to exclusive,
# checking only the lookup date's upper bound, and dropping the period from
# a validation-failure trace.


def test_week_straddling_the_reference_period_start_is_needs_review(tmp_path: Path) -> None:
    policy_dir = _write_policy_dir(
        tmp_path, reference_from="2026-03-02", param_effective_from="2026-01-01", param_effective_to=None
    )

    result = _run(
        policy_dir, week=AssessmentWeek(start=date(2026, 2, 27), end=date(2026, 3, 6)), modelled_date=date(2026, 3, 3)
    )

    assert result.outcome == "needs_review"
    assert "not wholly within" in (result.reason or "")


@pytest.mark.parametrize(
    ("week", "modelled_date"),
    [
        (AssessmentWeek(start=date(2026, 3, 2), end=date(2026, 3, 9)), date(2026, 3, 2)),  # starts on the period start
        (AssessmentWeek(start=date(2027, 3, 25), end=date(2027, 4, 1)), date(2027, 3, 25)),  # ends on the exclusive end
    ],
)
def test_weeks_meeting_the_reference_period_edges_exactly_are_accepted(
    tmp_path: Path, week: AssessmentWeek, modelled_date: date
) -> None:
    policy_dir = _write_policy_dir(
        tmp_path, reference_from="2026-03-02", param_effective_from="2026-03-02", param_effective_to="2027-04-01"
    )

    assert _passes_module_validation(policy_dir, week, modelled_date)


def test_lookup_date_before_the_week_is_needs_review(tmp_path: Path) -> None:
    policy_dir = _write_policy_dir(tmp_path)

    result = _run(policy_dir, modelled_date=date(2026, 5, 31))  # the day before WEEK starts

    assert result.outcome == "needs_review"
    assert "outside the assessment week" in (result.reason or "")


def test_validation_failure_trace_records_the_assessment_week(tmp_path: Path) -> None:
    policy_dir = _write_policy_dir(tmp_path, policy_id="working_for_families")

    result = _run(policy_dir)

    assert result.outcome == "needs_review"
    assert result.trace is not None
    assert result.trace.assessment_period == (WEEK.start, WEEK.end)


def test_open_ended_value_is_needs_review(tmp_path: Path) -> None:
    """v0.1 question set QS-2: an open-ended value cannot establish that it
    is still the law for the assessed week."""
    policy_dir = _write_policy_dir(tmp_path, param_effective_to=None)

    result = _run(policy_dir)

    assert result.outcome == "needs_review"
    assert "has no effective_to" in (result.reason or "")
