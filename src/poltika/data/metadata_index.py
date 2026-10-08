"""Task B0.1.1 (ADR-0023): a read-only index of dataset metadata.

The web catalogue lists what Poltika's datasets are without reading any of
them. This module reads only files under the metadata directory:

- the raw-snapshot manifests (`datasets/*.yaml`), validated as
  `DatasetManifest` and checked against their file names;
- the population specification files (`populations/*.yaml`), returned as
  paths for the caller to validate with its own schema;
- the canonical variable dictionary (`variables/dictionary.yaml`).

It never opens a raw or processed snapshot, so a deployment that ships no
`raw/` directory can still describe its datasets. Checking a snapshot's
bytes against its manifest stays with `DatasetRegistry`, which every
calculation path uses. This is the one `poltika.data` module `api/` may
import (REPOSITORY_STRUCTURE.md, the dependency boundary).
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import ValidationError

from poltika.data.manifest import DatasetManifest
from poltika.data.registry import DatasetRegistryError
from poltika.semantics.variables import DataDictionary

# A source checkout's metadata directory. A deployment that has no checkout
# sets POLTIKA_DATA_METADATA_DIR (the pilot image does).
DEFAULT_METADATA_DIR = Path(__file__).resolve().parents[3] / "data" / "metadata"


def metadata_dir() -> Path:
    configured = os.environ.get("POLTIKA_DATA_METADATA_DIR")
    return Path(configured) if configured else DEFAULT_METADATA_DIR


def dataset_manifests(root: Path) -> list[DatasetManifest]:
    """Every manifest under `root/datasets`, ordered by dataset and snapshot
    version. A missing directory, malformed or misnamed manifest raises
    `DatasetRegistryError`; an existing empty directory is a valid empty
    catalogue."""
    manifests: list[DatasetManifest] = []
    directory = root / "datasets"
    if not directory.is_dir():
        raise DatasetRegistryError("The dataset manifest directory is missing.")
    for path in sorted(directory.glob("*.yaml")):
        try:
            manifest = DatasetManifest.model_validate(yaml.safe_load(path.read_text()))
        except ValidationError as exc:
            raise DatasetRegistryError(f"{path.name}: invalid manifest\n{exc}") from exc
        if path.name != manifest.manifest_name:
            raise DatasetRegistryError(f"{path.name}: must be named '{manifest.manifest_name}'")
        manifests.append(manifest)
    return sorted(manifests, key=lambda m: (m.dataset_id, m.raw_snapshot_version))


def population_spec_paths(root: Path) -> list[Path]:
    directory = root / "populations"
    return sorted(directory.glob("*.yaml")) if directory.is_dir() else []


def variable_dictionary(root: Path) -> DataDictionary:
    path = root / "variables" / "dictionary.yaml"
    return DataDictionary.model_validate(yaml.safe_load(path.read_text()))
