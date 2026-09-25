"""Task 28.4: the combined WFF + Accommodation Supplement household runner.

Implements the Task 28.3 interaction contract (the AS specification's "Task
28.3 WFF-AS interaction contract" section):

- Each policy runs through its own module entry point, for its own period:
  WFF for its reviewed tax year, AS for an explicit assessment week. Results
  stay in their native periods; there is deliberately no combined total.
- There is no income coupling. Neither policy's output is added to,
  subtracted from, or used to derive the other's income input (CW 33(1)(a)
  and MB 13(2)(l); Schedule 3 cl 8(1)(l) and DEC-003).
- A small set of shared facts is compared as conservative gates (the
  policies' definitions differ, so a disagreement is escalated, never
  guessed). A disagreement makes every component `needs_review` -- except
  one already `unsupported`, which is kept (the Task 28.1 research gate,
  confirmed by Pete) -- with a reason naming both
  assertions. The runner never repairs one input from the other.

Both modules always run, so each replaced result keeps its own provenance
trace, and the original results are kept alongside ("preserve the
conflicting evidence"). A structural error a module raises propagates.
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
from poltika.engines.simulator.outcome import ComponentOutcome, ComponentResult, FactStatus
from poltika.engines.simulator.wff import (
    PartnerStatus,
    WffResult,
    WffScenario,
    run_wff_module,
)
from poltika.policy.loader import load_policy_spec

# AS partner types that describe a couple for the partner-status comparison.
# community_spouse_or_partner is deliberately not compared (Pete's Task 28.3
# decision): AS is already unsupported for it, and the Income Tax Act's
# separated-person test means the WFF status may legitimately differ.
_AS_COUPLE_PARTNER_TYPES = frozenset({PartnerType.ORDINARY_COUPLE, PartnerType.JOINT_TENANCY})

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
    # Contract precondition, a verified fact the caller supplies: the AS
    # claimant is the WFF claimant or their partner. Neither scenario type
    # carries it. UNKNOWN -> needs_review; EXCLUDED -> unsupported.
    as_claimant_is_wff_claimant_or_partner: FactStatus = FactStatus.UNKNOWN


@dataclass(frozen=True)
class CombinedResult:
    """Both policies' results in their native periods. There is no total: an
    annual WFF amount and a weekly AS amount are never summed or converted."""

    wff: WffResult
    accommodation_supplement: ComponentResult
    wff_period: tuple[date, date]
    accommodation_supplement_period: tuple[date, date]
    # The module results before any replacement ("preserve the conflicting
    # evidence"); equal to the fields above when nothing was flagged.
    original_wff: WffResult
    original_accommodation_supplement: ComponentResult
    # Each disagreement or precondition failure found, in contract order.
    contradictions: tuple[str, ...] = ()


# The Task 28.3 checks, in the order `shared_fact_contradictions` applies them
# (named in the combined provenance report, Task 34.3 F9).
SHARED_FACT_CHECKS: tuple[str, ...] = (
    "precondition: AS claimant is the WFF claimant or their partner",
    "AS assessment week inside the WFF year",
    "partner status",
    "main benefit vs WFF in-work eligibility",
    "main benefit vs WFF MC 6(b)",
    "main benefit vs WFF MD 14/15 protected family tax credit",
    "main benefit vs WFF MG 4 protected Best Start",
    "dependent children count",
)


def shared_fact_contradictions(
    scenario: CombinedHouseholdScenario, wff_period: tuple[date, date], assessment_week: AssessmentWeek
) -> tuple[str, ...]:
    """The Task 28.3 contract's conservative shared-fact checks. A fact that
    is unverified on either side (`None` in AS, `unknown` in WFF) is not
    compared; that policy's own gates handle it."""
    wff, as_ = scenario.wff, scenario.accommodation_supplement
    found: list[str] = []

    if scenario.as_claimant_is_wff_claimant_or_partner == FactStatus.UNKNOWN:
        found.append("precondition: the AS claimant is not verified to be the WFF claimant or their partner")

    if assessment_week.start < wff_period[0] or assessment_week.end > wff_period[1]:
        found.append(
            f"AS assessment week [{assessment_week.start}, {assessment_week.end}) is not inside the WFF "
            f"year [{wff_period[0]}, {wff_period[1]})"
        )

    as_couple = as_.partner_status in _AS_COUPLE_PARTNER_TYPES or (
        as_.claimant_category == ClaimantCategory.MIXED_BENEFIT_COUPLE
    )
    if wff.partner_status == PartnerStatus.SINGLE and as_couple:
        found.append("partner status: WFF asserts single, AS describes a couple")
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
        # Task 34.3 F2: MD 14(1) / MG 4(1) make a month with a main benefit
        # and family scheme income under the MD 13(3)(a)(i) / MG 3(2)(a)
        # amount a protected month. Income is annualised per month (MB 2),
        # which neither side models, so the gate is conservative: any
        # verified "protected credit does not apply" is flagged.
        if wff.ftc_iwtc_protected_or_direct_abatement == FactStatus.VERIFIED:
            found.append(
                f"main benefit: AS asserts {benefit} paid in the assessment week, WFF asserts no MD 14/15 "
                "protected family tax credit month verified"
            )
        if wff.best_start_protected_credit == FactStatus.VERIFIED:
            found.append(
                f"main benefit: AS asserts {benefit} paid in the assessment week, WFF asserts no MG 4 "
                "protected Best Start month verified"
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

    original_wff, original_as = wff_result, as_result
    contradictions: tuple[str, ...]
    if scenario.as_claimant_is_wff_claimant_or_partner == FactStatus.EXCLUDED:
        reason = "combined household run: the AS claimant is not the WFF claimant or their partner"
        wff_result = WffResult(
            **{f.name: _replace(getattr(wff_result, f.name), "unsupported", reason) for f in fields(WffResult)}
        )
        as_result = _replace(as_result, "unsupported", reason)
        contradictions = (reason,)
    else:
        contradictions = shared_fact_contradictions(scenario, wff_period, assessment_week)
        if contradictions:
            reason = "combined household run: shared facts disagree -- " + "; ".join(contradictions)
            wff_result = WffResult(
                **{f.name: _flag(getattr(wff_result, f.name), reason) for f in fields(WffResult)}
            )
            as_result = _flag(as_result, reason)

    return CombinedResult(
        wff=wff_result,
        accommodation_supplement=as_result,
        wff_period=wff_period,
        accommodation_supplement_period=as_period,
        original_wff=original_wff,
        original_accommodation_supplement=original_as,
        contradictions=contradictions,
    )


def _flag(result: ComponentResult, reason: str) -> ComponentResult:
    """A disagreement makes a component `needs_review`, except one already
    `unsupported`, which is kept (Task 28.3 contract precedence)."""
    if result.outcome == "unsupported":
        return result
    return _replace(result, "needs_review", reason)


def _replace(result: ComponentResult, outcome: ComponentOutcome, reason: str) -> ComponentResult:
    """Replace a component's outcome while keeping its provenance trace."""
    return replace(result, outcome=outcome, value=None, reason=reason)
