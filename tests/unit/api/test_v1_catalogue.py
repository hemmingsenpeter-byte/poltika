"""Task B0.1.1 (ADR-0023): the read-only `/api/v1` catalogue."""

from __future__ import annotations

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


def test_evidence_carries_every_source_with_its_rank_and_checks(client: TestClient) -> None:
    body = client.get("/api/v1/evidence").json()
    assert [p["policy_id"] for p in body] == ["working_for_families", "accommodation_supplement"]
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
    response = client.get("/api/v1/evidence", params={"policy": "income_tax"})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "policy_not_found"


def test_the_catalogue_is_in_the_openapi_contract(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    for path in ("/api/v1/meta", "/api/v1/models", "/api/v1/datasets", "/api/v1/evidence"):
        ok = schema["paths"][path]["get"]["responses"]["200"]["content"]["application/json"]
        assert ok["schema"], path
    assert "ModelDetail" in schema["components"]["schemas"]
