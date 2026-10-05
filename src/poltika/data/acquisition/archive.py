"""Source preservation archive: content-addressed blob store, metadata
snapshots, retrieval records and change detection (ADR-0022).

Layout under the archive root (never `data/raw`, never `data/metadata`):

    blobs/sha256/<ab>/<64-hex>                       exact response bytes
    metadata/<system>/<source id>/<sha256>.json      canonical SourceMetadata
    records/<system>/<source id>/<retrieval id>.json one retrieval event

Blob identity is the SHA-256 of the bytes only. Nothing is ever overwritten:
an existing blob is re-verified, a corrupt one raises `CorruptBlobError`, and
an existing record path raises `ArchiveError`. Writes use a temp file in the
same directory, fsync, then publish with `os.link` (fails if the target
exists), so a crash leaves no partial file at a final name and concurrent
writers of the same bytes are safe.
"""

from __future__ import annotations

import contextlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from poltika.common.errors import PoltikaError
from poltika.data.acquisition.models import (
    BlobStatus,
    ContentBlob,
    RetrievalRecord,
    SourceMetadata,
    canonical_json,
    make_retrieval_id,
    sha256_hex,
)
from poltika.data.acquisition.source import SourceObservation

ENV_ARCHIVE_DIR = "POLTIKA_SOURCE_ARCHIVE_DIR"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
# Retrieval ids are f"{UTC timestamp}Z-{fingerprint[:12]}" and carry an uppercase T and Z.
_RETRIEVAL_ID = re.compile(r"^[0-9][A-Za-z0-9_.-]*$")


class ArchiveError(PoltikaError):
    """Archive integrity or usage error."""


class CorruptBlobError(ArchiveError):
    """A stored object's bytes do not hash to its name."""


class UnsafePathError(ArchiveError):
    """An id or hash could not be safely used as a path component."""


def default_archive_root(repo_root: Path) -> Path:
    override = os.environ.get(ENV_ARCHIVE_DIR)
    if override:
        return Path(override)
    return repo_root / "data" / "source_archive" / "runtime"


def _check_sha256(value: str) -> str:
    if not isinstance(value, str) or not _SHA256.match(value):
        raise UnsafePathError("sha256 must be 64 lowercase hex characters")
    return value


def _check_component(value: str, label: str, *, retrieval: bool = False) -> str:
    pattern = _RETRIEVAL_ID if retrieval else _COMPONENT
    if (
        not isinstance(value, str)
        or not value
        or ".." in value
        or "/" in value
        or "\\" in value
        or "\x00" in value
        or not pattern.match(value)
    ):
        raise UnsafePathError(f"unsafe {label}: {value!r}")
    return value


def _fsync_dir(directory: Path) -> None:
    with contextlib.suppress(OSError):
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _write_exclusive(path: Path, data: bytes) -> bool:
    """Atomically publish `data` at `path` without overwriting.

    Returns True if this call created the file, False if it already existed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o444)
        try:
            os.link(tmp, path)
        except FileExistsError:
            return False
        _fsync_dir(path.parent)
        return True
    finally:
        with contextlib.suppress(FileNotFoundError):
            tmp.unlink()


class BlobStore(Protocol):
    def put(self, data: bytes) -> tuple[ContentBlob, BlobStatus]: ...

    def get(self, sha256: str) -> bytes: ...

    def exists(self, sha256: str) -> bool: ...


class LocalBlobStore:
    def __init__(self, root: Path) -> None:
        self._base = root / "blobs" / "sha256"

    def _path(self, sha256: str) -> Path:
        _check_sha256(sha256)
        return self._base / sha256[:2] / sha256

    def put(self, data: bytes) -> tuple[ContentBlob, BlobStatus]:
        digest = sha256_hex(data)
        path = self._path(digest)
        blob = ContentBlob(sha256=digest, size=len(data))
        if path.exists():
            self.get(digest)  # verifies; raises CorruptBlobError, never replaces
            return blob, BlobStatus.EXISTING
        if _write_exclusive(path, data):
            return blob, BlobStatus.CREATED
        self.get(digest)  # lost a race: verify the winner's bytes
        return blob, BlobStatus.EXISTING

    def get(self, sha256: str) -> bytes:
        path = self._path(sha256)
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise ArchiveError(f"blob sha256:{sha256} not found") from None
        if sha256_hex(data) != sha256:
            raise CorruptBlobError(f"blob sha256:{sha256} is corrupt: stored bytes do not match")
        return data

    def exists(self, sha256: str) -> bool:
        return self._path(sha256).exists()


@dataclass(frozen=True)
class PreserveResult:
    record: RetrievalRecord
    record_path: Path
    content_blob_status: BlobStatus
    metadata_blob_status: BlobStatus | None
    metadata_snapshot_status: BlobStatus | None


def _header(headers: tuple[tuple[str, str], ...], name: str) -> str | None:
    for key, value in headers:
        if key.lower() == name:
            return value
    return None


class SourceArchive:
    def __init__(self, root: Path, blobs: BlobStore | None = None) -> None:
        self.root = root
        self.blobs: BlobStore = blobs if blobs is not None else LocalBlobStore(root)

    def _dir(self, kind: str, source_system: str, source_id: str) -> Path:
        _check_component(source_system, "source_system")
        _check_component(source_id, "poltika_source_id")
        return self.root / kind / source_system / source_id

    def records(
        self, poltika_source_id: str, source_system: str | None = None
    ) -> list[RetrievalRecord]:
        """All records for a source, oldest first. `source_system` narrows the search;
        omitted, every system directory is searched."""
        _check_component(poltika_source_id, "poltika_source_id")
        base = self.root / "records"
        if not base.is_dir():
            return []
        systems = [source_system] if source_system else sorted(p.name for p in base.iterdir())
        found: list[RetrievalRecord] = []
        for system in systems:
            directory = self._dir("records", system, poltika_source_id)
            if not directory.is_dir():
                continue
            for path in directory.glob("*.json"):
                found.append(RetrievalRecord.model_validate_json(path.read_bytes()))
        return sorted(found, key=lambda r: (r.request_started_at, r.retrieval_id))

    def latest_record(
        self, poltika_source_id: str, source_system: str | None = None
    ) -> RetrievalRecord | None:
        found = self.records(poltika_source_id, source_system)
        return found[-1] if found else None

    def read_metadata(
        self, metadata_sha256: str, source_system: str, poltika_source_id: str
    ) -> SourceMetadata:
        _check_sha256(metadata_sha256)
        path = self._dir("metadata", source_system, poltika_source_id) / f"{metadata_sha256}.json"
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise ArchiveError(f"metadata snapshot {metadata_sha256} not found") from None
        if sha256_hex(data) != metadata_sha256:
            raise CorruptBlobError(f"metadata snapshot {metadata_sha256} is corrupt")
        return SourceMetadata.model_validate_json(data)

    def preserve(self, observation: SourceObservation, *, collector_version: str) -> PreserveResult:
        content = observation.content
        if not 200 <= content.status < 300:
            raise ArchiveError(f"only 2xx observations are preserved (got HTTP {content.status})")
        metadata = observation.metadata
        source_system = metadata.dataset.source_system
        source_id = observation.poltika_source_id
        meta_dir = self._dir("metadata", source_system, source_id)
        record_dir = self._dir("records", source_system, source_id)

        content_blob, content_status = self.blobs.put(content.body)

        raw_sha: str | None = None
        raw_status: BlobStatus | None = None
        if observation.native_metadata is not None:
            raw_blob, raw_status = self.blobs.put(observation.native_metadata.body)
            raw_sha = raw_blob.sha256

        meta_bytes = canonical_json(metadata)
        meta_sha = sha256_hex(meta_bytes)
        meta_path = meta_dir / f"{meta_sha}.json"
        if _write_exclusive(meta_path, meta_bytes):
            snapshot_status = BlobStatus.CREATED
        else:
            if sha256_hex(meta_path.read_bytes()) != meta_sha:
                raise CorruptBlobError(f"metadata snapshot {meta_sha} is corrupt")
            snapshot_status = BlobStatus.EXISTING

        previous = self.latest_record(source_id, source_system)
        content_changed: bool | None = None
        metadata_changed: bool | None = None
        if previous is not None:
            content_changed = previous.content_sha256 != content_blob.sha256
            if previous.metadata_sha256 is not None:
                metadata_changed = previous.metadata_sha256 != meta_sha

        request = content.request
        fingerprint = request.fingerprint()
        record = RetrievalRecord(
            retrieval_id=make_retrieval_id(content.started_at, fingerprint),
            poltika_source_id=source_id,
            source_system=source_system,
            dataset_identifier=metadata.dataset.source_dataset_identifier,
            distribution_identifier=metadata.distribution.distribution_identifier,
            request_method=request.method.upper(),
            endpoint=request.url,
            query_parameters=request.sorted_query(),
            request_body_sha256=sha256_hex(request.body) if request.body is not None else None,
            request_fingerprint=fingerprint,
            request_started_at=content.started_at,
            response_received_at=content.received_at,
            http_status=content.status,
            content_type=_header(content.headers, "content-type"),
            content_encoding=_header(content.headers, "content-encoding"),
            content_length=len(content.body),
            response_headers=content.headers,
            content_sha256=content_blob.sha256,
            blob_identifier=content_blob.identifier,
            metadata_sha256=meta_sha,
            metadata_raw_sha256=raw_sha,
            previous_retrieval_id=previous.retrieval_id if previous else None,
            previous_content_sha256=previous.content_sha256 if previous else None,
            previous_metadata_sha256=previous.metadata_sha256 if previous else None,
            content_changed=content_changed,
            metadata_changed=metadata_changed,
            collector_version=collector_version,
        )
        _check_component(record.retrieval_id, "retrieval_id", retrieval=True)
        record_path = record_dir / f"{record.retrieval_id}.json"
        if not _write_exclusive(record_path, canonical_json(record) + b"\n"):
            raise ArchiveError(f"record {record.retrieval_id} already exists; never overwritten")
        return PreserveResult(
            record=record,
            record_path=record_path,
            content_blob_status=content_status,
            metadata_blob_status=raw_status,
            metadata_snapshot_status=snapshot_status,
        )
