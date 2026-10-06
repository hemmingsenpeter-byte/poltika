"""Source preservation archive: the generic HTTP/retry layer and connector
contract (ADR-0022).

`fetch` is deterministic and secret-safe: secret headers are sent but never
serialised, hashed, repr'd or placed in an exception message. Retries are
bounded (no infinite loops), with exponential backoff and Retry-After.
Sleep and clock are injectable so tests are instant.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from poltika.common.errors import PoltikaError
from poltika.data.acquisition.models import (
    SAFE_RESPONSE_HEADERS,
    SECRET_HEADER_NAMES,
    Reference,
    SourceMetadata,
    canonical_json,
    redact,
    sha256_hex,
)

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})

# Default cap on one response body (D20): 50 MiB. A source whose responses are
# legitimately larger sets `max_response_bytes` in its catalogue entry.
DEFAULT_MAX_RESPONSE_BYTES = 50 * 1024 * 1024


class AcquisitionError(PoltikaError):
    """Base class for acquisition failures."""


class TransportError(AcquisitionError):
    """The request could not be completed (connection-level failure)."""


class TransportTimeoutError(TransportError):
    """The request timed out."""


class PermanentHttpError(AcquisitionError):
    """A non-retryable HTTP status (e.g. 400/401/403/404)."""

    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status


class RetriesExhaustedError(AcquisitionError):
    """Every bounded attempt failed with a transient error."""


class ResponseTooLargeError(AcquisitionError):
    """The response body is larger than the request's cap. It is refused, never
    truncated, and not retried."""

    def __init__(self, message: str, limit: int) -> None:
        super().__init__(message)
        self.limit = limit


class FetchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    method: str = "GET"
    url: str
    query: tuple[tuple[str, str], ...] = ()
    body: bytes | None = None
    headers: tuple[tuple[str, str], ...] = ()
    secret_headers: tuple[tuple[str, str], ...] = Field(default=(), exclude=True, repr=False)
    # A transport limit, not part of the request: never serialised or fingerprinted.
    max_response_bytes: int = Field(default=DEFAULT_MAX_RESPONSE_BYTES, gt=0, exclude=True)

    @field_validator("url")
    @classmethod
    def _url_clean(cls, v: str) -> str:
        parts = urllib.parse.urlsplit(v)
        if parts.query or parts.fragment:
            raise ValueError("url must not carry a query string or fragment; use `query`")
        if parts.username or parts.password:
            raise ValueError("url must not embed credentials")
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError("url must be an absolute http(s) URL")
        return v

    @field_validator("headers")
    @classmethod
    def _no_secret_headers(cls, v: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
        for name, _ in v:
            if name.strip().lower() in SECRET_HEADER_NAMES:
                raise ValueError(f"secret header {name!r} must go in secret_headers")
        return v

    def secret_values(self) -> tuple[str, ...]:
        return tuple(value for _, value in self.secret_headers if value)

    def sorted_query(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self.query))

    def fingerprint(self) -> str:
        return sha256_hex(
            canonical_json(
                {
                    "method": self.method.upper(),
                    "url": self.url,
                    "query": self.sorted_query(),
                    "body_sha256": sha256_hex(self.body) if self.body is not None else None,
                    "headers": sorted((n.lower(), v) for n, v in self.headers),
                }
            )
        )

    def full_url(self) -> str:
        if not self.query:
            return self.url
        return f"{self.url}?{urllib.parse.urlencode(self.sorted_query())}"


@dataclass(frozen=True)
class RawResponse:
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes


class Transport(Protocol):
    def send(self, request: FetchRequest, timeout: float) -> RawResponse: ...


class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only when scheme and host are both unchanged, so secret
    headers never go to another host or over a downgraded (https to http) hop."""

    def redirect_request(  # type: ignore[no-untyped-def]
        self, req, fp, code, msg, headers, newurl
    ):
        old = urllib.parse.urlsplit(req.full_url)
        new = urllib.parse.urlsplit(newurl)
        if (new.scheme.lower(), new.netloc.lower()) != (old.scheme.lower(), old.netloc.lower()):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _too_large(request: FetchRequest) -> ResponseTooLargeError:
    label = redact(f"{request.method.upper()} {request.full_url()}", request.secret_values())
    limit = request.max_response_bytes
    return ResponseTooLargeError(f"{label} -> response exceeds {limit} bytes (refused)", limit)


def _read_capped(stream: Any, request: FetchRequest) -> bytes:
    """Read at most the cap plus one byte, so an oversize body is detected
    without being held in memory in full."""
    limit = request.max_response_bytes
    headers = getattr(stream, "headers", None)
    declared = headers.get("Content-Length") if headers is not None else None
    if declared is not None and declared.strip().isdigit() and int(declared) > limit:
        raise _too_large(request)
    chunks: list[bytes] = []
    total = 0
    while total <= limit:
        chunk: bytes = stream.read(limit + 1 - total)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
    raise _too_large(request)


class UrllibTransport:
    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        secrets = request.secret_values()
        headers = dict(request.headers)
        headers.update(dict(request.secret_headers))
        req = urllib.request.Request(
            request.full_url(),
            data=request.body,
            method=request.method.upper(),
            headers=headers,
        )
        opener = urllib.request.build_opener(_SameHostRedirect)
        try:
            with opener.open(req, timeout=timeout) as resp:
                return RawResponse(
                    status=int(resp.status),
                    headers=tuple((k, v) for k, v in resp.headers.items()),
                    body=_read_capped(resp, request),
                )
        except urllib.error.HTTPError as exc:
            try:
                body = _read_capped(exc, request)
            finally:
                exc.close()
            return RawResponse(
                status=int(exc.code),
                headers=tuple((k, v) for k, v in exc.headers.items()),
                body=body,
            )
        except TimeoutError as exc:
            raise TransportTimeoutError(redact(f"timeout: {type(exc).__name__}", secrets)) from None
        except urllib.error.URLError as exc:
            text = redact(f"{type(exc).__name__}: {exc.reason}", secrets)
            if isinstance(exc.reason, TimeoutError):
                raise TransportTimeoutError(text) from None
            raise TransportError(text) from None
        except OSError as exc:
            raise TransportError(redact(f"{type(exc).__name__}: {exc}", secrets)) from None


class FetchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    request: FetchRequest
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    started_at: datetime
    received_at: datetime

    @field_validator("started_at", "received_at")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.utcoffset() is None:
            raise ValueError("datetime must be timezone-aware (UTC)")
        return v.astimezone(UTC)


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 4
    base_delay: float = 1.0
    max_delay: float = 60.0
    timeout: float = 60.0


DEFAULT_RETRY_POLICY = RetryPolicy()


def _safe_headers(headers: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            (name.lower(), value)
            for name, value in headers
            if name.lower() in SAFE_RESPONSE_HEADERS
        )
    )


def _retry_after_seconds(headers: tuple[tuple[str, str], ...], current: datetime) -> float | None:
    for name, value in headers:
        if name.lower() != "retry-after":
            continue
        value = value.strip()
        if value.isdigit():
            return float(value)
        try:
            when = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        return max(0.0, (when - current).total_seconds())
    return None


def fetch(
    request: FetchRequest,
    transport: Transport,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    *,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> FetchResponse:
    secrets = request.secret_values()
    label = redact(f"{request.method.upper()} {request.full_url()}", secrets)
    last = "no attempt made"
    for attempt in range(max(1, policy.max_attempts)):
        started = now()
        retry_after: float | None = None
        try:
            raw = transport.send(request, policy.timeout)
        except TransportError as exc:  # includes timeouts
            last = redact(f"{type(exc).__name__}: {exc}", secrets)
        else:
            if len(raw.body) > request.max_response_bytes:
                raise _too_large(request)
            if 200 <= raw.status < 300:
                return FetchResponse(
                    request=request,
                    status=raw.status,
                    headers=_safe_headers(raw.headers),
                    body=raw.body,
                    started_at=started,
                    received_at=now(),
                )
            if raw.status not in RETRYABLE_STATUSES:
                raise PermanentHttpError(f"{label} -> HTTP {raw.status} (not retried)", raw.status)
            last = f"HTTP {raw.status}"
            retry_after = _retry_after_seconds(raw.headers, now())
        if attempt + 1 >= max(1, policy.max_attempts):
            break
        backoff = min(policy.max_delay, policy.base_delay * (2**attempt))
        delay = backoff if retry_after is None else min(policy.max_delay, retry_after)
        sleep(delay)
    raise RetriesExhaustedError(
        redact(f"{label} failed after {max(1, policy.max_attempts)} attempts: {last}", secrets)
    )


class SourceObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    poltika_source_id: str
    metadata: SourceMetadata
    content: FetchResponse
    native_metadata: FetchResponse | None = None
    # Non-authoritative references: kept on the record, never hashed into `metadata`.
    secondary_references: tuple[Reference, ...] = ()


class SourceConnector(Protocol):
    source_system: str

    def observe(self, entry: Any, *, include_metadata: bool = True) -> SourceObservation: ...
