"""Pydantic models mirroring policy_specs/<policy>/policy.yaml's shape.

Deliberately minimal per Architecture Doctrine ("minimum abstraction demanded
by two real policies"): this models exactly what Task 11's parameter loader
needs to parse and validate. `assessment`/`inputs`/`components`/`outputs` are
modelled permissively (present and readable, not deeply validated) since
that's Task 12's concern, not Task 11's -- deepening them now, before a
second policy (Accommodation Supplement) exists to stress-test the shape,
would be exactly the premature abstraction the doctrine warns against.

See policy_specs/SCHEMA.md for the authoritative field-by-field description
this mirrors.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from itertools import pairwise

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PolicyStatus(str, Enum):
    """Top-level policy.yaml `status` values observed in this repo so far."""

    SCAFFOLD = "scaffold"
    DRAFT_PENDING_REVIEW = "draft_pending_review"
    APPROVED = "approved"


class ParameterReviewStatus(str, Enum):
    """Per-value `review_status` values observed in this repo so far.

    Deliberately a superset, not just {approved, needs_review}: earlier
    Task 10 drafts used draft_pending_independent_review before a value was
    reviewed at all, and nothing here should assume every future policy
    skips that state.
    """

    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review"
    DRAFT_PENDING_INDEPENDENT_REVIEW = "draft_pending_independent_review"
    DRAFT_PENDING_REVIEW = "draft_pending_review"


class ReferencePeriod(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    # "from" is a Python keyword; policy.yaml uses it as a plain YAML key, so
    # it's mapped via alias rather than a custom __init__ -- model_validate()
    # goes through Pydantic's core validator directly and does not call a
    # Python-level __init__ override for dict input.
    from_: date = Field(alias="from")
    to: date


class ParameterValue(BaseModel):
    """One effective-dated, source-linked value of a parameter."""

    model_config = ConfigDict(extra="allow")  # e.g. `note` is optional and free-form

    effective_from: date
    # Exclusive, per SCHEMA.md's "Version axes" -- and explicitly *optional*
    # there ("has effective_from, optional exclusive effective_to"), meaning
    # an open-ended final interval is a legitimate, schema-permitted shape,
    # not an omission to reject.
    effective_to: date | None = None
    # Decimal, not float: the approved WFF calculation sequence requires
    # exact decimal arithmetic, including a possible half-cent result from
    # the 27.5-cent abatement rate (0.275 * 3 as a float is
    # 0.8250000000000001; Decimal("0.275") * 3 is exactly 0.825). Pydantic
    # converts a YAML-parsed float via its str() round-trip, which is exact
    # for the decimal literals actually used here -- confirmed empirically,
    # not assumed.
    value: Decimal
    source_id: str
    locator: str
    review_status: ParameterReviewStatus

    @model_validator(mode="after")
    def _effective_to_after_effective_from(self) -> ParameterValue:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError(
                f"effective_to ({self.effective_to}) must be after "
                f"effective_from ({self.effective_from}) -- effective_to is exclusive"
            )
        return self


class ParameterSpec(BaseModel):
    """A named policy constant with one or more effective-dated values."""

    model_config = ConfigDict(extra="forbid")

    id: str
    value_type: str
    unit: str
    values: list[ParameterValue]

    @model_validator(mode="after")
    def _values_non_overlapping(self) -> ParameterSpec:
        # SCHEMA.md: "Intervals for the same key cannot overlap."
        ordered = sorted(self.values, key=lambda v: v.effective_from)
        for earlier, later in pairwise(ordered):
            if earlier.effective_to is None:
                # An open-ended interval covers [effective_from, infinity) --
                # by definition it overlaps any interval starting after it,
                # so it may only be the last (latest-starting) one.
                raise ValueError(
                    f"parameter '{self.id}' has an open-ended interval starting "
                    f"{earlier.effective_from} that is not the last interval -- "
                    f"a later interval starting {later.effective_from} also exists"
                )
            if later.effective_from < earlier.effective_to:
                raise ValueError(
                    f"parameter '{self.id}' has overlapping effective intervals: "
                    f"[{earlier.effective_from}, {earlier.effective_to}) and "
                    f"[{later.effective_from}, {later.effective_to})"
                )
        return self


class PolicySpec(BaseModel):
    """The full policy.yaml contract, per policy_specs/SCHEMA.md.

    `assessment`, `inputs`, `components`, and `outputs` are accepted as
    opaque data (whatever shape they arrive in) rather than deeply modelled
    -- Task 11 only needs to parse and validate the parameter/version/status
    surface; Task 12 owns interpreting the rest.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    policy_id: str
    policy_version: str | None
    status: PolicyStatus
    reference_period: ReferencePeriod
    source_catalog: str
    assessment: dict[str, object]
    inputs: list[dict[str, object]]
    parameters: list[ParameterSpec]
    components: list[dict[str, object]]
    outputs: dict[str, object]

    def parameter(self, parameter_id: str) -> ParameterSpec | None:
        return next((p for p in self.parameters if p.id == parameter_id), None)

    @model_validator(mode="after")
    def _no_duplicate_parameter_ids(self) -> PolicySpec:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for param in self.parameters:
            if param.id in seen:
                duplicates.add(param.id)
            seen.add(param.id)
        if duplicates:
            raise ValueError(
                f"duplicate parameter id(s) in policy.yaml: {sorted(duplicates)} -- "
                "a duplicate would silently overwrite the earlier entry when the "
                "loader indexes parameters by id"
            )
        return self
