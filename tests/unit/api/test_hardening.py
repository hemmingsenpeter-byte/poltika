"""Response headers and the request-size limit (`api/hardening.py`)."""

from __future__ import annotations

import base64
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from poltika.api.hardening import MAX_BODY_BYTES
from poltika.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("POLTIKA_REQUIRE_ACCESS_PASSWORD", raising=False)
    return TestClient(app)


def _assert_security_headers(headers: object) -> None:
    assert headers["x-content-type-options"] == "nosniff"  # type: ignore[index]
    assert headers["x-frame-options"] == "DENY"  # type: ignore[index]
    assert headers["referrer-policy"] == "no-referrer"  # type: ignore[index]
    assert "frame-ancestors 'none'" in headers["content-security-policy"]  # type: ignore[index]
    assert headers["strict-transport-security"].startswith("max-age=")  # type: ignore[index]


@pytest.mark.parametrize("path", ["/analyst", "/docs", "/openapi.json", "/healthz"])
def test_security_headers_on_every_response(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    _assert_security_headers(response.headers)


def test_security_headers_on_a_refused_request(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POLTIKA_ACCESS_PASSWORD", "p")
    response = client.get("/analyst")
    assert response.status_code == 401
    _assert_security_headers(response.headers)


def test_an_oversized_declared_body_is_refused(client: TestClient) -> None:
    response = client.post("/household/calculate", content=b"x" * (MAX_BODY_BYTES + 1))
    assert response.status_code == 413
    _assert_security_headers(response.headers)


def test_an_oversized_streamed_body_is_refused(client: TestClient) -> None:
    """No content-length: the size is only seen while reading."""

    def chunks() -> Iterator[bytes]:
        for _ in range(MAX_BODY_BYTES // 1024 + 2):
            yield b"x" * 1024

    response = client.post(
        "/household/calculate", content=chunks(), headers={"content-type": "application/json"}
    )
    assert response.status_code == 413


def test_a_malformed_content_length_is_refused(client: TestClient) -> None:
    response = client.post("/household/calculate", content=b"{}", headers={"content-length": "x"})
    assert response.status_code in (400, 413)


def test_a_body_under_the_limit_reaches_the_route(client: TestClient) -> None:
    assert client.post("/household/calculate", json={}).status_code == 422


def test_the_limit_applies_before_the_password_check(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POLTIKA_ACCESS_PASSWORD", "p")
    token = base64.b64encode(b"pilot:p").decode()
    response = client.post(
        "/household/calculate",
        content=b"x" * (MAX_BODY_BYTES + 1),
        headers={"Authorization": f"Basic {token}"},
    )
    assert response.status_code == 413

