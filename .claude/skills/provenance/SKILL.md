---
name: provenance
description: Use whenever creating, reading, or editing anything under policy_specs/*/sources.yaml, data/raw/, data/processed/, data/metadata/, or any external statistical dataset (Stats NZ, Treasury, IRD, MSD, etc.) — acquiring a dataset, writing a raw-snapshot manifest, or mapping a snapshot to a canonical Poltika variable. Governs what provenance a source or dataset must carry before it can be used.
---

# Provenance

Poltika has two distinct kinds of source material, and they carry different
provenance requirements. Don't conflate them.

## 1. Policy sources (legislation, regulations, agency guidance)

Already instantiated: `policy_specs/working_for_families/sources.yaml` and
`policy_specs/accommodation_supplement/sources.yaml`. Each entry needs, at
minimum: `id`, `kind` (legislation / regulations / amending_legislation /
agency_guidance / agency_rates / agency_worked_example / etc.), `title`,
`url`, and `covers` (what it establishes). Follow the existing pattern in
those two files rather than inventing a new shape — see doctrine/review-doctrine.md
for what a citation needs to support a decision.

## 2. External statistical datasets (Stats NZ, Treasury, IRD, MSD, etc.)

Not yet instantiated for v0.1 (see REPOSITORY_STRUCTURE.md — `data/` is
target-only until a task needs it: BUILD_PLAN.md Tasks 10a/10b, 22a). This is
governed by the **Data Acquisition Doctrine** (BUILD_PLAN.md) and
`doctrine/deterministic_core.md`: v0.1 depends on authoritative external
data, not a live API — datasets are manually acquired and frozen as
immutable, versioned raw snapshots.

Every raw snapshot's manifest (`data/metadata/datasets/<id>.yaml`, or
equivalent, once that directory is created) must record all eleven fields:

```yaml
source_organisation:      # e.g. Stats NZ
dataset_series:            # the named dataset/series
source_url_or_identifier:  # where appropriate
retrieval_date:            # when it was fetched
observation_reference_period:  # what period the data covers
units:
geography_population:      # where applicable
retrieval_method:          # manual_download for v0.1; stats_nz_api later
raw_snapshot_version:
transformation_version:
canonical_variable_mapping:  # which src/poltika/semantics/ variable(s) this feeds
```

If any field is unknown or unverifiable from the source itself, stop and flag
it — per CLAUDE.md's ground-truth rule, don't guess a retrieval date, period,
or geography to fill the manifest.

## Rules that apply to both kinds

- **Immutable snapshots.** A raw snapshot is never edited in place once
  acquired. A correction is a new versioned snapshot, not an edit — this is
  what makes a snapshot usable as a regression fixture (Task 10b/15/22a,
  BUILD_PLAN.md).
- **Minimum necessary, not the full catalogue.** Only acquire what a
  specific policy vertical actually needs to run and validate (Data
  Acquisition Doctrine) — this is not licence to bulk-ingest an agency's
  full catalogue "in case it's useful."
- **No source-specific leakage downstream.** Nothing outside the `data/`
  transformation layer reads a raw or processed file directly — see the
  dependency boundary table in REPOSITORY_STRUCTURE.md. Anything downstream
  reads only the canonical Poltika variable.
- **Change attribution.** When a canonical variable's value changes, the
  provenance chain (which snapshot, which transformation version) should
  make it possible to say whether the cause was a source data update, a
  transformation change, a parameter change, a policy-rule change, or a
  simulation-code change — this is what makes the Assurance/regression
  architecture work, not a parallel bookkeeping exercise.
