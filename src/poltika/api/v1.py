"""Task B0.1.1 (ADR-0023): the read-only `/api/v1` catalogue for the web app.

`/api/v1/meta`, `/models`, `/datasets` and `/evidence` describe what this
deployment runs: its policy versions, model registry, dataset metadata and
the evidence behind each deployed policy. They read files and rearrange
what is recorded there; nothing here calculates an amount.

Each location is deploy-time configuration, as the policy directories are
(ADR-0011): `POLTIKA_MODEL_REGISTRY_PATH` and `POLTIKA_DATA_METADATA_DIR`,
falling back to a source checkout. When one is missing the route answers
503 with `code: "catalogue_unavailable"` rather than an empty list, so the
web app can say the catalogue is unavailable instead of "none".
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from datetime import date
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any, NoReturn

import yaml
from fastapi import APIRouter, HTTPException

from poltika.api.access import configured_credentials
from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.income_tax import INCOME_TAX_POLICY_DIR
from poltika.api.v1_schemas import (
    AccessInfo,
    BuildInfo,
    DatasetCatalogue,
    DatasetDetail,
    DatasetSnapshot,
    DatasetSummary,
    ErrorBody,
    EvidenceSource,
    Meta,
    ModelCatalogue,
    ModelDetail,
    ModelSummary,
    ParameterEvidence,
    Period,
    PolicyEvidence,
    PolicyVersion,
    PopulationInfo,
    PopulationSpecSummary,
    PreservedSourcesState,
    RuleEvidence,
    Variable,
)
from poltika.api.wff import WFF_POLICY_DIR
from poltika.common.errors import PoltikaError
from poltika.data.manifest import DatasetManifest
from poltika.data.metadata_index import (
    dataset_manifests,
    metadata_dir,
    population_spec_paths,
    variable_dictionary,
)
from poltika.engines.assurance.evidence import evidence_coverage
from poltika.engines.assurance.model_cards import REGISTRY_PATH, Registry, load_registry
from poltika.engines.assurance.provenance import catalogue_source_entry
from poltika.policy.loader import load_policy_spec
from poltika.scenarios.microsim.synthetic import SyntheticSpec
from poltika.semantics.schemas.source_catalog import SourceCatalog

router = APIRouter(prefix="/api/v1", tags=["catalogue"])

# What the web app may show. `policy_comparison` is the Workbench's
# two-option comparison; everything else is a declared future capability
# that stays hidden until a task delivers it (ADR-0023).
CAPABILITIES: dict[str, bool] = {
    "policy_comparison": True,
    "outcome_explorer": False,
    "evidence_search": False,
    "assurance_dashboard": False,
    "collaboration": False,
    "natural_language_scenarios": False,
    "monte_carlo": False,
    "advanced_distributions": False,
}

_BUILD_NOTE = (
    "The commit the hosting platform reports for this deployment (RENDER_GIT_COMMIT). "
    "Display only: it is not part of any scenario or run identity."
)
_RAW_BYTES_NOTE = (
    "Listed from its manifest. The raw snapshot's bytes are checked against the recorded "
    "SHA-256 wherever a calculation reads them (DatasetRegistry); this catalogue reads "
    "no snapshot."
)
_ARCHIVE_NOTE = (
    "Source Archive snapshots are preserved separately (ADR-0022) and are not yet exposed "
    "in this catalogue."
)
_UNAVAILABLE: dict[int | str, dict[str, Any]] = {503: {"model": ErrorBody}}
_LOOKUP: dict[int | str, dict[str, Any]] = {404: {"model": ErrorBody}, **_UNAVAILABLE}
# What reading a malformed or unreadable catalogue file can raise.
_UNREADABLE = (OSError, yaml.YAMLError, ValueError, KeyError, TypeError, PoltikaError)


def _fail(status: int, code: str, message: str) -> NoReturn:
    raise HTTPException(status_code=status, detail={"code": code, "message": message})


@contextmanager
def _catalogue_read(what: str) -> Iterator[None]:
    """A missing or invalid catalogue file is a 503 the web app can name,
    never a bare 500. The message names the catalogue, not the server path."""
    try:
        yield
    except _UNREADABLE as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "catalogue_unavailable", "message": f"The {what} here is invalid."},
        ) from exc


def _deployed_policy_dirs() -> tuple[Path, ...]:
    return (WFF_POLICY_DIR, AS_POLICY_DIR)


def _evidence_policy_dirs() -> tuple[Path, ...]:
    """The policies whose evidence is catalogued: the deployed ones plus the
    draft income-tax policy. Income tax is kept out of `_deployed_policy_dirs`
    (the meta, workbench and scenario-source views) because it has no version
    and no workbench surface; its evidence is shown with `policy_version: null`."""
    return (*_deployed_policy_dirs(), INCOME_TAX_POLICY_DIR)


@router.get("/meta", response_model=Meta, responses=_UNAVAILABLE)
def meta() -> Meta:
    """The deployment's configuration. A population that is not configured,
    or cannot be read, is reported as `null` so the rest stays available."""
    policies = []
    for policy_dir in _deployed_policy_dirs():
        with _catalogue_read("policy specification"):
            spec = load_policy_spec(policy_dir / "policy.yaml")
        policies.append(
            PolicyVersion(
                policy_id=spec.policy_id,
                policy_version=spec.policy_version,
                status=spec.status.value,
                reference_period=_interval(spec.reference_period.from_, spec.reference_period.to),
            )
        )
    return Meta(
        package_version=_package_version(),
        build=BuildInfo(commit=os.environ.get("RENDER_GIT_COMMIT") or None, note=_BUILD_NOTE),
        policies=policies,
        population=_population_info(),
        access=AccessInfo(password_required=configured_credentials() is not None),
        capabilities=dict(CAPABILITIES),
    )


def _package_version() -> str:
    try:
        return package_version("poltika")
    except PackageNotFoundError:
        return "unknown"


def _population_info() -> PopulationInfo | None:
    # Imported here: the microsimulation router owns the population cache.
    from poltika.api.microsim import population

    try:
        p = population()
    except (HTTPException, OSError, ValueError):
        return None
    return PopulationInfo(
        population_id=p.population_id, version=p.version, synthetic=p.synthetic, label=p.label
    )


def _registry() -> Registry:
    configured = os.environ.get("POLTIKA_MODEL_REGISTRY_PATH")
    path = Path(configured) if configured else REGISTRY_PATH
    with _catalogue_read("model registry"):
        if not path.is_file():
            _fail(503, "catalogue_unavailable", "The model registry is not configured here.")
        return _load_registry(str(path), path.stat().st_mtime_ns)


@lru_cache(maxsize=2)
def _load_registry(path: str, mtime_ns: int) -> Registry:
    return load_registry(Path(path))


@router.get("/models", response_model=ModelCatalogue, responses=_UNAVAILABLE)
def models() -> ModelCatalogue:
    registry = _registry()
    return ModelCatalogue(
        validation_levels=list(registry.validation_levels),
        models=[
            ModelSummary(
                id=m.id,
                name=m.name,
                kind=m.kind,
                version=m.version,
                purpose=m.purpose,
                policy_versions=dict(m.policy_versions),
                depends_on=list(m.depends_on),
                validation_level=m.validation.level,
                label=registry.label(m.id),
            )
            for m in registry.models
        ],
    )


@router.get("/models/{model_id}", response_model=ModelDetail, responses=_LOOKUP)
def model_detail(model_id: str) -> ModelDetail:
    registry = _registry()
    if model_id not in {m.id for m in registry.models}:
        _fail(404, "model_not_found", f"No model '{model_id}' is registered.")
    return ModelDetail(
        model=registry.model(model_id),
        label=registry.label(model_id),
        used_by=sorted(m.id for m in registry.models if model_id in m.depends_on),
        validation_levels=list(registry.validation_levels),
    )


def _metadata_root() -> Path:
    root = metadata_dir()
    with _catalogue_read("dataset catalogue"):
        if not root.is_dir():
            _fail(503, "catalogue_unavailable", "The dataset catalogue is not configured here.")
    return root


def _manifests(root: Path) -> list[DatasetManifest]:
    with _catalogue_read("dataset catalogue"):
        return dataset_manifests(root)


def _period(manifest: DatasetManifest) -> Period:
    observed = manifest.observation_reference_period
    return _interval(observed.from_, observed.to)


def _interval(start: date, end: date) -> Period:
    return Period.model_validate({"from": start, "to": end})


def _by_dataset(manifests: Iterable[DatasetManifest]) -> dict[str, list[DatasetManifest]]:
    grouped: dict[str, list[DatasetManifest]] = {}
    for m in manifests:
        grouped.setdefault(m.dataset_id, []).append(m)
    return grouped


@router.get("/datasets", response_model=DatasetCatalogue, responses=_UNAVAILABLE)
def datasets() -> DatasetCatalogue:
    root = _metadata_root()
    summaries = []
    for dataset_id, versions in _by_dataset(_manifests(root)).items():
        latest = max(versions, key=lambda m: m.raw_snapshot_version)
        summaries.append(
            DatasetSummary(
                dataset_id=dataset_id,
                source_organisation=latest.source_organisation,
                dataset_series=latest.dataset_series,
                latest_snapshot_version=latest.raw_snapshot_version,
                latest_vintage=latest.vintage,
                latest_retrieval_date=latest.retrieval_date,
                observation_reference_period=_period(latest),
                snapshots=len(versions),
                variables=len({v for m in versions for v in m.canonical_variable_mapping}),
            )
        )
    populations = []
    for path in population_spec_paths(root):
        with _catalogue_read("population specification"):
            spec = SyntheticSpec.model_validate(yaml.safe_load(path.read_text()))
        populations.append(
            PopulationSpecSummary(
                population_id=spec.population_id,
                version=spec.version,
                households=spec.households,
                sources=list(spec.sources),
            )
        )
    return DatasetCatalogue(
        datasets=summaries,
        populations=populations,
        preserved_sources=PreservedSourcesState(note=_ARCHIVE_NOTE),
    )


@router.get("/datasets/{dataset_id}", response_model=DatasetDetail, responses=_LOOKUP)
def dataset_detail(dataset_id: str) -> DatasetDetail:
    root = _metadata_root()
    versions = _by_dataset(_manifests(root)).get(dataset_id)
    if not versions:
        _fail(404, "dataset_not_found", f"No dataset '{dataset_id}' is catalogued.")
    with _catalogue_read("variable dictionary"):
        defined = variable_dictionary(root).by_id()
    mapped = sorted({v for m in versions for v in m.canonical_variable_mapping})
    return DatasetDetail(
        dataset_id=dataset_id,
        snapshots=[
            DatasetSnapshot(
                raw_snapshot_version=m.raw_snapshot_version,
                vintage=m.vintage,
                sha256=m.sha256,
                raw_file=m.raw_file,
                transformation_id=m.transformation_id,
                transformation_version=m.transformation_version,
                source_organisation=m.source_organisation,
                dataset_series=m.dataset_series,
                source_url_or_identifier=m.source_url_or_identifier,
                retrieval_date=m.retrieval_date,
                retrieval_method=m.retrieval_method.value,
                observation_reference_period=_period(m),
                units=m.units,
                geography_population=m.geography_population,
                canonical_variable_mapping=list(m.canonical_variable_mapping),
            )
            for m in sorted(versions, key=lambda m: m.raw_snapshot_version, reverse=True)
        ],
        variables=[
            Variable(
                id=v.id,
                meaning=v.meaning,
                unit=v.unit,
                frequency=v.frequency.value,
                price_basis=v.price_basis.value,
                price_base=v.price_base,
                measure=v.measure.value,
                geography_population=v.geography_population,
                valid_from=v.valid_from,
                valid_to=v.valid_to,
            )
            for v in (defined[i] for i in mapped if i in defined)
        ],
        undefined_variables=[i for i in mapped if i not in defined],
        raw_bytes_note=_RAW_BYTES_NOTE,
    )


@router.get("/evidence", response_model=list[PolicyEvidence], responses=_LOOKUP)
def evidence(policy: str | None = None) -> list[PolicyEvidence]:
    with _catalogue_read("evidence catalogue"):
        reports = [_policy_evidence(d) for d in _evidence_policy_dirs()]
    if policy is None:
        return reports
    chosen = [r for r in reports if r.policy_id == policy]
    if not chosen:
        _fail(404, "policy_not_found", f"No deployed policy '{policy}'.")
    return chosen


def _policy_evidence(policy_dir: Path) -> PolicyEvidence:
    coverage = evidence_coverage(policy_dir)
    spec = load_policy_spec(policy_dir / "policy.yaml")
    raw = yaml.safe_load((policy_dir / spec.source_catalog).read_text())
    catalog = SourceCatalog.model_validate(raw)
    entries = {e["id"]: e for e in raw["sources"]}
    sources = []
    for source in catalog.sources:
        entry = catalogue_source_entry(source.id, entries[source.id])
        sources.append(
            EvidenceSource(
                id=source.id,
                kind=source.kind.value,
                source_type=source.source_type.value,
                authority_rank=source.authority_rank,
                title=source.title,
                url=source.url,
                audit_version_url=entry["audit_version_url"],
                checked_on=entry["checked_on"],
                check_evidence=entry["check_evidence"],
            )
        )
    as_of = raw.get("as_of")
    return PolicyEvidence(
        policy_id=coverage["policy_id"],
        policy_version=coverage["policy_version"],
        catalogue_as_of=None if as_of is None else str(as_of),
        sources=sources,
        parameters=[ParameterEvidence(**p) for p in coverage["parameters"]],
        rules=[RuleEvidence(**r) for r in coverage["rules"]],
        summary=coverage["summary"],
        problems=coverage["problems"],
    )
