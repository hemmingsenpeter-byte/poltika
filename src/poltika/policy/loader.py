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
    # Task 31: SHA-256 of the exact bytes this set was resolved from, keyed
    # by file name relative to the policy directory ("policy.yaml" and the
    # declared source_catalog). A provenance report verifies these before
    # resolving anything, so a later edit to either file cannot silently
    # stand in for what a run actually used. Empty for a hand-built set.
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
        },
    )


def _covers(value_effective_from: date, value_effective_to: date | None, modelled_date: date) -> bool:
    if modelled_date < value_effective_from:
        return False
    # effective_to is exclusive when present; None means open-ended (no upper bound).
    return value_effective_to is None or modelled_date < value_effective_to


def _resolve_parameter(param: ParameterSpec, modelled_date: date) -> ParameterResolution:
    matching = [
        v for v in param.values if _covers(v.effective_from, v.effective_to, modelled_date)
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
