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


CODELIST = (
    b"<structure:Codelists>"
    b'<structure:Codelist id="CL_X" agencyID="STATSNZ" version="1.0">'
    b'<common:Name xml:lang="en">Codes</common:Name>'
    b'<structure:Code id="A"><common:Name xml:lang="en">{name}</common:Name></structure:Code>'
    b"</structure:Codelist></structure:Codelists>"
)


def with_codelist(name: bytes = b"Alpha") -> bytes:
    xml = STRUCTURE.replace(
        b"<structure:Dataflows>", CODELIST.replace(b"{name}", name) + b"<structure:Dataflows>", 1
    )
    assert xml != STRUCTURE
    return xml


def test_data_dictionary_change_changes_metadata_hash() -> None:
    base = connector(Fake(structure=with_codelist())).observe(entry())
    renamed = connector(Fake(structure=with_codelist(b"Beta"))).observe(entry())
    assert renamed.content.body == base.content.body
    assert renamed.metadata.sha256() != base.metadata.sha256()
    # a structural element outside the dataflow (here a whole codelist) counts too
    assert connector(Fake()).observe(entry()).metadata.sha256() != base.metadata.sha256()


def test_header_and_formatting_do_not_change_the_structure_hash() -> None:
    base = connector(Fake(structure=with_codelist())).observe(entry()).metadata
    varied = with_codelist().replace(b"IDREF1", b"IDREF2").replace(b"2026-01-01", b"2030-05-05")
    varied = varied.replace(
        b'<structure:Dataflow id="OTHER_FLOW" agencyID="STATSNZ"',
        b'<structure:Dataflow   agencyID="STATSNZ"  id="OTHER_FLOW"',
    ).replace(b"<structure:Dataflows>", b"<structure:Dataflows>\n\n  ")
    assert varied != with_codelist()
    other = connector(Fake(structure=varied)).observe(entry()).metadata
    assert other.sha256() == base.sha256()


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
        "https://api.data.stats.govt.nz/rest?x=1",
        "https://api.data.stats.govt.nz/rest#frag",
        "https://api.data.stats.govt.nz/rest?",
        "https://api.data.stats.govt.nz/rest#",
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


# --- DTD refusal (PR B): the structure response never reaches ElementTree with a DTD.

# Pinned before the shared guard was introduced (main a8b214f): the parsed
# fixture, as SHA-256 of its sorted JSON dump, and its C14N hash.
STRUCTURE_DUMP_SHA256 = "caefaa927c76f3290771a0e56d64caa28ebf750235748ac03459dd6060556fbe"
STRUCTURE_C14N_SHA256 = "3fef544ef71cf1a1b0021fb46460e9496e2e394ccb335bb2d2c71ee3dd04518e"

DTD_PAYLOADS = [
    '<!DOCTYPE x SYSTEM "https://example.invalid/external.dtd">',
    '<!DOCTYPE x [<!ENTITY a SYSTEM "file:///never-read">]>',
    '<!DOCTYPE x [<!ENTITY % a SYSTEM "https://example.invalid/entity">%a;]>',
    '<!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;"><!ENTITY c "&b;&b;&b;&b;">]>',
]


def test_structure_parse_is_byte_identical_to_the_pre_guard_baseline() -> None:
    import hashlib
    import json

    parsed = parse_structure(STRUCTURE, parse_request(entry()))
    dump = json.dumps(parsed.model_dump(mode="json"), sort_keys=True).encode()
    assert hashlib.sha256(dump).hexdigest() == STRUCTURE_DUMP_SHA256
    assert parsed.native_fields["structure_c14n_sha256"] == STRUCTURE_C14N_SHA256


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
@pytest.mark.parametrize("doctype", DTD_PAYLOADS)
def test_structure_with_a_dtd_is_refused_before_element_tree(
    encoding: str, doctype: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    import xml.etree.ElementTree as ET

    def unexpected_parse(*args: object, **kwargs: object) -> None:
        pytest.fail("ElementTree parsed a DTD-bearing structure response")

    monkeypatch.setattr(ET, "fromstring", unexpected_parse)
    text = STRUCTURE.decode("utf-8").replace(
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<?xml version="1.0" encoding="{encoding}"?>{doctype}',
        1,
    )
    with pytest.raises(StatsNzError, match="declares a DTD or entity"):
        parse_structure(text.encode(encoding), parse_request(entry()))


def test_observe_refuses_a_dtd_bearing_structure_response() -> None:
    bomb = STRUCTURE.replace(
        b"?>", b'?><!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]>', 1
    )

    class Fixed:
        def send(self, request: FetchRequest, timeout: float) -> RawResponse:
            body = bomb if "/dataflow/" in request.url else DATA
            return RawResponse(200, (), body)

    connector = StatsNzConnector(api_key=KEY, transport=Fixed(), sleep=lambda _: None)
    with pytest.raises(StatsNzError, match="declares a DTD or entity"):
        connector.observe(entry())


def test_requests_carry_the_default_cap_or_the_catalogue_override() -> None:
    from poltika.data.acquisition.source import DEFAULT_MAX_RESPONSE_BYTES

    connector = StatsNzConnector(api_key=KEY)
    assert connector.data_request(entry()).max_response_bytes == DEFAULT_MAX_RESPONSE_BYTES
    larger = parse_catalogue(
        CATALOGUE.replace("    secondary_catalogue:", "    max_response_bytes: 200000000\n    secondary_catalogue:")
    ).get("syn_flow")
    assert connector.data_request(larger).max_response_bytes == 200_000_000
    assert connector.structure_request(larger).max_response_bytes == 200_000_000
    # The cap is a transport limit: it never changes the request fingerprint.
    assert connector.data_request(larger).fingerprint() == connector.data_request(entry()).fingerprint()


@pytest.mark.parametrize("value", ["0", "-1"])
def test_catalogue_cap_must_be_positive(value: str) -> None:
    with pytest.raises(CatalogueError):
        parse_catalogue(
            CATALOGUE.replace(
                "    secondary_catalogue:", f"    max_response_bytes: {value}\n    secondary_catalogue:"
            )
        )
