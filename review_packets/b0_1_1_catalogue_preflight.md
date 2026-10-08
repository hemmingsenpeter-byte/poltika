# Review Packet: Task B0.1.1 read-only catalogue — 7 October 2026

**Label:** author preflight plus a fresh same-model check (`poltika-reviewer`,
Sonnet). This is not an independent GPT/Codex review. The PR shows no
calculated amount, so no review-queue row is required (ADR-0020).

## Review inputs

- PR/diff: `prog/b0.1.1-catalogue` off `origin/main` `4c33c63`; reviewed
  head `bf1177b`, fixes in the following commit.
- Plan: `BUILD_PLAN_B0_1_WEB.md` B0.1.1 (PR #185), ADR-0023.
- Sources: none. The endpoints rearrange existing registry, manifest,
  dictionary, source-catalogue and evidence-coverage content.
- Tests: full suite 1721 passed, 22 skipped (at `bf1177b`); after the fixes,
  `tests/unit/api/test_v1_catalogue.py` (33 cases), the data and
  Source Archive boundary tests, ruff, `mypy --strict src`, the full suite.

## Independent review

### Expected behaviour (derived before reading the author's rationale)

- Every endpoint reads only metadata and returns typed JSON.
- A missing or invalid catalogue answers 503 `catalogue_unavailable`. An
  unknown id answers a coded 404. Neither leaks a server path.
- `api/` imports nothing from `poltika.data` except `metadata_index` and
  `manifest`, and never names the Source Archive.
- The image serves the catalogue from its own copies.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1 (P2): an invalid registry, manifest, population spec or dictionary returned 500 | CODE_ERROR | Fixed: one `_catalogue_read` guard maps every read error to 503; parametrised regression tests |
| R2 (P2): `/evidence` and `/meta` returned 500 on an invalid policy catalogue or a corrupt population file | CODE_ERROR | Fixed: `/evidence` maps to 503; `/meta` reports `population: null` |
| R3 (P3): 404s were missing from OpenAPI | CODE_ERROR | Fixed, with a test |
| R4 (P3): `/meta` returns `population: null` rather than 503 | INTERPRETATION_AMBIGUITY | Kept by design. `/meta` describes the deployment's configuration and must stay available when one part is absent. Documented in the route docstring. Tier B, not Pete's |
| R5 (P3): the boundary test checks static imports only | TEST_ERROR | Accepted. This matches every other boundary test here; a dynamic import would also be caught in review |
| Author-found: a response field named `source_archive` tripped the ADR-0022 naming test | ARCHITECTURE_ISSUE | Renamed `preserved_sources` before review |

Not verified: the Docker smoke test, which runs in CI's `pilot-image` job
because the self-hosted runner has no Docker.

## Resolution

All P2 findings fixed and regression-tested. Deferred Codex audit: none
required.
