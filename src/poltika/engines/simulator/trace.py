"""Task 31: per-component provenance trace.

A `ComponentTrace` records what one component's result was actually computed
from: the policy identity and artifact hashes of the parameter set, every
parameter the component consulted (including undeclared ones), every
scenario fact it read, any upstream component it depended on, and the
rounding and decision rules governing a `calculated` result.

The calculators stay pure and their component logic is untouched. Recording
happens around each component call, through two helpers:

- `recording_parameters()` gives the component a `PolicyParameterSet` whose
  `resolutions` mapping records every id looked up or tested for membership.
  Every parameter access in both calculators goes through that mapping (via
  `PolicyParameterSet.get()` or an `in` test), so nothing can be consulted
  without being recorded.
- `recording_copy()` gives the component a copy of a frozen dataclass (a
  scenario, or an upstream `ComponentResult`) that records which fields it
  reads. The copy is a real instance of the same class, so the component's
  type contract is unchanged.

Reads are recorded in first-read order with duplicates dropped, so a trace is
deterministic for a given scenario and parameter set.

No I/O, no network: resolving source ids against `sources.yaml` and checking
artifact hashes is `engines/assurance/`'s job, not the simulator's.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Literal, TypeVar, cast

from poltika.policy.loader import PolicyParameterSet

# The loader's three resolution outcomes, plus "undeclared": a parameter a
# component looked for that the policy does not declare at all (AS's
# deliberate v0.1 gap for base rates and the income level).
ParameterUseOutcome = Literal["resolved", "needs_review", "unsupported", "undeclared"]

_T = TypeVar("_T")

# Attribute a recording copy stores its read log under. Set after
# construction, so reads made by the dataclass's own __init__/__post_init__
# are not recorded as component reads.
_READS_ATTR = "_poltika_recorded_reads"


@dataclass(frozen=True)
class ParameterUse:
    """One parameter a component consulted, as the parameter set resolved it."""

    parameter_id: str
    outcome: ParameterUseOutcome
    value: Decimal | None = None
    unit: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    source_id: str | None = None
    locator: str | None = None
    review_status: str | None = None


@dataclass(frozen=True)
class InputUse:
    """One scenario fact a component read. Every v0.1 input is the caller's
    own assertion -- Poltika does not independently verify it (Task 21's
    conditional-simulation wording) -- so the trace says so explicitly."""

    name: str
    value: Any
    asserted_by: str = "caller"


@dataclass(frozen=True)
class ComponentTrace:
    component_id: str
    policy_id: str
    policy_version: str
    schema_version: str
    modelled_date: date
    # (file name, sha256) pairs, sorted by file name -- copied from the
    # parameter set, so the trace names the exact bytes the run used.
    artifact_sha256: tuple[tuple[str, str], ...]
    # SHA-256 of the whole scenario's canonical JSON (`scenario_sha256()`).
    # Two components belong to the same calculation only if this matches:
    # the same policy and date with a different household is a different run.
    scenario_sha256: str
    parameters: tuple[ParameterUse, ...] = ()
    inputs: tuple[InputUse, ...] = ()
    # Components whose result this one depended on, e.g. in-work tax credit
    # on family tax credit's remaining abatement (MD 2(2)(c)). Their
    # parameters and inputs are included in `parameters`/`inputs` above.
    upstream_components: tuple[str, ...] = ()
    # Rounding and ordering rules governing a `calculated` result's path,
    # each citing the provision the calculator implements. Empty for a
    # `needs_review`/`unsupported` result, whose `reason` says why.
    calculation_rules: tuple[str, ...] = ()
    # Decision artifacts (policy_specs/<policy>/decisions/) the calculated
    # path applied, e.g. ("DEC-001",).
    decisions: tuple[str, ...] = ()
    # The period the result is for, `[from, to)`: the WFF tax year or the AS
    # assessment week. Set by the module entry points; `None` for a bare
    # calculator call, which is not told its period.
    assessment_period: tuple[date, date] | None = None


class _RecordingResolutions(dict[str, Any]):
    """A `resolutions` dict that logs every id looked up or tested."""

    def __init__(self, base: dict[str, Any], log: list[str]) -> None:
        super().__init__(base)
        self._log = log

    def _record(self, key: object) -> None:
        if isinstance(key, str) and key not in self._log:
            self._log.append(key)

    def __getitem__(self, key: str) -> Any:
        self._record(key)
        return super().__getitem__(key)

    def __contains__(self, key: object) -> bool:
        self._record(key)
        return super().__contains__(key)

    def get(self, key: str, default: Any = None) -> Any:
        self._record(key)
        return super().get(key, default)


def recording_parameters(parameters: PolicyParameterSet) -> tuple[PolicyParameterSet, list[str]]:
    """A copy of `parameters` that logs every parameter id consulted."""
    log: list[str] = []
    return replace(parameters, resolutions=_RecordingResolutions(parameters.resolutions, log)), log


_recording_classes: dict[type, type] = {}


def _recording_class(cls: type) -> type:
    recording_cls = _recording_classes.get(cls)
    if recording_cls is None:
        field_names = frozenset(f.name for f in fields(cls))

        def __getattribute__(self: object, name: str) -> Any:
            value = object.__getattribute__(self, name)
            if name in field_names:
                try:
                    reads: list[str] = object.__getattribute__(self, _READS_ATTR)
                except AttributeError:
                    return value  # still constructing
                if name not in reads:
                    reads.append(name)
            return value

        recording_cls = type(f"_Recording{cls.__name__}", (cls,), {"__getattribute__": __getattribute__})
        _recording_classes[cls] = recording_cls
    return recording_cls


def recording_copy(instance: _T) -> tuple[_T, list[str]]:
    """A copy of a frozen dataclass instance that logs which fields are read.

    The copy is an instance of a subclass of `type(instance)`, built from the
    same field values, so it passes every isinstance check and type contract
    the original does. It re-runs `__post_init__` on those same values, which
    already passed it once.
    """
    cls = type(instance)
    values = {f.name: getattr(instance, f.name) for f in fields(cast(Any, instance)) if f.init}
    copy = _recording_class(cls)(**values)
    reads: list[str] = []
    object.__setattr__(copy, _READS_ATTR, reads)
    return cast(_T, copy), reads


def parameter_uses(parameters: PolicyParameterSet, parameter_ids: list[str]) -> tuple[ParameterUse, ...]:
    """`ParameterUse` records for the given ids, from the original
    (non-recording) parameter set, in the order given."""
    uses = []
    for parameter_id in parameter_ids:
        resolution = parameters.resolutions.get(parameter_id)
        if resolution is None:
            uses.append(ParameterUse(parameter_id=parameter_id, outcome="undeclared"))
            continue
        uses.append(
            ParameterUse(
                parameter_id=parameter_id,
                outcome=resolution.outcome,
                value=resolution.value,
                unit=resolution.unit,
                effective_from=resolution.effective_from,
                effective_to=resolution.effective_to,
                source_id=resolution.source_id,
                locator=resolution.locator,
                review_status=resolution.review_status,
            )
        )
    return tuple(uses)


def input_uses(scenario: object, field_names: list[str]) -> tuple[InputUse, ...]:
    """`InputUse` records for the given scenario fields, in the order given."""
    return tuple(InputUse(name=name, value=getattr(scenario, name)) for name in field_names)


def merge_ids(*id_lists: list[str]) -> list[str]:
    """Concatenate id lists in order, dropping later duplicates."""
    merged: list[str] = []
    for ids in id_lists:
        for item in ids:
            if item not in merged:
                merged.append(item)
    return merged


def trace_header(parameters: PolicyParameterSet, scenario: object) -> dict[str, Any]:
    """The run-identity fields every `ComponentTrace` from one calculation
    shares -- policy, lookup date, artifacts, and scenario -- as keyword
    arguments."""
    return {
        "policy_id": parameters.policy_id,
        "policy_version": parameters.policy_version,
        "schema_version": parameters.schema_version,
        "modelled_date": parameters.modelled_date,
        "artifact_sha256": tuple(sorted(parameters.artifact_sha256.items())),
        "scenario_sha256": scenario_sha256(scenario),
    }


def plain(value: Any) -> Any:
    """A JSON-safe rendering of a trace or scenario value: `Decimal` as a
    string (never a float), dates as ISO strings, enums by value,
    dataclasses as dicts (omitting any `trace` field)."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Enum):
        return plain(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: plain(getattr(value, f.name)) for f in fields(value) if f.name != "trace"}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): plain(item) for key, item in value.items()}
    raise TypeError(f"cannot render value of type {type(value).__name__}")


def scenario_sha256(scenario: object) -> str:
    """SHA-256 of the scenario's canonical JSON, including its type name,
    so equal facts give an equal identity and any changed fact does not."""
    canonical = json.dumps(
        {"type": type(scenario).__name__, "facts": plain(scenario)},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
