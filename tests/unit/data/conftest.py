"""Synthetic snapshots for the data-layer tests. Every value here is made up
and labelled as such; none describes a real publication."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

RAW_CSV = b"period_start,period_end,value\n2020-01-01,2021-01-01,100\n2021-01-01,2022-01-01,105\n"

VARIABLE: dict[str, Any] = {
    "id": "test.synthetic.level",
    "meaning": "Synthetic test series",
    "unit": "index",
    "frequency": "annual",
    "price_basis": "not_applicable",
    "measure": "stock",
    "geography_population": "synthetic",
    "valid_from": "2000-01-01",
}


def manifest_for(raw: bytes, **overrides: Any) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "dataset_id": "synthetic_series",
        "raw_file": "test_org/synthetic_series/v1/series.csv",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "vintage": "synthetic-release-1",
        "transformation_id": "synthetic_csv",
        "source_organisation": "Synthetic test organisation",
        "dataset_series": "Synthetic test series",
        "source_url_or_identifier": "test://synthetic",
        "retrieval_date": "2026-09-26",
        "observation_reference_period": {"from": "2020-01-01", "to": "2022-01-01"},
        "units": "index",
        "geography_population": "synthetic",
        "retrieval_method": "manual_download",
        "raw_snapshot_version": 1,
        "transformation_version": 1,
        "canonical_variable_mapping": ["test.synthetic.level"],
    }
    manifest.update(overrides)
    return manifest


@pytest.fixture
def data_root(tmp_path: Path) -> Callable[..., Path]:
    """Writes snapshots as `(raw_bytes, manifest_dict)` pairs and a dictionary."""

    def build(
        *snapshots: tuple[bytes, dict[str, Any]],
        variables: list[dict[str, Any]] | None = None,
    ) -> Path:
        root = tmp_path / "data"
        (root / "metadata" / "datasets").mkdir(parents=True, exist_ok=True)
        (root / "metadata" / "variables").mkdir(parents=True, exist_ok=True)
        for raw, manifest in snapshots:
            raw_path = root / "raw" / manifest["raw_file"]
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(raw)
            name = f"{manifest['dataset_id']}.v{manifest['raw_snapshot_version']}.yaml"
            (root / "metadata" / "datasets" / name).write_text(yaml.safe_dump(manifest))
        dictionary = {"variables": [VARIABLE] if variables is None else variables}
        (root / "metadata" / "variables" / "dictionary.yaml").write_text(yaml.safe_dump(dictionary))
        return root

    return build
