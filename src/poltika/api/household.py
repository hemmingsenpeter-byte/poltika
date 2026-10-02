"""Task 33.1: combined WFF + Accommodation Supplement household route.

Wraps Task 30's `run_scenario()` (the Task 28.4 combined runner) against the
internally pinned policy directories, never a caller-supplied path, and
returns both policies' results in their native periods: WFF annual, AS
weekly, with no combined total. The response also carries the shared-fact
disagreements, the run's scenario and result identities, and the Task 31.6
combined provenance report.

The request nests the existing per-policy request models, so the API's
vocabulary cannot drift from either calculator's: the WFF lookup date is
`wff.modelled_date`; the AS lookup date and week come from
`accommodation_supplement`. Every "verified" fact is the caller's own
assertion (see `poltika.api.main`).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from poltika.api.accommodation_supplement import (
    AS_POLICY_DIR,
    AsCalculationRequest,
    AsComponentResultResponse,
)
from poltika.api.accommodation_supplement import scenario_from_request as as_scenario_from_request
from poltika.api.wff import WFF_POLICY_DIR, WffCalculationRequest, WffCalculationResponse
from poltika.api.wff import ComponentResultResponse as WffComponentResponse
from poltika.api.wff import scenario_from_request as wff_scenario_from_request
from poltika.engines.assurance.explanation import explain, explanation_to_dict
from poltika.engines.assurance.provenance import build_combined_provenance_report
from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.outcome import FactStatus
from poltika.policy.facts import fact_index, load_fact_catalog
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.conditional import (
    COMPONENTS,
    FactIndex,
    MissingFact,
    Resolution,
    component,
    resolve,
)
from poltika.scenarios.conditional_text import explain_resolution
from poltika.scenarios.conditional_text import verify as verify_summary
from poltika.scenarios.intake import apply_answer, fact_for, next_step
from poltika.scenarios.record import (
    CodeIdentity,
    ScenarioRecord,
    ScenarioRun,
    detect_code_identity,
    run_scenario,
)

router = APIRouter(prefix="/household", tags=["household"])

# Source-checkout root when running from a checkout; inside an installed
# wheel there is no git repository, so the run is recorded as not
# reproducible (Task 30).
_CODE_ROOT = Path(__file__).resolve().parents[3]
# Task 34.3 F4: the code this process loaded is the code at startup.
_STARTUP_CODE = detect_code_identity(_CODE_ROOT)


def running_code_identity() -> CodeIdentity:
    """The startup identity, demoted to not reproducible when the checkout
    has moved or changed since the process started: a long-running server
    must not label its runs with a commit it never loaded."""
    now = detect_code_identity(_CODE_ROOT)
    if now == _STARTUP_CODE:
        return _STARTUP_CODE
    return replace(_STARTUP_CODE, source_tree_clean=False)


class HouseholdCalculationRequest(BaseModel):
    # v0.1 question set Q64: an unknown field is rejected, never ignored.
    model_config = ConfigDict(extra="forbid")

    wff: WffCalculationRequest
    accommodation_supplement: AsCalculationRequest
    # Task 28.3 precondition: the AS claimant is the WFF claimant or their
    # partner. Omitted means unverified.
    as_claimant_is_wff_claimant_or_partner: FactStatus = FactStatus.UNKNOWN


class AnswerOption(BaseModel):
    value: str
    label: str


class FactQuestion(BaseModel):
    """One missing fact, as its catalogue asks for it (ADR-0016)."""

    fact: str  # the slot label an answer names, e.g. children[0].best_start_cohort
    id: str  # the engine's missing_facts id
    question: str
    kind: str
    answers: list[AnswerOption]  # empty for amounts and counts
    unit: str | None
    rule: str
    blocks: list[str]

    @classmethod
    def of(cls, fact: MissingFact) -> FactQuestion:
        entry = fact.entry
        labels = entry.answers or entry.values or {}
        answers = [AnswerOption(value=v, label=labels[v]) for v in entry.domain()]
        if entry.kind == "attestation":
            answers = [AnswerOption(value="yes", label="Yes")]
        return cls(
            fact=fact.slot.label,
            id=entry.id,
            question=entry.question,
            kind=entry.kind,
            answers=answers,
            unit=entry.unit if entry.kind == "money" else None,
            rule=entry.rule,
            blocks=list(fact.blocks),
        )


class AssignedFact(BaseModel):
    fact: str
    value: str
    label: str


class BranchOutcome(BaseModel):
    outcome: Literal["calculated", "needs_review", "unsupported"]
    value: Decimal | None


class BranchResponse(BaseModel):
    """One ordinary engine run with the assignment filled in."""

    assignment: list[AssignedFact]
    components: dict[str, BranchOutcome]
    unresolved: list[str]


class BoundsResponse(BaseModel):
    low: Decimal | None
    high: Decimal | None
    calculated: int  # branches in which this component is calculated
    branches: int
    complete: bool  # every branch calculated: low and high are the whole range
    # "points": values at a numeric range's endpoints, not bounds (ADR-0016)
    kind: Literal["bounds", "points"]


class ResolutionResponse(BaseModel):
    """ADR-0016 conditional answer. Nothing here is `calculated`: the
    components' own outcomes above are unchanged."""

    known: dict[str, Decimal]
    missing: list[FactQuestion]
    branches: list[BranchResponse]
    bounds: dict[str, BoundsResponse]
    capped: bool
    next_question: FactQuestion | None
    # Task 1b.2d: the same in plain language, every figure verified against
    # the branches and bounds above (scenarios/conditional_text.py).
    summary: list[str]

    @classmethod
    def of(cls, res: Resolution) -> ResolutionResponse:
        entries = {m.slot: m.entry for m in res.missing}

        def label(slot_value: tuple[Any, str]) -> AssignedFact:
            slot, value = slot_value
            entry = entries.get(slot)
            labels = (entry.answers or entry.values or {}) if entry else {}
            return AssignedFact(fact=slot.label, value=value, label=labels.get(value, value))

        return cls(
            known=dict(res.known),
            missing=[FactQuestion.of(m) for m in res.missing],
            branches=[
                BranchResponse(
                    assignment=[label(a) for a in b.assignment],
                    components={
                        c: BranchOutcome(outcome=r.outcome, value=r.value)
                        for c in COMPONENTS
                        if (r := component(b.result, c))
                    },
                    unresolved=list(b.unresolved),
                )
                for b in res.branches
            ],
            bounds={
                name: BoundsResponse(
                    low=b.low,
                    high=b.high,
                    calculated=b.calculated,
                    branches=b.branches,
                    complete=b.complete,
                    kind=b.kind,
                )
                for name, b in res.bounds.items()
            },
            capped=res.capped,
            next_question=FactQuestion.of(res.next_question) if res.next_question else None,
            summary=_summary(res),
        )


def _summary(res: Resolution) -> list[str]:
    """The verified summary; a sentence that fails verification is a bug,
    so it is refused rather than shown."""
    sentences = explain_resolution(res)
    problems = verify_summary(sentences, res)
    if problems:
        raise RuntimeError(f"conditional summary failed verification: {problems}")
    return [s.text for s in sentences]


class HouseholdCalculationResponse(BaseModel):
    wff: WffCalculationResponse
    accommodation_supplement: AsComponentResultResponse
    wff_period: tuple[date, date]
    accommodation_supplement_period: tuple[date, date]
    contradictions: list[str]
    scenario_id: str
    result_id: str
    reproducible: bool
    provenance: dict[str, Any]
    # v0.1.5 Phase 3: a deterministic explanation per component, rendered
    # only from the recorded calculation (engines/assurance/explanation.py).
    explanations: dict[str, Any]
    # v0.3 Task 1b.5 (ADR-0016): what can be said without the missing facts.
    # Present only on /household/calculate and /household/intake, and only
    # when a component is waiting for a fact.
    resolution: ResolutionResponse | None = None


def record_from_request(request: HouseholdCalculationRequest) -> ScenarioRecord:
    """The Task 30 scenario record for a request; invalid combinations are 422."""
    as_request = request.accommodation_supplement
    try:
        return ScenarioRecord(
            household=CombinedHouseholdScenario(
                wff=wff_scenario_from_request(request.wff),
                accommodation_supplement=as_scenario_from_request(as_request),
                as_claimant_is_wff_claimant_or_partner=request.as_claimant_is_wff_claimant_or_partner,
            ),
            wff_lookup_date=request.wff.modelled_date,
            as_lookup_date=as_request.modelled_date,
            assessment_week=AssessmentWeek(
                start=as_request.assessment_week_start, end=as_request.assessment_week_end
            ),
            requested_wff_policy_version=request.wff.requested_policy_version,
            requested_as_policy_version=as_request.requested_policy_version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def execute(record: ScenarioRecord) -> ScenarioRun:
    """Run a record against the internally pinned policy directories."""
    return run_scenario(
        record, WFF_POLICY_DIR, AS_POLICY_DIR, code=running_code_identity()
    )


def response_from_run(run: ScenarioRun) -> HouseholdCalculationResponse:
    wff = run.result.wff
    return HouseholdCalculationResponse(
        wff=WffCalculationResponse(
            family_tax_credit=WffComponentResponse.from_component_result(wff.family_tax_credit),
            in_work_tax_credit=WffComponentResponse.from_component_result(wff.in_work_tax_credit),
            minimum_family_tax_credit=WffComponentResponse.from_component_result(
                wff.minimum_family_tax_credit
            ),
            best_start=WffComponentResponse.from_component_result(wff.best_start),
        ),
        accommodation_supplement=AsComponentResultResponse.from_component_result(
            run.result.accommodation_supplement
        ),
        wff_period=run.result.wff_period,
        accommodation_supplement_period=run.result.accommodation_supplement_period,
        contradictions=list(run.result.contradictions),
        scenario_id=run.scenario_id,
        result_id=run.result_id,
        reproducible=run.manifest.reproducible,
        provenance=build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR),
        explanations=explanations_for(run),
    )


def explanations_for(run: ScenarioRun) -> dict[str, Any]:
    """Each reported component's explanation, keyed by component id."""
    wff = run.result.wff
    components = {
        "family_tax_credit": wff.family_tax_credit,
        "in_work_tax_credit": wff.in_work_tax_credit,
        "minimum_family_tax_credit": wff.minimum_family_tax_credit,
        "best_start": wff.best_start,
        "accommodation_supplement": run.result.accommodation_supplement,
    }
    return {cid: explanation_to_dict(explain(cid, result)) for cid, result in components.items()}


@lru_cache(maxsize=1)
def facts() -> FactIndex:
    """The deployed fact catalogues (ADR-0016), beside each policy."""
    return fact_index(
        load_fact_catalog(WFF_POLICY_DIR),
        load_fact_catalog(AS_POLICY_DIR),
        load_fact_catalog(WFF_POLICY_DIR.parent / "wff_as_interaction"),
    )


def resolution_for(record: ScenarioRecord, run: ScenarioRun) -> ResolutionResponse | None:
    """The conditional answer, when a component is waiting for a fact."""
    result = run.result
    waiting = any(component(result, c).missing_facts for c in COMPONENTS)
    if not waiting:
        return None
    return ResolutionResponse.of(resolve(record, WFF_POLICY_DIR, AS_POLICY_DIR, facts()))


def calculated_with_resolution(record: ScenarioRecord) -> HouseholdCalculationResponse:
    run = execute(record)
    response = response_from_run(run)
    response.resolution = resolution_for(record, run)
    return response


@router.post("/calculate", response_model=HouseholdCalculationResponse)
def calculate(request: HouseholdCalculationRequest) -> HouseholdCalculationResponse:
    """Calculate WFF and Accommodation Supplement for one household.

    **This is a conditional simulation, not a verified entitlement
    determination.** Each policy is reported in its own period, and there is
    no combined total. A structural error (such as a policy-version
    mismatch) maps to 409 or 500 through the app-level handlers.

    When a component is waiting for a fact, `resolution` adds what can be
    said without it (ADR-0016): the household rerun for each admissible
    answer, with ranges and the most useful next question. Each branch is
    an ordinary engine run; nothing conditional is labelled `calculated`.
    """
    return calculated_with_resolution(record_from_request(request))


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact: str = Field(description="The fact's label, as a question's `fact` gives it")
    answer: str = Field(description="One of the question's answer values, or an amount or count")


class IntakeRequest(BaseModel):
    """Stateless: the caller sends the household as first entered, every
    answer so far in order, and every fact declined ("don't know")."""

    model_config = ConfigDict(extra="forbid")

    household: HouseholdCalculationRequest
    answers: list[Answer] = []
    declined: list[str] = []
    asked: list[str] = Field(default_factory=lambda: list(COMPONENTS), min_length=1)


class IntakeResponse(BaseModel):
    status: Literal["ready", "ask", "incomplete"]
    question: FactQuestion | None
    remaining: list[FactQuestion]
    calculation: HouseholdCalculationResponse


@router.post("/intake", response_model=IntakeResponse)
def intake(request: IntakeRequest) -> IntakeResponse:
    """v0.3 Task 1b.4-1b.5 (ADR-0016): the next question before a run.

    - `ask`: the next question for the components asked about, from the
      fact catalogue, with its admissible answers.
    - `ready`: nothing blocks them.
    - `incomplete`: only declined facts block them; `calculation.resolution`
      gives what can be said without them.

    `calculation` is always the household with the answers so far applied.
    An answer is the caller's assertion, like every `verified` input. An
    inadmissible answer is a 422 naming what is admissible; it is never
    coerced. "Don't know" is a declined fact, never a default.
    """
    unknown = sorted(set(request.asked) - set(COMPONENTS))
    if unknown:
        raise HTTPException(status_code=422, detail=f"unknown components asked: {unknown}")
    record = record_from_request(request.household)
    for i, given in enumerate(request.answers):
        try:
            record = apply_answer(record, fact_for(record, given.fact, facts()), given.answer)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"answers[{i}]: {exc}") from exc
    declined = []
    for i, label in enumerate(request.declined):
        try:
            declined.append(fact_for(record, label, facts()).slot.label)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"declined[{i}]: {exc}") from exc
    step = next_step(
        record,
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        facts(),
        asked=request.asked,
        declined=declined,
    )
    return IntakeResponse(
        status=step.status,
        question=FactQuestion.of(step.question) if step.question else None,
        remaining=[FactQuestion.of(m) for m in step.remaining],
        calculation=calculated_with_resolution(record),
    )
