"""Task 24.8: the Accommodation Supplement (AS) calculation route.

Mirrors `poltika.api.wff` (Task 21) exactly, adapted for AS's
single-component shape: this router wraps Task 24.7's `run_as_module()`
directly -- no `scenarios/`/`llm/` layer, single-module, per ADR-0010 and
ARCHITECTURE.md's request path.

Request fields mirror `AsScenario`'s fields and vocabulary exactly -- the
same `FactStatus`/`ClaimantCategory`/`TenureType`/`PartnerType`/`Area`
string enums `spec_cases.yaml`/`benchmarks.yaml` already use are reused
directly as Pydantic field types, not re-declared, so the API's vocabulary
cannot drift from the calculator's.

The policy directory is never caller-supplied -- pinned internally to
`policy_specs/accommodation_supplement`, per REPOSITORY_STRUCTURE.md's
dependency boundary ("no caller-supplied policy directory path"), and
resolved the same deploy-time-mount way as WFF's (ADR-0011):
`POLTIKA_POLICY_SPECS_DIR`, when set, wins; otherwise the
source-checkout-relative default.

Response value is typed `Decimal`, which Pydantic v2 serializes to JSON as
a string, preserving the exact-decimal precision `specification.md`'s
calculation sequence requires -- never a JSON number that risks float
rounding.
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
    run_as_module,
)
from poltika.engines.simulator.wff import ComponentResult, FactStatus


def _as_policy_dir() -> Path:
    """Resolve the AS `policy_specs/` directory.

    Deploy-time mount convention (ADR-0011), the same as
    `poltika.api.wff._wff_policy_dir()`: if `POLTIKA_POLICY_SPECS_DIR` is
    set, AS's directory is `<that path>/accommodation_supplement`.
    Falls back to the source-checkout-relative path for local development.
    """
    override = os.environ.get("POLTIKA_POLICY_SPECS_DIR")
    if override:
        return Path(override) / "accommodation_supplement"
    return Path(__file__).resolve().parents[3] / "policy_specs" / "accommodation_supplement"


AS_POLICY_DIR = _as_policy_dir()

router = APIRouter(prefix="/accommodation-supplement", tags=["accommodation-supplement"])


class AsCalculationRequest(BaseModel):
    """Mirrors `AsScenario`'s own fields; see this module's docstring."""

    # v0.1 question set Q64: an unknown field is rejected, never ignored.
    model_config = ConfigDict(extra="forbid")

    modelled_date: date
    # Required, no default: the AS assessment week, [start, end), exactly
    # seven days. modelled_date (the parameter lookup date) must fall in
    # it, and every rate used must cover the whole week. No weekday
    # convention is assumed; the caller states the week.
    assessment_week_start: date
    assessment_week_end: date
    # Required, no default -- Task 24.7's explicit version-selection
    # contract (`run_as_module()`'s own `requested_policy_version` is a
    # required keyword argument for the same reason): no implicit
    # "whatever's deployed" fallback at the API boundary either.
    requested_policy_version: str

    household_eligibility: FactStatus
    claimant_category: ClaimantCategory | None = None
    tenure_type: TenureType | None = None
    partner_status: PartnerType | None = None
    statistical_area_unit: Area | None = None
    weekly_accommodation_costs: Decimal | None = Field(default=None, ge=0)
    # StrictInt (Task 34.3 F8): `true` must not be read as one child.
    dependent_children_count: StrictInt | None = Field(default=None, ge=0)
    cash_assets: Decimal | None = Field(default=None, ge=0)
    exempt_cash_asset_status: FactStatus = FactStatus.UNKNOWN
    weekly_income: Decimal | None = Field(default=None, ge=0)
    # Task 26a repair (DEC-002): omitted means unverified -> needs_review,
    # never a silent pass.
    ordinary_rate_status: FactStatus = FactStatus.UNKNOWN
    eldest_dependent_child_under_16: FactStatus = FactStatus.UNKNOWN


class AsComponentResultResponse(BaseModel):
    """Pinned response shape for the single `accommodation_supplement`
    component -- see this module's docstring for why `value` is `Decimal`,
    not `float`. `value` is non-null iff `outcome == "calculated"`,
    mirroring `ComponentResult`'s own "never treat a missing value as
    zero" contract exactly."""

    outcome: Literal["calculated", "needs_review", "unsupported"]
    value: Decimal | None = None
    reason: str | None = None

    @classmethod
    def from_component_result(cls, result: ComponentResult) -> AsComponentResultResponse:
        return cls(outcome=result.outcome, value=result.value, reason=result.reason)


class AsCalculationResponse(BaseModel):
    accommodation_supplement: AsComponentResultResponse


def _scenario_from_request(request: AsCalculationRequest) -> AsScenario:
    return AsScenario(
        household_eligibility=request.household_eligibility,
        claimant_category=request.claimant_category,
        tenure_type=request.tenure_type,
        partner_status=request.partner_status,
        statistical_area_unit=request.statistical_area_unit,
        weekly_accommodation_costs=request.weekly_accommodation_costs,
        dependent_children_count=request.dependent_children_count,
        cash_assets=request.cash_assets,
        exempt_cash_asset_status=request.exempt_cash_asset_status,
        weekly_income=request.weekly_income,
        ordinary_rate_status=request.ordinary_rate_status,
        eldest_dependent_child_under_16=request.eldest_dependent_child_under_16,
    )


@router.post("/calculate", response_model=AsCalculationResponse)
def calculate(request: AsCalculationRequest) -> AsCalculationResponse:
    """Calculate Accommodation Supplement entitlement for one scenario.

    **This is a conditional simulation, not a verified entitlement
    determination.** Every `"verified"` fact in the request is the
    caller's own assertion -- Poltika does not independently confirm it
    against any government record (see the app-level description in
    `poltika.api.main` for the full statement).

    Wraps `run_as_module()` directly against the internally-pinned
    `policy_specs/accommodation_supplement` directory. A `PoltikaError`
    raised by the loader (e.g. a `requested_policy_version` mismatch) is
    not caught here -- it propagates to the app-level exception handlers
    registered in `poltika.api.main`, which map it to an explicit HTTP
    status rather than a 200.
    """
    try:
        scenario = _scenario_from_request(request)
        assessment_week = AssessmentWeek(start=request.assessment_week_start, end=request.assessment_week_end)
    except ValueError as exc:
        # A structural contradiction the dataclass itself rejects (e.g. a
        # negative amount past Pydantic's own `ge=0`) -- a caller input
        # problem, not a server fault, so 422 like any other
        # request-validation failure, not an unhandled 500.
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = run_as_module(
        AS_POLICY_DIR,
        request.modelled_date,
        scenario,
        requested_policy_version=request.requested_policy_version,
        assessment_week=assessment_week,
    )

    return AsCalculationResponse(
        accommodation_supplement=AsComponentResultResponse.from_component_result(result)
    )
