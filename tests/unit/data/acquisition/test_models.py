"""Models: identity, determinism, unknown-stays-unknown, UTC, redaction."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from poltika.data.acquisition.models import (
    SECRET_HEADER_NAMES,
    DatasetDescriptor,
    Reference,
    ReferenceKind,
    RetrievalRecord,
    canonical_json,
    redact,
    sha256_hex,
)

from .conftest import T0, make_metadata


def test_sha256_of_exact_bytes() -> None:
    assert sha256_hex(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert sha256_hex(b"a\r\n") != sha256_hex(b"a\n")


def test_canonical_json_key_order_and_sequence_stability() -> None:
    assert canonical_json({"b": 1, "a": (1, 2)}) == canonical_json({"a": [1, 2], "b": 1})
    assert canonical_json({"a": "é"}) == '{"a":"é"}'.encode()
    with pytest.raises(ValueError):
        canonical_json({"a": float("nan")})


def test_metadata_hash_deterministic_and_tuple_list_stable() -> None:
    a = make_metadata(keywords=("x", "y"))
    b = make_metadata(keywords=["x", "y"])  # type: ignore[arg-type]
    assert a.sha256() == b.sha256()
    assert a.sha256() != make_metadata(keywords=("y", "x")).sha256()


def test_identity_independent_of_title() -> None:
    a = make_metadata(title="Old title")
    b = make_metadata(title="New title")
    assert a.dataset.source_dataset_identifier == b.dataset.source_dataset_identifier
    assert a.sha256() != b.sha256()  # title is metadata evidence, not identity


def test_unknown_stays_none() -> None:
    d = DatasetDescriptor(source_system="s", source_dataset_identifier="i")
    for name in ("issued", "modified", "licence", "rights", "temporal_coverage", "title"):
        assert getattr(d, name) is None


def test_dates_are_distinct_and_not_derived() -> None:
    d = make_metadata(issued="2020-01-01", modified=None).dataset
    assert d.issued == "2020-01-01"
    assert d.modified is None
    assert not hasattr(d, "retrieved")


def test_extra_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        DatasetDescriptor(source_system="s", source_dataset_identifier="i", bogus=1)  # type: ignore[call-arg]


def test_reference_blob_hash_validated() -> None:
    Reference(kind=ReferenceKind.METHODOLOGY, url="https://example.invalid/m")
    with pytest.raises(ValidationError):
        Reference(kind=ReferenceKind.METHODOLOGY, url="u", preserved_blob_sha256="zz")


def test_redact() -> None:
    assert redact("token abc and abcd", ["abc", "abcd", ""]) == "token [REDACTED] and [REDACTED]"
    assert redact("nothing", []) == "nothing"


def test_secret_header_names_lowercase() -> None:
    assert all(n == n.lower() for n in SECRET_HEADER_NAMES)
    assert {"authorization", "cookie", "ocp-apim-subscription-key"} <= SECRET_HEADER_NAMES


def _record_kwargs(**over: object) -> dict[str, object]:
    base: dict[str, object] = {
        "retrieval_id": "r",
        "poltika_source_id": "s",
        "source_system": "x",
        "dataset_identifier": "d",
        "distribution_identifier": "dd",
        "request_method": "GET",
        "endpoint": "https://example.invalid/",
        "query_parameters": (),
        "request_body_sha256": None,
        "request_fingerprint": "f" * 64,
        "request_started_at": T0,
        "response_received_at": T0,
        "http_status": 200,
        "content_type": None,
        "content_encoding": None,
        "content_length": 0,
        "response_headers": (),
        "content_sha256": "a" * 64,
        "blob_identifier": "sha256:" + "a" * 64,
        "metadata_sha256": None,
        "metadata_raw_sha256": None,
        "previous_retrieval_id": None,
        "previous_content_sha256": None,
        "previous_metadata_sha256": None,
        "content_changed": None,
        "metadata_changed": None,
        "collector_version": "t",
    }
    base.update(over)
    return base


def test_record_rejects_naive_datetime_and_normalises_to_utc() -> None:
    with pytest.raises(ValidationError):
        RetrievalRecord(**_record_kwargs(request_started_at=datetime(2026, 1, 1)))  # noqa: DTZ001  # type: ignore[arg-type]
    nz = timezone(timedelta(hours=13))
    rec = RetrievalRecord(**_record_kwargs(request_started_at=datetime(2026, 1, 2, 1, tzinfo=nz)))  # type: ignore[arg-type]
    assert rec.request_started_at == datetime(2026, 1, 1, 12, tzinfo=UTC)
    assert '"request_started_at":"2026-01-01T12:00:00Z"' in canonical_json(rec).decode()


def test_record_json_round_trip() -> None:
    rec = RetrievalRecord(**_record_kwargs())  # type: ignore[arg-type]
    assert RetrievalRecord.model_validate_json(canonical_json(rec)) == rec
