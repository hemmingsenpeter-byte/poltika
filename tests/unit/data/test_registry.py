from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from poltika.data.registry import DatasetRegistry, DatasetRegistryError
from tests.unit.data.conftest import RAW_CSV, manifest_for

REPO_DATA = Path(__file__).resolve().parents[3] / "data"


def test_repository_data_matches_its_manifests() -> None:
    DatasetRegistry(REPO_DATA)


def test_resolves_latest_and_by_vintage(data_root: Callable[..., Path]) -> None:
    corrected = RAW_CSV + b"2022-01-01,2023-01-01,110\n"
    root = data_root(
        (RAW_CSV, manifest_for(RAW_CSV)),
        (
            corrected,
            manifest_for(
                corrected,
                raw_file="test_org/synthetic_series/v2/series.csv",
                raw_snapshot_version=2,
                vintage="synthetic-release-2",
            ),
        ),
    )
    registry = DatasetRegistry(root)
    assert registry.resolve("synthetic_series").manifest.raw_snapshot_version == 2
    assert (
        registry.resolve("synthetic_series", "synthetic-release-1").manifest.raw_snapshot_version
        == 1
    )
    with pytest.raises(DatasetRegistryError, match="no snapshot"):
        registry.resolve("synthetic_series", "synthetic-release-9")
    with pytest.raises(DatasetRegistryError, match="no snapshot"):
        registry.resolve("other")


def test_edited_snapshot_fails(data_root: Callable[..., Path]) -> None:
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)))
    (root / "raw" / "test_org/synthetic_series/v1/series.csv").write_bytes(RAW_CSV + b"\n")
    with pytest.raises(DatasetRegistryError, match="never edited"):
        DatasetRegistry(root)


def test_missing_raw_file_fails(data_root: Callable[..., Path]) -> None:
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)))
    (root / "raw" / "test_org/synthetic_series/v1/series.csv").unlink()
    with pytest.raises(DatasetRegistryError, match="missing"):
        DatasetRegistry(root)


def test_raw_file_without_manifest_fails(data_root: Callable[..., Path]) -> None:
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)))
    (root / "raw" / "stray.csv").write_bytes(b"x")
    with pytest.raises(DatasetRegistryError, match="no manifest"):
        DatasetRegistry(root)


def test_manifest_name_must_match(data_root: Callable[..., Path]) -> None:
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)))
    manifests = root / "metadata" / "datasets"
    (manifests / "synthetic_series.v1.yaml").rename(manifests / "renamed.yaml")
    with pytest.raises(DatasetRegistryError, match="must be named"):
        DatasetRegistry(root)


def test_raw_file_outside_raw_fails(data_root: Callable[..., Path]) -> None:
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)))
    manifest = manifest_for(RAW_CSV, raw_file="../metadata/variables/dictionary.yaml")
    (root / "metadata" / "datasets" / "synthetic_series.v1.yaml").write_text(
        yaml.safe_dump(manifest)
    )
    (root / "raw" / "test_org/synthetic_series/v1/series.csv").unlink()
    with pytest.raises(DatasetRegistryError, match="outside raw"):
        DatasetRegistry(root)


def test_two_manifests_for_one_file_fail(data_root: Callable[..., Path]) -> None:
    root = data_root(
        (RAW_CSV, manifest_for(RAW_CSV)),
        (RAW_CSV, manifest_for(RAW_CSV, raw_snapshot_version=2)),
    )
    with pytest.raises(DatasetRegistryError, match="same raw file"):
        DatasetRegistry(root)
