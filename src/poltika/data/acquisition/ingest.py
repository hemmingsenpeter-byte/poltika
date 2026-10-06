"""Source preservation archive: ingestion orchestration and the Stats NZ CLI
(ADR-0022).

`scripts/ingest/stats_nz.py` is a thin entry point. All logic lives here so it
is type-checked and testable.

Failure policy for `--all` (decided and tested): independent sources do not
block each other. A failure on one source is reported, the remaining sources
still run, and the exit code is 1 if any source failed. Evidence already
preserved is never rolled back; every retrieval is its own record. Disabled
entries are skipped and reported, and do not count as failures.

Exit codes: 0 success, 1 acquisition failure, 2 usage error or missing key.

Order per source: fetch, hash and persist evidence (`SourceArchive.preserve`),
then, only if enabled and only after that succeeded, optional advisory
enrichment, which can never fail ingestion. A dry run builds and prints the
requests and touches neither the network nor the archive.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from poltika.data.acquisition.archive import SourceArchive, default_archive_root
from poltika.data.acquisition.catalogue import (
    CatalogueError,
    SourceCatalogue,
    SourceEntry,
    default_catalogue_path,
    load_catalogue,
)
from poltika.data.acquisition.data_govt_nz import lookup_package
from poltika.data.acquisition.models import redact
from poltika.data.acquisition.source import SourceConnector, Transport
from poltika.data.acquisition.stats_nz import ENV_API_KEY, StatsNzConnector

COLLECTOR_VERSION = "poltika-source-archive/0.1"
CONTENT_SAMPLE_BYTES = 8 * 1024

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

EnrichFn = Callable[..., Any]


@dataclass(frozen=True)
class SourceResult:
    source_id: str
    ok: bool
    skipped: bool = False
    dataset: str | None = None
    distribution: str | None = None
    http_status: int | None = None
    size: int | None = None
    content_sha256: str | None = None
    metadata_sha256: str | None = None
    content_changed: bool | None = None
    metadata_changed: bool | None = None
    content_blob: str | None = None
    metadata_blob: str | None = None
    retrieval_id: str | None = None
    record_path: str | None = None
    enrichment: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class RunReport:
    results: tuple[SourceResult, ...]
    dry_run: bool
    lines: tuple[str, ...]

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.ok and not r.skipped)

    @property
    def exit_code(self) -> int:
        return EXIT_FAILED if self.failed else EXIT_OK


def _changed(value: bool | None) -> str:
    return "first observation" if value is None else ("yes" if value else "no")


def _not_fetched(r: SourceResult) -> bool:
    return r.metadata_sha256 is None


def result_lines(r: SourceResult) -> list[str]:
    if r.skipped:
        return [f"source: {r.source_id}", "  skipped: disabled in the catalogue"]
    if not r.ok:
        return [f"source: {r.source_id}", f"  FAILED: {r.error}"]
    lines = [
        f"source: {r.source_id}",
        f"  dataset: {r.dataset}",
        f"  distribution: {r.distribution}",
        f"  http: {r.http_status}",
        f"  bytes: {r.size}",
        f"  content sha256: {r.content_sha256}",
        f"  metadata sha256: {'not fetched' if _not_fetched(r) else r.metadata_sha256}",
        f"  content changed: {_changed(r.content_changed)}",
        f"  metadata changed: {'not fetched' if _not_fetched(r) else _changed(r.metadata_changed)}",
        f"  content blob: {r.content_blob}",
    ]
    if r.metadata_blob is not None:
        lines.append(f"  native metadata blob: {r.metadata_blob}")
    lines.append(f"  retrieval record: {r.retrieval_id} created")
    if r.enrichment is not None:
        lines.append(f"  advisory enrichment: {r.enrichment}")
    return lines


def _dry_run_lines(
    connector: StatsNzConnector, entry: SourceEntry, include_metadata: bool
) -> list[str]:
    lines = [f"source: {entry.id}", f"  dataset: {entry.dataset.identifier}"]
    lines.append(f"  distribution: {entry.distribution.identifier}")
    for label, request in connector.plan(entry, include_metadata=include_metadata):
        query = "&".join(f"{k}={v}" for k, v in request.sorted_query())
        lines.append(f"  {label} request: {request.method} {request.url}")
        lines.append(f"    query: {query or '(none)'}")
        lines.append(f"    fingerprint: {request.fingerprint()}")
    lines.append("  dry run: no network call, nothing written")
    return lines


def _enrich(
    enrich_fn: EnrichFn | None,
    archive_root: Path,
    result: Any,
    metadata: Any,
    sample: bytes,
    env: Mapping[str, str],
    secrets: Iterable[str],
) -> str:
    """Advisory enrichment. Every outcome is a string; nothing is raised."""
    try:
        fn: EnrichFn
        if enrich_fn is not None:
            fn = enrich_fn
        else:
            from poltika.data.acquisition.enrichment import enrich as default_enrich

            fn = default_enrich
        advisory = fn(archive_root, result.record, metadata, sample, env=env)
        outcome = str(getattr(advisory, "outcome", "unknown"))
        error = getattr(advisory, "error", None)
        text = f"{outcome} (advisory, non-authoritative)"
        return redact(f"{text}: {error}", secrets) if error else text
    except Exception as exc:  # noqa: BLE001 - enrichment can never fail ingestion
        return redact(f"failed ({type(exc).__name__}) (advisory, non-authoritative)", secrets)


def run_sources(
    entries: Sequence[SourceEntry],
    connector: StatsNzConnector | SourceConnector,
    archive: SourceArchive,
    *,
    dry_run: bool = False,
    include_metadata: bool = True,
    enrich: bool = True,
    env: Mapping[str, str] | None = None,
    enrich_fn: EnrichFn | None = None,
    secrets: Iterable[str] = (),
) -> RunReport:
    """Run each entry independently. Continue past a failure; report every one."""
    environ: Mapping[str, str] = os.environ if env is None else env
    secret_list = tuple(secrets)
    results: list[SourceResult] = []
    lines: list[str] = []
    for entry in entries:
        if not entry.enabled:
            result = SourceResult(source_id=entry.id, ok=False, skipped=True)
            results.append(result)
            lines.extend(result_lines(result))
            continue
        if dry_run:
            if not isinstance(connector, StatsNzConnector):
                raise TypeError("dry run needs a connector that can plan requests")
            lines.extend(_dry_run_lines(connector, entry, include_metadata))
            results.append(
                SourceResult(source_id=entry.id, ok=True, dataset=entry.dataset.identifier)
            )
            continue
        try:
            observation = connector.observe(entry, include_metadata=include_metadata)
            preserved = archive.preserve(observation, collector_version=COLLECTOR_VERSION)
            record = preserved.record
            enrichment: str | None = None
            if enrich:
                enrichment = _enrich(
                    enrich_fn,
                    archive.root,
                    preserved,
                    observation.metadata,
                    observation.content.body[:CONTENT_SAMPLE_BYTES],
                    environ,
                    secret_list,
                )
            result = SourceResult(
                source_id=entry.id,
                ok=True,
                dataset=record.dataset_identifier,
                distribution=record.distribution_identifier,
                http_status=record.http_status,
                size=record.content_length,
                content_sha256=record.content_sha256,
                metadata_sha256=record.metadata_sha256,
                content_changed=record.content_changed,
                metadata_changed=record.metadata_changed,
                content_blob=preserved.content_blob_status.value,
                metadata_blob=(
                    preserved.metadata_blob_status.value
                    if preserved.metadata_blob_status is not None
                    else None
                ),
                retrieval_id=record.retrieval_id,
                record_path=str(preserved.record_path),
                enrichment=enrichment,
            )
        except Exception as exc:  # noqa: BLE001 - one failing source never blocks the others
            message = redact(f"{type(exc).__name__}: {exc}", secret_list)
            result = SourceResult(source_id=entry.id, ok=False, error=message)
        results.append(result)
        lines.extend(result_lines(result))
    report_lines = tuple(lines)
    return RunReport(results=tuple(results), dry_run=dry_run, lines=report_lines)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stats_nz.py",
        description=(
            "Preserve Stats NZ Aotearoa Data Explorer source evidence. "
            f"Needs {ENV_API_KEY} for a real fetch. Preservation only: nothing here is "
            "validated or approved for modelling."
        ),
    )
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--list", action="store_true", help="list catalogue entries and exit")
    what.add_argument("--dataset", metavar="ID", help="ingest one catalogue entry")
    what.add_argument("--all", action="store_true", help="ingest every enabled entry")
    parser.add_argument(
        "--dry-run", action="store_true", help="print requests; no network, no writes"
    )
    parser.add_argument(
        "--no-metadata", action="store_true", help="skip the structure (metadata) request"
    )
    parser.add_argument(
        "--no-enrich", action="store_true", help="skip optional advisory enrichment"
    )
    parser.add_argument(
        "--with-secondary-catalogue",
        action="store_true",
        help="look up configured data.govt.nz package names (one extra request each)",
    )
    parser.add_argument("--archive-dir", type=Path, help="archive root (default: see below)")
    parser.add_argument("--catalogue", type=Path, help="catalogue YAML (default: stats_nz.yaml)")
    parser.epilog = (
        "Archive root: --archive-dir, else POLTIKA_SOURCE_ARCHIVE_DIR, "
        "else data/source_archive/runtime. Exit codes: 0 ok, 1 acquisition failure, "
        "2 usage error or missing key."
    )
    return parser


def _list_lines(catalogue: SourceCatalogue) -> list[str]:
    lines = []
    for entry in catalogue.sources:
        state = "enabled" if entry.enabled else "disabled"
        lines.append(
            f"{entry.id}\t{state}\t{entry.dataset.identifier}\t{entry.distribution.identifier}"
        )
    return lines


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    transport: Transport | None = None,
    repo_root: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    enrich_fn: EnrichFn | None = None,
) -> int:
    out = stdout if stdout is not None else sys.stdout
    err = stderr if stderr is not None else sys.stderr
    environ: Mapping[str, str] = os.environ if env is None else env
    root = repo_root if repo_root is not None else _repo_root()
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    catalogue_path = args.catalogue or default_catalogue_path(root)
    try:
        catalogue = load_catalogue(catalogue_path)
    except CatalogueError as exc:
        print(f"error: {exc}", file=err)
        return EXIT_USAGE

    if args.list:
        for line in _list_lines(catalogue):
            print(line, file=out)
        return EXIT_OK

    if args.dataset:
        try:
            entry = catalogue.get(args.dataset)
        except CatalogueError as exc:
            print(f"error: {exc}", file=err)
            return EXIT_USAGE
        if not entry.enabled:
            print(f"error: source {entry.id!r} is disabled in the catalogue", file=err)
            return EXIT_USAGE
        entries: tuple[SourceEntry, ...] = (entry,)
    else:
        entries = catalogue.sources

    api_key = environ.get(ENV_API_KEY, "").strip() or None
    if not args.dry_run and api_key is None:
        print(
            f"error: {ENV_API_KEY} is not set. A real fetch needs a Stats NZ API subscription "
            "key in that environment variable. Use --dry-run to see the requests without it.",
            file=err,
        )
        return EXIT_USAGE

    connector = StatsNzConnector(
        api_key,
        transport,
        secondary_lookup=(
            (lambda name: lookup_package(name, transport))
            if args.with_secondary_catalogue
            else None
        ),
    )
    archive_root = (
        args.archive_dir if args.archive_dir else default_archive_root_from(environ, root)
    )
    archive = SourceArchive(archive_root)
    report = run_sources(
        entries,
        connector,
        archive,
        dry_run=args.dry_run,
        include_metadata=not args.no_metadata,
        enrich=not args.no_enrich,
        env=environ,
        enrich_fn=enrich_fn,
        secrets=connector.secrets,
    )
    for line in report.lines:
        print(line, file=out)
    if not args.dry_run:
        print(
            f"summary: {len(report.results) - report.failed} ok, {report.failed} failed", file=out
        )
    return report.exit_code


def default_archive_root_from(environ: Mapping[str, str], repo_root: Path) -> Path:
    """`default_archive_root` reads the process environment; honour an injected one."""
    override = environ.get("POLTIKA_SOURCE_ARCHIVE_DIR")
    if override:
        return Path(override)
    return default_archive_root(repo_root)
