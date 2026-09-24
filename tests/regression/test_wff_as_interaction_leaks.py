"""Task 28.5 regressions: each named for the income leak it prevents
(Task 28.3 contract: no coupling in either direction). The household is the
leak-sensitive interaction case `non_beneficiary_sole_parent_receives_both_
with_no_income_leak`, whose derivation shows the size of each leak."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.wff import FactStatus, VerifiedIncome
from poltika.scenarios.combined import (
    CombinedHouseholdScenario,
    CombinedResult,
    run_combined_household,
)
from tests.conftest import (
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    as_scenario_from_yaml,
    wff_scenario_from_yaml,
)

CASES_PATH = Path(__file__).resolve().parents[2] / "policy_specs" / "wff_as_interaction" / "spec_cases.yaml"
LOOKUP = date(2026, 6, 1)
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))


def _case() -> dict[str, Any]:
    cases = yaml.safe_load(CASES_PATH.read_text())["interaction_cases"]
    return next(c for c in cases if c["id"] == "non_beneficiary_sole_parent_receives_both_with_no_income_leak")


def _run(**as_overrides: Any) -> CombinedResult:
    case = _case()
    wff = wff_scenario_from_yaml(case["wff"])
    as_ = replace(as_scenario_from_yaml(case["accommodation_supplement"]), **as_overrides)
    return run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        CombinedHouseholdScenario(
            wff=wff, accommodation_supplement=as_, as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED
        ),
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )


def test_as_amount_is_not_added_to_wff_family_scheme_income() -> None:
    """If AS ($163/week, $8,476 a year) leaked into WFF income, family tax
    credit would abate below its full rate. It must not."""
    result = _run()
    assert result.accommodation_supplement.outcome == "calculated"
    assert result.wff.family_tax_credit.value == Decimal(7921)
    # A larger AS amount changes nothing for WFF either.
    bigger_as = _run(weekly_accommodation_costs=Decimal(700))
    assert bigger_as.accommodation_supplement.value != result.accommodation_supplement.value
    assert bigger_as.wff == result.wff


def test_wff_credit_is_not_added_to_as_chargeable_income() -> None:
    """If WFF ($7,921/year, $152.33/week) leaked into AS income, the $800
    weekly income would exceed the $906 level and AS would be reduced. It
    must not (Schedule 3 cl 8(1)(l); DEC-003)."""
    result = _run()
    assert result.accommodation_supplement.value == Decimal(163)
    assert result.wff.family_tax_credit.value == Decimal(7921)


def test_wff_income_change_leaves_as_unchanged() -> None:
    case = _case()
    wff = replace(wff_scenario_from_yaml(case["wff"]), family_scheme_income=VerifiedIncome(Decimal(90000)))
    result = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        CombinedHouseholdScenario(
            wff=wff,
            accommodation_supplement=as_scenario_from_yaml(case["accommodation_supplement"]),
            as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
        ),
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )
    assert result.wff.family_tax_credit.value != Decimal(7921)
    assert result.accommodation_supplement.value == Decimal(163)
