"""Task 33.2/33.3: the stored scenario routes end to end (FastAPI TestClient)
against a throwaway real PostgreSQL server, plus the route-level status
mapping for store errors."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.api.scenarios import get_store
from poltika.common.errors import ImmutableRecordError, StoreError
from tests.unit.api.test_household_api import _payload

client = TestClient(app)
UNKNOWN_ID = "0" * 64


@pytest.fixture
def stored_database(database_url: str, monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("POLTIKA_DATABASE_URL", database_url)
    return database_url


@pytest.mark.postgres
def test_create_fetch_replay_and_rerun(stored_database: str) -> None:
    created = client.post("/scenarios", json=_payload())
    assert created.status_code == 201
    body = created.json()
    # Same household result as /household/calculate (golden g2).
    assert body["accommodation_supplement"]["value"] == "220"
    assert body == client.post("/household/calculate", json=_payload()).json()

    result_id = body["result_id"]
    fetched = client.get(f"/scenarios/{result_id}")
    assert fetched.status_code == 200
    stored = fetched.json()
    assert stored["scenario_id"] == body["scenario_id"]
    assert stored["result"]["accommodation_supplement"]["value"] == "220"
    assert stored["record"]["as_lookup_date"] == "2026-06-01"

    replayed = client.post(f"/scenarios/{result_id}/replay")
    assert replayed.json() == {"result_id": result_id, "reproduced": True}

    rerun = client.post(f"/scenarios/{result_id}/rerun").json()
    assert rerun["original_result_id"] == result_id
    assert rerun["changed_artifacts"] == []
    assert rerun["result_changed"] is False
    assert client.get(f"/scenarios/{rerun['new_result_id']}").status_code == 200


@pytest.mark.postgres
def test_unknown_result_id_is_404(stored_database: str) -> None:
    for response in (
        client.get(f"/scenarios/{UNKNOWN_ID}"),
        client.post(f"/scenarios/{UNKNOWN_ID}/replay"),
        client.post(f"/scenarios/{UNKNOWN_ID}/rerun"),
    ):
        assert response.status_code == 404
        assert response.json() == {"detail": f"no stored run {UNKNOWN_ID}"}


def test_malformed_result_id_is_422(monkeypatch: pytest.MonkeyPatch) -> None:
    # Never connected: validation fails before the store is used.
    monkeypatch.setenv("POLTIKA_DATABASE_URL", "postgresql+psycopg://nobody@127.0.0.1:1/none")
    assert client.get("/scenarios/not-a-hash").status_code == 422


def test_store_routes_are_503_when_no_database_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("POLTIKA_DATABASE_URL", raising=False)
    assert client.post("/scenarios", json=_payload()).status_code == 503
    assert client.get(f"/scenarios/{UNKNOWN_ID}").status_code == 503
    # The stateless route is unaffected.
    assert client.post("/household/calculate", json=_payload()).status_code == 200


class _FailingStore:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def get_run(self, result_id: str) -> None:
        raise self.exc


@pytest.fixture
def failing_store() -> Iterator[type[_FailingStore]]:
    yield _FailingStore
    app.dependency_overrides.clear()


def test_immutable_record_conflict_is_409(failing_store: type[_FailingStore]) -> None:
    app.dependency_overrides[get_store] = lambda: failing_store(
        ImmutableRecordError("run abc is already stored with different result_json")
    )
    response = client.get(f"/scenarios/{UNKNOWN_ID}")
    assert response.status_code == 409


def test_other_store_errors_are_generic_500s(failing_store: type[_FailingStore]) -> None:
    secret = "/private/var/secret/path/policy.yaml no longer matches"
    app.dependency_overrides[get_store] = lambda: failing_store(StoreError(secret))
    response = TestClient(app, raise_server_exceptions=False).get(f"/scenarios/{UNKNOWN_ID}")
    assert response.status_code == 500
    assert "secret" not in response.text
