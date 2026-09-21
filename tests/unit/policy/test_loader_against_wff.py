"""Task 11.4: exercise the loader against the real, approved WFF policy.yaml.

Confirms `in_work_base` reaches the calculator as `needs_review`, never a
silent $7,670 -- the specific behaviour BUILD_PLAN.md Task 11.4 requires --
and that every approved rate resolves to the exact value Task 10's review
confirmed against primary sources.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from poltika.policy.loader import load_policy_parameters

WFF_POLICY_DIR = Path(__file__).parents[3] / "policy_specs" / "working_for_families"
MODELLED_DATE = date(2026, 6, 1)  # inside the 2026-27 reference period


def test_wff_policy_loads_and_is_approved() -> None:
    result = load_policy_parameters(WFF_POLICY_DIR, MODELLED_DATE)

    assert result.policy_id == "working_for_families"
    assert result.policy_version == "0.1.0"


def test_in_work_base_is_needs_review_not_a_silent_value() -> None:
    result = load_policy_parameters(WFF_POLICY_DIR, MODELLED_DATE)

    resolution = result.get("in_work_base")
    assert resolution.outcome == "needs_review"
    assert resolution.value is None


def test_approved_rates_resolve_to_the_reviewed_values() -> None:
    result = load_policy_parameters(WFF_POLICY_DIR, MODELLED_DATE)

    expected = {
        "family_tax_credit_eldest_child": 7921,
        "family_tax_credit_additional_child": 6454,
        "family_tax_credit_abatement_threshold": 44900,
        "family_tax_credit_abatement_rate": 0.275,
        "in_work_additional_child": 780,
        "minimum_family_prescribed_amount": 36604,
        "best_start_annual_amount": 4041,
        "best_start_abatement_threshold": 79000,
        "best_start_abatement_rate": 0.21,
    }
    for parameter_id, expected_value in expected.items():
        resolution = result.get(parameter_id)
        assert resolution.outcome == "resolved", parameter_id
        assert resolution.value == expected_value, parameter_id


def test_date_outside_reference_period_is_unsupported() -> None:
    result = load_policy_parameters(WFF_POLICY_DIR, date(2030, 1, 1))

    resolution = result.get("family_tax_credit_eldest_child")
    assert resolution.outcome == "unsupported"
    assert resolution.value is None
