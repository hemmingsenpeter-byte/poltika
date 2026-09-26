"""Task 11: the WFF/AS parameter loader.

Per BUILD_PLAN.md Task 11.1: requested policy + modelled date in; typed
parameter values or an explicit unresolved outcome out -- never a silent
substitution, never a network call, never a source-specific format. Reads
`policy.yaml` directly (already the canonical Poltika representation, not a
raw external source), consistent with REPOSITORY_STRUCTURE.md's dependency
boundary for `src/poltika/policy/`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Literal

import yaml

from poltika.common.errors import (
    ArtifactHashMismatchError,
    InvalidSourceCatalogError,
    PolicyNotApprovedError,
    PolicyVersionMismatchError,
    UnresolvedSourceIdError,
    UnsupportedSchemaVersionError,
)
from poltika.semantics.schemas.policy_spec import (
    ParameterReviewStatus,
    ParameterSpec,
    PolicySpec,
    PolicyStatus,
    covers,
)

# Task 11.2: reject any schema_version outside this set before interpreting
# anything else, per SCHEMA.md's Task 7 review response.
SUPPORTED_SCHEMA_VERSIONS = frozenset({"0.1"})

ResolutionOutcome = Literal["resolved", "needs_review", "unsupported"]


@dataclass(frozen=True)
class ParameterResolution:
    """The result of resolving one parameter for one modelled date.

    `outcome == "resolved"` is the only case where `value` is populated.
    Task 12 must not treat a missing `value` as zero -- `reason` explains
    why it's absent (Task 11.4: this is exactly how `in_work_base`'s
    `needs_review` status reaches the calculator contract, not resolved
    away inside the loader).
    """

    parameter_id: str
    outcome: ResolutionOutcome
    value: Decimal | None = None
    unit: str | None = None
    reason: str | None = None
    source_id: str | None = None
    locator: str | None = None
    # Task 31: the matched value's own interval and review status, carried
    # through so a provenance trace can say exactly which dated value was
    # used. `None` when no interval matched (outcome "unsupported").
    effective_from: date | None = None
    effective_to: date | None = None
    review_status: str | None = None


@dataclass(frozen=True)
class PolicyParameterSet:
    """All of one policy's parameters, resolved for one modelled date."""

    policy_id: str
    policy_version: str
    schema_version: str
    modelled_date: date
    resolutions: dict[str, ParameterResolution]
    # Task 31: SHA-256 of the files this set was resolved from, keyed by
    # path relative to the policy directory: "policy.yaml" and the declared
    # source_catalog (hashed from the exact bytes parsed), plus
    # "specification.md" and each decisions/DEC-*.md present when the set
    # was loaded. A provenance report verifies all of them before resolving
    # anything, so a later edit to any of them cannot silently stand in for
    # what the run used. Empty for a hand-built set.
    artifact_sha256: dict[str, str] = field(default_factory=dict)

    def get(self, parameter_id: str) -> ParameterResolution:
        try:
            return self.resolutions[parameter_id]
        except KeyError:
            raise KeyError(
                f"no such parameter '{parameter_id}' in policy '{self.policy_id}'"
            ) from None


def load_policy_spec(policy_yaml_path: Path) -> PolicySpec:
    """Parse and validate policy.yaml in isolation. Raises on any structural problem."""
    return _parse_policy_spec(policy_yaml_path.read_bytes())


def load_bound_policy_spec(policy_dir: Path, parameters: PolicyParameterSet) -> PolicySpec:
    """Re-read `policy.yaml` for a module's own checks on `parameters`, which
    were loaded from it, and refuse it if its bytes are not the ones the
    parameters were resolved from (their recorded `artifact_sha256`).
    Otherwise a file replaced between the two reads would have its reference
    period and intervals checked while the parameters, and the hash every
    trace records, came from the earlier file."""
    policy_yaml_bytes = (policy_dir / "policy.yaml").read_bytes()
    digest = _sha256(policy_yaml_bytes)
    if digest != parameters.artifact_sha256.get("policy.yaml"):
        raise ArtifactHashMismatchError(
            f"policy '{parameters.policy_id}' policy.yaml is not the file its parameters were loaded from"
        )
    # v0.2 Task 7.4: a population run calls this twice per household, and
    # parsing the YAML was nearly all of its time. The bytes are still read
    # and hashed on every call, so the check above is unchanged; only the
    # parse of bytes already seen is reused, by their hash. Callers get a
    # deep copy, so no caller can change another's spec.
    cached = _BOUND_SPECS.get(digest)
    if cached is None:
        cached = _parse_policy_spec(policy_yaml_bytes)
        if len(_BOUND_SPECS) >= _BOUND_SPEC_CACHE_SIZE:
            _BOUND_SPECS.pop(next(iter(_BOUND_SPECS)))
        _BOUND_SPECS[digest] = cached
    return cached.model_copy(deep=True)


_BOUND_SPEC_CACHE_SIZE = 16
_BOUND_SPECS: dict[str, PolicySpec] = {}


def _parse_policy_spec(policy_yaml_bytes: bytes) -> PolicySpec:
    raw = yaml.safe_load(policy_yaml_bytes)
    return PolicySpec.model_validate(raw)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _resolve_source_catalog_path(policy_dir: Path, source_catalog: str) -> Path:
    """Resolve policy.yaml's declared `source_catalog` safely, honouring it
    rather than silently assuming "sources.yaml" regardless of what's
    declared -- a policy.yaml naming a different catalogue must actually
    use it, or fail loudly.
    """
    candidate = Path(source_catalog)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise InvalidSourceCatalogError(
            f"source_catalog '{source_catalog}' must be a plain relative path "
            "within the policy directory, not an absolute path or one containing '..'"
        )

    resolved_dir = policy_dir.resolve()
    resolved = (policy_dir / candidate).resolve()
    if resolved != resolved_dir and resolved_dir not in resolved.parents:
        raise InvalidSourceCatalogError(
            f"source_catalog '{source_catalog}' resolves outside the policy "
            f"directory ({resolved} is not within {resolved_dir})"
        )
    if not resolved.is_file():
        raise InvalidSourceCatalogError(
            f"source_catalog '{source_catalog}' does not exist at {resolved}"
        )
    return resolved


def _resolve_source_ids(spec: PolicySpec, sources_yaml_bytes: bytes, sources_yaml_path: Path) -> None:
    raw = yaml.safe_load(sources_yaml_bytes)
    known_ids = {entry["id"] for entry in raw.get("sources", [])}
    for param in spec.parameters:
        for value in param.values:
            if value.source_id not in known_ids:
                raise UnresolvedSourceIdError(
                    f"parameter '{param.id}' value effective {value.effective_from} "
                    f"cites unknown source_id '{value.source_id}' "
                    f"(not present in {sources_yaml_path.name})"
                )


def load_policy_parameters(
    policy_dir: Path,
    modelled_date: date,
    *,
    requested_policy_version: str | None = None,
) -> PolicyParameterSet:
    """Load and resolve one policy's parameters for one modelled date.

    Raises for top-level gate failures -- unsupported schema version, policy
    not approved, a requested/actual policy_version mismatch, malformed or
    overlapping intervals (caught by ParameterSpec's own validator),
    unresolved source IDs. These are data-integrity problems Task 12 should
    never have to handle per-parameter.

    Never raises for an individual parameter having no matching interval or
    a non-approved `review_status` at the requested date: each parameter
    resolves independently to "resolved", "needs_review", or "unsupported",
    per SCHEMA.md's "No matching interval means unsupported, not the newest
    value and not zero." Task 12 owns deciding what a needs_review/
    unsupported parameter means for its component's outcome state; the
    loader's job ends at reporting the resolution faithfully (Task 11.4).
    """
    policy_yaml_path = policy_dir / "policy.yaml"

    # Each file is read once and parsed from those same bytes, so the
    # recorded hash is of exactly what was used, not a second read.
    policy_yaml_bytes = policy_yaml_path.read_bytes()
    spec = _parse_policy_spec(policy_yaml_bytes)

    if spec.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise UnsupportedSchemaVersionError(
            f"policy.yaml declares schema_version '{spec.schema_version}'; "
            f"this loader supports {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )

    if spec.status is not PolicyStatus.APPROVED:
        raise PolicyNotApprovedError(
            f"policy '{spec.policy_id}' has status '{spec.status.value}', not "
            "'approved'; a scaffold or draft must never be treated as executable"
        )

    if spec.policy_version is None:
        # Should be unreachable once status == approved, per SCHEMA.md's
        # "Version axes" -- but an invariant elsewhere is not a reason to
        # skip checking it here.
        raise PolicyNotApprovedError(
            f"policy '{spec.policy_id}' has status 'approved' but no policy_version set"
        )

    if (
        requested_policy_version is not None
        and requested_policy_version != spec.policy_version
    ):
        raise PolicyVersionMismatchError(
            f"requested policy_version '{requested_policy_version}' but "
            f"policy.yaml holds '{spec.policy_version}'"
        )

    sources_yaml_path = _resolve_source_catalog_path(policy_dir, spec.source_catalog)
    sources_yaml_bytes = sources_yaml_path.read_bytes()
    _resolve_source_ids(spec, sources_yaml_bytes, sources_yaml_path)

    resolutions = {
        param.id: _resolve_parameter(param, modelled_date) for param in spec.parameters
    }

    return PolicyParameterSet(
        policy_id=spec.policy_id,
        policy_version=spec.policy_version,
        schema_version=spec.schema_version,
        modelled_date=modelled_date,
        resolutions=resolutions,
        artifact_sha256={
            "policy.yaml": _sha256(policy_yaml_bytes),
            spec.source_catalog: _sha256(sources_yaml_bytes),
            **_specification_and_decision_hashes(policy_dir),
        },
    )


def check_preloaded_parameters(
    parameters: PolicyParameterSet, modelled_date: date, requested_policy_version: str
) -> None:
    """v0.2: a module given parameters loaded earlier (a population run
    loads them once) refuses a set resolved for another date or version, so
    passing them in can't change what a module calculates. Binding to the
    policy directory's files is still checked by `load_bound_policy_spec()`."""
    if parameters.modelled_date != modelled_date:
        raise ValueError(
            f"parameters were resolved for {parameters.modelled_date}, not {modelled_date}"
        )
    if parameters.policy_version != requested_policy_version:
        raise PolicyVersionMismatchError(
            f"parameters are policy_version '{parameters.policy_version}', "
            f"not the requested '{requested_policy_version}'"
        )


def _specification_and_decision_hashes(policy_dir: Path) -> dict[str, str]:
    """Hashes of the rule and decision texts a provenance report resolves
    against (Task 31.3), bound when the parameters are loaded rather than
    when a report is later built. Only files that exist are bound; a report
    refuses a run that did not bind what it needs."""
    hashes = {}
    specification = policy_dir / "specification.md"
    if specification.is_file():
        hashes["specification.md"] = _sha256(specification.read_bytes())
    for decision in sorted((policy_dir / "decisions").glob("DEC-*.md")):
        hashes[f"decisions/{decision.name}"] = _sha256(decision.read_bytes())
    return hashes


def _resolve_parameter(param: ParameterSpec, modelled_date: date) -> ParameterResolution:
    matching = [
        v for v in param.values if covers(v.effective_from, v.effective_to, modelled_date)
    ]

    if not matching:
        return ParameterResolution(
            parameter_id=param.id,
            outcome="unsupported",
            reason=f"no effective interval covers {modelled_date} for parameter '{param.id}'",
        )

    # ParameterSpec's own validator already rejects overlapping intervals at
    # load time, so at most one can match here; this documents that
    # invariant rather than silently relying on it.
    assert len(matching) == 1, (
        f"parameter '{param.id}' has overlapping intervals covering {modelled_date}; "
        "should have been rejected at load time"
    )
    value = matching[0]

    if value.review_status is not ParameterReviewStatus.APPROVED:
        return ParameterResolution(
            parameter_id=param.id,
            outcome="needs_review",
            reason=(
                f"parameter '{param.id}' value effective {value.effective_from} has "
                f"review_status '{value.review_status.value}', not 'approved' -- "
                "Task 11.4: this must reach the calculator contract, not be resolved "
                "to a number here"
            ),
            source_id=value.source_id,
            locator=value.locator,
            effective_from=value.effective_from,
            effective_to=value.effective_to,
            review_status=value.review_status.value,
        )

    return ParameterResolution(
        parameter_id=param.id,
        outcome="resolved",
        value=value.value,
        unit=param.unit.value,
        source_id=value.source_id,
        locator=value.locator,
        effective_from=value.effective_from,
        effective_to=value.effective_to,
        review_status=value.review_status.value,
    )
