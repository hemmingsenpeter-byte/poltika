"""Stats NZ connector (ADR-0022): request determinism, secret safety and
metadata extraction. Synthetic fixtures only; no live network."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poltika.data.acquisition.catalogue import CatalogueError, SourceEntry, parse_catalogue
from poltika.data.acquisition.models import ReferenceKind
from poltika.data.acquisition.source import (
    FetchRequest,
    PermanentHttpError,
    RawResponse,
    RetryPolicy,
    TransportError,
)
from poltika.data.acquisition.stats_nz import (
    API_KEY_HEADER,
    StatsNzConnector,
    StatsNzError,
    parse_request,
    parse_structure,
)

FIX = Path(__file__).parent / "fixtures" / "stats_nz"
STRUCTURE = (FIX / "structure_dataflow.xml").read_bytes()
DATA = (FIX / "data.csv").read_bytes()
KEY = "SENTINEL-STATSNZ-KEY-0123456789"

CATALOGUE = """
source_system: stats_nz
sources:
  - id: syn_flow
    verification: synthetic
    note: Synthetic test table
    dataset:
      identifier: "STATSNZ:TST_TST_001"
      publisher_identifier: STATSNZ
      publisher_name: Reviewer Configured Name
      licence: Reviewer licence
      accrual_periodicity: Reviewer periodicity
      landing_page: https://example.invalid/page
      references:
        - {kind: methodology, url: "https://example.invalid/method"}
    distribution: {identifier: ade_csv, access_kind: api, format: csv, media_type: text/csv}
    request:
      agency_id: STATSNZ
      dataflow_id: TST_TST_001
      version: "1.0"
    secondary_catalogue: {data_govt_nz_package: pkg-one}
"""


def entry() -> SourceEntry:
    return parse_catalogue(CATALOGUE).get("syn_flow")


class Fake:
    """Routes by URL path; records every request it sees."""

    def __init__(self, structure: bytes = STRUCTURE, data: bytes = DATA) -> None:
        self.structure, self.data = structure, data
        self.requests: list[FetchRequest] = []
        self.fail_structure: int | None = None

    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        self.requests.append(request)
        if "/dataflow/" in request.url:
            if self.fail_structure is not None:
                return RawResponse(self.fail_structure, (), b"")
            return RawResponse(200, (("Content-Type", "application/xml"),), self.structure)
        return RawResponse(200, (("Content-Type", "text/csv"),), self.data)


FAST = RetryPolicy(max_attempts=1)


def connector(fake: Fake, key: str | None = KEY) -> StatsNzConnector:
    return StatsNzConnector(
        key,
        fake,
        FAST,
        now=lambda: datetime(2026, 10, 6, tzinfo=UTC),
        sleep=lambda s: None,
    )


def test_requests_are_deterministic_and_follow_documented_shape() -> None:
    a, b = connector(Fake()), connector(Fake(), key="a-different-key")
    ra, rb = a.data_request(entry()), b.data_request(entry())
    assert ra.model_dump() == rb.model_dump()  # secret headers are excluded from dumps
    assert ra.fingerprint() == rb.fingerprint()  # key is not in the fingerprint
    assert ra.url == "https://api.data.stats.govt.nz/rest/data/STATSNZ,TST_TST_001,1.0/all"
    assert ra.query == (("format", "csvfilewithlabels"),)
    sr = a.structure_request(entry())
    assert sr.url == "https://api.data.stats.govt.nz/rest/dataflow/STATSNZ/TST_TST_001/1.0"
    assert dict(sr.query) == {"references": "all", "detail": "referencepartial"}
    assert a.structure_request(entry()).fingerprint() == sr.fingerprint()


def test_key_goes_only_into_secret_headers() -> None:
    req = connector(Fake()).data_request(entry())
    assert req.secret_headers == ((API_KEY_HEADER, KEY),)
    assert KEY not in repr(req) and KEY not in req.model_dump_json()
    assert all(KEY not in v for _, v in req.headers)
    assert KEY not in req.fingerprint()
    # without a key a request can still be planned (dry run) with the same fingerprint
    keyless = connector(Fake(), key=None).data_request(entry())
    assert keyless.secret_headers == ()
    assert keyless.fingerprint() == req.fingerprint()


def test_blank_key_is_no_key() -> None:
    assert not StatsNzConnector("   ").has_api_key


def test_plan_labels_requests() -> None:
    c = connector(Fake())
    assert [label for label, _ in c.plan(entry())] == ["content", "metadata"]
    assert [label for label, _ in c.plan(entry(), include_metadata=False)] == ["content"]


def test_observe_extracts_source_stated_metadata() -> None:
    fake = Fake()
    obs = connector(fake).observe(entry())
    assert obs.content.body == DATA
    assert obs.native_metadata is not None and obs.native_metadata.body == STRUCTURE
    ds = obs.metadata.dataset
    assert ds.source_dataset_identifier == "STATSNZ:TST_TST_001"
    assert ds.title == "Synthetic test table"
    assert ds.description == "Invented description."
    assert ds.version == "1.0"
    assert ds.publisher_identifier == "STATSNZ"
    # as the source represented it, never copied from the catalogue
    assert ds.publisher_name_at_capture == "Synthetic Agency Name"
    assert ds.publisher_name == "Reviewer Configured Name"
    assert ds.licence == "Reviewer licence"
    assert ds.accrual_periodicity == "Reviewer periodicity"
    assert ds.landing_page == "https://example.invalid/page"
    assert ds.references[0].kind is ReferenceKind.METHODOLOGY
    # dates are never derived or invented
    assert ds.issued is None and ds.modified is None and ds.temporal_coverage is None
    nf = obs.metadata.native_fields
    assert nf["annotation.NonProductionDataflow.en"] == "true"
    assert nf["dataflow.is_final"] == "false"
    assert all("Prepared" not in k and "IDREF" not in v for k, v in nf.items())
    assert obs.metadata.distribution.source_resource_identifier == "STATSNZ,TST_TST_001,1.0"
    assert obs.metadata.distribution.dataset_identifier == ds.source_dataset_identifier


def test_publisher_at_capture_is_none_when_source_does_not_say() -> None:
    xml = re.sub(rb"<structure:Agency .*?</structure:Agency>", b"", STRUCTURE, flags=re.DOTALL)
    obs = connector(Fake(structure=xml)).observe(entry())
    assert obs.metadata.dataset.publisher_name_at_capture is None
    assert obs.metadata.dataset.publisher_name == "Reviewer Configured Name"


def test_volatile_header_change_leaves_metadata_unchanged() -> None:
    later = STRUCTURE.replace(b"2026-01-01T00:00:00.0000000", b"2027-02-02T00:00:00.0000000")
    later = later.replace(b"IDREF1", b"IDREF999")
    assert later != STRUCTURE
    m1 = connector(Fake()).observe(entry()).metadata
    m2 = connector(Fake(structure=later)).observe(entry()).metadata
    assert m1.sha256() == m2.sha256()


def test_name_or_annotation_change_changes_metadata_only() -> None:
    renamed = STRUCTURE.replace(b"Synthetic test table", b"Synthetic test table (revised)")
    annotated = STRUCTURE.replace(
        b'<common:AnnotationText xml:lang="en">true<',
        b'<common:AnnotationText xml:lang="en">false<',
    )
    base = connector(Fake()).observe(entry())
    for variant in (renamed, annotated):
        assert variant != STRUCTURE
        other = connector(Fake(structure=variant)).observe(entry())
        assert other.metadata.sha256() != base.metadata.sha256()
        assert other.content.body == base.content.body  # bytes unchanged


def test_no_metadata_mode_makes_only_the_data_request() -> None:
    fake = Fake()
    obs = connector(fake).observe(entry(), include_metadata=False)
    assert len(fake.requests) == 1
    assert obs.native_metadata is None
    assert obs.metadata.dataset.title is None
    assert obs.metadata.dataset.publisher_name_at_capture is None
    assert obs.metadata.native_fields == {}


def test_secondary_reference_added_only_when_lookup_succeeds_and_failure_is_harmless() -> None:
    from poltika.data.acquisition.models import Reference

    ref = Reference(
        kind=ReferenceKind.SECONDARY_CATALOGUE_RECORD,
        url="https://x.invalid/p",
        authoritative=False,
    )
    ok = StatsNzConnector(KEY, Fake(), FAST, secondary_lookup=lambda name: ref)
    observed = ok.observe(entry())
    assert observed.secondary_references == (ref,) and ref.authoritative is False
    # outside the hashed metadata: a flaky lookup cannot flip metadata_sha256
    bare = StatsNzConnector(KEY, Fake(), FAST).observe(entry())
    assert observed.metadata.sha256() == bare.metadata.sha256()

    def boom(name: str) -> Reference | None:
        raise RuntimeError("down")

    bad = StatsNzConnector(KEY, Fake(), FAST, secondary_lookup=boom)
    assert bad.observe(entry()).secondary_references == ()
    assert bad.observe(entry()).metadata.dataset.references == entry().dataset.references
    none = StatsNzConnector(KEY, Fake(), FAST)  # no lookup configured
    assert none.observe(entry()).secondary_references == ()


def test_identifier_must_match_request_block() -> None:
    bad = parse_catalogue(CATALOGUE.replace("STATSNZ:TST_TST_001", "STATSNZ:OTHER")).get("syn_flow")
    with pytest.raises(StatsNzError, match="does not match"):
        parse_request(bad)


def test_unparseable_or_wrong_structure_is_an_error() -> None:
    spec = parse_request(entry())
    with pytest.raises(StatsNzError, match="not valid XML"):
        parse_structure(b"<not xml", spec)
    with pytest.raises(StatsNzError, match="does not describe"):
        parse_structure(STRUCTURE.replace(b'id="TST_TST_001"', b'id="ZZZ"'), spec)


def test_errors_never_contain_the_key() -> None:
    fake = Fake()
    fake.fail_structure = 401
    with pytest.raises(PermanentHttpError) as exc:
        connector(fake).observe(entry())
    assert KEY not in str(exc.value)

    class Down:
        def send(self, request: FetchRequest, timeout: float) -> RawResponse:
            raise TransportError(f"connection to host failed with {request.secret_headers}")

    with pytest.raises(Exception) as exc2:
        StatsNzConnector(KEY, Down(), FAST).observe(entry())
    assert KEY not in str(exc2.value)


@pytest.mark.parametrize(
    "base",
    [
        "http://api.data.stats.govt.nz/rest",
        "http://apis.stats.govt.nz",
        "https://evil.example/rest",
        "https://api.data.stats.govt.nz.evil.example/rest",
        "https://user:pw@api.data.stats.govt.nz/rest",
        "https://api.data.stats.govt.nz:8443/rest",
    ],
)
def test_base_url_must_be_https_on_the_allow_listed_host(base: str) -> None:
    text = CATALOGUE.replace('version: "1.0"', f'version: "1.0"\n      base_url: {base!r}', 1)
    assert base in text
    with pytest.raises(CatalogueError, match="base_url"):
        parse_catalogue(text)


def test_default_and_explicit_allowed_base_url_load() -> None:
    explicit = "https://api.data.stats.govt.nz/rest"
    text = CATALOGUE.replace('version: "1.0"', f'version: "1.0"\n      base_url: {explicit}', 1)
    assert parse_catalogue(text).get("syn_flow").request["base_url"] == explicit
