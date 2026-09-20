# ADR-0003: Data acquisition boundary — manual/frozen datasets for v0.1

**Date:** 2026-09-21
**Status:** accepted

## Context

Poltika's simulator needs authoritative external data (e.g. Stats NZ
geography data for the Accommodation Supplement area lookup). Building live
API ingestion this early — authentication, retries, rate limits,
schema-change handling, refresh scheduling — would spend v0.1 effort on
ingestion infrastructure instead of proving the semantic data layer, the
deterministic simulator, and the Assurance system.

## Decision

v0.1 depends on authoritative external data, not on any live statistical
API. Datasets are manually acquired and frozen as immutable, versioned raw
snapshots, then transformed and validated into canonical Poltika variables
that the simulator consumes. Only the minimum datasets a given policy
vertical actually needs are acquired — not a full agency catalogue.
Retrieval method is recorded as `manual_download` for v0.1 and can later
become `stats_nz_api` (or equivalent) without changing the canonical
variable or simulator interface. Frozen datasets double as regression
fixtures inside the existing Assurance/provenance architecture. See the
Data Acquisition Doctrine in BUILD_PLAN.md for the full rule.

## Consequences

- v0.1 stays deterministic, reproducible, and debuggable without API
  auth/retry/rate-limit/schema-change engineering
- Source acquisition and simulation remain decoupled: the simulator never
  depends on a source-specific representation (API response, CSV structure,
  endpoint)
- Automated ingestion (Stats NZ API connector, scheduled refreshes, further
  government-source connectors, schema-change detection, broader dataset
  coverage) becomes a post-v0.1 capability-driven addition, not tied to a
  fixed version number
- Frozen snapshots give a stable base for regression fixtures and for
  attributing future output changes to source data updates, transformation
  changes, parameter changes, policy-rule changes, or simulation-code
  changes
