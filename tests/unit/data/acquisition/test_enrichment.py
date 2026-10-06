"""Source-preservation archive (ADR-0022): the optional advisory enrichment.

Synthetic data only; no live network. Enrichment must be a no-op when not
configured, must never raise, must never alter evidence, and must never put a
credential in its payload.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poltika.data.acquisition import enrichment
from poltika.data.acquisition.enrichment import (
    ENDPOINT,
    SAMPLE_CAP_BYTES,
    AdvisoryResult,
    build_payload,
    enrich,
)
from poltika.data.acquisition.models import (
    NON_AUTHORITATIVE_ADVISORY,
    AccessKind,
    DatasetDescriptor,
    DistributionDescriptor,
    RetrievalRecord,
    SourceMetadata,
    make_retrieval_id,
)
from poltika.data.acquisition.source import (
    FetchRequest,
    RawResponse,
    TransportError,
    TransportTimeoutError,
)

OPENROUTER_KEY = "sk-or-SYNTHETIC-KEY-0001"
STATS_KEY = "STATSNZ-SENTINEL-KEY-9999"
ENV = {
    "OPENROUTER_API_KEY": OPENROUTER_KEY,
    "POLTIKA_OPENROUTER_MODEL": "synthetic/model:free",
    "POLTIKA_STATS_NZ_API_KEY": STATS_KEY,
}
T0 = datetime(2026, 10, 6, 1, 2, 3, tzinfo=UTC)


class FakeTransport:
    def __init__(self, response: RawResponse | Exception) -> None:
        self.response = response
        self.requests: list[FetchRequest] = []

    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        self.requests.append(request)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def _ok_body(content: str = '{"schema_summary": "a table"}') -> bytes:
    return json.dumps(
        {"choices": [{"message": {"role": "assistant", "content": content}}]}
    ).encode()


def _metadata() -> SourceMetadata:
    return SourceMetadata(
        dataset=DatasetDescriptor(source_system="stats_nz", source_dataset_identifier="SYN:DF"),
        distribution=DistributionDescriptor(
            distribution_identifier="syn_csv",
            dataset_identifier="SYN:DF",
            access_kind=AccessKind.API,
        ),
    )


def _record(size: int) -> RetrievalRecord:
    content = hashlib.sha256(b"x").hexdigest()
    return RetrievalRecord(
        retrieval_id=make_retrieval_id(T0, "ab" * 32),
        poltika_source_id="syn_source",
        source_system="stats_nz",
        dataset_identifier="SYN:DF",
        distribution_identifier="syn_csv",
        request_method="GET",
        endpoint="https://example.invalid/data",
        query_parameters=(),
        request_body_sha256=None,
        request_fingerprint="ab" * 32,
        request_started_at=T0,
        response_received_at=T0,
        http_status=200,
        content_type="text/csv",
        content_encoding=None,
        content_length=size,
        response_headers=(),
        content_sha256=content,
        blob_identifier=f"sha256:{content}",
        metadata_sha256=None,
        metadata_raw_sha256=None,
        previous_retrieval_id=None,
        previous_content_sha256=None,
        previous_metadata_sha256=None,
        content_changed=None,
        metadata_changed=None,
        collector_version="test",
    )


def _populate_archive(root: Path) -> None:
    for sub in ("records", "metadata", "blobs"):
        d = root / sub / "stats_nz"
        d.mkdir(parents=True)
        (d / "evidence.json").write_bytes(f"evidence-{sub}".encode())


def _tree_hash(root: Path, skip: str = "advisory") -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if skip in p.relative_to(root).parts[:1]:
            continue
        h.update(str(p.relative_to(root)).encode())
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def _run(root: Path, transport: FakeTransport, env: dict[str, str] | None = None) -> AdvisoryResult:
    sample = b"a,b\n1,2\n"
    return enrich(
        root,
        _record(len(sample)),
        _metadata(),
        sample,
        transport=transport,
        env=ENV if env is None else env,
        now=lambda: T0,
    )


@pytest.mark.parametrize(
    "env",
    [
        {},
        {"OPENROUTER_API_KEY": OPENROUTER_KEY},
        {"POLTIKA_OPENROUTER_MODEL": "m"},
        {"OPENROUTER_API_KEY": "  ", "POLTIKA_OPENROUTER_MODEL": "m"},
    ],
)
def test_not_configured_is_skipped_with_no_network_and_no_file(
    tmp_path: Path, env: dict[str, str]
) -> None:
    transport = FakeTransport(RawResponse(200, (), _ok_body()))
    result = _run(tmp_path, transport, env)
    assert result.outcome == "skipped"
    assert transport.requests == []
    assert list(tmp_path.rglob("*")) == []


def test_success_writes_marked_advisory_file_only_under_advisory(tmp_path: Path) -> None:
    _populate_archive(tmp_path)
    before = _tree_hash(tmp_path)
    transport = FakeTransport(RawResponse(200, (), _ok_body()))
    result = _run(tmp_path, transport)
    assert result.outcome == "ok"
    assert result.path is not None
    advisory = tmp_path / "advisory" / "stats_nz" / "syn_source"
    assert result.path.parent == advisory
    doc = json.loads(result.path.read_text())
    assert doc["status"] == NON_AUTHORITATIVE_ADVISORY
    assert doc["provider"] == "openrouter"
    assert doc["model"] == "synthetic/model:free"
    assert doc["created_at"] == T0.isoformat()
    assert doc["input_sha256"] == result.input_sha256
    assert doc["outcome"] == "ok"
    assert doc["output"] == {"schema_summary": "a table"}
    assert result.path.name.startswith(_record(1).retrieval_id)
    assert result.input_sha256 is not None and result.input_sha256[:12] in result.path.name
    # Evidence directories are byte-for-byte unchanged and nothing else appeared.
    assert _tree_hash(tmp_path) == before
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "advisory",
        "blobs",
        "metadata",
        "records",
    ]
    assert transport.requests[0].url == ENDPOINT


def test_non_json_model_answer_is_kept_as_text(tmp_path: Path) -> None:
    result = _run(tmp_path, FakeTransport(RawResponse(200, (), _ok_body("plain words"))))
    assert result.outcome == "ok" and result.path is not None
    assert json.loads(result.path.read_text())["output"] == "plain words"


@pytest.mark.parametrize(
    "response",
    [
        RawResponse(429, (("Retry-After", "5"),), b'{"error": {"code": 429}}'),
        RawResponse(400, (), b"{}"),
        RawResponse(401, (), b"{}"),
        RawResponse(404, (), b'{"error": {"message": "model removed"}}'),
        RawResponse(500, (), b""),
        RawResponse(503, (), b""),
        RawResponse(200, (), b"not json"),
        RawResponse(200, (), b'{"choices": []}'),
        RawResponse(200, (), _ok_body("   ")),
        RawResponse(200, (), b"\xff\xfe"),
        TransportTimeoutError("timed out"),
        TransportError("connection reset"),
        RuntimeError(f"boom {OPENROUTER_KEY}"),
    ],
    ids=lambda r: repr(r)[:40],
)
def test_failures_never_raise_leave_evidence_alone_and_leak_nothing(
    tmp_path: Path, response: RawResponse | Exception
) -> None:
    _populate_archive(tmp_path)
    before = _tree_hash(tmp_path)
    result = _run(tmp_path, FakeTransport(response))
    assert result.outcome == "failed"
    assert result.error is not None and OPENROUTER_KEY not in result.error
    assert _tree_hash(tmp_path) == before
    for p in (tmp_path / "advisory").rglob("*.json"):
        text = p.read_text()
        assert OPENROUTER_KEY not in text
        assert json.loads(text)["outcome"] == "failed"
        assert json.loads(text)["status"] == NON_AUTHORITATIVE_ADVISORY


def test_unwritable_advisory_dir_is_a_failed_result_not_an_exception(tmp_path: Path) -> None:
    (tmp_path / "advisory").write_text("a file where a directory should be")
    result = _run(tmp_path, FakeTransport(RawResponse(200, (), _ok_body())))
    assert result.outcome == "failed"


def test_unsafe_record_identifier_fails_without_writing(tmp_path: Path) -> None:
    bad = _record(1).model_copy(update={"poltika_source_id": "../escape"})
    result = enrich(
        tmp_path,
        bad,
        _metadata(),
        b"x",
        transport=FakeTransport(RawResponse(200, (), _ok_body())),
        env=ENV,
        now=lambda: T0,
    )
    assert result.outcome == "failed"
    assert list(tmp_path.rglob("*")) == []


def test_payload_has_no_credentials_and_key_only_in_secret_headers(tmp_path: Path) -> None:
    transport = FakeTransport(RawResponse(200, (), _ok_body()))
    _run(tmp_path, transport)
    (request,) = transport.requests
    visible = request.model_dump_json() + repr(request) + (request.body or b"").decode()
    assert OPENROUTER_KEY not in visible
    assert STATS_KEY not in visible
    assert "bearer" not in visible.lower()
    assert [n.lower() for n, _ in request.headers] == ["accept", "content-type"]
    assert request.secret_headers == (("Authorization", f"Bearer {OPENROUTER_KEY}"),)
    for path in tmp_path.rglob("*.json"):
        assert STATS_KEY not in path.read_text()


def test_payload_contains_canonical_metadata_and_a_bounded_sample() -> None:
    big = b"x" * (SAMPLE_CAP_BYTES * 10)
    payload = build_payload("m", _metadata(), big, len(big))
    user = json.loads(payload["messages"][1]["content"])
    assert user["content_sample_bytes"] == SAMPLE_CAP_BYTES
    assert len(user["content_sample_utf8_lossy"]) == SAMPLE_CAP_BYTES
    assert user["content_sample_is_truncated"] is True
    assert user["content_total_bytes"] == len(big)
    assert user["canonical_source_metadata"]["dataset"]["source_dataset_identifier"] == "SYN:DF"
    assert len(json.dumps(payload)) < SAMPLE_CAP_BYTES + 8192
    assert "non-authoritative" in payload["messages"][0]["content"].lower()
    assert payload["model"] == "m"


def test_a_good_advisory_is_not_replaced_by_a_later_failure(tmp_path: Path) -> None:
    good = _run(tmp_path, FakeTransport(RawResponse(200, (), _ok_body())))
    assert good.path is not None
    kept = good.path.read_bytes()
    again = _run(tmp_path, FakeTransport(RawResponse(500, (), b"")))
    assert again.outcome == "failed"
    assert good.path.read_bytes() == kept


def test_no_hardcoded_model_in_module() -> None:
    source = Path(enrichment.__file__).read_text()
    assert ":free" not in source and "gpt-" not in source and "claude-" not in source
