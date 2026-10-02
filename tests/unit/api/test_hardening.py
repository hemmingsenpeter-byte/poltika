"""Response headers and the request-size limit (`api/hardening.py`)."""

from __future__ import annotations

import asyncio
import base64
from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from poltika.api.hardening import MAX_BODY_BYTES, BodyLimitMiddleware, SecurityHeadersMiddleware
from poltika.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("POLTIKA_REQUIRE_ACCESS_PASSWORD", raising=False)
    return TestClient(app)


def _assert_security_headers(headers: httpx.Headers) -> None:
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in headers["content-security-policy"]
    assert headers["strict-transport-security"].startswith("max-age=")


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
    _assert_security_headers(response.headers)


@pytest.mark.parametrize("declared", [None, b"2"])
def test_stream_limit_stops_reading_after_multiple_chunks(declared: bytes | None) -> None:
    """Actual ASGI chunks, including a dishonest small Content-Length:
    the consumer stops before reading the rest of an oversized stream."""
    chunks = [b"x" * MAX_BODY_BYTES, b"x", b"unread trailing data"]
    reads = 0
    sent: list[Message] = []

    async def receive() -> Message:
        nonlocal reads
        body = chunks[reads]
        reads += 1
        return {"type": "http.request", "body": body, "more_body": reads < len(chunks)}

    async def send(message: Message) -> None:
        sent.append(message)

    async def consume(scope: Scope, receive: Receive, send: Send) -> None:
        while (await receive())["more_body"]:
            pass
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    scope: Scope = {
        "type": "http", "headers": [] if declared is None else [(b"content-length", declared)]
    }
    middleware = SecurityHeadersMiddleware(BodyLimitMiddleware(consume))
    asyncio.run(middleware(scope, receive, send))
    assert reads == 2
    assert sent[0]["status"] == 413
    assert dict(sent[0]["headers"])[b"x-content-type-options"] == b"nosniff"


def test_a_malformed_content_length_is_refused(client: TestClient) -> None:
    response = client.post("/household/calculate", content=b"{}", headers={"content-length": "x"})
    assert response.status_code in (400, 413)


def test_a_huge_content_length_is_refused_without_integer_conversion(client: TestClient) -> None:
    response = client.post(
        "/household/calculate", content=b"{}", headers={"content-length": "9" * 5000}
    )
    assert response.status_code == 413
    _assert_security_headers(response.headers)


def test_a_long_zero_padded_content_length_reaches_the_route(client: TestClient) -> None:
    response = client.post(
        "/household/calculate", content=b"{}", headers={"content-length": "0" * 5000 + "2"}
    )
    assert response.status_code == 422


@pytest.mark.parametrize("streamed", [False, True])
def test_a_body_exactly_at_the_limit_reaches_the_route(client: TestClient, streamed: bool) -> None:
    body = b" " * (MAX_BODY_BYTES - 2) + b"{}"
    content = iter([body[:MAX_BODY_BYTES // 2], body[MAX_BODY_BYTES // 2:]]) if streamed else body
    response = client.post(
        "/household/calculate", content=content, headers={"content-type": "application/json"}
    )
    assert response.status_code == 422
    _assert_security_headers(response.headers)


def test_security_headers_on_an_unexpected_server_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from poltika.api import analyst

    def fail(path: object) -> dict[str, object]:
        raise RuntimeError("private deployment detail")

    monkeypatch.setattr(analyst, "evidence_coverage", fail)
    response = TestClient(app, raise_server_exceptions=False).get("/analyst/evidence")
    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert "private deployment detail" not in response.text
    _assert_security_headers(response.headers)


def test_a_body_under_the_limit_reaches_the_route(client: TestClient) -> None:
    assert client.post("/household/calculate", json={}).status_code == 422


@pytest.mark.parametrize("credentials", [None, "pilot:wrong", "pilot:p"])
def test_the_limit_applies_before_the_password_check(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, credentials: str | None
) -> None:
    monkeypatch.setenv("POLTIKA_ACCESS_PASSWORD", "p")
    headers = {}
    if credentials is not None:
        token = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    response = client.post(
        "/household/calculate",
        content=b"x" * (MAX_BODY_BYTES + 1),
        headers=headers,
    )
    assert response.status_code == 413
