# Review Packet: passive source-preservation archive (ADR-0022) — 6 October 2026

Label: **author preflight** plus three **fresh same-model checks** (Sonnet
`poltika-reviewer` passes) and one same-model provenance check. Not an
independent GPT/Codex review.

## Review inputs

- PR/diff: `origin/main` 240da13 → branch `feat/source-preservation-archive`
  (0c12bf4 implementation; 39fda80 and eb1b1df review fixes; this packet and
  the ADR status change).
- Primary sources:
  - Stats NZ, "Aotearoa Data Explorer API user guide",
    https://www.stats.govt.nz/tools/aotearoa-data-explorer/ade-api-user-guide/
    (base URL `https://api.data.stats.govt.nz/rest/`, header
    `Ocp-Apim-Subscription-Key`, data and dataflow URL shapes, `format` values).
  - ADE dataflow listing,
    https://api.data.stats.govt.nz/rest/dataflow/STATSNZ/all?detail=allstubs
    (fetched 5 October 2026: 911 dataflows, `last-modified` 4 October 2026).
  - Stats NZ copyright, https://www.stats.govt.nz/about-us/copyright, and API
    Portal terms, https://portal.apis.stats.govt.nz/terms (CC BY 4.0).
  - data.govt.nz guidance and `data-govt-nz/*` repositories, structural prior
    art only (URLs in ADR-0022).
- Specification: Pete's 6 October 2026 brief; ADR-0022; ADR-0003.
- Checks on eb1b1df: `uv run pytest -q` 1503 passed, 22 skipped, 2 deselected;
  `uv run ruff check src tests` clean; `uv run mypy --strict src` clean (90
  files).

## Independent review

### Independently derived expected behaviour

- The archive sits upstream of `data/raw/`. Nothing on the governed path
  (`registry`, `context`, `transform`, `transforms/`) or downstream (`engines`,
  `policy`, `scenarios`, `api`, `llm`) imports `poltika.data.acquisition` or
  names the archive path. `DatasetManifest` and the existing boundary tests are
  unchanged.
- Exact response bytes are stored once under their SHA-256. Blobs and records
  are never overwritten, and a corrupt blob is detected. Every successful
  retrieval writes a new record, including unchanged ones.
- `content_changed` and `metadata_changed` are independent, all four
  combinations are reachable, and the first observation has neither.
- Unknown metadata stays `None`. Issued, modified, temporal coverage and
  retrieval time are separate fields, and none is inferred from another.
  `publisher_name_at_capture` comes from the source response, never the YAML.
- The Stats NZ key is never persisted, logged, fingerprinted, put in a query
  string or exception, sent to OpenRouter, or sent to another host or over
  plain http.
- HTTP retries are bounded and honour `Retry-After`. 429 and 5xx are retried;
  other 4xx are permanent.
- OpenRouter enrichment is optional and runs after preservation. It never
  raises into ingestion, never touches records, metadata or blobs, and is
  labelled `NON_AUTHORITATIVE_ADVISORY_METADATA`.
- Catalogue identifiers come from citable Stats NZ sources; nothing is guessed.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| Round 1, P2: a run without native metadata, or a failed optional data.govt.nz lookup, gave `metadata_changed=True` when nothing changed. | CODE_ERROR | Fixed in 39fda80. |
| Round 1, P3: a same-host https→http redirect would carry the subscription key over plain http. | CODE_ERROR | Fixed in 39fda80. |
| Round 1, nit: catalogue `base_url` was free text, so the key went to whatever host it named. | ARCHITECTURE_ISSUE | Fixed in 39fda80: https on `api.data.stats.govt.nz` only. |
| Round 2, P2: `metadata_changed` ignored codelist, concept scheme and DSD changes (the data dictionary), though the docs said it covered them. | CODE_ERROR | Fixed in eb1b1df: C14N 2.0 hash of the structure message with `message:Header` removed. |
| Round 2, P3: a `--no-metadata` run printed "first observation". | CODE_ERROR | Fixed in eb1b1df: prints "not fetched". |
| Round 2, nit: `base_url` accepted a query or fragment. | CODE_ERROR | Fixed in eb1b1df. |
| Round 3, nit: a namespace-prefix rename combined with a QName-valued attribute would change the structure hash. | CODE_ERROR | Open; ADE structure messages are not known to use such attributes. |
| Round 3, question: if the server reorders codelists, `metadata_changed` flips. | INTERPRETATION_AMBIGUITY | Open; needs live output to check. The raw bytes are kept either way. |
| ADE's listing has no CPI, HLFS or GDP/national-accounts dataflow, so the brief's coverage goal can't be met from ADE alone. | MISSING_SOURCE | Not guessed. Recorded in `stats_nz.yaml`; needs another Stats NZ distribution. |

Provenance check of `stats_nz.yaml` (unauthenticated HTTP): the four dataflow
identifiers (`STATSNZ:POPES_SUB_004`, `INC_INC_011`, `HES_HES_003`,
`INC_INC_001`, version 1.0) and their titles match the live listing. The
licence, rights and attribution wording match the Stats NZ copyright page.
`landing_page`, `accrual_periodicity` and `secondary_catalogue` are null
because no citable source states them. The listing marks every dataflow
`isFinal="false"` with a `NonProductionDataflow` annotation, and each entry
notes this.

Round 3 verdict: no P1 or P2 remains on eb1b1df.

## Author response

The orchestrating session wrote the interface contract, so it knew the design
rationale. Three Sonnet agents implemented the change against that contract:
the core archive; the Stats NZ connector, catalogue and CLI; and the
governance docs, enrichment and boundary tests. The review passes received
only the brief, the contract and the diff.

Decisions D5–D8 are in `docs/decision_log.md`. Pete accepted ADR-0022 on
6 October 2026.

Not verified:
- No authenticated Stats NZ call has been made, because
  `POLTIKA_STATS_NZ_API_KEY` was not available. The data endpoints and the
  byte stability of `csvfilewithlabels` are checked against the documentation
  only.
- OpenRouter has not been called.
- Concurrent writers were reasoned about, not stress-tested.
- Bandit could not run locally. CI's static-analysis job runs it.

## Resolution

- Every P2, P3 and round 1–2 nit is fixed, each with a regression test that
  fails on the earlier head.
- The round 3 items and the CPI/HLFS/GDP gap stay open as follow-ups.

## Deferred Codex audit

Not required before merge: there are no `policy_specs/`,
`engines/simulator/` or calculated-amount changes. When Codex is available,
inspect 0c12bf4, 39fda80 and eb1b1df, focusing on:

- secret handling in `source.py` and `stats_nz.py`;
- blob and record atomicity in `archive.py`;
- the metadata comparison and structure-hash rules in
  `SourceArchive.preserve` and `stats_nz._structure_c14n_sha256`.
