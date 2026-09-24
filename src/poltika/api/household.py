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

from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from poltika.api.accommodation_supplement import (
    AS_POLICY_DIR,
    AsCalculationRequest,
    AsComponentResultResponse,
)
from poltika.api.accommodation_supplement import _scenario_from_request as _as_scenario
from poltika.api.wff import WFF_POLICY_DIR, WffCalculationRequest, WffCalculationResponse
from poltika.api.wff import ComponentResultResponse as WffComponentResponse
from poltika.api.wff import _scenario_from_request as _wff_scenario
from poltika.engines.assurance.provenance import build_combined_provenance_report
from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.wff import FactStatus
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.record import ScenarioRecord, ScenarioRun, detect_code_identity, run_scenario

router = APIRouter(prefix="/household", tags=["household"])

# Source-checkout root when running from a checkout; inside an installed
# wheel there is no git repository, so the run is recorded as not
# reproducible (Task 30).
_CODE_ROOT = Path(__file__).resolve().parents[3]


class HouseholdCalculationRequest(BaseModel):
    wff: WffCalculationRequest
    accommodation_supplement: AsCalculationRequest
    # Task 28.3 precondition: the AS claimant is the WFF claimant or their
    # partner. Omitted means unverified.
    as_claimant_is_wff_claimant_or_partner: FactStatus = FactStatus.UNKNOWN


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


def record_from_request(request: HouseholdCalculationRequest) -> ScenarioRecord:
    """The Task 30 scenario record for a request; invalid combinations are 422."""
    as_request = request.accommodation_supplement
    try:
        return ScenarioRecord(
            household=CombinedHouseholdScenario(
                wff=_wff_scenario(request.wff),
                accommodation_supplement=_as_scenario(as_request),
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
        record, WFF_POLICY_DIR, AS_POLICY_DIR, code=detect_code_identity(_CODE_ROOT)
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
    )


@router.post("/calculate", response_model=HouseholdCalculationResponse)
def calculate(request: HouseholdCalculationRequest) -> HouseholdCalculationResponse:
    """Calculate WFF and Accommodation Supplement for one household.

    **This is a conditional simulation, not a verified entitlement
    determination.** Each policy is reported in its own period, and there is
    no combined total. A structural error (such as a policy-version
    mismatch) maps to 409 or 500 through the app-level handlers.
    """
    return response_from_run(execute(record_from_request(request)))
