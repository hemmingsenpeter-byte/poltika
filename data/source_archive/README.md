# data/source_archive/

**SOURCE PRESERVATION ONLY**

Presence in this archive does not mean Poltika has validated,
interpreted, semantically mapped, endorsed or approved this
dataset for modelling.

**Models must never read this archive directly.**

Only data promoted through Poltika's governed data pipeline may
reach DataContext and deterministic calculation engines.

---

The archive is evidence of what an authoritative source exposed at a specific point
in time (a Fact about publication, `doctrine/epistemic-constitution.md`). It is
not `data/raw/`, which holds the minimum snapshots a policy vertical needs, each
with a manifest and a canonical mapping. See
[ADR-0022](../../adr/0022-passive-authoritative-source-preservation-boundary.md),
which extends [ADR-0003](../../adr/0003-data-acquisition-boundary.md) and
replaces nothing. Nothing in `poltika.data.registry`, `context`, `transform` or
`transforms/` reads this directory, and nothing outside `poltika.data.acquisition`
may name it (`tests/unit/data/acquisition/test_archive_boundary.py`).

## What is committed, and what is not

| Path | Committed | Holds |
| --- | --- | --- |
| `README.md` | yes | this file |
| `sources/<source_system>.yaml` | yes | reviewed definitions of what to retrieve (`sources/stats_nz.yaml`); never credentials |
| `runtime/` | **no** (gitignored) | blobs, records, metadata and advisory output |

Never commit blobs, credentials, generated indexes or OpenRouter responses.
`POLTIKA_SOURCE_ARCHIVE_DIR` moves the whole runtime tree elsewhere.

## The four entities, and why they are separate

| Entity | Is | Stored as |
| --- | --- | --- |
| `DatasetDescriptor` | What the dataset is: stable publisher identifier, title, publisher, issued/modified, coverage, source update frequency, licence, rights, references | canonical JSON in `metadata/`, addressed by hash |
| `DistributionDescriptor` | One way to obtain it: API or file, URL, format, media type, any licence override | inside the same canonical `SourceMetadata` JSON |
| `RetrievalRecord` | One event: what was requested, when, the HTTP status, the hashes of the bytes and metadata, what changed since the last record | one JSON file per event in `records/`, never edited |
| `ContentBlob` | The exact response bytes | `blobs/sha256/<ab>/<hex>`, addressed by SHA-256 only |

They change at different rates and for different reasons. A dataset keeps its
identity while its title, licence or methodology note changes. A dataset has
several distributions. One distribution is retrieved many times, and most
retrievals return identical bytes. The bytes carry no timestamps, so the same
bytes are one blob however many events saw them. Merging them would either rewrite
history when metadata changes or duplicate large files on every retrieval.

Identity is the publisher's `source_dataset_identifier`, never a display title.
Unknown stays unknown: a field the source did not state is `null`, never
inferred or guessed.

## On-disk layout

```text
<root>/                          POLTIKA_SOURCE_ARCHIVE_DIR, default data/source_archive/runtime
├── blobs/sha256/<ab>/<64 hex>   exact bytes, read-only, written once
├── metadata/<system>/<source id>/<metadata sha256>.json   canonical SourceMetadata
├── records/<system>/<source id>/<retrieval id>.json       one RetrievalRecord
└── advisory/<system>/<source id>/<retrieval id>.<input hash[:12]>.json   optional, non-authoritative
```

A retrieval id is the UTC start time plus a request fingerprint
(`20261006T010203123456Z-<12 hex>`). No index file exists: the latest record is
found by scanning one directory (ADR-0022). Every path component is validated;
`..` and separators are refused.

## The four change states

Each retrieval records both flags. `content_changed` compares with the latest earlier
record for the same source; `metadata_changed` compares with the most recent earlier
record that has a `metadata_sha256` (`previous_metadata_sha256` names it). All four combinations are preserved as retrieval events:

| `content_changed` | `metadata_changed` | Meaning |
| --- | --- | --- |
| false | false | nothing new; a record is still written (one more observation) |
| true | false | new bytes, same source metadata |
| false | true | same bytes, but the source changed its title, licence, methodology, update date, dictionary or caveats |
| true | true | both |

The first observation of a source has `null` flags (no previous record).
A run that did not fetch the source's native metadata (`--no-metadata`) has
`metadata_sha256`, `metadata_raw_sha256` and `metadata_changed` all `null`: no canonical
metadata snapshot is written and its thinner descriptor is never compared, so a
metadata-off run cannot fake a change in either direction. The optional data.govt.nz
reference (`authoritative=false`) is stored on the record as `secondary_references`,
outside the hashed metadata, so a failed or successful secondary lookup cannot flip
`metadata_changed`. Volatile message
fields (such as an SDMX `Prepared` timestamp) are left out of the canonical metadata,
so they cannot fake a change; the raw metadata response is still kept verbatim as a
blob (`metadata_raw_sha256`).

## Point-in-time fields

Five different times are kept apart and never inferred from one another:

| Question | Field |
| --- | --- |
| What period do the observations describe? | `temporal_coverage` (observation/reference period) |
| When did the source first publish it? | `issued` |
| When did the source say it was last changed? | `modified` (and a distribution's `source_modified`) |
| What revision or vintage is it? | `version`, if the source publishes one |
| When did Poltika retrieve it? | `request_started_at`, `response_received_at` on the record |

Together with `publisher_name_at_capture` this answers "what information and
metadata were available to an analyst as of T?". Source publication frequency
(`accrual_periodicity`) is separate from Poltika's own cadence (`check_frequency`,
unset in v1). There is no scheduler; run the CLI from cron.

Licence, rights and attribution sit on the dataset, with an optional per-distribution
override. They are recorded as the source states them, never inferred from the
publisher or by a model.

## Environment variables

| Variable | Used by | Effect |
| --- | --- | --- |
| `POLTIKA_SOURCE_ARCHIVE_DIR` | archive, CLI | root of the runtime tree; default `data/source_archive/runtime` |
| `POLTIKA_STATS_NZ_API_KEY` | Stats NZ connector | subscription key for the Aotearoa Data Explorer API; sent only as a request header; never printed, logged, hashed or stored; never sent to OpenRouter |
| `OPENROUTER_API_KEY` | enrichment | optional; with the model, enables advisory enrichment |
| `POLTIKA_OPENROUTER_MODEL` | enrichment | optional; any model or router id you choose; none is hardcoded; unset means enrichment is skipped |

The archive works fully with both OpenRouter variables unset.

## Optional advisory enrichment

After evidence is stored, `poltika.data.acquisition.enrichment` may ask the configured
model for a schema summary, column explanations, suggested tags and candidate
relationships. The request carries at most the first 8 KiB of the content and the
canonical metadata, never a key or header. The answer is written to `advisory/`
with `status: NON_AUTHORITATIVE_ADVISORY_METADATA`, the provider, model,
`created_at`, `input_sha256`, `output` and `outcome` (`ok`, `skipped` or `failed`).
It is an AI hypothesis. It never changes bytes, identity, licence, dates or a
mapping, and any failure (rate limit, error, removed model) leaves ingestion
successful.

## CLI

Live retrieval needs `POLTIKA_STATS_NZ_API_KEY`. `--list` and `--dry-run` need no key,
touch no network and write nothing.

```sh
uv run python scripts/ingest/stats_nz.py --list
uv run python scripts/ingest/stats_nz.py --all --dry-run

export POLTIKA_STATS_NZ_API_KEY=...        # your own Stats NZ subscription key
uv run python scripts/ingest/stats_nz.py --dataset stats_nz_ade_popes_sub_004
uv run python scripts/ingest/stats_nz.py --all
```

Other flags: `--no-metadata` (skip the structure request), `--no-enrich` (skip
advisory enrichment), `--with-secondary-catalogue` (look up configured data.govt.nz
package names, one extra request each), `--archive-dir` and `--catalogue`
(override the archive root and the catalogue YAML).

Per source it prints the dataset, distribution, HTTP status, bytes, content and
metadata SHA-256, whether each changed, the content blob (created or existing),
the native metadata blob, the retrieval record written and the advisory
enrichment outcome. `--all` continues past a failed source, reports it, and
exits 1 if any source failed. Exit codes: 0 success, 1 acquisition failure,
2 usage error or missing key. Failed retrievals (non-2xx, exhausted retries)
are reported only; they write no record.

## Promotion path

There is no automatic promotion. Admitting archived material to modelling takes
every step, each human-gated (ADR-0022):

archive → analytical requirement → a human selects the exact version → provenance
checked (`.claude/skills/provenance/SKILL.md`) → transformation implemented →
canonical mapping reviewed → `DatasetManifest` → bytes admitted to `data/raw/` →
`DatasetRegistry` → `DataContext`.

An LLM cannot approve or perform any step.
