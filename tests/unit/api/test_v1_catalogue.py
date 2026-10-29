"""Task B0.1.1 (ADR-0023): the read-only `/api/v1` catalogue."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.api.v1 import CAPABILITIES
from poltika.api.wff import WFF_POLICY_DIR
from poltika.data.metadata_index import DEFAULT_METADATA_DIR
from poltika.engines.assurance.model_cards import REGISTRY_PATH, load_registry


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_meta_names_the_deployed_policies_and_hides_future_capabilities(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc123")
    body = client.get("/api/v1/meta").json()
    versions = {p["policy_id"]: p["policy_version"] for p in body["policies"]}
    assert versions == {"working_for_families": "0.1.0", "accommodation_supplement": "0.1.1"}
    wff = next(p for p in body["policies"] if p["policy_id"] == "working_for_families")
    assert wff["reference_period"] == {"from": "2026-04-01", "to": "2027-04-01"}
    assert body["build"]["commit"] == "abc123"
    assert "not part of any scenario or run identity" in body["build"]["note"]
    assert body["capabilities"] == CAPABILITIES
    assert body["capabilities"]["natural_language_scenarios"] is False


def test_meta_reports_access_and_a_missing_population(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("POLTIKA_POPULATION_PATH", raising=False)
    body = client.get("/api/v1/meta").json()
    assert body["access"] == {"password_required": False}
    assert body["population"] is None


def test_models_match_the_registry(client: TestClient) -> None:
    registry = load_registry()
    body = client.get("/api/v1/models").json()
    assert [m["id"] for m in body["models"]] == [m.id for m in registry.models]
    for m in body["models"]:
        assert m["label"] == registry.label(m["id"])
    assert body["validation_levels"] == list(registry.validation_levels)


def test_a_model_names_what_relies_on_it(client: TestClient) -> None:
    body = client.get("/api/v1/models/wff_engine").json()
    assert body["model"]["id"] == "wff_engine"
    assert body["model"]["limitations"]
    assert "combined_runner" in body["used_by"]


def test_an_unknown_model_is_a_coded_404(client: TestClient) -> None:
    response = client.get("/api/v1/models/no_such_model")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "model_not_found"


def test_a_missing_registry_is_unavailable_not_empty(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("POLTIKA_MODEL_REGISTRY_PATH", str(tmp_path / "absent.yaml"))
    response = client.get("/api/v1/models")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"


def test_the_registry_location_is_configurable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    copy = tmp_path / "registry.yaml"
    shutil.copy(REGISTRY_PATH, copy)
    monkeypatch.setenv("POLTIKA_MODEL_REGISTRY_PATH", str(copy))
    assert client.get("/api/v1/models").status_code == 200


def test_datasets_list_every_manifest_and_leave_the_archive_closed(client: TestClient) -> None:
    body = client.get("/api/v1/datasets").json()
    on_disk = {
        p.name.rsplit(".v", 1)[0] for p in (DEFAULT_METADATA_DIR / "datasets").glob("*.yaml")
    }
    assert {d["dataset_id"] for d in body["datasets"]} == on_disk
    wff = next(
        d for d in body["datasets"] if d["dataset_id"] == "ird_working_for_families_statistics"
    )
    assert wff["snapshots"] == 2 and wff["latest_snapshot_version"] == 2
    assert [p["population_id"] for p in body["populations"]] == ["nz_synthetic_development"]
    assert body["populations"][0]["synthetic"] is True
    assert body["preserved_sources"]["exposed"] is False


def test_a_dataset_lists_snapshots_newest_first_with_their_variables(client: TestClient) -> None:
    body = client.get("/api/v1/datasets/ird_working_for_families_statistics").json()
    assert [s["raw_snapshot_version"] for s in body["snapshots"]] == [2, 1]
    assert all(len(s["sha256"]) == 64 for s in body["snapshots"])
    mapped = {v for s in body["snapshots"] for v in s["canonical_variable_mapping"]}
    assert {v["id"] for v in body["variables"]} | set(body["undefined_variables"]) == mapped
    assert "reads no snapshot" in body["raw_bytes_note"]


def test_an_unknown_dataset_is_a_coded_404(client: TestClient) -> None:
    response = client.get("/api/v1/datasets/no_such_dataset")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "dataset_not_found"


def test_the_dataset_catalogue_works_without_raw_snapshots(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # A deployment ships metadata only: the catalogue must not need data/raw.
    shutil.copytree(DEFAULT_METADATA_DIR, tmp_path / "metadata")
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(tmp_path / "metadata"))
    assert client.get("/api/v1/datasets").status_code == 200


def test_a_misnamed_manifest_makes_the_catalogue_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "metadata"
    shutil.copytree(DEFAULT_METADATA_DIR, root)
    first = min((root / "datasets").glob("*.yaml"))
    first.rename(first.with_name("renamed.v9.yaml"))
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(root))
    response = client.get("/api/v1/datasets")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"


def test_a_missing_metadata_directory_is_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(tmp_path / "absent"))
    assert client.get("/api/v1/datasets").json()["detail"]["code"] == "catalogue_unavailable"


@pytest.mark.parametrize(
    "path", ["/api/v1/datasets", "/api/v1/datasets/ird_working_for_families_statistics"]
)
def test_a_missing_manifest_directory_is_unavailable_not_empty_or_not_found(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, path: str
) -> None:
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(tmp_path))
    response = client.get(path)
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"
    assert str(tmp_path) not in response.text


def test_an_existing_empty_manifest_directory_is_a_valid_empty_catalogue(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "datasets").mkdir()
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(tmp_path))
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    assert response.json()["datasets"] == []
    response = client.get("/api/v1/datasets/no_such_dataset")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "dataset_not_found"


def test_a_missing_dictionary_is_unavailable_not_undefined_variables(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "metadata"
    shutil.copytree(DEFAULT_METADATA_DIR, root)
    (root / "variables" / "dictionary.yaml").unlink()
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(root))
    response = client.get("/api/v1/datasets/ird_working_for_families_statistics")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"
    assert str(tmp_path) not in response.text


@pytest.mark.skipif(os.name != "posix", reason="requires POSIX directory permissions")
@pytest.mark.parametrize(
    ("path", "configuration"),
    [
        ("/api/v1/models", "POLTIKA_MODEL_REGISTRY_PATH"),
        ("/api/v1/datasets", "POLTIKA_DATA_METADATA_DIR"),
    ],
)
def test_an_unreadable_catalogue_ancestor_is_unavailable_not_a_500(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    path: str,
    configuration: str,
) -> None:
    private = tmp_path / "private"
    private.mkdir()
    asset = private / "asset"
    if configuration == "POLTIKA_MODEL_REGISTRY_PATH":
        shutil.copy(REGISTRY_PATH, asset)
    else:
        asset.mkdir()
    monkeypatch.setenv(configuration, str(asset))
    private.chmod(0)
    try:
        if os.access(private, os.X_OK):
            pytest.skip("the current user can bypass directory permissions")
        response = client.get(path)
    finally:
        private.chmod(0o700)
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"
    assert str(tmp_path) not in response.text


def test_evidence_carries_every_source_with_its_rank_and_checks(client: TestClient) -> None:
    body = client.get("/api/v1/evidence").json()
    assert [p["policy_id"] for p in body] == [
        "working_for_families",
        "accommodation_supplement",
        "income_tax",
    ]
    for policy in body:
        catalogue = yaml.safe_load(
            (WFF_POLICY_DIR.parent / policy["policy_id"] / "sources.yaml").read_text()
        )
        assert [s["id"] for s in policy["sources"]] == [s["id"] for s in catalogue["sources"]]
        assert all(1 <= s["authority_rank"] <= 4 for s in policy["sources"])
        assert policy["parameters"] and policy["rules"]
        assert policy["problems"] == []
        assert policy["summary"]["parameter_values"] == len(policy["parameters"])


def test_evidence_filters_by_policy_and_rejects_an_undeployed_one(client: TestClient) -> None:
    body = client.get("/api/v1/evidence", params={"policy": "accommodation_supplement"}).json()
    assert [p["policy_id"] for p in body] == ["accommodation_supplement"]
    response = client.get("/api/v1/evidence", params={"policy": "no_such_policy"})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "policy_not_found"


def test_evidence_lists_the_draft_income_tax_policy_unversioned_and_unapproved(client: TestClient) -> None:
    (policy,) = client.get("/api/v1/evidence", params={"policy": "income_tax"}).json()
    assert policy["policy_version"] is None
    assert policy["summary"]["approved_parameter_values"] == 0
    assert {p["review_status"] for p in policy["parameters"]} == {"needs_review"}
    assert policy["problems"] == []
    meta = client.get("/api/v1/meta").json()
    assert "income_tax" not in [p["policy_id"] for p in meta["policies"]]


def test_the_catalogue_is_in_the_openapi_contract(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    for path in ("/api/v1/meta", "/api/v1/models", "/api/v1/datasets", "/api/v1/evidence"):
        ok = schema["paths"][path]["get"]["responses"]["200"]["content"]["application/json"]
        assert ok["schema"], path
    assert "ModelDetail" in schema["components"]["schemas"]


@pytest.mark.parametrize("content", ["a: [unclosed", "models: 5"])
def test_an_invalid_registry_is_unavailable_not_a_500(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, content: str
) -> None:
    broken = tmp_path / "registry.yaml"
    broken.write_text(content)
    monkeypatch.setenv("POLTIKA_MODEL_REGISTRY_PATH", str(broken))
    for path in ("/api/v1/models", "/api/v1/models/wff_engine"):
        response = client.get(path)
        assert response.status_code == 503, path
        assert response.json()["detail"]["code"] == "catalogue_unavailable"
        assert str(tmp_path) not in response.text


@pytest.mark.parametrize(
    ("relative", "path"),
    [
        ("datasets/stats_nz_household_net_worth.v1.yaml", "/api/v1/datasets"),
        ("populations/nz_synthetic_development.v1.yaml", "/api/v1/datasets"),
        ("variables/dictionary.yaml", "/api/v1/datasets/stats_nz_household_net_worth"),
    ],
)
def test_an_unparseable_metadata_file_is_unavailable_not_a_500(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, relative: str, path: str
) -> None:
    root = tmp_path / "metadata"
    shutil.copytree(DEFAULT_METADATA_DIR, root)
    (root / relative).write_text("key: [unclosed")
    monkeypatch.setenv("POLTIKA_DATA_METADATA_DIR", str(root))
    response = client.get(path)
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"
    assert str(tmp_path) not in response.text


def test_an_invalid_policy_catalogue_makes_evidence_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    copy = tmp_path / "accommodation_supplement"
    shutil.copytree(WFF_POLICY_DIR.parent / "accommodation_supplement", copy)
    (copy / "sources.yaml").write_text("sources: [unclosed")
    monkeypatch.setattr("poltika.api.v1._deployed_policy_dirs", lambda: (WFF_POLICY_DIR, copy))
    response = client.get("/api/v1/evidence")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "catalogue_unavailable"


def test_meta_survives_an_unreadable_population(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    corrupt = tmp_path / "population.json"
    corrupt.write_text("{not json")
    monkeypatch.setenv("POLTIKA_POPULATION_PATH", str(corrupt))
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    assert response.json()["population"] is None


def test_lookups_document_their_404s(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    for path in ("/api/v1/models/{model_id}", "/api/v1/datasets/{dataset_id}", "/api/v1/evidence"):
        assert {"404", "503"} <= set(paths[path]["get"]["responses"]), path
