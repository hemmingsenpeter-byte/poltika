"""v0.2 Task 1.2: the raw-snapshot manifest.

One manifest per raw snapshot, at `data/metadata/datasets/<dataset_id>.v<N>.yaml`.
It carries the eleven provenance fields the Data Acquisition Doctrine and
`.claude/skills/provenance/SKILL.md` require, plus what makes the snapshot
checkable and resolvable:

- `dataset_id`, `raw_file` and `sha256`: which file this is and its exact bytes;
- `vintage`: the publication's release (a correction to the same release is
  a new `raw_snapshot_version`, a later release is a new `vintage`);
- `transformation_id`: the registered transformation that reads it
  (`transformation_version` is that transformation's version).

Every field is required. A field that can't be verified from the source
itself is a reason to stop and flag, not to guess (CLAUDE.md ground truth).
"""

from __future__ import annotations

import re
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_ID = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
_VARIABLE_ID = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class RetrievalMethod(str, Enum):
    MANUAL_DOWNLOAD = "manual_download"
    STATS_NZ_API = "stats_nz_api"


class ObservationPeriod(BaseModel):
    """The period the data covers, `[from, to)` like every other Poltika
    interval."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_: date = Field(alias="from")
    to: date

    @model_validator(mode="after")
    def _ordered(self) -> ObservationPeriod:
        if self.to <= self.from_:
            raise ValueError(f"observation period [{self.from_}, {self.to}) is empty")
        return self


class DatasetManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset_id: str
    raw_file: str
    sha256: str
    vintage: str
    transformation_id: str

    # The eleven provenance fields.
    source_organisation: str
    dataset_series: str
    source_url_or_identifier: str
    retrieval_date: date
    observation_reference_period: ObservationPeriod
    units: str
    geography_population: str
    retrieval_method: RetrievalMethod
    raw_snapshot_version: int = Field(ge=1)
    transformation_version: int = Field(ge=1)
    canonical_variable_mapping: list[str] = Field(min_length=1)

    @field_validator("dataset_id", "transformation_id")
    @classmethod
    def _snake_id(cls, value: str) -> str:
        if not _ID.match(value):
            raise ValueError(f"'{value}' is not a lower_snake_case id")
        return value

    @field_validator("sha256")
    @classmethod
    def _hex_digest(cls, value: str) -> str:
        if not _SHA256.match(value):
            raise ValueError("sha256 must be 64 lowercase hex characters")
        return value

    @field_validator("canonical_variable_mapping")
    @classmethod
    def _variable_ids(cls, value: list[str]) -> list[str]:
        bad = [v for v in value if not _VARIABLE_ID.match(v)]
        if bad:
            raise ValueError(f"not dotted canonical variable ids: {bad}")
        if len(set(value)) != len(value):
            raise ValueError("canonical_variable_mapping lists a variable twice")
        return value

    @field_validator(
        "vintage",
        "source_organisation",
        "dataset_series",
        "source_url_or_identifier",
        "units",
        "geography_population",
        "raw_file",
    )
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @property
    def manifest_name(self) -> str:
        return f"{self.dataset_id}.v{self.raw_snapshot_version}.yaml"
