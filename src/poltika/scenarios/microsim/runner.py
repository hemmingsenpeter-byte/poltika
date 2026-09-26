"""v0.2 Tasks 7.1-7.3: run a population under the baseline and a reform.

Every household that validation didn't mark `invalid` runs twice through
`run_combined_household`: once with the approved parameters, once with the
reform's copy. There is no other calculation path. Parameters are loaded
once per (policy, lookup date, version), not once per household.

Per household and component, the run keeps the outcome, value and reason
code, not the full trace. A household's explanation comes from rerunning it
singly (Phase 9).

**Units.** WFF components are annual amounts for the tax year, and the
Accommodation Supplement is a weekly amount for the assessment week. They
are kept apart and never added (`UNITS`).

**Deltas.** A component's delta is calculated only when both runs
calculated it. Otherwise it is `needs_review` if either run was, and
`unsupported` if not. A household that validation marked `needs_review`
has every delta `needs_review`, whatever the engines returned.

**Identity.** `run_id` hashes everything the results depend on: the
population's content hash, the reform, the code identity and the policy
files the parameters were bound to. `results_sha256` hashes the results.
Rerunning the same inputs reproduces both (7.3).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from poltika.engines.simulator.outcome import ComponentOutcome, ComponentResult
from poltika.engines.simulator.trace import plain
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from poltika.scenarios.combined import CombinedResult, run_combined_household
from poltika.scenarios.microsim.reform import Reform, apply_reform
from poltika.scenarios.microsim.validation import (
    PopulationValidation,
    RecordStatus,
    validate_population,
)
from poltika.scenarios.record import CodeIdentity, ScenarioRecord
from poltika.semantics.population import PopulationDataset

WFF_COMPONENTS = (
    "family_tax_credit",
    "in_work_tax_credit",
    "minimum_family_tax_credit",
    "best_start",
)
AS_COMPONENT = "accommodation_supplement"
COMPONENTS = (*WFF_COMPONENTS, AS_COMPONENT)
UNITS: dict[str, str] = {
    **{c: "NZD per tax year" for c in WFF_COMPONENTS},
    AS_COMPONENT: "NZD per week",
}

DeltaOutcome = Literal["calculated", "needs_review", "unsupported"]


@dataclass(frozen=True)
class ComponentOutcomeValue:
    outcome: ComponentOutcome
    value: Decimal | None
    code: str | None


@dataclass(frozen=True)
class ComponentDelta:
    outcome: DeltaOutcome
    baseline: ComponentOutcomeValue
    reform: ComponentOutcomeValue
    delta: Decimal | None  # only when outcome == "calculated"


@dataclass(frozen=True)
class HouseholdResult:
    household_id: str
    weight: Decimal
    record_status: RecordStatus
    components: dict[str, ComponentDelta]


@dataclass(frozen=True)
class OverriddenParameter:
    """What a reform changed, with the baseline's evidence (R7, Module T)."""

    policy_id: str
    parameter_id: str
    modelled_date: str
    unit: str | None
    baseline_outcome: str
    baseline_value: Decimal | None
    baseline_source_id: str | None
    baseline_locator: str | None
    reform_value: Decimal


@dataclass(frozen=True)
class PopulationRun:
    run_id: str
    results_sha256: str
    population_id: str
    population_version: int
    population_sha256: str
    synthetic: bool
    label: str
    reform: Reform
    code: CodeIdentity
    policy_artifacts: tuple[tuple[str, str], ...]
    overridden: tuple[OverriddenParameter, ...]
    validation: PopulationValidation
    households: tuple[HouseholdResult, ...]  # invalid households are not run


def run_population(
    population: PopulationDataset,
    reform: Reform,
    wff_policy_dir: Path,
    as_policy_dir: Path,
    *,
    code: CodeIdentity,
) -> PopulationRun:
    reform.check_supported()
    validation = validate_population(population)
    loaded: dict[tuple[str, Any, str], tuple[PolicyParameterSet, PolicyParameterSet]] = {}

    def parameters(
        policy_dir: Path, lookup: Any, version: str
    ) -> tuple[PolicyParameterSet, PolicyParameterSet]:
        key = (str(policy_dir), lookup, version)
        if key not in loaded:
            baseline = load_policy_parameters(policy_dir, lookup, requested_policy_version=version)
            loaded[key] = (baseline, apply_reform(baseline, reform))
        return loaded[key]

    results: list[HouseholdResult] = []
    for checked in validation.households:
        if checked.record is None:
            continue
        record = checked.record
        wff_base, wff_reform = parameters(
            wff_policy_dir, record.wff_lookup_date, record.requested_wff_policy_version
        )
        as_base, as_reform = parameters(
            as_policy_dir, record.as_lookup_date, record.requested_as_policy_version
        )
        base = _run(record, wff_policy_dir, as_policy_dir, wff_base, as_base)
        new = _run(record, wff_policy_dir, as_policy_dir, wff_reform, as_reform)
        results.append(
            HouseholdResult(
                household_id=checked.household_id,
                weight=validation.weights[checked.household_id],
                record_status=checked.status,
                components={
                    c: _delta(_component(base, c), _component(new, c), checked.status)
                    for c in COMPONENTS
                },
            )
        )

    artifacts = sorted(
        {
            (f"{baseline.policy_id}/{path}", sha)
            for baseline, _ in loaded.values()
            for path, sha in baseline.artifact_sha256.items()
        }
    )
    overridden = sorted(
        {
            OverriddenParameter(
                policy_id=baseline.policy_id,
                parameter_id=pid,
                modelled_date=baseline.modelled_date.isoformat(),
                unit=before.unit,
                baseline_outcome=before.outcome,
                baseline_value=before.value,
                baseline_source_id=before.source_id,
                baseline_locator=before.locator,
                reform_value=after.value,
            )
            for baseline, reformed in loaded.values()
            for pid, after in reformed.resolutions.items()
            if (before := baseline.resolutions[pid]) != after and after.value is not None
        },
        key=lambda o: (o.policy_id, o.parameter_id, o.modelled_date),
    )
    population_sha = population.content_sha256()
    run_id = _sha256(
        {
            "population_sha256": population_sha,
            "reform_sha256": reform.reform_sha256(),
            "code": plain(code),
            "policy_artifacts": artifacts,
        }
    )
    households = tuple(results)
    return PopulationRun(
        run_id=run_id,
        results_sha256=results_sha256(households),
        population_id=population.population_id,
        population_version=population.version,
        population_sha256=population_sha,
        synthetic=population.synthetic,
        label=population.label,
        reform=reform,
        code=code,
        policy_artifacts=tuple(artifacts),
        overridden=tuple(overridden),
        validation=validation,
        households=households,
    )


def results_sha256(households: tuple[HouseholdResult, ...]) -> str:
    return _sha256([plain(h) for h in sorted(households, key=lambda h: h.household_id)])


def _run(
    record: ScenarioRecord,
    wff_policy_dir: Path,
    as_policy_dir: Path,
    wff: PolicyParameterSet,
    as_: PolicyParameterSet,
) -> CombinedResult:
    return run_combined_household(
        wff_policy_dir,
        as_policy_dir,
        record.household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
        wff_parameters=wff,
        as_parameters=as_,
    )


def _component(result: CombinedResult, component: str) -> ComponentOutcomeValue:
    c: ComponentResult = (
        result.accommodation_supplement
        if component == AS_COMPONENT
        else getattr(result.wff, component)
    )
    return ComponentOutcomeValue(outcome=c.outcome, value=c.value, code=c.code)


def _delta(
    base: ComponentOutcomeValue, new: ComponentOutcomeValue, status: RecordStatus
) -> ComponentDelta:
    if status is RecordStatus.NEEDS_REVIEW:
        return ComponentDelta("needs_review", base, new, None)
    if base.outcome == "calculated" and new.outcome == "calculated":
        assert base.value is not None and new.value is not None
        return ComponentDelta("calculated", base, new, new.value - base.value)
    if "needs_review" in (base.outcome, new.outcome):
        return ComponentDelta("needs_review", base, new, None)
    return ComponentDelta("unsupported", base, new, None)


def _sha256(content: Any) -> str:
    text = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
