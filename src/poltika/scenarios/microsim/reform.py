"""v0.2 Tasks 6.1-6.3: reforms as parameter overrides.

A `Reform` changes named parameters of one or both v0.1 policies with `set`,
`add` or `multiply`. It is applied to a `PolicyParameterSet` already loaded
from the approved `policy.yaml`, and produces a copy. `policy.yaml` is never
edited, and no reform value is ever `approved`.

An overridden resolution carries `review_status: scenario_assumption`, no
`source_id`, and a locator naming the reform. It flows into every trace,
so a reform result shows exactly which values were assumed rather than
sourced (`BUILD_PLAN_v0_2.md` R7). Its interval is the baseline value's, so
the modules' period invariants still apply.

Validation (6.2) refuses:

- a policy Poltika doesn't model (`UnsupportedReformError`), rather than
  approximating it;
- an unknown parameter, or one overridden twice;
- `add` or `multiply` on a value that didn't resolve (`needs_review` or
  `unsupported`). A `set` may replace it, which is how an in-work tax
  credit rate assumption is labelled;
- a negative money value, or a rate outside [0, 1].

Whether a valid value is sensible policy is not Poltika's call.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from poltika.common.errors import PoltikaError
from poltika.policy.loader import ParameterResolution, PolicyParameterSet
from poltika.semantics.schemas.policy_spec import ParameterUnit

MODELLED_POLICIES = frozenset({"working_for_families", "accommodation_supplement"})
SCENARIO_ASSUMPTION = "scenario_assumption"

# Units whose value is a rate: a fraction of a dollar withdrawn per dollar.
_RATE_UNITS = frozenset(
    {ParameterUnit.FRACTION.value, ParameterUnit.NZD_PER_COMPLETE_NZD_ABOVE_THRESHOLD.value}
)


class UnsupportedReformError(PoltikaError):
    """The reform names a policy Poltika does not model."""


class InvalidReformError(PoltikaError):
    """The reform can't be applied to these parameters."""


class Operation(str, Enum):
    SET = "set"
    ADD = "add"
    MULTIPLY = "multiply"


class Override(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    parameter_id: str
    operation: Operation
    value: Decimal


class Reform(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    reform_id: str = Field(min_length=1)
    description: str = ""
    overrides: tuple[Override, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _one_override_per_parameter(self) -> Reform:
        keys = [(o.policy_id, o.parameter_id) for o in self.overrides]
        duplicates = sorted({k for k in keys if keys.count(k) > 1})
        if duplicates:
            raise ValueError(f"parameters overridden more than once: {duplicates}")
        return self

    def reform_sha256(self) -> str:
        canonical = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def check_supported(self) -> None:
        unsupported = sorted({o.policy_id for o in self.overrides} - MODELLED_POLICIES)
        if unsupported:
            raise UnsupportedReformError(
                f"reform '{self.reform_id}' changes {unsupported}; Poltika models only "
                f"{sorted(MODELLED_POLICIES)}"
            )


def apply_reform(parameters: PolicyParameterSet, reform: Reform) -> PolicyParameterSet:
    """The reform's overrides for `parameters.policy_id`, applied to a copy.
    Overrides for the other policy are ignored here and applied to its own
    set."""
    reform.check_supported()
    resolutions = dict(parameters.resolutions)
    for override in reform.overrides:
        if override.policy_id != parameters.policy_id:
            continue
        baseline = resolutions.get(override.parameter_id)
        if baseline is None:
            raise InvalidReformError(
                f"reform '{reform.reform_id}': '{parameters.policy_id}' has no parameter "
                f"'{override.parameter_id}'"
            )
        resolutions[override.parameter_id] = _overridden(baseline, override, reform.reform_id)
    return replace(parameters, resolutions=resolutions)


def _overridden(
    baseline: ParameterResolution, override: Override, reform_id: str
) -> ParameterResolution:
    where = f"reform '{reform_id}': {override.parameter_id}"
    if override.operation is Operation.SET:
        value = override.value
    elif baseline.outcome != "resolved" or baseline.value is None:
        raise InvalidReformError(
            f"{where}: can't {override.operation.value} to a value that is {baseline.outcome} "
            f"({baseline.reason}); use set"
        )
    elif override.operation is Operation.ADD:
        value = baseline.value + override.value
    else:
        value = baseline.value * override.value
    if value < 0:
        raise InvalidReformError(f"{where}: the result {value} is negative")
    if (
        override.policy_id == "accommodation_supplement"
        and override.parameter_id == "asset_imputation_step_size"
        and value == 0
    ):
        raise InvalidReformError(f"{where}: the divisor must be positive")
    if baseline.unit in _RATE_UNITS and value > 1:
        raise InvalidReformError(f"{where}: the result {value} is a rate above 1")
    if baseline.effective_from is None:
        raise InvalidReformError(f"{where}: no baseline interval covers the modelled date")
    return replace(
        baseline,
        outcome="resolved",
        value=value,
        reason=None,
        source_id=None,
        locator=f"{where} {override.operation.value} {override.value} (baseline {baseline.value})",
        review_status=SCENARIO_ASSUMPTION,
    )
