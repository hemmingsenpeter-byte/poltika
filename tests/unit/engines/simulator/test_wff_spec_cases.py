"""Task 13: spec tests.

Per doctrine/test-doctrine.md's "Spec tests for the declared policy
specification" class and ADR-0005's design ("hand-calculated spec-test
expected values, loaded by Task 13 tests rather than hardcoded"): this file
is a thin loader/runner over
`policy_specs/working_for_families/spec_cases.yaml`, not a place to author
new expected values in Python. The values themselves, and their by-hand
derivation, live in that YAML file, which is one of
`.github/workflows/statutory-value-guard.yml`'s protected paths.

Not under a separate `tests/spec/` directory: REPOSITORY_STRUCTURE.md's
target `tests/` tree lists `unit`, `integration`, `regression`, `fixtures`
only, no `spec` entry, and CLAUDE.md says a proposed component with no
obvious location means updating that file deliberately, not creating an
ad-hoc directory. This is functionally a pytest unit test (it loads a
fixture and asserts pure-function output), so it lives alongside
`test_wff.py` rather than expanding the architecture unilaterally.

Every case runs against the real, approved
`policy_specs/working_for_families/policy.yaml` (see that YAML file's own
docstring for why `in_work_tax_credit` is `needs_review` in most cases --
a live legal fact about the real spec, not a test gap).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    calculate_wff,
)
from poltika.policy.loader import load_policy_parameters

WFF_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "working_for_families"
SPEC_CASES_PATH = WFF_POLICY_DIR / "spec_cases.yaml"


def _load_spec_cases() -> list[dict[str, Any]]:
    raw = yaml.safe_load(SPEC_CASES_PATH.read_text())
    cases: list[dict[str, Any]] = raw["spec_cases"]
    return cases


def _income_from_yaml(raw: dict[str, Any] | None) -> VerifiedIncome | None:
    if raw is None:
        return None
    partner_amount = raw.get("partner_amount")
    return VerifiedIncome(
        claimant_amount=Decimal(raw["claimant_amount"]),
        partner_amount=Decimal(partner_amount) if partner_amount is not None else None,
    )


def _child_from_yaml(raw: dict[str, Any]) -> ChildFacts:
    return ChildFacts(
        qualifies_whole_year=FactStatus(raw["qualifies_whole_year"]),
        best_start_cohort=BestStartCohort(raw["best_start_cohort"]),
        best_start_no_disqualifying_payment=FactStatus(raw["best_start_no_disqualifying_payment"]),
    )


def _scenario_from_yaml(raw: dict[str, Any]) -> WffScenario:
    net_income = raw.get("net_family_scheme_income")
    return WffScenario(
        household_eligibility=FactStatus(raw["household_eligibility"]),
        extra_instalment_status=FactStatus(raw["extra_instalment_status"]),
        children=[_child_from_yaml(c) for c in raw.get("children", [])],
        partner_status=PartnerStatus(raw["partner_status"]),
        family_scheme_income=_income_from_yaml(raw.get("family_scheme_income")),
        net_family_scheme_income=Decimal(net_income) if net_income is not None else None,
        net_family_scheme_income_me3_attested=raw.get("net_family_scheme_income_me3_attested", False),
        in_work_eligibility=FactStatus(raw["in_work_eligibility"]),
        ftc_iwtc_protected_or_direct_abatement=FactStatus(raw["ftc_iwtc_protected_or_direct_abatement"]),
        mc6a_veterans_payment=FactStatus(raw["mc6a_veterans_payment"]),
        mc6b_disqualifying_payment=FactStatus(raw["mc6b_disqualifying_payment"]),
        minimum_family_full_time_earner_weeks=FactStatus(raw["minimum_family_full_time_earner_weeks"]),
        best_start_no_shared_care=FactStatus(raw["best_start_no_shared_care"]),
        best_start_protected_credit=FactStatus(raw["best_start_protected_credit"]),
    )


_CASES = _load_spec_cases()
_CASE_IDS = [case["id"] for case in _CASES]


def test_spec_cases_file_is_non_empty() -> None:
    """A guard against an accidental empty/reverted spec_cases.yaml silently
    passing an empty parametrised suite -- pytest reports 0 cases run as
    green, which would hide a real regression."""
    assert len(_CASES) >= 20


def test_spec_case_ids_are_unique() -> None:
    assert len(_CASE_IDS) == len(set(_CASE_IDS)), "duplicate spec_cases.yaml id"


@pytest.mark.parametrize("case", _CASES, ids=_CASE_IDS)
def test_wff_spec_case(case: dict[str, Any]) -> None:
    # PyYAML parses an unquoted ISO date as datetime.date already; this
    # only matters if a future case author quotes it as a plain string.
    modelled_date = case["modelled_date"]
    if isinstance(modelled_date, str):
        modelled_date = date.fromisoformat(modelled_date)

    parameters = load_policy_parameters(
        WFF_POLICY_DIR, modelled_date, requested_policy_version=case["policy_version"]
    )
    scenario = _scenario_from_yaml(case["scenario"])

    result = calculate_wff(scenario, parameters)

    component_results = {
        "family_tax_credit": result.family_tax_credit,
        "in_work_tax_credit": result.in_work_tax_credit,
        "minimum_family_tax_credit": result.minimum_family_tax_credit,
        "best_start": result.best_start,
    }

    # A case whose `expected` block omits a component previously passed
    # silently -- the loop below only ever checked the keys present, so a
    # missing or misspelled component id was never actually asserted on.
    # Every case must cover all four components explicitly, even when a
    # component isn't the point of that case, so nothing goes unchecked.
    assert set(case["expected"].keys()) == set(component_results.keys()), (
        f"{case['id']}: expected block must cover exactly "
        f"{sorted(component_results.keys())}, got {sorted(case['expected'].keys())}"
    )

    for component_id, expected in case["expected"].items():
        actual = component_results[component_id]
        assert actual.outcome == expected["outcome"], (
            f"{case['id']}.{component_id}: expected outcome "
            f"'{expected['outcome']}', got '{actual.outcome}' (reason: {actual.reason})"
        )
        if expected["outcome"] == "calculated":
            assert actual.value == Decimal(expected["value"]), (
                f"{case['id']}.{component_id}: expected value "
                f"{expected['value']}, got {actual.value}"
            )
        else:
            assert actual.value is None, f"{case['id']}.{component_id}: expected no value, got {actual.value}"
