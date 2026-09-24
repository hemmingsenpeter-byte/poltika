"""Task 28.4: the combined WFF + Accommodation Supplement household runner.

Implements the Task 28.3 interaction contract (the AS specification's "Task
28.3 WFF-AS interaction contract" section):

- Each policy runs through its own module entry point, for its own period:
  WFF for its reviewed tax year, AS for an explicit assessment week. Results
  stay in their native periods; there is deliberately no combined total.
- There is no income coupling. Neither policy's output is added to,
  subtracted from, or used to derive the other's income input (CW 33(1)(a)
  and MB 13(2)(l); Schedule 3 cl 8(1)(l) and DEC-003).
- A small set of shared-fact contradictions, which the two policies'
  definitions make certain, are checked. Any contradiction makes every
  component of both policies `needs_review`, with a reason naming both
  assertions. The runner never repairs one input from the other, because it
  cannot know which assertion is wrong.

Both modules still run when a contradiction is found, so each replaced
result keeps its own provenance trace.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import date
from pathlib import Path

from poltika.engines.simulator.accommodation_supplement import (
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    run_as_module,
)
from poltika.engines.simulator.wff import (
    ComponentResult,
    FactStatus,
    PartnerStatus,
    WffResult,
    WffScenario,
    run_wff_module,
)
from poltika.policy.loader import load_policy_spec

# AS claimant categories that are main benefits (Social Security Act
# Schedule 2 "main benefit"); non-beneficiary and the unsupported categories
# are not.
_MAIN_BENEFIT_CATEGORIES = frozenset(
    {
        ClaimantCategory.JOBSEEKER_SUPPORT,
        ClaimantCategory.SOLE_PARENT_SUPPORT,
        ClaimantCategory.SUPPORTED_LIVING_PAYMENT,
    }
)


@dataclass(frozen=True)
class CombinedHouseholdScenario:
    """One household described for both policies. Each scenario keeps its own
    policy's definitions and period; the runner only checks the two for the
    contract's certain contradictions."""

    wff: WffScenario
    accommodation_supplement: AsScenario


@dataclass(frozen=True)
class CombinedResult:
    """Both policies' results in their native periods. There is no total: an
    annual WFF amount and a weekly AS amount are never summed or converted."""

    wff: WffResult
    accommodation_supplement: ComponentResult
    wff_period: tuple[date, date]
    accommodation_supplement_period: tuple[date, date]
    # Each shared-fact contradiction found, in the order checked. Non-empty
    # means every component above is a `needs_review` replacement.
    contradictions: tuple[str, ...] = ()


def shared_fact_contradictions(
    scenario: CombinedHouseholdScenario, wff_period: tuple[date, date], assessment_week: AssessmentWeek
) -> tuple[str, ...]:
    """The Task 28.3 contract's checks. Only contradictions the definitions
    make certain are reported; an unverified fact on either side is left to
    that policy's own gates."""
    wff, as_ = scenario.wff, scenario.accommodation_supplement
    found: list[str] = []

    if assessment_week.start < wff_period[0] or assessment_week.end > wff_period[1]:
        found.append(
            f"AS assessment week [{assessment_week.start}, {assessment_week.end}) is not inside the WFF "
            f"year [{wff_period[0]}, {wff_period[1]})"
        )

    if wff.partner_status == PartnerStatus.SINGLE and as_.partner_status == PartnerType.ORDINARY_COUPLE:
        found.append("partner status: WFF asserts single, AS asserts an ordinary couple")
    if wff.partner_status == PartnerStatus.PARTNERED and as_.partner_status == PartnerType.SINGLE:
        found.append("partner status: WFF asserts partnered, AS asserts single")

    if as_.claimant_category in _MAIN_BENEFIT_CATEGORIES:
        benefit = as_.claimant_category.value
        if wff.in_work_eligibility == FactStatus.VERIFIED:
            found.append(
                f"main benefit: AS asserts {benefit} paid in the assessment week, WFF asserts in-work "
                "eligibility (no main-benefit period in the year) verified"
            )
        if wff.mc6b_disqualifying_payment == FactStatus.VERIFIED:
            found.append(
                f"main benefit: AS asserts {benefit} paid in the assessment week, WFF asserts MC 6(b) "
                "(no main benefit received in the period) verified"
            )

    if as_.dependent_children_count is not None and as_.dependent_children_count != len(wff.children):
        found.append(
            f"dependent children: WFF lists {len(wff.children)}, AS asserts {as_.dependent_children_count}"
        )

    return tuple(found)


def run_combined_household(
    wff_policy_dir: Path,
    as_policy_dir: Path,
    scenario: CombinedHouseholdScenario,
    *,
    wff_lookup_date: date,
    as_lookup_date: date,
    assessment_week: AssessmentWeek,
    requested_wff_policy_version: str,
    requested_as_policy_version: str,
) -> CombinedResult:
    """Run WFF for its tax year and AS for `assessment_week`, then apply the
    Task 28.3 shared-fact checks. Every date and version is explicit; there
    is no default household period."""
    wff_result = run_wff_module(
        wff_policy_dir, wff_lookup_date, scenario.wff, requested_policy_version=requested_wff_policy_version
    )
    as_result = run_as_module(
        as_policy_dir,
        as_lookup_date,
        scenario.accommodation_supplement,
        requested_policy_version=requested_as_policy_version,
        assessment_week=assessment_week,
    )
    reference = load_policy_spec(wff_policy_dir / "policy.yaml").reference_period
    wff_period = (reference.from_, reference.to)
    as_period = (assessment_week.start, assessment_week.end)

    contradictions = shared_fact_contradictions(scenario, wff_period, assessment_week)
    if contradictions:
        reason = "combined household run: shared facts contradict -- " + "; ".join(contradictions)
        wff_result = WffResult(
            **{f.name: _needs_review(getattr(wff_result, f.name), reason) for f in fields(WffResult)}
        )
        as_result = _needs_review(as_result, reason)

    return CombinedResult(
        wff=wff_result,
        accommodation_supplement=as_result,
        wff_period=wff_period,
        accommodation_supplement_period=as_period,
        contradictions=contradictions,
    )


def _needs_review(result: ComponentResult, reason: str) -> ComponentResult:
    """Replace a component's outcome while keeping its provenance trace."""
    return replace(result, outcome="needs_review", value=None, reason=reason)
