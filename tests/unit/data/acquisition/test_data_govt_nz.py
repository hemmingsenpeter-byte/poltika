"""Optional data.govt.nz secondary reference (ADR-0022). No live network."""

from __future__ import annotations

import json

from poltika.data.acquisition.data_govt_nz import CKAN_API, lookup_package
from poltika.data.acquisition.models import ReferenceKind
from poltika.data.acquisition.source import FetchRequest, RawResponse, RetryPolicy, TransportError


class Fake:
    def __init__(self, status: int = 200, body: bytes = b"", exc: Exception | None = None) -> None:
        self.status, self.body, self.exc = status, body, exc
        self.requests: list[FetchRequest] = []

    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        self.requests.append(request)
        if self.exc:
            raise self.exc
        return RawResponse(self.status, (), self.body)


FAST = RetryPolicy(max_attempts=1)


def ckan(name: str, success: bool = True) -> bytes:
    return json.dumps({"success": success, "result": {"name": name, "title": "T"}}).encode()


def test_success_is_non_authoritative_secondary_record() -> None:
    fake = Fake(body=ckan("pkg-one"))
    ref = lookup_package("pkg-one", fake, FAST)
    assert ref is not None
    assert ref.kind is ReferenceKind.SECONDARY_CATALOGUE_RECORD
    assert ref.authoritative is False
    assert ref.url == "https://catalogue.data.govt.nz/dataset/pkg-one"
    assert fake.requests[0].url == CKAN_API
    assert fake.requests[0].query == (("id", "pkg-one"),)


def test_no_config_makes_no_request() -> None:
    fake = Fake(body=ckan("x"))
    assert lookup_package(None, fake, FAST) is None
    assert lookup_package("", fake, FAST) is None
    assert fake.requests == []


def test_failures_return_none_and_never_raise() -> None:
    assert lookup_package("p", Fake(status=404), FAST) is None
    assert lookup_package("p", Fake(status=500), FAST) is None
    assert lookup_package("p", Fake(exc=TransportError("down")), FAST) is None
    assert lookup_package("p", Fake(body=b"not json"), FAST) is None
    assert lookup_package("p", Fake(body=b"[]"), FAST) is None
    assert lookup_package("p", Fake(body=ckan("p", success=False)), FAST) is None


def test_name_mismatch_is_no_match() -> None:
    assert lookup_package("pkg-one", Fake(body=ckan("pkg-two")), FAST) is None
