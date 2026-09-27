"""Password protection for a hosted pilot (`api/access.py`)."""

from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient

from poltika.api.access import AccessConfigError, configured_credentials
from poltika.api.main import app


def _basic(user: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def protected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLTIKA_ACCESS_PASSWORD", "s3cret pass")
    monkeypatch.delenv("POLTIKA_ACCESS_USER", raising=False)


def test_open_without_a_password(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("POLTIKA_REQUIRE_ACCESS_PASSWORD", raising=False)
    assert client.get("/analyst").status_code == 200


@pytest.mark.usefixtures("protected")
@pytest.mark.parametrize("path", ["/analyst", "/analyst/examples", "/docs", "/openapi.json"])
def test_every_route_needs_the_password(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"].startswith('Basic realm="Poltika pilot"')
    assert response.headers["cache-control"] == "no-store"
    assert client.get(path, headers=_basic("pilot", "s3cret pass")).status_code == 200


@pytest.mark.usefixtures("protected")
def test_post_routes_are_protected_too(client: TestClient) -> None:
    assert client.post("/household/calculate", json={}).status_code == 401


@pytest.mark.usefixtures("protected")
@pytest.mark.parametrize(
    "headers",
    [
        _basic("pilot", "wrong"),
        _basic("someone", "s3cret pass"),
        _basic("pilot", "s3cret pass "),
        {"Authorization": "Basic not-base64!"},
        {"Authorization": "Basic " + base64.b64encode(b"no-colon").decode()},
        {"Authorization": "Bearer s3cret pass"},
    ],
)
def test_wrong_or_malformed_credentials_are_refused(
    client: TestClient, headers: dict[str, str]
) -> None:
    assert client.get("/analyst", headers=headers).status_code == 401


@pytest.mark.usefixtures("protected")
def test_healthz_stays_open_and_says_nothing(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200 and response.json() == {"status": "ok"}


def test_custom_username(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLTIKA_ACCESS_PASSWORD", "p")
    monkeypatch.setenv("POLTIKA_ACCESS_USER", "pete")
    assert client.get("/analyst", headers=_basic("pilot", "p")).status_code == 401
    assert client.get("/analyst", headers=_basic("pete", "p")).status_code == 200


def test_required_password_refuses_to_start(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    monkeypatch.setenv("POLTIKA_REQUIRE_ACCESS_PASSWORD", "1")
    with pytest.raises(AccessConfigError):
        configured_credentials()
    with pytest.raises(AccessConfigError), TestClient(app):
        pass
