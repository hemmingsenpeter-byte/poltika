"""Task 21: the WFF calculation route.

Per ADR-0010 and ARCHITECTURE.md's request path ("FastAPI receives a
structured ScenarioRequest-shaped Pydantic model, calls straight into the
deterministic engine"), this router wraps Task 20's `run_wff_module()`
directly -- no `scenarios/` or `llm/` layer yet, single-module (WFF only).

Request fields mirror `WffScenario`'s fields and vocabulary exactly --
the same `FactStatus`/`BestStartCohort`/`PartnerStatus` string enums
`spec_cases.yaml`/`benchmarks.yaml` already use ("verified"/"excluded"/
"unknown", etc.) are reused directly as Pydantic field types, not
re-declared, so the API's vocabulary cannot drift from the calculator's.

The policy directory is never caller-supplied -- pinned internally to
`policy_specs/working_for_families`, per REPOSITORY_STRUCTURE.md's
dependency boundary ("no caller-supplied policy directory path").

Response component values are typed `Decimal`, which Pydantic v2
serializes to JSON as a string (verified: `Decimal("12345.825")` ->
`"12345.825"`, never a float), preserving the exact-decimal/possible-
half-cent precision `specification.md`'s calculation sequence requires --
never a JSON number that risks float rounding.
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    ComponentResult,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    run_wff_module,
)


def _wff_policy_dir() -> Path:
    """Resolve the WFF `policy_specs/` directory.

    Deploy-time mount convention (ADR-0011, Task 21's deployment gate): if
    `POLTIKA_POLICY_SPECS_DIR` is set, WFF's directory is `<that path>/
    working_for_families` -- `policy_specs/` is deploy-time configuration,
    supplied by whoever runs the installed artifact, never baked into the
    wheel itself (confirmed absent from a built wheel, PR #22 review
    finding). Falls back to the source-checkout-relative path for local
    development, unchanged from Task 21's original behaviour -- most
    contributors never need to set the environment variable at all.
    """
    override = os.environ.get("POLTIKA_POLICY_SPECS_DIR")
    if override:
        return Path(override) / "working_for_families"
    return Path(__file__).resolve().parents[3] / "policy_specs" / "working_for_families"


WFF_POLICY_DIR = _wff_policy_dir()

router = APIRouter(prefix="/wff", tags=["wff"])


class ChildFactsRequest(BaseModel):
    # v0.1 question set Q64: an unknown field is rejected, never ignored.
    model_config = ConfigDict(extra="forbid")

    qualifies_whole_year: FactStatus
    best_start_cohort: BestStartCohort = BestStartCohort.UNKNOWN
    best_start_no_disqualifying_payment: FactStatus = FactStatus.UNKNOWN


class VerifiedIncomeRequest(BaseModel):
    # v0.1 question set Q64: an unknown field is rejected, never ignored.
    model_config = ConfigDict(extra="forbid")

    claimant_amount: Decimal = Field(ge=0)
    partner_amount: Decimal | None = Field(default=None, ge=0)


class WffCalculationRequest(BaseModel):
    """Mirrors `WffScenario`'s own fields; see this module's docstring."""

    # v0.1 question set Q64: an unknown field is rejected, never ignored.
    model_config = ConfigDict(extra="forbid")

    modelled_date: date
    # Required, no default -- Task 20's explicit version-selection
    # contract (`run_wff_module()`'s own `requested_policy_version`
    # is a required keyword argument for the same reason): no implicit
    # "whatever's deployed" fallback at the API boundary either.
    requested_policy_version: str

    household_eligibility: FactStatus
    extra_instalment_status: FactStatus
    # Required (Task 34.3 F8): an omitted child list is a missing fact, not
    # a verified "no children"; `[]` asserts there are none.
    children: list[ChildFactsRequest]
    partner_status: PartnerStatus = PartnerStatus.UNKNOWN
    family_scheme_income: VerifiedIncomeRequest | None = None
    net_family_scheme_income: Decimal | None = Field(default=None, ge=0)
    net_family_scheme_income_me3_attested: bool = False
    in_work_eligibility: FactStatus = FactStatus.UNKNOWN
    ftc_iwtc_protected_or_direct_abatement: FactStatus = FactStatus.UNKNOWN
    mc6a_veterans_payment: FactStatus = FactStatus.UNKNOWN
    mc6b_disqualifying_payment: FactStatus = FactStatus.UNKNOWN
    minimum_family_full_time_earner_weeks: FactStatus = FactStatus.UNKNOWN
    best_start_no_shared_care: FactStatus = FactStatus.UNKNOWN
    best_start_protected_credit: FactStatus = FactStatus.UNKNOWN


class ComponentResultResponse(BaseModel):
    """Pinned response shape for one WFF component -- see this module's
    docstring for why `value` is `Decimal`, not `float`. `value` is
    non-null iff `outcome == "calculated"`, mirroring `ComponentResult`'s
    own "never treat a missing value as zero" contract exactly."""

    outcome: Literal["calculated", "needs_review", "unsupported"]
    value: Decimal | None = None
    reason: str | None = None

    @classmethod
    def from_component_result(cls, result: ComponentResult) -> ComponentResultResponse:
        return cls(outcome=result.outcome, value=result.value, reason=result.reason)


class WffCalculationResponse(BaseModel):
    family_tax_credit: ComponentResultResponse
    in_work_tax_credit: ComponentResultResponse
    minimum_family_tax_credit: ComponentResultResponse
    best_start: ComponentResultResponse


def _scenario_from_request(request: WffCalculationRequest) -> WffScenario:
    family_scheme_income = None
    if request.family_scheme_income is not None:
        family_scheme_income = VerifiedIncome(
            claimant_amount=request.family_scheme_income.claimant_amount,
            partner_amount=request.family_scheme_income.partner_amount,
        )

    return WffScenario(
        household_eligibility=request.household_eligibility,
        extra_instalment_status=request.extra_instalment_status,
        children=[
            ChildFacts(
                qualifies_whole_year=child.qualifies_whole_year,
                best_start_cohort=child.best_start_cohort,
                best_start_no_disqualifying_payment=child.best_start_no_disqualifying_payment,
            )
            for child in request.children
        ],
        partner_status=request.partner_status,
        family_scheme_income=family_scheme_income,
        net_family_scheme_income=request.net_family_scheme_income,
        net_family_scheme_income_me3_attested=request.net_family_scheme_income_me3_attested,
        in_work_eligibility=request.in_work_eligibility,
        ftc_iwtc_protected_or_direct_abatement=request.ftc_iwtc_protected_or_direct_abatement,
        mc6a_veterans_payment=request.mc6a_veterans_payment,
        mc6b_disqualifying_payment=request.mc6b_disqualifying_payment,
        minimum_family_full_time_earner_weeks=request.minimum_family_full_time_earner_weeks,
        best_start_no_shared_care=request.best_start_no_shared_care,
        best_start_protected_credit=request.best_start_protected_credit,
    )


@router.post("/calculate", response_model=WffCalculationResponse)
def calculate(request: WffCalculationRequest) -> WffCalculationResponse:
    """Calculate WFF entitlement for one scenario.

    **This is a conditional simulation, not a verified entitlement
    determination.** Every `"verified"` fact in the request (e.g.
    `household_eligibility: "verified"`) is the caller's own assertion --
    Poltika does not independently confirm it against any government
    record. A `calculated` result is only as reliable as the caller's own
    verification of the facts it supplied (see the app-level description
    in `poltika.api.main` for the full statement; PR #22 review finding).

    Wraps `run_wff_module()` directly against the internally-pinned
    `policy_specs/working_for_families` directory. A `PoltikaError` raised
    by the loader (e.g. a `requested_policy_version` mismatch) is not
    caught here -- it propagates to the app-level exception handlers
    registered in `poltika.api.main`, which map it to an explicit HTTP
    status rather than a 200.
    """
    try:
        scenario = _scenario_from_request(request)
    except ValueError as exc:
        # A structural contradiction the dataclasses themselves reject
        # (e.g. a negative amount past Pydantic's own `ge=0`, or a SINGLE
        # claimant with a partner_amount set) -- a caller input problem,
        # not a server fault, so 422 like any other request-validation
        # failure, not an unhandled 500.
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = run_wff_module(
        WFF_POLICY_DIR,
        request.modelled_date,
        scenario,
        requested_policy_version=request.requested_policy_version,
    )

    return WffCalculationResponse(
        family_tax_credit=ComponentResultResponse.from_component_result(result.family_tax_credit),
        in_work_tax_credit=ComponentResultResponse.from_component_result(result.in_work_tax_credit),
        minimum_family_tax_credit=ComponentResultResponse.from_component_result(
            result.minimum_family_tax_credit
        ),
        best_start=ComponentResultResponse.from_component_result(result.best_start),
    )
