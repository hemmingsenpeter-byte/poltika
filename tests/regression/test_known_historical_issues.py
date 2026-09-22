"""Task 15: regression tests for known historical issues.

Per doctrine/test-doctrine.md's "Regression tests for known historical
issues" class -- distinct from Task 13's spec tests (hand-calculated from
POLICY_SPECS) and Task 14's benchmark tests (checked against IRD's
published examples). Every test here is traceable to a specific,
previously real defect and the PR/finding that caught it, not a
restatement of a general spec/benchmark case.

Task 10b's "frozen dataset-snapshot fixtures... same scenario + same
snapshot must yield the same deterministic result" is intentionally NOT
addressed here: Task 10b was closed N/A for WFF (no external statistical
dataset needed for this policy), so there is no dataset snapshot to freeze
for WFF. That half of Task 15 applies once Accommodation Supplement's
Task 22a introduces a real Stats NZ snapshot -- this is a scope boundary,
not an oversight.

Where an existing `spec_cases.yaml`/`benchmarks.yaml` case already
isolates a historical defect, these tests load and reuse that case by id
(via `tests/conftest.py`'s helpers) rather than re-authoring the scenario.
Where no such case exists -- defects that live in `calculate_wff()`'s own
logic, or in the test-harness completeness guards themselves -- a minimal,
independent scenario is constructed directly here, deliberately not
importing from `test_wff.py`'s own copies of these bugs: this file is
meant to be a second, independent line of defense, not a mirror of the
first one.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    calculate_wff,
)
from poltika.policy.loader import load_policy_parameters
from tests.conftest import (
    load_wff_benchmark_case,
    load_wff_spec_case,
    wff_scenario_from_yaml,
)
from tests.unit.engines.simulator.test_wff_benchmarks import (
    test_wff_benchmark as run_wff_benchmark_case,
)
from tests.unit.engines.simulator.test_wff_spec_cases import test_wff_spec_case as run_wff_spec_case


def _single_claimant_one_child(**overrides: object) -> WffScenario:
    base: dict[str, object] = {
        "household_eligibility": FactStatus.VERIFIED,
        "extra_instalment_status": FactStatus.VERIFIED,
        "partner_status": PartnerStatus.SINGLE,
        "children": [
            ChildFacts(
                qualifies_whole_year=FactStatus.VERIFIED,
                best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
                best_start_no_disqualifying_payment=FactStatus.VERIFIED,
            )
        ],
        "family_scheme_income": VerifiedIncome(claimant_amount=Decimal(30000)),
        "net_family_scheme_income": Decimal(30000),
        "net_family_scheme_income_me3_attested": True,
        "in_work_eligibility": FactStatus.VERIFIED,
        "ftc_iwtc_protected_or_direct_abatement": FactStatus.VERIFIED,
        "mc6a_veterans_payment": FactStatus.VERIFIED,
        "mc6b_disqualifying_payment": FactStatus.VERIFIED,
        "minimum_family_full_time_earner_weeks": FactStatus.VERIFIED,
        "best_start_no_shared_care": FactStatus.VERIFIED,
        "best_start_protected_credit": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return WffScenario(**base)  # type: ignore[arg-type]


# --- Calculator-logic defects (no existing spec/benchmark case isolates these) -


def test_md2_2_c_carryover_does_not_silently_assume_zero_abatement(
    wff_synthetic_all_approved_parameters,
) -> None:
    """Historical issue: caught during Task 12 development, before any
    external review, and fixed in the same commit that first implemented
    calculate_wff() (BUILD_PLAN.md Task 12). MD 2(2)(c) passes any family
    tax credit abatement remainder to in-work tax credit. The first draft
    computed in-work tax credit independently once its own gates passed,
    silently assuming ZERO remaining abatement whenever family tax credit
    itself could not be calculated (e.g. unverified income) -- which would
    have overstated in-work tax credit by the full, un-netted amount.
    """
    scenario = _single_claimant_one_child(family_scheme_income=None)

    result = calculate_wff(scenario, wff_synthetic_all_approved_parameters)

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.in_work_tax_credit.outcome == "needs_review", (
        "in-work tax credit must inherit family tax credit's needs_review via "
        "MD 2(2)(c), not silently compute a full, un-netted amount"
    )
    assert result.in_work_tax_credit.value is None


def test_best_start_other_cohort_child_is_not_a_false_zero(real_wff_parameters) -> None:
    """Historical issue: Task 12, first PR #14 re-review finding. A child
    outside the narrow 2024-04-01..2025-03-31 v0.1 Best Start cohort was
    represented by a bare `bool` defaulting to False, collapsing "outside
    this narrow branch, entitlement genuinely unresolved" and "verified
    zero entitlement" into the same calculated-zero outcome -- despite
    specification.md already saying later birth cohorts "require separate
    review; do not apply this branch to them"."""
    scenario = _single_claimant_one_child(
        children=[
            ChildFacts(
                qualifies_whole_year=FactStatus.VERIFIED,
                best_start_cohort=BestStartCohort.OTHER_COHORT_UNSUPPORTED,
                best_start_no_disqualifying_payment=FactStatus.UNKNOWN,
            )
        ]
    )

    result = calculate_wff(scenario, real_wff_parameters)

    assert result.best_start.outcome == "unsupported"
    assert result.best_start.value is None


def test_partnered_missing_partner_income_is_not_treated_as_single(real_wff_parameters) -> None:
    """Historical issue: Task 12, second PR #14 re-review finding.
    `VerifiedIncome.partner_amount is None` was the correct shape both for
    a genuinely single claimant and for a partnered claimant whose
    partner's income was never verified -- indistinguishable without an
    independent partner-status fact, so a partnered household could
    silently produce a numeric result using the claimant's income alone."""
    scenario = _single_claimant_one_child(
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=VerifiedIncome(claimant_amount=Decimal(30000)),
    )

    result = calculate_wff(scenario, real_wff_parameters)

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.family_tax_credit.value is None
    assert "partner" in (result.family_tax_credit.reason or "").lower()


def test_unknown_partner_status_blocks_minimum_family_tax_credit(real_wff_parameters) -> None:
    """Historical issue: Task 12, third PR #14 re-review finding. Minimum
    family tax credit's own MA 7 full-time-earner test has a different
    hour threshold for a single claimant (20 hours) than a partnered one
    (30 combined hours) per specification.md -- `PartnerStatus.UNKNOWN`
    blocked family tax credit and Best Start (which use combined income)
    but did NOT block minimum family tax credit, which doesn't use
    combined income at all and so was missed by that first fix."""
    scenario = _single_claimant_one_child(partner_status=PartnerStatus.UNKNOWN)

    result = calculate_wff(scenario, real_wff_parameters)

    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.value is None
    assert "full-time-earner" in (result.minimum_family_tax_credit.reason or "")


def test_mftc_missing_family_scheme_income_is_not_calculated_without_it(
    wff_synthetic_all_approved_parameters,
) -> None:
    """Historical issue: Task 17's independent adversarial review.
    `_minimum_family_tax_credit()` checked `net_family_scheme_income_me3_
    attested` and `net_family_scheme_income`, but never
    `scenario.family_scheme_income is not None` -- unlike
    `_family_tax_credit()` and `_best_start()`, which both gate on it. ME
    3(3)(a)(i)'s own net-family-scheme-income formula starts from the
    person's family scheme income, so a household without a verified
    family-scheme-income input could still produce a `calculated` minimum
    family tax credit result (reproduced against the real approved
    parameter set: net income 30,000 and `family_scheme_income=None`
    returned `calculated: 6604`)."""
    scenario = _single_claimant_one_child(family_scheme_income=None)

    result = calculate_wff(scenario, wff_synthetic_all_approved_parameters)

    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.value is None
    assert "family_scheme_income" in (result.minimum_family_tax_credit.reason or "")


def test_mftc_partnered_missing_partner_income_blocks_mftc(
    wff_synthetic_all_approved_parameters,
) -> None:
    """Historical issue: Task 17's independent adversarial review, same
    root cause as the missing-family-scheme-income case above. A
    partnered claimant's own family-scheme-income verification must show
    each person's amount (specification.md's accepted domain boundary) --
    before this fix, minimum family tax credit had no family-scheme-income
    gate at all, so a partnered household with only the claimant's amount
    verified would silently produce a numeric minimum family tax credit
    result using an unverified combined figure, exactly the gap
    `test_partnered_missing_partner_income_is_not_treated_as_single`
    above already closed for family tax credit."""
    scenario = _single_claimant_one_child(
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=VerifiedIncome(claimant_amount=Decimal(30000)),
    )

    result = calculate_wff(scenario, wff_synthetic_all_approved_parameters)

    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.value is None
    assert "partner" in (result.minimum_family_tax_credit.reason or "").lower()


def _policy_dir_with_one_parameter(
    tmp_path: Path, *, effective_from: str, effective_to: str | None
) -> Path:
    policy_dir = tmp_path / "policy"
    policy_dir.mkdir()
    policy = {
        "schema_version": "0.1",
        "policy_id": "interval_regression_wff",
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": "2026-04-01", "to": "2027-04-01"},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            {
                "id": "family_tax_credit_eldest_child",
                "value_type": "money",
                "unit": "NZD_per_tax_year",
                "values": [
                    {
                        "effective_from": effective_from,
                        "effective_to": effective_to,
                        "value": "7921",
                        "source_id": "test-source",
                        "locator": "s 1",
                        "review_status": "approved",
                    }
                ],
            }
        ],
        "components": [],
        "outputs": {},
    }
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    return policy_dir


def test_parameter_interval_ending_before_reference_period_is_needs_review(tmp_path: Path) -> None:
    """Historical issue: Task 17's independent adversarial review.
    `_resolve_parameter()` matched whichever single interval covered the
    requested `modelled_date` and returned it `resolved` without checking
    that the interval spans the *complete* reference period the annual
    formulas assume -- specification.md's accepted contract explicitly
    requires selecting "the law and parameter interval for the complete
    assessment period", not a point-in-time match. Here the parameter's
    approved interval ends 2027-01-01, before the reference period's
    2027-04-01 end, even though it covers the requested 2026-06-01
    modelled date."""
    policy_dir = _policy_dir_with_one_parameter(
        tmp_path, effective_from="2026-04-01", effective_to="2027-01-01"
    )

    parameters = load_policy_parameters(policy_dir, date(2026, 6, 1))
    resolution = parameters.get("family_tax_credit_eldest_child")

    assert resolution.outcome == "needs_review"
    assert resolution.value is None
    assert "complete reference period" in (resolution.reason or "")


def test_parameter_interval_starting_after_reference_period_is_needs_review(tmp_path: Path) -> None:
    """Historical issue: Task 17's independent adversarial review, the
    mirror case of the test above -- a mismatched parameter whose approved
    interval starts 2026-07-01, after the reference period's 2026-04-01
    start, even though it covers the requested 2026-08-01 modelled date.
    Both directions must be caught: a point-in-time match alone cannot
    verify a full-year rate in either direction."""
    policy_dir = _policy_dir_with_one_parameter(
        tmp_path, effective_from="2026-07-01", effective_to="2027-04-01"
    )

    parameters = load_policy_parameters(policy_dir, date(2026, 8, 1))
    resolution = parameters.get("family_tax_credit_eldest_child")

    assert resolution.outcome == "needs_review"
    assert resolution.value is None
    assert "complete reference period" in (resolution.reason or "")


# --- Missing/incomplete fixture defects (reuse the existing case by id) --------


def test_md14_15_case_exists_and_is_correct(real_wff_parameters) -> None:
    """Historical issue: Task 13, PR #15's first review finding.
    BUILD_PLAN.md's coverage list claimed spec_cases.yaml had an MD 14/15
    protected-credit case, but no case actually set
    ftc_iwtc_protected_or_direct_abatement: excluded -- the case simply
    didn't exist. Loads the real case by id (added in PR #15's fix) so
    that if it were ever deleted or its facts changed to stop exercising
    MD 14/15, this test -- not just the general spec-case suite -- fails
    with a name that names the historical gap."""
    case = load_wff_spec_case("md14_15_protected_credit_excludes_ftc_and_iwtc_not_mftc_or_best_start")
    assert case["scenario"]["ftc_iwtc_protected_or_direct_abatement"] == "excluded"

    scenario = wff_scenario_from_yaml(case["scenario"])
    result = calculate_wff(scenario, real_wff_parameters)

    assert result.family_tax_credit.outcome == "unsupported"
    assert result.in_work_tax_credit.outcome == "unsupported"
    assert result.minimum_family_tax_credit.outcome == "calculated"
    assert result.best_start.outcome == "calculated"


def test_household_income_not_mislabelled_as_claimant_amount() -> None:
    """Historical issue: Task 14, PR #16's second review round. Three
    partnered benchmark cases (Rahui, Claire & Laura, Faraj) put a
    published HOUSEHOLD income directly into
    `family_scheme_income.claimant_amount`, misrepresenting a combined
    figure as one person's individually verified amount --
    `VerifiedIncome.claimant_amount` means specifically the claimant's own
    verified amount. Checks all three cases: an earlier revision of this
    test checked only Rahui and asserted the other two were "the same fix
    applied identically" without actually verifying that, which would not
    have caught a regression reintroducing the mistake in just one of the
    other two (PR #17's own review finding)."""
    case_ids = (
        "ird_ftc_rahui_partnered_combined_income_not_individually_verified",
        "ird_ftc_iwtc_claire_laura_partnered_abatement_carryover",
        "ird_faraj_in_year_birth_fails_whole_year_domain",
    )
    for case_id in case_ids:
        case = load_wff_benchmark_case(case_id)
        assert case["scenario"]["family_scheme_income"] is None, (
            f"{case_id}: a household total must not be recorded as one person's "
            "claimant_amount -- see PR #16's second review round"
        )


def test_child_born_in_year_is_not_marked_qualifying_whole_year() -> None:
    """Historical issue: Task 14, PR #16's second review round. The Faraj
    benchmark case marked a child `qualifies_whole_year: verified` despite
    IRD stating directly that child was born 1 June 2026 -- partway
    through the 2026-27 tax year, so she could not have been in care for
    the whole tax year. Because the household gate applies to every
    component before any component-specific logic runs, this one
    scenario-construction mistake would have silently produced a wrong
    unsupported/needs_review mix rather than the correct all-four
    `unsupported`."""
    case = load_wff_benchmark_case("ird_faraj_in_year_birth_fails_whole_year_domain")
    child = case["scenario"]["children"][0]

    assert child["qualifies_whole_year"] == "excluded", (
        "a child with a stated in-year birth date must not be marked as "
        "qualifying for the whole tax year -- see PR #16's second review round"
    )
    assert all(
        case["expected"][component]["outcome"] == "unsupported"
        for component in ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start")
    )


# --- Test-harness guard defects (exercise the real guard, not a copy of it) ----


def test_spec_case_completeness_guard_still_catches_an_incomplete_case() -> None:
    """Historical issue: Task 13, PR #15's second review finding. The
    spec-case test runner's per-component loop only ever checked whichever
    keys a case's `expected` block happened to include -- a case with an
    incomplete `expected` block would have passed without that missing
    component ever being asserted on. Calls the real, currently-shipping
    `test_wff_spec_case()` (not a re-implementation of its check) with a
    deliberately truncated case, and requires it to fail loudly."""
    case = dict(load_wff_spec_case("single_ordinary_low_income"))
    case["expected"] = {"family_tax_credit": case["expected"]["family_tax_credit"]}

    with pytest.raises(AssertionError, match="expected block must cover exactly"):
        run_wff_spec_case(case)


def test_benchmark_completeness_guard_still_catches_an_incomplete_case(
    wff_synthetic_all_approved_parameters,
) -> None:
    """Same historical issue and same fix as the spec-case guard above,
    applied to `test_wff_benchmarks.py`'s independently-implemented
    completeness check -- a separate piece of code that could separately
    regress. Calls the real, currently-shipping `test_wff_benchmark()`."""
    case = dict(load_wff_benchmark_case("ird_ftc_sarah_full_credit"))
    case["expected"] = {"family_tax_credit": case["expected"]["family_tax_credit"]}

    with pytest.raises(AssertionError, match="expected block must cover exactly"):
        run_wff_benchmark_case(case, wff_synthetic_all_approved_parameters)
