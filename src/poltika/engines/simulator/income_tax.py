"""Programme Phase B Task 7: basic annual income tax for one individual.

Implements the outcome contract of the draft specification
`policy_specs/income_tax/specification.md` (rules IT-01 to IT-08) for the
D11 slice: one whole-year ordinary New Zealand resident natural person with
ordinary salary or wages only, no deductions or available losses, the
general basic rates, and whole-dollar annual taxable income (Q17, an
Assumption). Nothing here derives taxable income: the caller attests it.

No result in this version is `calculated`. Three server-owned gates, none of
which a caller's assertion can clear, stand between a supported scenario and
an amount:

1. the policy must be `approved` (the loader refuses a draft);
2. every band parameter must resolve as `approved`, which for 2026-27 waits
   on Royal assent of the annual-rates bill and a dated source check (Q16,
   DEC-001);
3. the final-output precision method must be sourced and reviewed (DEC-004).
   `FINAL_OUTPUT_METHOD_APPROVED` records that gate.

`basic_tax_band_sum()` is the exact per-dollar Schedule 1 Part A Table 1 sum
the specification gives as conditional arithmetic. It is tested with
synthetic parameters only and is not reached from a result while gate 3 is
open, so no candidate value becomes a result.

Known facts outside the slice are `unsupported` (`not_modelled`) before any
missing fact is `needs_review`; a missing fact is never zero.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import date
from decimal import Decimal
from enum import Enum
from pathlib import Path

from poltika.engines.simulator.outcome import ComponentResult, FactStatus
from poltika.engines.simulator.trace import (
    CalculationStep,
    ComponentTrace,
    input_uses,
    parameter_uses,
    record_step,
    trace_header,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters, load_policy_spec
from poltika.semantics.schemas.policy_spec import PolicyStatus

POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "income_tax"
COMPONENT_ID = "basic_annual_income_tax"

# DEC-004: no sourced, reviewed method yet turns the exact band sum (which can
# carry sub-cent amounts, e.g. $15,603 gives $1,638.525) into a final amount.
FINAL_OUTPUT_METHOD_APPROVED = False

# (upper-bound parameter, rate parameter) per Table 1 row; the last row has no
# upper bound. Band widths are endpoint differences, not parameters.
_BANDS: tuple[tuple[str | None, str], ...] = (
    ("band_1_upper", "band_1_rate"),
    ("band_2_upper", "band_2_rate"),
    ("band_3_upper", "band_3_rate"),
    ("band_4_upper", "band_4_rate"),
    (None, "band_5_rate"),
)
REQUIRED_PARAMETER_IDS = tuple(p for band in _BANDS for p in band if p is not None)


class ResidenceScope(str, Enum):
    WHOLE_YEAR_ORDINARY_NZ_RESIDENT = "whole_year_ordinary_nz_resident"
    NON_RESIDENT = "non_resident"
    CHANGING_RESIDENCE = "changing_residence"
    SPECIAL_RESIDENCE_REGIME = "special_residence_regime"


class TaxYearBasis(str, Enum):
    STANDARD_2026_27 = "standard_2026_27"
    NON_STANDARD_YEAR = "non_standard_year"
    OTHER_STANDARD_YEAR = "other_standard_year"


class IncomeComposition(str, Enum):
    ORDINARY_SALARY_WAGES_ONLY = "ordinary_salary_wages_only"
    MAIN_BENEFIT = "main_benefit"
    BUSINESS_SELF_EMPLOYMENT = "business_self_employment"
    INVESTMENT_OR_RENT = "investment_or_rent"
    FOREIGN_INCOME = "foreign_income"
    UNUSUAL_EMPLOYMENT_ITEMS = "unusual_employment_items"
    SCHEDULAR_OR_PIE = "schedular_or_pie"
    OTHER_OR_MIXED_INCOME = "other_or_mixed_income"


@dataclass(frozen=True)
class IncomeTaxScenario:
    """One individual's caller-asserted facts for the 2026-27 tax year.
    `None` means not asserted (unknown), never a default."""

    individual_status: FactStatus
    residence_scope: ResidenceScope | None
    tax_year_basis: TaxYearBasis | None
    income_composition: IncomeComposition | None
    no_deductions_status: FactStatus
    no_available_losses_status: FactStatus
    general_basic_rate_status: FactStatus
    taxable_income_basis_attestation: bool | None
    annual_taxable_income: Decimal | None

    def __post_init__(self) -> None:
        income = self.annual_taxable_income
        if income is not None and (not isinstance(income, Decimal) or not income.is_finite()):
            raise ValueError("annual_taxable_income must be a finite Decimal or None")


def _unsupported(reason: str, code: str) -> ComponentResult:
    return ComponentResult(outcome="unsupported", reason=reason, code=code, category="not_modelled")


def _needs_review(reason: str, code: str, missing: tuple[str, ...] = ()) -> ComponentResult:
    return ComponentResult(outcome="needs_review", reason=reason, code=code, missing_facts=missing)


def _scenario_outcome(scenario: IncomeTaxScenario) -> ComponentResult | None:
    """The scope refusal or missing-fact result, or None when every fact is
    verified inside the slice. Known exclusions are checked first, so an
    `unsupported` fact outranks any missing one (IT-01 to IT-05, Q17)."""
    s = scenario
    exclusions = [
        (s.individual_status is FactStatus.EXCLUDED, "IT_NOT_NATURAL_PERSON", "the taxpayer is not one natural person"),
        (
            s.residence_scope not in (None, ResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT),
            "IT_RESIDENCE_NOT_MODELLED",
            f"residence scope '{s.residence_scope.value if s.residence_scope else ''}' is outside the slice",
        ),
        (
            s.tax_year_basis not in (None, TaxYearBasis.STANDARD_2026_27),
            "IT_TAX_YEAR_NOT_MODELLED",
            f"tax year basis '{s.tax_year_basis.value if s.tax_year_basis else ''}' is outside the slice",
        ),
        (
            s.income_composition not in (None, IncomeComposition.ORDINARY_SALARY_WAGES_ONLY),
            "IT_INCOME_COMPOSITION_NOT_MODELLED",
            (
                f"income composition '{s.income_composition.value if s.income_composition else ''}' is outside "
                "the ordinary salary and wages slice"
            ),
        ),
        (s.no_deductions_status is FactStatus.EXCLUDED, "IT_DEDUCTIONS_NOT_MODELLED", "deductions apply"),
        (s.no_available_losses_status is FactStatus.EXCLUDED, "IT_LOSSES_NOT_MODELLED", "available losses apply"),
        (
            s.general_basic_rate_status is FactStatus.EXCLUDED,
            "IT_SPECIAL_BASIC_RATE_NOT_MODELLED",
            "a basic rate other than the general Table 1 rate applies",
        ),
    ]
    income = s.annual_taxable_income
    if income is not None:
        exclusions.append(
            (income < 0, "IT_NEGATIVE_INCOME_NOT_MODELLED", "negative taxable income is outside the slice")
        )
        exclusions.append(
            (
                income >= 0 and income != income.to_integral_value(),
                "IT_FRACTIONAL_INCOME_NOT_MODELLED",
                "taxable income is not a whole number of dollars; Q17 admits whole dollars only and never rounds",
            )
        )
    for applies, code, reason in exclusions:
        if applies:
            return _unsupported(f"Outside the supported income-tax slice: {reason}.", code)

    missing = tuple(
        name
        for name, unknown in (
            ("individual_status", s.individual_status is FactStatus.UNKNOWN),
            ("residence_scope", s.residence_scope is None),
            ("tax_year_basis", s.tax_year_basis is None),
            ("income_composition", s.income_composition is None),
            ("no_deductions_status", s.no_deductions_status is FactStatus.UNKNOWN),
            ("no_available_losses_status", s.no_available_losses_status is FactStatus.UNKNOWN),
            ("general_basic_rate_status", s.general_basic_rate_status is FactStatus.UNKNOWN),
            ("taxable_income_basis_attestation", s.taxable_income_basis_attestation is None),
            ("annual_taxable_income", income is None),
        )
        if unknown
    )
    if missing:
        return _needs_review(f"Not yet verified: {', '.join(missing)}.", "IT_FACTS_UNVERIFIED", missing)
    if s.taxable_income_basis_attestation is False:
        return _needs_review(
            "The caller has not attested that the amount is annual taxable income classified and allocated to "
            "2026-27 (BC 2-5, BD 1 and BD 3); Poltika does not derive it.",
            "IT_TAXABLE_INCOME_NOT_ATTESTED",
        )
    return None


def basic_tax_band_sum(
    taxable_income: Decimal, parameters: PolicyParameterSet, steps: list[CalculationStep] | None = None
) -> Decimal:
    """Exact Schedule 1 Part A Table 1 per-dollar sum for a non-negative
    whole-dollar income: each band's dollars times its rate, with no
    intermediate or final rounding. Every parameter must be resolved."""
    if taxable_income < 0 or taxable_income != taxable_income.to_integral_value():
        raise ValueError("basic_tax_band_sum takes a non-negative whole-dollar income")
    total = Decimal(0)
    lower = Decimal(0)
    for number, (upper_id, rate_id) in enumerate(_BANDS, start=1):
        rate = _resolved(parameters, rate_id)
        upper = _resolved(parameters, upper_id) if upper_id else None
        top = taxable_income if upper is None else min(taxable_income, upper)
        dollars = max(top - lower, Decimal(0))
        total += record_step(
            steps,
            f"IT_BAND_{number}",
            "IT-05",
            f"Table 1 row {number}",
            dollars * rate,
            dollars_in_band=dollars,
            band_rate=rate,
        )
        if upper is None or taxable_income <= upper:
            break
        lower = upper
    return record_step(steps, "IT_BASIC_TAX_SUM", "IT-05", "Sum of the bands", total, taxable_income=taxable_income)


def _resolved(parameters: PolicyParameterSet, parameter_id: str) -> Decimal:
    resolution = parameters.get(parameter_id)
    if resolution.outcome != "resolved" or resolution.value is None:
        raise ValueError(f"parameter '{parameter_id}' is {resolution.outcome}, not resolved")
    return resolution.value


def calculate_income_tax(scenario: IncomeTaxScenario, parameters: PolicyParameterSet) -> ComponentResult:
    """The basic annual income tax component for an approved parameter set,
    traced with the policy identity, every fact and every band parameter."""
    result = _calculate(scenario, parameters)
    declared = [p for p in REQUIRED_PARAMETER_IDS if p in parameters.resolutions]
    return replace(
        result,
        trace=ComponentTrace(
            component_id=COMPONENT_ID,
            **trace_header(parameters, scenario),
            parameters=parameter_uses(parameters, declared),
            inputs=input_uses(scenario, [f.name for f in fields(scenario)]),
        ),
    )


def _calculate(scenario: IncomeTaxScenario, parameters: PolicyParameterSet) -> ComponentResult:
    refused = _scenario_outcome(scenario)
    if refused is not None:
        return refused
    for parameter_id in REQUIRED_PARAMETER_IDS:
        if parameter_id not in parameters.resolutions:
            return _unsupported(
                f"Policy declares no parameter '{parameter_id}'.", "IT_PARAMETER_UNDECLARED"
            )
        resolution = parameters.get(parameter_id)
        if resolution.outcome == "unsupported":
            return _unsupported(
                f"No '{parameter_id}' value covers {parameters.modelled_date.isoformat()}.", "IT_PARAMETER_NO_INTERVAL"
            )
        if resolution.outcome != "resolved":
            return _needs_review(
                f"Parameter '{parameter_id}' is not approved: {resolution.reason}", "IT_PARAMETER_NOT_APPROVED"
            )
    if not FINAL_OUTPUT_METHOD_APPROVED:
        return _needs_review(
            "No sourced and reviewed method yet gives the final basic tax amount from the exact band sum "
            "(DEC-004); no amount is produced.",
            "IT_OUTPUT_PRECISION_UNRESOLVED",
        )
    raise NotImplementedError("wire the DEC-004 method here when it is approved")  # pragma: no cover


def run_income_tax_module(
    scenario: IncomeTaxScenario, *, policy_dir: Path = POLICY_DIR, modelled_date: date = date(2026, 4, 1)
) -> ComponentResult:
    """Module entry point: the scenario's own outcome first (so `unsupported`
    outranks every gate), then the policy-approval gate. A draft policy is
    never loaded as executable, so its candidate values cannot reach a result."""
    refused = _scenario_outcome(scenario)
    if refused is not None:
        return refused
    spec = load_policy_spec(policy_dir / "policy.yaml")
    if spec.status is not PolicyStatus.APPROVED:
        return _needs_review(
            f"The income-tax policy is '{spec.status.value}', not approved: its 2026-27 rates await Royal assent "
            "of the annual-rates bill and a dated source check (Q16, DEC-001), and its values await review.",
            "IT_POLICY_NOT_APPROVED",
        )
    return calculate_income_tax(scenario, load_policy_parameters(policy_dir, modelled_date))
