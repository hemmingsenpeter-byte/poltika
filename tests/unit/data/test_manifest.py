from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from poltika.data.manifest import DatasetManifest, RetrievalMethod
from tests.unit.data.conftest import RAW_CSV, manifest_for

PROVENANCE_FIELDS = [
    "source_organisation",
    "dataset_series",
    "source_url_or_identifier",
    "retrieval_date",
    "observation_reference_period",
    "units",
    "geography_population",
    "retrieval_method",
    "raw_snapshot_version",
    "transformation_version",
    "canonical_variable_mapping",
]


def test_valid_manifest() -> None:
    m = DatasetManifest.model_validate(manifest_for(RAW_CSV))
    assert m.retrieval_method is RetrievalMethod.MANUAL_DOWNLOAD
    assert m.manifest_name == "synthetic_series.v1.yaml"


@pytest.mark.parametrize("field", PROVENANCE_FIELDS)
def test_every_provenance_field_is_required(field: str) -> None:
    manifest = manifest_for(RAW_CSV)
    del manifest[field]
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(manifest)


def test_the_eleven_fields_are_all_modelled() -> None:
    assert len(PROVENANCE_FIELDS) == 11
    assert set(PROVENANCE_FIELDS) <= set(DatasetManifest.model_fields)


@pytest.mark.parametrize(
    "overrides",
    [
        {"units": "  "},
        {"sha256": "ABC"},
        {"dataset_id": "Bad-Id"},
        {"retrieval_method": "scraped"},
        {"raw_snapshot_version": 0},
        {"canonical_variable_mapping": []},
        {"canonical_variable_mapping": ["nodots"]},
        {"canonical_variable_mapping": ["a.b", "a.b"]},
        {"observation_reference_period": {"from": "2022-01-01", "to": "2022-01-01"}},
        {"unexpected": "field"},
    ],
)
def test_rejects(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(manifest_for(RAW_CSV, **overrides))
