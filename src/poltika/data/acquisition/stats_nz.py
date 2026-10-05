"""Source preservation archive: the Stats NZ Aotearoa Data Explorer connector
(ADR-0022).

Request shape, from the Stats NZ "Aotearoa Data Explorer API user guide"
(https://www.stats.govt.nz/tools/aotearoa-data-explorer/ade-api-user-guide/):

    data       GET {base}/data/{agency},{dataflow},{version}/{selection}?format=...
    structure  GET {base}/dataflow/{agency}/{dataflow}/{version}?references=...&detail=...

Both need the subscription key in the `Ocp-Apim-Subscription-Key` header. The
key is passed in by the composition root, goes only into
`FetchRequest.secret_headers`, and is never part of a fingerprint, record,
metadata snapshot, log line or exception message.

Metadata. The structure response is preserved byte for byte as the native
metadata blob. The canonical `SourceMetadata` is built from source-stated
values only (dataflow name, description, version, annotations, agency). The
SDMX message header (`Prepared`, message id, sender, receiver) is volatile, so
it is excluded: an unchanged dataflow must hash to the same metadata, and a
changed name or annotation must not. Reviewer values from the catalogue fill
publisher name, landing page, licence, rights, attribution, publication
frequency and references, because ADE does not publish them. `issued`,
`modified` and temporal coverage stay `None`: this connector does not know
which annotation means which, and never derives one date from another.
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from poltika.data.acquisition.catalogue import SourceEntry
from poltika.data.acquisition.data_govt_nz import SecondaryLookup
from poltika.data.acquisition.models import (
    DatasetDescriptor,
    DistributionDescriptor,
    Reference,
    SourceMetadata,
)
from poltika.data.acquisition.source import (
    DEFAULT_RETRY_POLICY,
    AcquisitionError,
    FetchRequest,
    RetryPolicy,
    SourceObservation,
    Transport,
    UrllibTransport,
    fetch,
)

SOURCE_SYSTEM = "stats_nz"
API_KEY_HEADER = "Ocp-Apim-Subscription-Key"
ENV_API_KEY = "POLTIKA_STATS_NZ_API_KEY"
# Constant on purpose: the request fingerprint must not change between runs.
USER_AGENT = "Poltika-SourceArchive/1.0 (Language=Python)"

_NS_STRUCTURE = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure"
_NS_COMMON = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class StatsNzError(AcquisitionError):
    """A Stats NZ specific failure (bad catalogue request, unparseable structure)."""


class StatsNzRequest(BaseModel):
    """The connector-specific `request` block of a catalogue entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_url: str = "https://api.data.stats.govt.nz/rest"
    agency_id: str
    dataflow_id: str
    version: str
    selection: str = "all"
    data_format: str = "csvfilewithlabels"
    structure_references: str = "all"
    structure_detail: str = "referencepartial"

    @property
    def dataset_identifier(self) -> str:
        return f"{self.agency_id}:{self.dataflow_id}"


def parse_request(entry: SourceEntry) -> StatsNzRequest:
    try:
        spec = StatsNzRequest.model_validate(entry.request)
    except ValueError as exc:
        raise StatsNzError(f"{entry.id}: invalid request block: {exc}") from None
    if spec.dataset_identifier != entry.dataset.identifier:
        raise StatsNzError(
            f"{entry.id}: dataset.identifier {entry.dataset.identifier!r} does not match "
            f"request agency_id/dataflow_id {spec.dataset_identifier!r}"
        )
    return spec


def _tag(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def _text(node: ET.Element | None) -> str | None:
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value or None


def _lang(node: ET.Element) -> str:
    return node.get(_XML_LANG) or "und"


class ParsedStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str | None
    description: str | None
    version: str | None
    publisher_identifier: str | None
    publisher_name_at_capture: str | None
    languages: tuple[str, ...]
    native_fields: dict[str, str]


def parse_structure(body: bytes, spec: StatsNzRequest) -> ParsedStructure:
    """Extract source-stated, non-volatile values for one dataflow.

    Nothing under `message:Header` is read."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        raise StatsNzError(
            f"structure response for {spec.dataset_identifier} is not valid XML"
        ) from None
    flow: ET.Element | None = None
    for candidate in root.iter(_tag(_NS_STRUCTURE, "Dataflow")):
        if candidate.get("id") == spec.dataflow_id and candidate.get("agencyID") == spec.agency_id:
            flow = candidate
            break
    if flow is None:
        raise StatsNzError(f"structure response does not describe {spec.dataset_identifier}")

    names = {_lang(n): _text(n) for n in flow.findall(_tag(_NS_COMMON, "Name"))}
    descriptions = {_lang(n): _text(n) for n in flow.findall(_tag(_NS_COMMON, "Description"))}
    title = names.get("en") or next((v for v in names.values() if v), None)
    description = descriptions.get("en") or next((v for v in descriptions.values() if v), None)

    fields: dict[str, str] = {
        "dataflow.id": flow.get("id") or "",
        "dataflow.agency_id": flow.get("agencyID") or "",
    }
    for attr, label in (
        ("version", "dataflow.version"),
        ("isFinal", "dataflow.is_final"),
        ("validFrom", "dataflow.valid_from"),
        ("validTo", "dataflow.valid_to"),
    ):
        value = flow.get(attr)
        if value is not None:
            fields[label] = value
    for lang, value in names.items():
        if value:
            fields[f"dataflow.name.{lang}"] = value
    for lang, value in descriptions.items():
        if value:
            fields[f"dataflow.description.{lang}"] = value

    # Annotations are source-stated; repeated types keep document order.
    for annotation in flow.findall(
        f"{_tag(_NS_COMMON, 'Annotations')}/{_tag(_NS_COMMON, 'Annotation')}"
    ):
        kind = _text(annotation.find(_tag(_NS_COMMON, "AnnotationType"))) or "untyped"
        parts = {
            f"annotation.{kind}.title": [
                v
                for n in annotation.findall(_tag(_NS_COMMON, "AnnotationTitle"))
                if (v := _text(n))
            ],
        }
        for n in annotation.findall(_tag(_NS_COMMON, "AnnotationText")):
            value = _text(n)
            if value:
                parts.setdefault(f"annotation.{kind}.{_lang(n)}", []).append(value)
        for key, values in parts.items():
            if values:
                existing = fields.get(key)
                joined = "\n".join(values)
                fields[key] = joined if existing is None else f"{existing}\n{joined}"

    agency_name: str | None = None
    for agency in root.iter(_tag(_NS_STRUCTURE, "Agency")):
        if agency.get("id") == spec.agency_id:
            agency_names = {_lang(n): _text(n) for n in agency.findall(_tag(_NS_COMMON, "Name"))}
            agency_name = agency_names.get("en") or next(
                (v for v in agency_names.values() if v), None
            )
            break

    languages = tuple(sorted({lang for lang in names if lang != "und"}))
    return ParsedStructure(
        title=title,
        description=description,
        version=flow.get("version"),
        publisher_identifier=flow.get("agencyID"),
        publisher_name_at_capture=agency_name,
        languages=languages,
        native_fields=fields,
    )


def build_metadata(
    entry: SourceEntry,
    spec: StatsNzRequest,
    parsed: ParsedStructure | None,
    secondary: Reference | None = None,
) -> SourceMetadata:
    """Combine source-stated values (win) with the reviewer's catalogue values."""
    references = list(entry.dataset.references)
    if secondary is not None:
        references.append(secondary)
    dataset = DatasetDescriptor(
        source_system=SOURCE_SYSTEM,
        source_dataset_identifier=entry.dataset.identifier,
        title=parsed.title if parsed else None,
        description=parsed.description if parsed else None,
        publisher_identifier=(
            parsed.publisher_identifier
            if parsed and parsed.publisher_identifier
            else entry.dataset.publisher_identifier
        ),
        publisher_name=entry.dataset.publisher_name,
        publisher_name_at_capture=parsed.publisher_name_at_capture if parsed else None,
        accrual_periodicity=entry.dataset.accrual_periodicity,
        licence=entry.dataset.licence,
        rights=entry.dataset.rights,
        attribution=entry.dataset.attribution,
        landing_page=entry.dataset.landing_page,
        languages=parsed.languages if parsed else (),
        references=tuple(references),
        version=parsed.version if parsed else spec.version,
    )
    distribution = DistributionDescriptor(
        distribution_identifier=entry.distribution.identifier,
        dataset_identifier=entry.dataset.identifier,
        access_kind=entry.distribution.access_kind,
        title=entry.distribution.title,
        access_url=entry.distribution.access_url,
        media_type=entry.distribution.media_type,
        format=entry.distribution.format,
        source_resource_identifier=f"{spec.agency_id},{spec.dataflow_id},{spec.version}",
    )
    return SourceMetadata(
        dataset=dataset,
        distribution=distribution,
        native_fields=dict(parsed.native_fields) if parsed else {},
    )


class StatsNzConnector:
    """Fetches one ADE dataflow's data and structural metadata."""

    source_system = SOURCE_SYSTEM

    def __init__(
        self,
        api_key: str | None,
        transport: Transport | None = None,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        *,
        secondary_lookup: SecondaryLookup | None = None,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._api_key = api_key.strip() if api_key and api_key.strip() else None
        self._transport: Transport = transport if transport is not None else UrllibTransport()
        self._policy = retry_policy
        self._secondary_lookup = secondary_lookup
        self._sleep = sleep
        self._now = now

    @property
    def has_api_key(self) -> bool:
        return self._api_key is not None

    @property
    def secrets(self) -> tuple[str, ...]:
        return (self._api_key,) if self._api_key else ()

    def _secret_headers(self) -> tuple[tuple[str, str], ...]:
        return ((API_KEY_HEADER, self._api_key),) if self._api_key else ()

    def _headers(self, accept: str) -> tuple[tuple[str, str], ...]:
        return (
            ("Accept", accept),
            ("Accept-Encoding", "identity"),
            ("User-Agent", USER_AGENT),
        )

    def data_request(self, entry: SourceEntry) -> FetchRequest:
        spec = parse_request(entry)
        base = spec.base_url.rstrip("/")
        return FetchRequest(
            url=f"{base}/data/{spec.agency_id},{spec.dataflow_id},{spec.version}/{spec.selection}",
            query=(("format", spec.data_format),),
            headers=self._headers("*/*"),
            secret_headers=self._secret_headers(),
        )

    def structure_request(self, entry: SourceEntry) -> FetchRequest:
        spec = parse_request(entry)
        base = spec.base_url.rstrip("/")
        return FetchRequest(
            url=f"{base}/dataflow/{spec.agency_id}/{spec.dataflow_id}/{spec.version}",
            query=(
                ("detail", spec.structure_detail),
                ("references", spec.structure_references),
            ),
            headers=self._headers("application/xml"),
            secret_headers=self._secret_headers(),
        )

    def plan(
        self, entry: SourceEntry, *, include_metadata: bool = True
    ) -> tuple[tuple[str, FetchRequest], ...]:
        """The requests `observe` would send, labelled. No network."""
        planned = [("content", self.data_request(entry))]
        if include_metadata:
            planned.append(("metadata", self.structure_request(entry)))
        return tuple(planned)

    def _secondary_reference(self, entry: SourceEntry) -> Reference | None:
        package = entry.secondary_catalogue.data_govt_nz_package
        if package is None or self._secondary_lookup is None:
            return None
        try:
            return self._secondary_lookup(package)
        except Exception:  # noqa: BLE001 - a secondary lookup never fails acquisition
            return None

    def observe(self, entry: SourceEntry, *, include_metadata: bool = True) -> SourceObservation:
        spec = parse_request(entry)
        content = fetch(
            self.data_request(entry),
            self._transport,
            self._policy,
            sleep=self._sleep,
            now=self._now,
        )
        native = None
        parsed: ParsedStructure | None = None
        if include_metadata:
            native = fetch(
                self.structure_request(entry),
                self._transport,
                self._policy,
                sleep=self._sleep,
                now=self._now,
            )
            parsed = parse_structure(native.body, spec)
        metadata = build_metadata(entry, spec, parsed, self._secondary_reference(entry))
        return SourceObservation(
            poltika_source_id=entry.id,
            metadata=metadata,
            content=content,
            native_metadata=native,
        )
