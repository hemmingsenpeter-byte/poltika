"""Source preservation archive: descriptors, retrieval records, canonical JSON,
hashing and redaction (ADR-0022).

Four separate persistence concepts, mirroring DCAT/data.json semantics:

- `DatasetDescriptor`: what the publisher calls a dataset (identity is the
  publisher's stable identifier, never a display title);
- `DistributionDescriptor`: one way to obtain that dataset (several per dataset);
- `ContentBlob`: the exact response bytes, addressed by SHA-256 of the bytes only;
- `RetrievalRecord`: one auditable retrieval event, never overwritten.

This is evidence of what a source exposed at a point in time. It is NOT
governed modelling data. Nothing here may be imported from, or read by, the
registry, DataContext or models. Unknown values stay `None`; nothing is
inferred (issued, modified and retrieved are independent fields).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

ARCHIVE_RECORD_SCHEMA_VERSION = 1
NON_AUTHORITATIVE_ADVISORY = "NON_AUTHORITATIVE_ADVISORY_METADATA"

SECRET_HEADER_NAMES: frozenset[str] = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "ocp-apim-subscription-key",
        "api-key",
    }
)

SAFE_RESPONSE_HEADERS: frozenset[str] = frozenset(
    {
        "content-type",
        "content-length",
        "content-encoding",
        "etag",
        "last-modified",
        "date",
        "cache-control",
    }
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _plain(value: object) -> Any:
    """Reduce models, tuples and datetimes to JSON-native values."""
    if isinstance(value, BaseModel):
        return _plain(value.model_dump(mode="json", by_alias=False))
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, bytes):
        raise TypeError("bytes are not canonical-JSON serialisable; hash them first")
    return value


def canonical_json(value: object) -> bytes:
    """Deterministic UTF-8 JSON: sorted keys, compact separators, no NaN."""
    return json.dumps(
        _plain(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def redact(text: str, secrets: Iterable[str]) -> str:
    """Replace every non-empty secret in `text` with [REDACTED]."""
    for secret in sorted({s for s in secrets if s}, key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    return text


def _require_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware (UTC)")
    return value.astimezone(UTC)


class ReferenceKind(str, Enum):
    LANDING_PAGE = "landing_page"
    DATA_DICTIONARY = "data_dictionary"
    METHODOLOGY = "methodology"
    TECHNICAL_NOTES = "technical_notes"
    CLASSIFICATION = "classification"
    CODE_LIST = "code_list"
    VOCABULARY = "vocabulary"
    RELEASE_NOTES = "release_notes"
    LICENCE = "licence"
    SECONDARY_CATALOGUE_RECORD = "secondary_catalogue_record"
    OTHER = "other"


class Reference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: ReferenceKind
    url: str
    title: str | None = None
    authoritative: bool = True
    preserved_blob_sha256: str | None = None

    @field_validator("preserved_blob_sha256")
    @classmethod
    def _hex(cls, v: str | None) -> str | None:
        if v is not None and not _SHA256.match(v):
            raise ValueError("preserved_blob_sha256 must be 64 lowercase hex characters")
        return v


class DatasetDescriptor(BaseModel):
    """DCAT/data.json "dataset". Identity is (source_system,
    source_dataset_identifier), never `title`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_system: str
    source_dataset_identifier: str
    title: str | None = None
    description: str | None = None
    publisher_identifier: str | None = None
    publisher_name: str | None = None
    publisher_name_at_capture: str | None = None
    issued: str | None = None
    modified: str | None = None
    temporal_coverage: str | None = None
    spatial_coverage: str | None = None
    accrual_periodicity: str | None = None
    licence: str | None = None
    rights: str | None = None
    attribution: str | None = None
    landing_page: str | None = None
    keywords: tuple[str, ...] = ()
    themes: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    references: tuple[Reference, ...] = ()
    version: str | None = None


class AccessKind(str, Enum):
    API = "api"
    FILE = "file"


class DistributionDescriptor(BaseModel):
    """DCAT "distribution": one way to obtain a dataset."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    distribution_identifier: str
    dataset_identifier: str
    access_kind: AccessKind
    title: str | None = None
    description: str | None = None
    access_url: str | None = None
    download_url: str | None = None
    media_type: str | None = None
    format: str | None = None
    source_resource_identifier: str | None = None
    licence_override: str | None = None
    rights_override: str | None = None
    source_created: str | None = None
    source_modified: str | None = None


class SourceMetadata(BaseModel):
    """Deterministic source metadata for one observation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset: DatasetDescriptor
    distribution: DistributionDescriptor
    native_fields: dict[str, str] = {}

    def sha256(self) -> str:
        return sha256_hex(canonical_json(self))


class BlobStatus(str, Enum):
    CREATED = "created"
    EXISTING = "existing"


class ContentBlob(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sha256: str
    size: int

    @field_validator("sha256")
    @classmethod
    def _hex(cls, v: str) -> str:
        if not _SHA256.match(v):
            raise ValueError("sha256 must be 64 lowercase hex characters")
        return v

    @property
    def identifier(self) -> str:
        return f"sha256:{self.sha256}"


def make_retrieval_id(started_at: datetime, fingerprint: str) -> str:
    return f"{started_at.astimezone(UTC):%Y%m%dT%H%M%S%fZ}-{fingerprint[:12]}"


class RetrievalRecord(BaseModel):
    """One auditable retrieval event. Written once, never overwritten."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    record_schema_version: int = ARCHIVE_RECORD_SCHEMA_VERSION
    retrieval_id: str
    poltika_source_id: str
    source_system: str
    dataset_identifier: str
    distribution_identifier: str
    request_method: str
    endpoint: str
    query_parameters: tuple[tuple[str, str], ...]
    request_body_sha256: str | None
    request_fingerprint: str
    request_started_at: datetime
    response_received_at: datetime
    http_status: int
    content_type: str | None
    content_encoding: str | None
    content_length: int
    response_headers: tuple[tuple[str, str], ...]
    content_sha256: str
    blob_identifier: str
    metadata_sha256: str | None
    metadata_raw_sha256: str | None
    previous_retrieval_id: str | None
    previous_content_sha256: str | None
    previous_metadata_sha256: str | None
    content_changed: bool | None
    metadata_changed: bool | None
    # Non-authoritative secondary-catalogue references; outside the hashed metadata.
    secondary_references: tuple[Reference, ...] = ()
    collector_version: str

    @field_validator("request_started_at", "response_received_at")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return _require_utc(v)
