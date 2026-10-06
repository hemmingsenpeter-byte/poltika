"""Optional OpenRouter advisory enrichment of a preserved retrieval.

Runs only after `SourceArchive.preserve()` has returned, so the evidence is
already on disk. It asks a language model for an advisory summary (schema,
column explanations, suggested tags, candidate relationships) and stores the
answer under `<root>/advisory/`, marked `NON_AUTHORITATIVE_ADVISORY_METADATA`.

Boundaries, each tested in `tests/unit/data/acquisition/test_enrichment.py`:

- Not configured (`OPENROUTER_API_KEY` or `POLTIKA_OPENROUTER_MODEL` unset)
  means `skipped`: no network call, no file. No model is hardcoded.
- It never raises. A rate limit, 4xx/5xx, timeout, malformed answer or a
  removed model gives outcome `failed` and ingestion carries on.
- It writes only under `advisory/`. It never touches `records/`,
  `metadata/` or `blobs/`.
- The payload holds a bounded content sample and the canonical
  `SourceMetadata` JSON. The OpenRouter key travels only in
  `FetchRequest.secret_headers`; no Stats NZ key or other credential is ever
  in scope here.
- The output is advisory. It never establishes identity, licence, dates,
  provenance, a manifest or a mapping (spec section 18).
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from poltika.data.acquisition.models import (
    NON_AUTHORITATIVE_ADVISORY,
    RetrievalRecord,
    SourceMetadata,
    canonical_json,
    redact,
    sha256_hex,
)
from poltika.data.acquisition.source import FetchRequest, Transport

ENV_API_KEY = "OPENROUTER_API_KEY"
ENV_MODEL = "POLTIKA_OPENROUTER_MODEL"
PROVIDER = "openrouter"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
SAMPLE_CAP_BYTES = 8 * 1024
OUTPUT_CAP_CHARS = 64 * 1024
REQUEST_TIMEOUT_SECONDS = 30.0
MAX_COMPLETION_TOKENS = 1024
_ERROR_CAP_CHARS = 300
_SAFE_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
_SAFE_RETRIEVAL_ID = re.compile(r"^[0-9][A-Za-z0-9_.-]*$")  # matches archive.py

OUTCOME_OK = "ok"
OUTCOME_SKIPPED = "skipped"
OUTCOME_FAILED = "failed"

SYSTEM_PROMPT = (
    "You assist a data archivist. Everything you write is NON-AUTHORITATIVE ADVISORY "
    "metadata: a human has not checked it and it must never be used as a fact about the "
    "source. Using only the metadata and the bounded content sample supplied, reply with "
    "JSON holding exactly these keys: schema_summary (string), column_explanations "
    "(object of column name to short explanation), suggested_tags (list of strings), "
    "candidate_relationships (list of strings, each a possible link to another dataset "
    "or concept, stated as a hypothesis). Do not state a licence, a publication or "
    "revision date, a publisher identity, a dataset identifier or any provenance. If you "
    "cannot tell, say 'unknown'."
)


@dataclass(frozen=True)
class AdvisoryResult:
    outcome: str  # "ok" | "skipped" | "failed"
    path: Path | None = None
    input_sha256: str | None = None
    error: str | None = None


def _now() -> datetime:
    return datetime.now(UTC)


def _safe(component: str, pattern: re.Pattern[str] = _SAFE_COMPONENT) -> str:
    if not pattern.match(component) or ".." in component:
        raise ValueError("unsafe path component")
    return component


def build_payload(
    model: str, metadata: SourceMetadata, content_sample: bytes, content_size: int
) -> dict[str, Any]:
    """The request body: model, prompt, bounded sample and canonical metadata. No secrets."""
    sample = content_sample[:SAMPLE_CAP_BYTES]
    user = {
        "canonical_source_metadata": json.loads(canonical_json(metadata)),
        "content_sample_utf8_lossy": sample.decode("utf-8", errors="replace"),
        "content_sample_bytes": len(sample),
        "content_total_bytes": content_size,
        "content_sample_is_truncated": content_size > len(sample),
    }
    return {
        "model": model,
        "temperature": 0,
        "max_tokens": MAX_COMPLETION_TOKENS,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user, sort_keys=True, ensure_ascii=False)},
        ],
    }


def _extract_output(body: bytes) -> object:
    parsed = json.loads(body.decode("utf-8"))
    content = parsed["choices"][0]["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise ValueError("empty model answer")
    content = content[:OUTPUT_CAP_CHARS]
    try:
        return json.loads(content)
    except ValueError:
        return content


def _advisory_path(root: Path, record: RetrievalRecord, input_sha256: str) -> Path:
    return (
        root
        / "advisory"
        / _safe(record.source_system)
        / _safe(record.poltika_source_id)
        / f"{_safe(record.retrieval_id, _SAFE_RETRIEVAL_ID)}.{input_sha256[:12]}.json"
    )


def _already_ok(path: Path) -> bool:
    try:
        return bool(json.loads(path.read_text("utf-8")).get("outcome") == OUTCOME_OK)
    except (OSError, ValueError):
        return False


def _write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".advisory-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(canonical_json(document))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def enrich(
    archive_root: Path,
    record: RetrievalRecord,
    metadata: SourceMetadata,
    content_sample: bytes,
    *,
    transport: Transport | None = None,
    env: Mapping[str, str] | None = None,
    now: Callable[[], datetime] = _now,
) -> AdvisoryResult:
    """Ask the configured model for advisory metadata. Never raises."""
    environ = os.environ if env is None else env
    key = environ.get(ENV_API_KEY, "").strip()
    model = environ.get(ENV_MODEL, "").strip()
    if not key or not model:
        return AdvisoryResult(OUTCOME_SKIPPED, error="OpenRouter is not configured")
    try:
        payload = build_payload(model, metadata, content_sample, record.content_length)
        input_sha256 = sha256_hex(canonical_json(payload["messages"]))
        path = _advisory_path(archive_root, record, input_sha256)
    except Exception as exc:  # noqa: BLE001 - enrichment must never reach ingestion
        return AdvisoryResult(OUTCOME_FAILED, error=_safe_error(exc, key))
    outcome, output, error = _ask(payload, key, transport)
    document: dict[str, Any] = {
        "status": NON_AUTHORITATIVE_ADVISORY,
        "provider": PROVIDER,
        "model": model,
        "created_at": now().astimezone(UTC).isoformat(),
        "input_sha256": input_sha256,
        "poltika_source_id": record.poltika_source_id,
        "retrieval_id": record.retrieval_id,
        "content_sha256": record.content_sha256,
        "output": output,
        "outcome": outcome,
        "error": error,
    }
    try:
        if not _already_ok(path):
            _write(path, document)
    except Exception as exc:  # noqa: BLE001
        return AdvisoryResult(OUTCOME_FAILED, None, input_sha256, _safe_error(exc, key))
    return AdvisoryResult(outcome, path, input_sha256, error)


def _safe_error(exc: BaseException, key: str) -> str:
    text = f"{type(exc).__name__}: {exc}"
    return redact(text, [key])[:_ERROR_CAP_CHARS]


def _ask(
    payload: dict[str, Any], key: str, transport: Transport | None
) -> tuple[str, object, str | None]:
    try:
        if transport is None:
            from poltika.data.acquisition.source import UrllibTransport

            transport = UrllibTransport()
        request = FetchRequest(
            method="POST",
            url=ENDPOINT,
            body=json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8"),
            headers=(("Accept", "application/json"), ("Content-Type", "application/json")),
            secret_headers=(("Authorization", f"Bearer {key}"),),
        )
        response = transport.send(request, REQUEST_TIMEOUT_SECONDS)
        if not 200 <= response.status < 300:
            return OUTCOME_FAILED, None, f"OpenRouter returned HTTP {response.status}"
        return OUTCOME_OK, _extract_output(response.body), None
    except Exception as exc:  # noqa: BLE001 - timeouts, malformed JSON, anything
        return OUTCOME_FAILED, None, _safe_error(exc, key)
