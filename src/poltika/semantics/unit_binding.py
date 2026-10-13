"""Programme Task 5: bind the units a policy.yaml declares to the registries.

`policy.yaml` writes a unit as one string, such as `NZD_per_week`, which fuses
a currency, a period and sometimes a per-entity qualifier. The registries keep
those apart: `units` (what is measured), `periods` (the `PeriodType`) and
`entities`. This module is the one explicit table that decomposes each
declared unit into a registered unit id, an optional `PeriodType` and an
optional qualifier. It performs no conversion: a binding names a period but
never turns an annual amount into a weekly one (`periods.convert_amount` and
`units.convert` still refuse).

A period is `None` when the unit has no period (a rate, a count or a stock
amount such as an asset ceiling), and `UNRESOLVED` would mark a unit whose
period the repository's sources do not settle. An unresolved period is never
guessed; a use under any period is accepted only because the binding says so
explicitly.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict

from poltika.common.errors import UnboundPolicyUnitError
from poltika.semantics.periods import PeriodType
from poltika.semantics.schemas.policy_spec import ParameterUnit
from poltika.semantics.units import get_unit


class PeriodStatus(str, Enum):
    NONE = "none"  # a rate, count or stock: no period belongs to the unit
    BOUND = "bound"  # the unit's own name states the period
    UNRESOLVED = "unresolved"  # sources do not settle the period; escalated


class PerEntity(str, Enum):
    """A per-entity qualifier. `child` is a person in the WFF
    `dependent_child` role; person identifiers stay unassigned (Task 6)."""

    CHILD = "child"

    # Note: `semantics.entities.EntityType` has no `child`; a child is a
    # person in the `dependent_child` role (`population.PersonRole`), so this
    # qualifier is a role, not an entity type, and is deliberately not mapped.


class UnitBinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_unit: ParameterUnit
    unit_id: str  # a key of `semantics.units.UNITS`
    period: PeriodType | None
    period_status: PeriodStatus
    per: PerEntity | None = None
    # Meaning carried by the policy unit that no registry models.
    qualifier: str | None = None
    note: str


def _b(
    policy_unit: ParameterUnit,
    unit_id: str,
    period: PeriodType | None,
    status: PeriodStatus,
    note: str,
    *,
    per: PerEntity | None = None,
    qualifier: str | None = None,
) -> UnitBinding:
    return UnitBinding(
        policy_unit=policy_unit,
        unit_id=unit_id,
        period=period,
        period_status=status,
        per=per,
        qualifier=qualifier,
        note=note,
    )


_BINDINGS: tuple[UnitBinding, ...] = (
    _b(ParameterUnit.NZD_PER_TAX_YEAR, "nzd", PeriodType.TAX_YEAR, PeriodStatus.BOUND,
       "WFF annual amount."),
    _b(ParameterUnit.NZD_PER_TAX_YEAR_AFTER_TAX, "nzd", PeriodType.TAX_YEAR, PeriodStatus.BOUND,
       "WFF annual amount after tax (MFTC attested income).", qualifier="after_tax"),
    _b(ParameterUnit.NZD_PER_CHILD_PER_TAX_YEAR, "nzd", PeriodType.TAX_YEAR, PeriodStatus.BOUND,
       "WFF annual amount for each child.", per=PerEntity.CHILD),
    _b(ParameterUnit.NZD_PER_COMPLETE_NZD_ABOVE_THRESHOLD, "ratio", None, PeriodStatus.NONE,
       "A rate of reduction per complete dollar above a threshold. Whether the "
       "dollar is floored is calculator logic.", qualifier="per_complete_nzd_above_threshold"),
    _b(ParameterUnit.NZD, "nzd", None, PeriodStatus.NONE,
       "AS stock amount (asset ceilings, imputation thresholds, step size): an "
       "amount held, not a flow (Q19 (1), D38). A parameter applies over its "
       "validity dates; a household balance is the caller's for the assessment week."),
    _b(ParameterUnit.NZD_PER_WEEK, "nzd", PeriodType.ASSESSMENT_WEEK, PeriodStatus.BOUND,
       "AS weekly amount: the explicit 7-day assessment week (policy 0.1.1)."),
    _b(ParameterUnit.FRACTION, "ratio", None, PeriodStatus.NONE, "A dimensionless fraction."),
)

UNIT_BINDINGS: Mapping[str, UnitBinding] = MappingProxyType(
    {b.policy_unit.value: b for b in _BINDINGS}
)

# The `period:` values policy.yaml inputs and membership declare, bound to PeriodType.
# `day` is an assessment lookup date, `PeriodType.POINT_IN_TIME`.
INPUT_PERIODS: Mapping[str, PeriodType] = MappingProxyType(
    {
        "full_tax_year": PeriodType.TAX_YEAR,
        "tax_year": PeriodType.TAX_YEAR,  # assessment.membership_period
        "assessment_week": PeriodType.ASSESSMENT_WEEK,
        "day": PeriodType.POINT_IN_TIME,
    }
)


def bind_unit(policy_unit: str) -> UnitBinding:
    try:
        return UNIT_BINDINGS[policy_unit]
    except KeyError:
        raise UnboundPolicyUnitError(f"policy unit '{policy_unit}' has no binding") from None


def bind_input_period(period: str) -> PeriodType:
    try:
        return INPUT_PERIODS[period]
    except KeyError:
        raise UnboundPolicyUnitError(f"input period '{period}' has no PeriodType") from None


def check_input(policy_unit: str, input_period: str | None) -> UnitBinding:
    """Check a unit used under an input period. A bound period must equal the
    input's period; no value is converted between periods."""
    binding = bind_unit(policy_unit)
    get_unit(binding.unit_id)  # raises UnknownUnitError if unregistered
    if input_period is None:
        raise UnboundPolicyUnitError(f"unit '{policy_unit}' is used with no period")
    used = bind_input_period(input_period)
    if binding.period_status is PeriodStatus.BOUND and binding.period is not used:
        raise UnboundPolicyUnitError(
            f"unit '{policy_unit}' is a {binding.period.value if binding.period else None} "
            f"amount but is used under period '{input_period}' ({used.value})"
        )
    return binding


def check_parameter(policy_unit: str, policy_period: str) -> UnitBinding:
    """Check a parameter's unit against the policy's own period
    (`assessment.membership_period`). A unit with a bound period must match
    it; a rate or an unresolved stock carries no period to compare."""
    return check_input(policy_unit, policy_period)
