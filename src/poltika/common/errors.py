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


class StoreError(PoltikaError):
    """The scenario store cannot save or replay faithfully (Task 32)."""


class ImmutableRecordError(StoreError):
    """An id already stored with different content: runs are never edited in
    place (ADR-0013, BUILD_PLAN Task 32.2)."""


class StoredRunNotFoundError(StoreError):
    """No stored run has the requested result id (Task 33.2: 404)."""


class UnknownUnitError(PoltikaError):
    """A unit id is not in the unit registry (Task 2.2)."""


class UnitConversionError(PoltikaError):
    """A unit conversion or rescale is refused (Task 2.2)."""


class IncompatibleUnitsError(UnitConversionError):
    """A rescale between units that differ in more than scale: dimension,
    price basis or currency."""


class MissingConversionRuleError(UnitConversionError):
    """No named, sourced conversion rule exists for the requested units.
    A conversion such as nominal to real is never implicit."""


class UnknownPeriodTypeError(PoltikaError):
    """A period type id is not in the closed period-type vocabulary
    (`semantics/periods.py`, Programme Task 2.3)."""


class UnknownPeriodRelationError(PoltikaError):
    """A period relation id is not in the registered set of named rules."""


class PeriodRelationMismatchError(PoltikaError):
    """A registered period relation was applied to periods of other types."""


class PeriodConversionRefusedError(PoltikaError):
    """A value conversion between period types was asked for, but no named
    rule with a cited source exists for it (v0.2 D8: none without a stated
    rule). Nothing is converted and no default factor is used."""
