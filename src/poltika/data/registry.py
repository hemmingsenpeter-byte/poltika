"""v0.2 Task 1.4: the dataset registry.

Loads every manifest under `<data_root>/metadata/datasets/` and checks the
snapshots against them:

- each manifest's file name is `<dataset_id>.v<raw_snapshot_version>.yaml`;
- each raw file sits under `<data_root>/raw/` and its SHA-256 matches;
- no two manifests claim the same raw file (the file name already makes
  each `(dataset_id, raw_snapshot_version)` unique);
- every file under `raw/` (other than README.md) has a manifest.

Any failure raises `DatasetRegistryError`: a snapshot that doesn't match its
manifest must never be read. `resolve()` answers "dataset X as at vintage V",
or the latest snapshot when no vintage is given.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from poltika.common.errors import PoltikaError
from poltika.data.manifest import DatasetManifest


class DatasetRegistryError(PoltikaError):
    """A manifest or raw snapshot is missing, malformed or doesn't match."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Snapshot:
    manifest: DatasetManifest
    path: Path


class DatasetRegistry:
    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        self._snapshots = _load(data_root)

    def snapshots(self) -> list[Snapshot]:
        return sorted(
            self._snapshots,
            key=lambda s: (s.manifest.dataset_id, s.manifest.raw_snapshot_version),
        )

    def resolve(self, dataset_id: str, vintage: str | None = None) -> Snapshot:
        """The snapshot of `dataset_id` for `vintage`, or its latest snapshot.

        The highest matching `raw_snapshot_version` wins: a correction
        supersedes the file it corrects without editing it.
        """
        candidates = [
            s
            for s in self._snapshots
            if s.manifest.dataset_id == dataset_id
            and (vintage is None or s.manifest.vintage == vintage)
        ]
        if not candidates:
            wanted = dataset_id if vintage is None else f"{dataset_id} at vintage '{vintage}'"
            raise DatasetRegistryError(f"no snapshot of {wanted}")
        return max(candidates, key=lambda s: s.manifest.raw_snapshot_version)


def _load(data_root: Path) -> list[Snapshot]:
    raw_root = data_root / "raw"
    manifest_dir = data_root / "metadata" / "datasets"
    snapshots: list[Snapshot] = []
    for manifest_path in sorted(manifest_dir.glob("*.yaml")) if manifest_dir.is_dir() else []:
        try:
            manifest = DatasetManifest.model_validate(yaml.safe_load(manifest_path.read_text()))
        except ValidationError as exc:
            raise DatasetRegistryError(f"{manifest_path.name}: invalid manifest\n{exc}") from exc
        if manifest_path.name != manifest.manifest_name:
            raise DatasetRegistryError(
                f"{manifest_path.name}: must be named '{manifest.manifest_name}'"
            )
        raw_path = (raw_root / manifest.raw_file).resolve()
        if not raw_path.is_relative_to(raw_root.resolve()):
            raise DatasetRegistryError(f"{manifest_path.name}: raw_file is outside raw/")
        if not raw_path.is_file():
            raise DatasetRegistryError(
                f"{manifest_path.name}: raw file '{manifest.raw_file}' is missing"
            )
        actual = sha256_of(raw_path)
        if actual != manifest.sha256:
            raise DatasetRegistryError(
                f"{manifest_path.name}: '{manifest.raw_file}' has sha256 {actual}, "
                f"the manifest records {manifest.sha256}. A raw snapshot is never edited; "
                "a correction is a new raw_snapshot_version."
            )
        snapshots.append(Snapshot(manifest=manifest, path=raw_path))

    _check_unique(snapshots)
    if raw_root.is_dir():
        claimed = {s.path for s in snapshots}
        orphans = sorted(
            str(p.relative_to(raw_root))
            for p in raw_root.rglob("*")
            if p.is_file() and p.name != "README.md" and p.resolve() not in claimed
        )
        if orphans:
            raise DatasetRegistryError(f"raw files with no manifest: {orphans}")
    return snapshots


def _check_unique(snapshots: list[Snapshot]) -> None:
    # (dataset_id, raw_snapshot_version) is unique by manifest file name, so
    # only a shared raw file is left to catch.
    seen: dict[Path, str] = {}
    for s in snapshots:
        name = s.manifest.manifest_name
        if s.path in seen:
            raise DatasetRegistryError(f"{name} and {seen[s.path]} claim the same raw file")
        seen[s.path] = name
