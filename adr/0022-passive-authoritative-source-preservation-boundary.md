# ADR-0022: Passive authoritative-source preservation boundary

**Date:** 6 October 2026
**Status:** proposed. Tier A/B engineering decision under ADR-0020, logged in
`docs/decision_log.md` (D5-D8). It extends ADR-0003 and replaces nothing. It
does not mark Programme Step 27 ("Historical policy/data states") started or
complete.

## Context

ADR-0003 fixed the v0.1 data boundary: datasets are acquired manually, frozen
as immutable raw snapshots and admitted only through a manifest, the dataset
registry and a reviewed transformation. It also set the "minimum necessary"
rule: only the datasets a policy vertical actually needs enter `data/raw/`.
ADR-0003 named automated ingestion, scheduled refreshes and connectors as a
later, capability-driven addition.

Poltika needs to accumulate point-in-time evidence of what authoritative
sources published, starting with Stats NZ, before any analytical requirement
names a dataset. Historical validation, representative microsimulation,
national-state reconstruction and as-of analysis (Programme Steps 27-29) all
ask "what information and metadata were available to an analyst as of T?".
Sources overwrite and revise. An observation not taken at the time cannot be
recovered later.

The risk is the opposite one: broad preservation quietly becoming broad
admission. `DatasetManifest.canonical_variable_mapping`, `DatasetRegistry` and
`DataContext` are the governed gate. This ADR gives preservation a separate,
labelled place so the gate is neither weakened nor bypassed.

## Decision

1. **Passive preservation is allowed before a requirement exists.** Poltika may
   retrieve and keep public authoritative material without an analytical need
   naming it.
2. **Preserved material is evidence, not governed modelling data.** An archive
   record is a Fact about publication under `doctrine/epistemic-constitution.md`:
   this source exposed these bytes and this metadata at this time. It is not a
   claim that Poltika has validated, interpreted, mapped or approved them. A
   caller's or an LLM's statement about the data is never a Fact.
3. **ADR-0003's "minimum necessary" rule for `data/raw/` is unchanged.** Broad
   preservation does not override it. `data/source_archive/` is not
   `data/raw/`.
4. **Preservation and model admission are separate epistemic states.** Nothing
   becomes modelling data by being preserved.
5. **Models cannot access the archive.** `DatasetRegistry`, `DataContext`,
   transformations, engines, policy, scenarios, the API and the LLM layer do not
   import or name it. `tests/unit/data/acquisition/test_archive_boundary.py`
   enforces this and adds to `tests/unit/data/test_boundary.py` without weakening it.
6. **Exact source bytes are immutable.** The response body is stored as received,
   addressed by its SHA-256. Nothing is decoded, normalised, re-encoded or
   rewritten. A stored blob is never overwritten; a corrupt one is reported, not
   repaired.
7. **Duplicate content is stored once.** Content-addressed storage: five
   identical retrievals make five records and one blob.
8. **Every retrieval event is individually auditable.** Each successful
   retrieval writes a new `RetrievalRecord` (request, timestamps, status, hashes,
   previous-retrieval links, change flags, collector version), including one whose
   bytes and metadata are unchanged. Records are never edited.
9. **Source metadata is historical evidence.** The canonical `SourceMetadata` is
   stored by its own hash, only for a retrieval that fetched the source's native
   metadata; a run without it has `metadata_sha256`, `metadata_raw_sha256` and
   `metadata_changed` null. `metadata_changed` compares with the most recent earlier
   record that has a `metadata_sha256`. Non-authoritative secondary references sit on
   the record (`secondary_references`), outside the hash. A metadata change is preserved even when the bytes did
   not change (`content_changed=false`, `metadata_changed=true`), and the reverse.
10. **Publisher identity is recorded as the source represented it at that time**
    (`publisher_identifier` and `publisher_name_at_capture`). A later rename, merger
    or abolition never rewrites a stored record. There is no organisation registry.
11. **Credentials are never preserved.** Secret headers are sent, never serialised,
    hashed, logged or placed in an exception message. Neither the Stats NZ key
    nor the OpenRouter key appears in a record, fingerprint, advisory file or payload
    sent to another party.
12. **An LLM's output about the metadata is advisory only.** It is stored apart from
    the evidence under `advisory/`, marked `NON_AUTHORITATIVE_ADVISORY_METADATA`,
    and is an AI hypothesis. It never changes bytes, identity, licence, dates,
    provenance, a manifest or a mapping, and never promotes anything.
13. **Formal promotion keeps every existing rule.** Provenance
    (`.claude/skills/provenance/SKILL.md`), the transformation registry, the
    semantic mapping and validation all apply unchanged, with the path in
    "Promotion path" below.
14. **`REPOSITORY_STRUCTURE.md` is updated deliberately** for `data/source_archive/`,
    `src/poltika/data/acquisition/` and `scripts/ingest/`.

### Choices made here (Tier A/B, reversible)

- **v1 preserves successful (2xx) retrievals only.** A 4xx/5xx or exhausted
  retry is a reported failure, not a record. Retries are bounded; 429, 5xx and
  timeouts retry with backoff and `Retry-After`; other 4xx fail at once. Failed
  attempts are not evidence of what the source published, and a record
  must mean "these bytes were exposed". A failed-attempt log can be added later
  as a separate entity without changing records.
- **Local filesystem, content-addressed, behind a `BlobStore` protocol**
  (`put`, `get`, `exists`). `LocalBlobStore` is the only implementation. Object
  stores (S3, R2, B2, Azure) can implement the protocol later without changing
  acquisition. None is built now.
- **No SQLite (or other) index in v1.** Records are small JSON files under
  `records/<system>/<source id>/`, and the only lookup acquisition needs is "latest
  record for this source", which is a scan of one directory, sorted by
  request start time then `retrieval_id`. A derived index would be a second
  copy of the truth to keep consistent, would need rebuild and corruption
  handling, and the archive holds a handful of sources retrieved at most daily. Add
  one only when a measured query needs it; it would be rebuildable from records and
  gitignored.
- **Canonical metadata excludes volatile message-header fields; the raw metadata
  bytes are preserved verbatim.** SDMX responses carry fields such as a
  `Prepared` timestamp that change on every request. Hashing them would make
  `metadata_changed` true every time. The canonical `SourceMetadata` (and so
  `metadata_sha256`) omits them, while the exact native metadata response is also
  stored as a blob (`metadata_raw_sha256`), so nothing the source sent is lost.
- **`--all` continues past a failed source** and exits non-zero if any failed
  (`poltika.data.acquisition.ingest`, tested; see D6).

## Prior art

Reviewed on 6 October 2026 as structural prior art only
(`doctrine/ip-doctrine.md`, `.claude/skills/clean-room-research`). Only repository
READMEs and the published guidance were read. No code was copied, imported or
adapted, and no behaviour was taken from any of it.

| Source | Licence (as stated) | Used for |
| --- | --- | --- |
| [data-govt-nz/schema](https://github.com/data-govt-nz/schema) | MIT, Crown copyright 2015 DIA ([LICENSE.md](https://raw.githubusercontent.com/data-govt-nz/schema/master/LICENSE.md)) | The data.json field set data.govt.nz harvests: identifier, title, description, publisher, issued, modified, license, temporal, spatial, accrualPeriodicity, landingPage, references, language, keyword, theme, distribution |
| [data.govt.nz: automating dataset updates / what is a data.json](https://data.govt.nz/catalogue-guide/releasing-data-on-data-govt-nz/automating-dataset-updates) (live guidance; also served at `/manage-data/releasing-data-on-data-govt-nz/automating-dataset-updates/`) | Site terms | What is live today: data.json is a Project Open Data derivative of W3C DCAT, harvested monthly, weekly or daily; required dataset fields title, description, identifier, license, publisher, contactPoint, distribution; a distribution needs `downloadURL` or `accessURL` and a title |
| [data-govt-nz/developers](https://github.com/data-govt-nz/developers) | Not read (LICENSE.md not shown); no content reused | Confirms the catalogue is CKAN with `package_*`/`resource_*` metadata actions; guidance for API consumers, not a metadata specification |
| [data-govt-nz/govt-org-register](https://github.com/data-govt-nz/govt-org-register) | Not read (LICENSE.md not shown); no content reused | Prototype dataset that models organisations changing over time (machinery of government), the reason `publisher_name_at_capture` exists |
| [data-govt-nz/ckanext-dia](https://github.com/data-govt-nz/ckanext-dia) | AGPL-3.0 | Only the README: DIA customises the CKAN CSW and DCAT-JSON harvesters. **Code was not read or used.** AGPL code must not enter Poltika |

The GitHub-era schema README and the live guidance agree on the field set. The
live page embeds the schema table and names no separate schema link, and it
requires `contactPoint`, which Poltika does not capture (below). Whether any
repository is archived could not be established from the README text.

**Retained:** (1) stable dataset identifiers; (2) dataset metadata separate from
distributions; (3) publisher identity; (4) licence and rights; (5) issued distinct
from modified; (6) temporal and spatial coverage; (7) update frequency; (8) landing
pages and reference documents; (9) several distributions per dataset; (10)
data.json/DCAT-inspired, machine-readable names; (11) publisher organisations
change over time.

**Deliberately not adopted:** CKAN (no catalogue deployment, no `ckanext`); a
DCAT server or any harvest endpoint; RDF, JSON-LD or an ontology; the government
organisation register (identity is recorded as stated at capture, nothing is resolved);
bidirectional DCAT conversion; ISO 8601 normalisation of `issued`, `modified`,
`temporal` and `accrualPeriodicity` (stored exactly as the source stated them,
because inferring a date or period is forbidden); the NZGOAL licence-URI
constraint (the licence is recorded as the source states it, never inferred);
`contactPoint` (a source publisher's contact is not needed to preserve evidence,
and unknown stays unknown); any harvesting behaviour. `data.govt.nz` may be
referenced as a *secondary* catalogue record (`authoritative: false`), never as
the source of content or metadata.

### Field mapping

Poltika names are internal. The right-hand column is the external equivalent, for
a later `to_data_json_metadata()` export only; there is no import.

| Poltika field | data.json / DCAT term | Note |
| --- | --- | --- |
| `DatasetDescriptor.source_system` | none | Poltika scope for the identifier |
| `source_dataset_identifier` | `identifier` / `dct:identifier` | the publisher's stable id, never a title |
| `title`, `description` | `title`, `description` | |
| `publisher_identifier` | `publisher` / `dct:publisher` | id of the organisation, as configured |
| `publisher_name` | `publisher.name` | as the reviewed catalogue configured it |
| `publisher_name_at_capture` | none | Poltika addition; never rewritten |
| `issued`, `modified` | `issued`, `modified` / `dct:issued`, `dct:modified` | kept as stated, not parsed |
| `temporal_coverage`, `spatial_coverage` | `temporal`, `spatial` / `dct:temporal`, `dct:spatial` | observation/reference period, as stated |
| `accrual_periodicity` | `accrualPeriodicity` / `dct:accrualPeriodicity` | the source's publication frequency, not our check cadence |
| `licence` | `license` / `dct:license` | as stated by the source |
| `rights` | `dct:rights` | DCAT term; not in the NZ data.json field list |
| `attribution` | none | Poltika addition (a credit line the source asks for) |
| `landing_page` | `landingPage` / `dcat:landingPage` | |
| `keywords`, `themes`, `languages` | `keyword`, `theme`, `language` | |
| `references` (`Reference`) | `references` | NZ field is a URL array; `kind`, `authoritative`, `preserved_blob_sha256` are Poltika additions |
| `version` | `dcat:version` | DCAT, not data.json; a source's revision label, if one exists |
| `DistributionDescriptor.distribution_identifier` | `dct:identifier` on a distribution | Poltika-stable; data.json has none |
| `dataset_identifier` | parent dataset | nesting in data.json, an explicit key here |
| `access_kind` | `accessURL` vs `downloadURL` | API (`accessURL`) or file (`downloadURL`) |
| `title`, `description` | distribution `title`, `description` | |
| `access_url`, `download_url` | `accessURL`, `downloadURL` | |
| `media_type`, `format` | `mediaType`, `format` | |
| `source_resource_identifier` | CKAN resource id | only for a data.govt.nz-style resource |
| `licence_override`, `rights_override` | distribution-level `dct:license`, `dct:rights` | override the dataset's value |
| `source_created`, `source_modified` | distribution `dct:issued`, `dct:modified` | |
| `check_frequency` (catalogue entry) | none | Poltika's own cadence, deliberately separate from `accrual_periodicity` |

## Promotion path

There is no automatic promotion. Each step is a separate, human-gated act:

1. archive: evidence of what a source published
2. an analytical requirement names the need
3. a human selects the exact archived version
4. provenance is checked (`.claude/skills/provenance/SKILL.md`)
5. the transformation is implemented and registered
6. the canonical mapping is reviewed
7. a `DatasetManifest` is written
8. the exact bytes are admitted to `data/raw/` (minimum necessary), guarded by
   `data-snapshot-guard`
9. `DatasetRegistry` verifies it
10. `DataContext` serves its canonical variables

A step that cannot be completed stops the path; it does not skip a step. An LLM
cannot perform any of steps 2-8.

## Consequences

- Point-in-time evidence accrues from now, ahead of Step 27, without changing a
  calculated amount, a manifest field or a registry rule.
- The archive can disagree with `data/raw/` (a later retrieval differs from the
  admitted snapshot). That is expected: they answer different questions.
- Records are never rewritten, so a collector bug is corrected by a new record or a
  note, not an edit; `collector_version` identifies the code.
- Scanning records is O(records per source). Revisit when a source has thousands.
- Failed retrievals leave no trace in the archive (CLI output only) until a separate
  attempt log is justified.
- Provenance of a record is only as good as the connector's hash of exact
  bytes. A transfer-decoded body is stored as delivered; `content_encoding` is
  recorded.
- No live ingestion happens until `POLTIKA_STATS_NZ_API_KEY` is supplied; no
  production snapshot is committed. `data/source_archive/runtime/` is gitignored.
- Rejected: committing blobs (licence and size undecided, ADR-0003); writing into
  `data/raw/` automatically; a plugin framework; a scheduler (the CLI is
  cron-friendly); a CKAN/DCAT deployment.

## Reversal

Superseding this ADR leaves existing runtime archives readable as plain JSON and
content-addressed files. Removing the package touches nothing in the governed path,
because nothing in it imports the archive.
