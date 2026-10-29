"""Task B0.1.1 (ADR-0023): response models for the `/api/v1` catalogue.

These are the contracts the web frontend's generated TypeScript types come
from (`web/src/api/schema.gen.ts`, B0.1.3). They describe what already
exists -- policy, model and dataset metadata, and evidence -- and carry no
calculated amount.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from poltika.engines.assurance.model_cards import Model


class _Out(BaseModel):
    model_config = ConfigDict(frozen=True)


class Period(_Out):
    """`[from, to)`, like every other Poltika interval."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    from_: date = Field(alias="from")
    to: date


class ApiError(_Out):
    """The body of a 4xx/5xx from `/api/v1`: a stable code the UI keys its
    state on, and a message for people."""

    code: str
    message: str


class BuildInfo(_Out):
    commit: str | None
    note: str


class PolicyVersion(_Out):
    policy_id: str
    policy_version: str | None
    status: str
    reference_period: Period


class PopulationInfo(_Out):
    population_id: str
    version: int
    synthetic: bool
    label: str


class AccessInfo(_Out):
    password_required: bool


class Meta(_Out):
    service: Literal["poltika"] = "poltika"
    api_version: Literal["v1"] = "v1"
    package_version: str
    build: BuildInfo
    policies: list[PolicyVersion]
    population: PopulationInfo | None
    access: AccessInfo
    capabilities: dict[str, bool]


class ModelSummary(_Out):
    id: str
    name: str
    kind: str
    version: str
    purpose: str
    policy_versions: dict[str, str]
    depends_on: list[str]
    validation_level: str
    # The least mature validation level among the model and everything it
    # relies on (`Registry.label`): the one to show beside its results.
    label: str


class ModelCatalogue(_Out):
    validation_levels: list[str]
    models: list[ModelSummary]


class ModelDetail(_Out):
    model: Model
    label: str
    used_by: list[str]
    validation_levels: list[str]


class DatasetSnapshot(_Out):
    raw_snapshot_version: int
    vintage: str
    sha256: str
    raw_file: str
    transformation_id: str
    transformation_version: int
    source_organisation: str
    dataset_series: str
    source_url_or_identifier: str
    retrieval_date: date
    retrieval_method: str
    observation_reference_period: Period
    units: str
    geography_population: str
    canonical_variable_mapping: list[str]


class DatasetSummary(_Out):
    dataset_id: str
    source_organisation: str
    dataset_series: str
    latest_snapshot_version: int
    latest_vintage: str
    latest_retrieval_date: date
    observation_reference_period: Period
    snapshots: int
    variables: int


class PopulationSpecSummary(_Out):
    population_id: str
    version: int
    households: int
    synthetic: Literal[True] = True
    sources: list[str]


class PreservedSourcesState(_Out):
    exposed: Literal[False] = False
    note: str


class DatasetCatalogue(_Out):
    datasets: list[DatasetSummary]
    populations: list[PopulationSpecSummary]
    preserved_sources: PreservedSourcesState


class Variable(_Out):
    id: str
    meaning: str
    unit: str
    frequency: str
    price_basis: str
    price_base: str | None
    measure: str
    geography_population: str
    valid_from: date
    valid_to: date | None


class DatasetDetail(_Out):
    dataset_id: str
    snapshots: list[DatasetSnapshot]
    variables: list[Variable]
    # Variable ids a manifest maps that the dictionary does not define.
    undefined_variables: list[str]
    raw_bytes_note: str


class SourceCheck(_Out):
    field: str
    date: str


class CheckEvidence(_Out):
    field: str
    text: str


class EvidenceSource(_Out):
    id: str
    kind: str
    source_type: str
    authority_rank: int
    title: str
    url: str
    audit_version_url: str | None
    checked_on: list[SourceCheck]
    check_evidence: list[CheckEvidence]


class ParameterEvidence(_Out):
    parameter_id: str
    effective_from: str
    source_id: str
    locator: str | None
    review_status: str
    source_type: str | None = None
    authority_rank: int | None = None


class RuleEvidence(_Out):
    rule_id: str
    sources: list[str]
    cites_primary_legislation: bool


class PolicyEvidence(_Out):
    policy_id: str
    # Null for a draft policy that has no approved version (income tax).
    policy_version: str | None
    catalogue_as_of: str | None
    sources: list[EvidenceSource]
    parameters: list[ParameterEvidence]
    rules: list[RuleEvidence]
    summary: dict[str, int]
    problems: list[str]


class ErrorBody(_Out):
    """FastAPI's error envelope with `ApiError` inside: `{"detail": {...}}`."""

    detail: ApiError
