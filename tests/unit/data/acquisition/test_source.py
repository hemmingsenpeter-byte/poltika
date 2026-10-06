"""HTTP layer: secrets, retries, Retry-After, permanent errors. No network."""

from __future__ import annotations

import urllib.error
from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from poltika.data.acquisition.models import redact
from poltika.data.acquisition.source import (
    FetchRequest,
    PermanentHttpError,
    RawResponse,
    RetriesExhaustedError,
    RetryPolicy,
    TransportError,
    TransportTimeoutError,
    UrllibTransport,
    fetch,
)

SECRET = "s3cr3t-key-VALUE-123"
NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


class ScriptedTransport:
    def __init__(self, *steps: RawResponse | Exception) -> None:
        self.steps = list(steps)
        self.calls = 0

    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        self.calls += 1
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def ok(body: bytes = b"hello") -> RawResponse:
    return RawResponse(200, (("Content-Type", "text/plain"), ("Set-Cookie", "a=b")), body)


def status(code: int, *headers: tuple[str, str]) -> RawResponse:
    return RawResponse(code, headers, b"")


def run(
    transport: ScriptedTransport,
    policy: RetryPolicy | None = None,
    request: FetchRequest | None = None,
) -> tuple[list[float], Callable[[], object]]:
    sleeps: list[float] = []

    def go() -> object:
        return fetch(
            request or FetchRequest(url="https://example.invalid/x"),
            transport,
            policy or RetryPolicy(),
            sleep=sleeps.append,
            now=lambda: NOW,
        )

    return sleeps, go


def test_200_returns_safe_headers_only() -> None:
    t = ScriptedTransport(ok())
    _, go = run(t)
    resp = go()
    assert resp.status == 200 and resp.body == b"hello"  # type: ignore[attr-defined]
    assert resp.headers == (("content-type", "text/plain"),)  # type: ignore[attr-defined]


def test_429_then_200() -> None:
    sleeps, go = run(ScriptedTransport(status(429), ok()))
    go()
    assert sleeps == [1.0]


@pytest.mark.parametrize("code", [500, 502, 503, 504])
def test_transient_5xx_retried(code: int) -> None:
    t = ScriptedTransport(status(code), status(code), ok())
    sleeps, go = run(t)
    go()
    assert t.calls == 3 and sleeps == [1.0, 2.0]


def test_retry_after_seconds_honoured_and_capped() -> None:
    sleeps, go = run(
        ScriptedTransport(
            status(429, ("Retry-After", "7")), status(503, ("retry-after", "999")), ok()
        ),
        RetryPolicy(max_delay=30.0),
    )
    go()
    assert sleeps == [7.0, 30.0]


def test_retry_after_http_date_honoured() -> None:
    sleeps, go = run(
        ScriptedTransport(status(429, ("Retry-After", "Thu, 01 Jan 2026 12:00:09 GMT")), ok())
    )
    go()
    assert sleeps == [9.0]


@pytest.mark.parametrize("code", [400, 401, 403, 404])
def test_permanent_4xx_not_retried(code: int) -> None:
    t = ScriptedTransport(status(code), ok())
    sleeps, go = run(t)
    with pytest.raises(PermanentHttpError) as exc:
        go()
    assert exc.value.status == code and t.calls == 1 and sleeps == []


def test_timeout_retried_then_exhausted() -> None:
    t = ScriptedTransport(*[TransportTimeoutError("timeout")] * 3)
    sleeps, go = run(t, RetryPolicy(max_attempts=3))
    with pytest.raises(RetriesExhaustedError):
        go()
    assert t.calls == 3 and len(sleeps) == 2


def test_timeout_then_success() -> None:
    t = ScriptedTransport(TransportTimeoutError("timeout"), ok())
    _, go = run(t)
    go()
    assert t.calls == 2


def test_max_attempts_bound_respected() -> None:
    t = ScriptedTransport(*[status(503)] * 10)
    _, go = run(t, RetryPolicy(max_attempts=2))
    with pytest.raises(RetriesExhaustedError):
        go()
    assert t.calls == 2


def test_backoff_capped() -> None:
    t = ScriptedTransport(*[status(503)] * 5)
    sleeps, go = run(t, RetryPolicy(max_attempts=5, base_delay=10, max_delay=25))
    with pytest.raises(RetriesExhaustedError):
        go()
    assert sleeps == [10, 20, 25, 25]


def secret_request() -> FetchRequest:
    return FetchRequest(
        url="https://example.invalid/x",
        headers=(("Accept", "text/csv"),),
        secret_headers=(("Ocp-Apim-Subscription-Key", SECRET),),
    )


def test_secret_never_in_repr_dump_fingerprint_or_errors() -> None:
    req = secret_request()
    plain = FetchRequest(url="https://example.invalid/x", headers=(("Accept", "text/csv"),))
    assert req.fingerprint() == plain.fingerprint()
    for text in (repr(req), req.model_dump_json(), str(req.model_dump())):
        assert SECRET not in text
    for step in (status(404), TransportError(f"boom {SECRET}")):
        _, go = run(ScriptedTransport(step), RetryPolicy(max_attempts=1), req)
        with pytest.raises((PermanentHttpError, RetriesExhaustedError)) as exc:
            go()
        assert SECRET not in str(exc.value)
    assert redact(f"x {SECRET}", req.secret_values()) == "x [REDACTED]"


@pytest.mark.parametrize(
    "name", ["Authorization", "COOKIE", "x-api-key", "Ocp-Apim-Subscription-Key"]
)
def test_secret_header_names_rejected_in_plain_headers(name: str) -> None:
    with pytest.raises(ValidationError):
        FetchRequest(url="https://example.invalid/x", headers=((name, "v"),))


@pytest.mark.parametrize(
    "url", ["https://e.invalid/x?k=v", "https://user:pw@e.invalid/x", "file:///etc/passwd", "/rel"]
)
def test_url_validation(url: str) -> None:
    with pytest.raises(ValidationError):
        FetchRequest(url=url)


def test_fingerprint_deterministic_and_query_order_insensitive() -> None:
    a = FetchRequest(url="https://e.invalid/x", query=(("a", "1"), ("b", "2")))
    b = FetchRequest(url="https://e.invalid/x", query=(("b", "2"), ("a", "1")))
    assert a.fingerprint() == b.fingerprint()
    assert a.full_url() == "https://e.invalid/x?a=1&b=2"
    assert a.fingerprint() != FetchRequest(url="https://e.invalid/y").fingerprint()


class _FakeOpener:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def open(self, req: object, timeout: float) -> object:
        raise self.exc


def _patched(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    monkeypatch.setattr(
        "poltika.data.acquisition.source.urllib.request.build_opener",
        lambda *a, **k: _FakeOpener(exc),
    )


def test_urllib_timeout_and_urlerror_are_redacted(monkeypatch: pytest.MonkeyPatch) -> None:
    req = secret_request()
    _patched(monkeypatch, TimeoutError(SECRET))
    with pytest.raises(TransportTimeoutError) as t:
        UrllibTransport().send(req, 1.0)
    assert SECRET not in str(t.value)
    _patched(monkeypatch, urllib.error.URLError(f"dns {SECRET}"))
    with pytest.raises(TransportError) as e:
        UrllibTransport().send(req, 1.0)
    assert SECRET not in str(e.value) and not isinstance(e.value, TransportTimeoutError)
    _patched(monkeypatch, urllib.error.URLError(TimeoutError("slow")))
    with pytest.raises(TransportTimeoutError):
        UrllibTransport().send(req, 1.0)


def test_urllib_http_error_becomes_raw_response(monkeypatch: pytest.MonkeyPatch) -> None:
    import io
    from email.message import Message

    h = Message()
    h["Retry-After"] = "3"
    err = urllib.error.HTTPError("https://e.invalid/x", 429, "Too Many", h, io.BytesIO(b"slow"))
    _patched(monkeypatch, err)
    raw = UrllibTransport().send(FetchRequest(url="https://e.invalid/x"), 1.0)
    assert raw.status == 429 and raw.body == b"slow" and ("Retry-After", "3") in raw.headers


@pytest.mark.parametrize(
    ("old", "new", "follows"),
    [
        ("https://api.example.invalid/a", "https://api.example.invalid/b", True),
        ("https://api.example.invalid/a", "http://api.example.invalid/b", False),  # downgrade
        ("https://api.example.invalid/a", "https://other.example.invalid/b", False),
        ("http://api.example.invalid/a", "https://api.example.invalid/b", False),
    ],
)
def test_redirects_only_when_scheme_and_host_unchanged(old: str, new: str, follows: bool) -> None:
    import urllib.request

    from poltika.data.acquisition.source import _SameHostRedirect

    req = urllib.request.Request(old, headers={"Ocp-Apim-Subscription-Key": SECRET})
    result = _SameHostRedirect().redirect_request(req, None, 302, "Found", {}, new)
    assert (result is not None) is follows
    if result is not None:
        assert result.full_url == new


# --- Response cap (PR B, D20): oversize bodies are refused, never truncated.


class _Body:
    """A urllib response stand-in that serves `size` bytes in small reads."""

    def __init__(self, size: int, content_length: str | None = None) -> None:
        from email.message import Message

        self.remaining = size
        self.read_total = 0
        self.status = 200
        self.headers = Message()
        if content_length is not None:
            self.headers["Content-Length"] = content_length

    def read(self, amt: int | None = None) -> bytes:
        assert amt is not None, "an unbounded read() must never happen"
        n = min(amt, self.remaining, 7)
        self.remaining -= n
        self.read_total += n
        return b"x" * n

    def __enter__(self) -> _Body:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _BodyOpener:
    def __init__(self, body: _Body) -> None:
        self.body = body

    def open(self, req: object, timeout: float) -> _Body:
        return self.body


def _serve(monkeypatch: pytest.MonkeyPatch, body: _Body) -> None:
    monkeypatch.setattr(
        "poltika.data.acquisition.source.urllib.request.build_opener",
        lambda *a, **k: _BodyOpener(body),
    )


def test_default_cap_is_50_mib() -> None:
    from poltika.data.acquisition.source import DEFAULT_MAX_RESPONSE_BYTES

    assert DEFAULT_MAX_RESPONSE_BYTES == 50 * 1024 * 1024
    assert FetchRequest(url="https://e.invalid/x").max_response_bytes == DEFAULT_MAX_RESPONSE_BYTES


@pytest.mark.parametrize("size", [0, 1, 99, 100])
def test_urllib_body_at_or_under_the_cap_is_read_whole(
    monkeypatch: pytest.MonkeyPatch, size: int
) -> None:
    _serve(monkeypatch, _Body(size))
    raw = UrllibTransport().send(FetchRequest(url="https://e.invalid/x", max_response_bytes=100), 1.0)
    assert raw.body == b"x" * size


def test_urllib_body_over_the_cap_is_refused_without_reading_it_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from poltika.data.acquisition.source import ResponseTooLargeError

    body = _Body(10_000)
    _serve(monkeypatch, body)
    req = FetchRequest(
        url="https://e.invalid/x",
        secret_headers=(("Ocp-Apim-Subscription-Key", SECRET),),
        max_response_bytes=100,
    )
    with pytest.raises(ResponseTooLargeError) as e:
        UrllibTransport().send(req, 1.0)
    assert e.value.limit == 100 and "100 bytes" in str(e.value) and SECRET not in str(e.value)
    assert body.read_total == 101


def test_urllib_declared_oversize_is_refused_before_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    from poltika.data.acquisition.source import ResponseTooLargeError

    body = _Body(10, content_length="101")
    _serve(monkeypatch, body)
    with pytest.raises(ResponseTooLargeError):
        UrllibTransport().send(FetchRequest(url="https://e.invalid/x", max_response_bytes=100), 1.0)
    assert body.read_total == 0


def test_urllib_http_error_body_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    import io
    from email.message import Message

    from poltika.data.acquisition.source import ResponseTooLargeError

    err = urllib.error.HTTPError("https://e.invalid/x", 503, "Busy", Message(), io.BytesIO(b"y" * 101))
    _patched(monkeypatch, err)
    with pytest.raises(ResponseTooLargeError):
        UrllibTransport().send(FetchRequest(url="https://e.invalid/x", max_response_bytes=100), 1.0)


@pytest.mark.parametrize("code", [200, 503])
def test_fetch_refuses_oversize_from_any_transport_and_does_not_retry(code: int) -> None:
    from poltika.data.acquisition.source import ResponseTooLargeError

    t = ScriptedTransport(RawResponse(code, (), b"z" * 101), ok())
    _, go = run(t, request=FetchRequest(url="https://e.invalid/x", max_response_bytes=100))
    with pytest.raises(ResponseTooLargeError):
        go()
    assert t.calls == 1


def test_fetch_keeps_a_body_exactly_at_the_cap() -> None:
    t = ScriptedTransport(ok(b"z" * 100))
    _, go = run(t, request=FetchRequest(url="https://e.invalid/x", max_response_bytes=100))
    assert go().body == b"z" * 100  # type: ignore[attr-defined]


def test_cap_is_never_serialised() -> None:
    req = FetchRequest(url="https://e.invalid/x", max_response_bytes=100)
    assert "max_response_bytes" not in req.model_dump()
    assert req.fingerprint() == FetchRequest(url="https://e.invalid/x").fingerprint()


@pytest.mark.parametrize("value", [0, -1])
def test_cap_must_be_positive(value: int) -> None:
    with pytest.raises(ValidationError):
        FetchRequest(url="https://e.invalid/x", max_response_bytes=value)
