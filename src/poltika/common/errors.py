"""Shared exception types for the policy loader and, later, other engines."""

from __future__ import annotations


class PoltikaError(Exception):
    """Base class for all Poltika-raised errors."""


class UnsupportedSchemaVersionError(PoltikaError):
    """The policy file declares a schema_version this loader doesn't support."""


class PolicyNotApprovedError(PoltikaError):
    """The policy file's top-level status is not "approved".

    Per SCHEMA.md's Task 7 review response: a scaffold or draft must never be
    treated as an approved executable specification, regardless of whether a
    policy_version happens to be set.
    """


class PolicyVersionMismatchError(PoltikaError):
    """A specific policy_version was requested but the file holds a different one."""


class InvalidParameterIntervalsError(PoltikaError):
    """A parameter's effective-dated values overlap or are otherwise malformed.

    This is a data-integrity error in policy.yaml itself, raised at load time
    -- distinct from a single date simply falling outside every interval,
    which is a normal, expected `unsupported` resolution outcome, not an error.
    """


class UnresolvedSourceIdError(PoltikaError):
    """A parameter value's source_id does not resolve against the declared
    source_catalog."""


class InvalidSourceCatalogError(PoltikaError):
    """A policy's declared `source_catalog` is unsafe or doesn't exist.

    Covers both an escaping/absolute path and a simply-missing file --
    the declared value is never silently substituted with a hardcoded
    "sources.yaml" guess.
    """


class ProvenanceError(PoltikaError):
    """A provenance report cannot be built faithfully -- e.g. a result has
    no trace, or a cited source, rule, or decision does not resolve. The
    report is refused rather than built with gaps (Task 31)."""


class ArtifactHashMismatchError(ProvenanceError):
    """A file a run used no longer matches the hash its trace recorded.

    A report must describe what the run actually used; resolving sources or
    rules against a since-edited file would silently substitute current
    content for historical content (BUILD_PLAN.md Task 31.3)."""
