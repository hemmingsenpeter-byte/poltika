"""Shared pytest fixtures and policy-case helpers.

Extracted here rather than copy-pasted a fourth time: `test_wff.py` (Task
12), `test_wff_spec_cases.py` (Task 13), and `test_wff_benchmarks.py`
(Task 14) each already define their own near-identical synthetic-fixture
builder and YAML-to-`WffScenario` conversion helpers. Those three files
are left untouched -- they're already reviewed and merged, and touching
them isn't what Task 15 is for -- but a fourth copy for
`tests/regression/` would cross from "three similar lines is fine" into
real, avoidable duplication. This module is pytest-root-level so any test
file under `tests/` can use its fixtures without an explicit import
(pytest's ordinary `conftest.py` discovery). The AS YAML helpers moved
here at their third consumer for Task 24.2, following the same rule.
"""

from __future__ import annotations

from dataclasses import replace
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
    _entry_threshold_parameter_id,
    _income_level_parameter_id,
    _rate_household,
)
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
)
from poltika.policy.loader import ParameterResolution, PolicyParameterSet, load_policy_parameters

WFF_POLICY_DIR = Path(__file__).resolve().parent.parent / "policy_specs" / "working_for_families"
WFF_MODELLED_DATE = date(2026, 6, 1)
AS_POLICY_DIR = Path(__file__).resolve().parent.parent / "policy_specs" / "accommodation_supplement"
AS_MODELLED_DATE = date(2026, 6, 1)
AS_POLICY_VERSION = "0.1.1"
AS_ALLOWED_PARAMETER_ASSUMPTIONS = {"entry_threshold", "income_level"}


def _param(param_id: str, value_type: str, unit: str, value: str) -> dict[str, Any]:
    return {
        "id": param_id,
        "value_type": value_type,
        "unit": unit,
        "values": [
            {
                "effective_from": "2026-04-01",
                "effective_to": "2027-04-01",
                "value": value,
                "source_id": "test-source",
                "locator": "s 1",
                "review_status": "approved",
            }
        ],
    }


@pytest.fixture(scope="session")
def real_wff_parameters() -> PolicyParameterSet:
    """The real, approved `policy_specs/working_for_families/policy.yaml`
    -- `in_work_base` carries its live `needs_review` status (Task 10.2's
    rate-status contract), so this is the fixture to use whenever that
    gate itself is part of what's being protected against regressing."""
    return load_policy_parameters(WFF_POLICY_DIR, WFF_MODELLED_DATE)


@pytest.fixture(scope="session")
def wff_synthetic_all_approved_parameters(
    tmp_path_factory: pytest.TempPathFactory,
) -> PolicyParameterSet:
    """Same statutory rates as the real approved WFF `policy.yaml`, but
    with every parameter -- including `in_work_base` -- approved. Same
    design `test_wff.py` (Task 12) and `test_wff_benchmarks.py` (Task 14)
    already established: isolates arithmetic/logic checks from the
    already-protected live rate-status gate (`spec_cases.yaml`, Task 13)."""
    policy_dir = tmp_path_factory.mktemp("wff_regression_fixture")
    policy = {
        "schema_version": "0.1",
        "policy_id": "regression_wff",
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": "2026-04-01", "to": "2027-04-01"},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            _param("family_tax_credit_eldest_child", "money", "NZD_per_tax_year", "7921"),
            _param("family_tax_credit_additional_child", "money", "NZD_per_tax_year", "6454"),
            _param("family_tax_credit_abatement_threshold", "money", "NZD_per_tax_year", "44900"),
            _param(
                "family_tax_credit_abatement_rate",
                "fraction",
                "NZD_per_complete_NZD_above_threshold",
                "0.275",
            ),
            _param("in_work_base", "money", "NZD_per_tax_year", "7670"),
            _param("in_work_additional_child", "money", "NZD_per_tax_year", "780"),
            _param(
                "minimum_family_prescribed_amount",
                "money",
                "NZD_per_tax_year_after_tax",
                "36604",
            ),
            _param("best_start_annual_amount", "money", "NZD_per_child_per_tax_year", "4041"),
            _param("best_start_abatement_threshold", "money", "NZD_per_tax_year", "79000"),
            _param(
                "best_start_abatement_rate",
                "fraction",
                "NZD_per_complete_NZD_above_threshold",
                "0.21",
            ),
        ],
        "components": [],
        "outputs": {},
    }
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    return load_policy_parameters(policy_dir, WFF_MODELLED_DATE)


def wff_income_from_yaml(raw: dict[str, Any] | None) -> VerifiedIncome | None:
    if raw is None:
        return None
    partner_amount = raw.get("partner_amount")
    return VerifiedIncome(
        claimant_amount=Decimal(raw["claimant_amount"]),
        partner_amount=Decimal(partner_amount) if partner_amount is not None else None,
    )


def wff_child_from_yaml(raw: dict[str, Any]) -> ChildFacts:
    return ChildFacts(
        qualifies_whole_year=FactStatus(raw["qualifies_whole_year"]),
        best_start_cohort=BestStartCohort(raw["best_start_cohort"]),
        best_start_no_disqualifying_payment=FactStatus(raw["best_start_no_disqualifying_payment"]),
    )


def wff_scenario_from_yaml(raw: dict[str, Any]) -> WffScenario:
    """Convert one `spec_cases.yaml`/`benchmarks.yaml` case's `scenario`
    block into a `WffScenario` -- the same conversion `test_wff_spec_cases.
    py` and `test_wff_benchmarks.py` each already do inline; shared here so
    `tests/regression/` can load a specific case by id without
    reimplementing it a third time."""
    net_income = raw.get("net_family_scheme_income")
    return WffScenario(
        household_eligibility=FactStatus(raw["household_eligibility"]),
        extra_instalment_status=FactStatus(raw["extra_instalment_status"]),
        children=[wff_child_from_yaml(c) for c in raw.get("children", [])],
        partner_status=PartnerStatus(raw["partner_status"]),
        family_scheme_income=wff_income_from_yaml(raw.get("family_scheme_income")),
        net_family_scheme_income=Decimal(net_income) if net_income is not None else None,
        net_family_scheme_income_me3_attested=raw.get(
            "net_family_scheme_income_me3_attested", False
        ),
        in_work_eligibility=FactStatus(raw["in_work_eligibility"]),
        ftc_iwtc_protected_or_direct_abatement=FactStatus(
            raw["ftc_iwtc_protected_or_direct_abatement"]
        ),
        mc6a_veterans_payment=FactStatus(raw["mc6a_veterans_payment"]),
        mc6b_disqualifying_payment=FactStatus(raw["mc6b_disqualifying_payment"]),
        minimum_family_full_time_earner_weeks=FactStatus(
            raw["minimum_family_full_time_earner_weeks"]
        ),
        best_start_no_shared_care=FactStatus(raw["best_start_no_shared_care"]),
        best_start_protected_credit=FactStatus(raw["best_start_protected_credit"]),
    )


def load_wff_spec_case(case_id: str) -> dict[str, Any]:
    """Load one named case from `spec_cases.yaml` by id (Task 13)."""
    raw = yaml.safe_load((WFF_POLICY_DIR / "spec_cases.yaml").read_text())
    cases: list[dict[str, Any]] = raw["spec_cases"]
    for case in cases:
        if case["id"] == case_id:
            return case
    raise KeyError(f"no spec_cases.yaml case with id {case_id!r}")


def load_wff_benchmark_case(case_id: str) -> dict[str, Any]:
    """Load one named case from `benchmarks.yaml` by id (Task 14)."""
    raw = yaml.safe_load((WFF_POLICY_DIR / "benchmarks.yaml").read_text())
    cases: list[dict[str, Any]] = raw["benchmarks"]
    for case in cases:
        if case["id"] == case_id:
            return case
    raise KeyError(f"no benchmarks.yaml case with id {case_id!r}")


def load_as_cases(path: Path, key: str) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text())
    cases: list[dict[str, Any]] = raw[key]
    return cases


def as_scenario_from_yaml(raw: dict[str, Any]) -> AsScenario:
    def optional_decimal(key: str) -> Decimal | None:
        value = raw.get(key)
        return Decimal(value) if value is not None else None

    return AsScenario(
        household_eligibility=FactStatus(raw["household_eligibility"]),
        claimant_category=(
            ClaimantCategory(raw["claimant_category"]) if raw.get("claimant_category") else None
        ),
        tenure_type=TenureType(raw["tenure_type"]) if raw.get("tenure_type") else None,
        partner_status=(PartnerType(raw["partner_status"]) if raw.get("partner_status") else None),
        statistical_area_unit=(
            Area(raw["statistical_area_unit"]) if raw.get("statistical_area_unit") else None
        ),
        weekly_accommodation_costs=optional_decimal("weekly_accommodation_costs"),
        dependent_children_count=raw.get("dependent_children_count"),
        cash_assets=optional_decimal("cash_assets"),
        exempt_cash_asset_status=FactStatus(raw["exempt_cash_asset_status"]),
        weekly_income=optional_decimal("weekly_income"),
        # Absent means unverified, never a silent pass (Task 26a repair).
        ordinary_rate_status=FactStatus(raw.get("ordinary_rate_status", "unknown")),
        eldest_dependent_child_under_16=FactStatus(raw.get("eldest_dependent_child_under_16", "unknown")),
    )


def as_parameters_for_case(case: dict[str, Any]) -> PolicyParameterSet:
    """Load real AS parameters and add only a case's explicit test assumptions.

    Assumptions are keyed by the Task 26a repair's ids
    (`as_entry_threshold_<claimant>_<rate_household>`,
    `as_income_level_non_beneficiary_<rate_household>`), built from the
    case's own scenario facts. A missing fact fails loudly rather than
    guessing a household row.
    """
    base = load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE, requested_policy_version=AS_POLICY_VERSION)
    assumptions = case.get("parameter_assumptions", {})
    assert set(assumptions) <= AS_ALLOWED_PARAMETER_ASSUMPTIONS, (
        f"{case['id']}: unknown parameter assumption(s) "
        f"{set(assumptions) - AS_ALLOWED_PARAMETER_ASSUMPTIONS}"
    )
    resolutions = dict(base.resolutions)
    category = case["scenario"].get("claimant_category")
    if assumptions and category is not None:
        partner_status_raw = case["scenario"].get("partner_status")
        dependent_children_count = case["scenario"].get("dependent_children_count")
        assert partner_status_raw is not None and dependent_children_count is not None, (
            f"{case['id']}: a parameter assumption needs partner_status and "
            "dependent_children_count in the case's scenario to select the rate-household row"
        )
        rate_household = _rate_household(PartnerType(partner_status_raw), dependent_children_count)
        ids = {
            "entry_threshold": _entry_threshold_parameter_id(ClaimantCategory(category), rate_household),
            "income_level": _income_level_parameter_id(rate_household),
        }
        for key, value in assumptions.items():
            resolutions[ids[key]] = ParameterResolution(
                parameter_id=ids[key],
                outcome="resolved",
                value=Decimal(value),
                unit="NZD_per_week",
                source_id="test-case-assumption",
                locator=case["id"],
            )
    return replace(base, resolutions=resolutions)
