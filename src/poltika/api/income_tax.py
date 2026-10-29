"""Programme Task 7 / v0.3 Phase 2.3: the income-tax calculation route.

Wraps `run_income_tax_module()` directly, in the idiom of `api/wff.py` and
`api/accommodation_supplement.py`: a strict request model that mirrors
`IncomeTaxScenario`'s fields and vocabulary (the engine's own enums are the
field types, so the API cannot drift from the calculator), a pinned policy
directory, and a single component response with a deterministic explanation.

Every income-tax value is still draft (`policy.yaml` is
`draft_pending_review`, `policy_version: null`, every parameter
`needs_review`), so no real request can be `calculated`: a result is
`needs_review` or `unsupported`, `value` is null, and nothing here derives
or invents a figure.

`requested_policy_version` is optional here, unlike WFF and AS. The draft
policy has no version (`null`), so a required string could never match; omit
it to accept the draft, and any string is a 409 mismatch until a version is
approved.

Money is a decimal string. A JSON number (float or integer) is rejected, so
no binary float can reach the engine. Income is non-negative and finite, as
in WFF; a fractional amount is accepted by the model and is `unsupported`
in the engine (Q17), never rounded.
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictBool

from poltika.engines.assurance.explanation import explain, explanation_to_dict
from poltika.engines.simulator.income_tax import (
    COMPONENT_ID,
    IncomeComposition,
    IncomeTaxScenario,
    ResidenceScope,
    TaxYearBasis,
    run_income_tax_module,
)
from poltika.engines.simulator.outcome import ComponentResult, FactStatus


def _income_tax_policy_dir() -> Path:
    """Resolve the income-tax `policy_specs/` directory (ADR-0011): the
    `POLTIKA_POLICY_SPECS_DIR` override, else the source-checkout path."""
    override = os.environ.get("POLTIKA_POLICY_SPECS_DIR")
    if override:
        return Path(override) / "income_tax"
    return Path(__file__).resolve().parents[3] / "policy_specs" / "income_tax"


INCOME_TAX_POLICY_DIR = _income_tax_policy_dir()

router = APIRouter(prefix="/income-tax", tags=["income-tax"])


def _decimal_string(value: object) -> object:
    """Money is a decimal string (or a `Decimal` from Python): a JSON number
    would arrive as a binary float or integer and is refused."""
    if isinstance(value, bool) or not isinstance(value, str | Decimal):
        raise ValueError("money must be a decimal string, not a number")  # noqa: TRY004 -- pydantic needs ValueError
    return value


MoneyString = Annotated[Decimal, BeforeValidator(_decimal_string)]


class IncomeTaxCalculationRequest(BaseModel):
    """Mirrors `IncomeTaxScenario`'s own fields; see this module's docstring."""

    # v0.1 question set Q64: an unknown field is rejected, never ignored.
    model_config = ConfigDict(extra="forbid")

    modelled_date: date
    requested_policy_version: str | None = None

    # Omitted means unverified: needs_review naming the fact, never a pass.
    individual_status: FactStatus = FactStatus.UNKNOWN
    residence_scope: ResidenceScope | None = None
    tax_year_basis: TaxYearBasis | None = None
    income_composition: IncomeComposition | None = None
    no_deductions_status: FactStatus = FactStatus.UNKNOWN
    no_available_losses_status: FactStatus = FactStatus.UNKNOWN
    general_basic_rate_status: FactStatus = FactStatus.UNKNOWN
    # None is "not asserted"; `false` is "asserted not attested" -- distinct
    # outcomes in the engine. StrictBool: `"true"` or `1` is not an attestation.
    taxable_income_basis_attestation: StrictBool | None = None
    annual_taxable_income: MoneyString | None = Field(default=None, ge=0, allow_inf_nan=False)


class IncomeTaxComponentResponse(BaseModel):
    """Pinned response shape for the single `basic_annual_income_tax`
    component. `value` is non-null iff `outcome == "calculated"`; while the
    policy is draft it is always null."""

    outcome: Literal["calculated", "needs_review", "unsupported"]
    value: Decimal | None = None
    reason: str | None = None
    code: str | None = None
    category: Literal["evidenced_exclusion", "not_modelled"] | None = None
    missing_facts: list[str] = []

    @classmethod
    def from_component_result(cls, result: ComponentResult) -> IncomeTaxComponentResponse:
        return cls(
            outcome=result.outcome,
            value=result.value,
            reason=result.reason,
            code=result.code,
            category=result.category,
            missing_facts=list(result.missing_facts),
        )


class IncomeTaxCalculationResponse(BaseModel):
    basic_annual_income_tax: IncomeTaxComponentResponse
    # The deterministic explanation of the result (steps, assumption ledger
    # and evidence trace), as for WFF and AS.
    explanation: dict[str, Any]


def scenario_from_request(request: IncomeTaxCalculationRequest) -> IncomeTaxScenario:
    """The `IncomeTaxScenario` a request describes."""
    return IncomeTaxScenario(
        individual_status=request.individual_status,
        residence_scope=request.residence_scope,
        tax_year_basis=request.tax_year_basis,
        income_composition=request.income_composition,
        no_deductions_status=request.no_deductions_status,
        no_available_losses_status=request.no_available_losses_status,
        general_basic_rate_status=request.general_basic_rate_status,
        taxable_income_basis_attestation=request.taxable_income_basis_attestation,
        annual_taxable_income=request.annual_taxable_income,
    )


@router.post("/calculate", response_model=IncomeTaxCalculationResponse)
def calculate(request: IncomeTaxCalculationRequest) -> IncomeTaxCalculationResponse:
    """Calculate basic annual income tax for one individual.

    **This is a conditional simulation, not a verified determination.**
    Every `"verified"` fact and the attested taxable income are the caller's
    own assertion; Poltika derives no taxable income. The income-tax policy
    is draft, so this route returns `needs_review` or `unsupported` and never
    an amount (see this module's docstring).

    A `PoltikaError` raised by the loader (e.g. a `requested_policy_version`
    mismatch) is not caught here -- it propagates to the app-level handlers
    in `poltika.api.main`, which map it to an explicit HTTP status.
    """
    try:
        scenario = scenario_from_request(request)
    except ValueError as exc:
        # A structural contradiction the dataclass rejects: a caller input
        # problem, so 422 like any other request-validation failure.
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = run_income_tax_module(
        scenario,
        policy_dir=INCOME_TAX_POLICY_DIR,
        modelled_date=request.modelled_date,
        requested_policy_version=request.requested_policy_version,
    )

    return IncomeTaxCalculationResponse(
        basic_annual_income_tax=IncomeTaxComponentResponse.from_component_result(result),
        explanation=explanation_to_dict(explain(COMPONENT_ID, result)),
    )
