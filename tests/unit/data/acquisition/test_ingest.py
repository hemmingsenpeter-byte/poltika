"""Ingestion orchestration (ADR-0022): failure policy, dry run, enrichment
isolation and secret safety. Synthetic data; no live network."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from poltika.data.acquisition.archive import SourceArchive
from poltika.data.acquisition.catalogue import SourceEntry, parse_catalogue
from poltika.data.acquisition.ingest import run_sources
from poltika.data.acquisition.source import FetchRequest, RawResponse, RetryPolicy
from poltika.data.acquisition.stats_nz import StatsNzConnector

FIX = Path(__file__).parent / "fixtures" / "stats_nz"
STRUCTURE = (FIX / "structure_dataflow.xml").read_bytes()
DATA = (FIX / "data.csv").read_bytes()
KEY = "SENTINEL-INGEST-KEY-4242424242"

BLOCK = """
  - id: {sid}
    enabled: {enabled}
    verification: synthetic
    dataset: {{identifier: "STATSNZ:{df}"}}
    distribution: {{identifier: ade_csv, access_kind: api}}
    request: {{agency_id: STATSNZ, dataflow_id: {df}, version: "1.0"}}
"""


def entries(*specs: tuple[str, str, bool]) -> list[SourceEntry]:
    text = "source_system: stats_nz\nsources:\n" + "".join(
        BLOCK.format(sid=s, df=d, enabled=str(e).lower()) for s, d, e in specs
    )
    return list(parse_catalogue(text).sources)


class Fake:
    def __init__(self, fail_flow: str | None = None, structure: bytes = STRUCTURE) -> None:
        self.fail_flow, self.structure = fail_flow, structure
        self.requests: list[FetchRequest] = []

    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        self.requests.append(request)
        if self.fail_flow and self.fail_flow in request.url:
            return RawResponse(404, (), b"nope")
        if "/dataflow/" in request.url:
            # the synthetic structure describes TST_TST_001; relabel for other flows
            flow = request.url.rsplit("/", 2)[-2]
            return RawResponse(200, (), self.structure.replace(b"TST_TST_001", flow.encode()))
        return RawResponse(200, (("Content-Type", "text/csv"),), DATA)


def make(fake: Fake) -> StatsNzConnector:
    return StatsNzConnector(
        KEY,
        fake,
        RetryPolicy(max_attempts=1),
        now=lambda: datetime.now(UTC),
        sleep=lambda s: None,
    )


def test_all_continues_after_a_failure_and_exits_non_zero(tmp_path: Path) -> None:
    fake = Fake(fail_flow="BAD_FLOW")
    ents = entries(("one", "TST_A", True), ("bad", "BAD_FLOW", True), ("three", "TST_C", True))
    archive = SourceArchive(tmp_path / "a")
    report = run_sources(ents, make(fake), archive, enrich=False, secrets=[KEY])
    assert [r.ok for r in report.results] == [True, False, True]
    assert report.failed == 1
    assert report.exit_code == 1
    # the source after the failure was still fetched and preserved
    assert archive.latest_record("three") is not None
    assert archive.latest_record("bad") is None
    assert any("FAILED" in line and "404" in line for line in report.lines)


def test_all_success_exits_zero_and_reports_spec_fields(tmp_path: Path) -> None:
    archive = SourceArchive(tmp_path / "a")
    report = run_sources(entries(("one", "TST_A", True)), make(Fake()), archive, enrich=False)
    assert report.exit_code == 0
    text = "\n".join(report.lines)
    for label in (
        "dataset: STATSNZ:TST_A",
        "distribution: ade_csv",
        "http: 200",
        f"bytes: {len(DATA)}",
        "content sha256:",
        "metadata sha256:",
        "content changed: first observation",
        "metadata changed: first observation",
        "content blob: created",
        "native metadata blob: created",
        "retrieval record:",
    ):
        assert label in text
    # a second run: unchanged content, existing blob, a new record
    again = run_sources(entries(("one", "TST_A", True)), make(Fake()), archive, enrich=False)
    text2 = "\n".join(again.lines)
    assert "content changed: no" in text2 and "content blob: existing" in text2
    assert len(archive.records("one")) == 2


def test_disabled_entries_are_skipped_not_failed(tmp_path: Path) -> None:
    fake = Fake()
    archive = SourceArchive(tmp_path / "a")
    report = run_sources(
        entries(("disabled_one", "TST_A", False), ("enabled_one", "TST_B", True)),
        make(fake),
        archive,
        enrich=False,
    )
    assert report.exit_code == 0
    assert report.results[0].skipped
    assert archive.latest_record("disabled_one") is None
    assert not any("TST_A" in r.url for r in fake.requests)


def test_dry_run_makes_no_network_calls_and_writes_nothing(tmp_path: Path) -> None:
    fake = Fake()
    root = tmp_path / "a"
    report = run_sources(
        entries(("one", "TST_A", True)),
        StatsNzConnector(None, fake),  # no key needed
        SourceArchive(root),
        dry_run=True,
    )
    assert fake.requests == []
    assert not root.exists()
    text = "\n".join(report.lines)
    assert "fingerprint:" in text and "/data/STATSNZ,TST_A,1.0/all" in text
    assert "format=csvfilewithlabels" in text
    assert "no network call" in text
    assert report.exit_code == 0


def test_enrichment_runs_only_after_preserve_and_only_when_enabled(tmp_path: Path) -> None:
    seen: list[Any] = []

    def fake_enrich(root: Path, record: Any, metadata: Any, sample: bytes, **kw: Any) -> Any:
        # evidence is already on disk when enrichment is called
        assert SourceArchive(root).latest_record("one") is not None
        seen.append((record.retrieval_id, sample))

        class R:
            outcome = "ok"
            error = None

        return R()

    archive = SourceArchive(tmp_path / "a")
    report = run_sources(
        entries(("one", "TST_A", True)), make(Fake()), archive, enrich_fn=fake_enrich
    )
    assert len(seen) == 1 and seen[0][1] == DATA
    assert any("advisory enrichment: ok" in line for line in report.lines)
    off = run_sources(
        entries(("one", "TST_A", True)), make(Fake()), archive, enrich=False, enrich_fn=fake_enrich
    )
    assert len(seen) == 1
    assert not any("advisory" in line for line in off.lines)


def test_enrichment_failure_cannot_fail_ingestion(tmp_path: Path) -> None:
    def boom(*a: Any, **k: Any) -> Any:
        raise RuntimeError(f"model gone {KEY}")

    archive = SourceArchive(tmp_path / "a")
    report = run_sources(
        entries(("one", "TST_A", True)), make(Fake()), archive, enrich_fn=boom, secrets=[KEY]
    )
    assert report.exit_code == 0
    assert any("failed" in line and "advisory" in line for line in report.lines)
    assert KEY not in "\n".join(report.lines)


def test_key_is_nowhere_in_archive_or_report(tmp_path: Path) -> None:
    root = tmp_path / "a"
    report = run_sources(
        entries(("one", "TST_A", True), ("bad", "BAD_FLOW", True)),
        make(Fake(fail_flow="BAD_FLOW")),
        SourceArchive(root),
        enrich=False,
        secrets=[KEY],
    )
    assert KEY not in "\n".join(report.lines)
    files = [p for p in root.rglob("*") if p.is_file()]
    assert files
    for path in files:
        assert KEY.encode() not in path.read_bytes(), path
        assert KEY not in str(path)
