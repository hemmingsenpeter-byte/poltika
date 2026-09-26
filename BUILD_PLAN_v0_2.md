# Poltika v0.2 Build Plan: authoritative data foundation

**Date:** 26 September 2026
**Status:** Approved 26 September 2026, with the recommended decisions below
(D1's date is fixed at Task 5.1).
**Starts:** Sprint 1 needs no external data and touches no v0.1 file, so it
can start now. The later sprints follow once v0.1.5 ships. It runs alongside
v0.1.6 (`BUILD_PLAN_v0_1_6.md`), which touches different files.

`BUILD_PLAN.md`'s doctrines apply unchanged. The ones that matter most here:

- **Data Acquisition Doctrine:** authoritative source → acquisition →
  immutable raw snapshot → transformation and validation → canonical
  variable → simulator → Assurance. Only the datasets a slice needs.
- **Dependency boundary** (`REPOSITORY_STRUCTURE.md`): nothing outside
  `src/poltika/data/` reads a raw or processed file. Everything downstream
  reads canonical variables.
- **Ground truth:** every value comes from a cited publication. If a
  manifest field can't be verified from the source, stop and flag it
  (`.claude/skills/provenance/SKILL.md`).

## What v0.2 delivers

`ROADMAP.md`'s exit gate:

> For a historical date, Poltika reconstructs the major fiscal and economic
> baseline from authoritative NZ data and traces every material input.

The roadmap lists the full scope: connectors, scheduled refreshes, a wide
range of series. This plan builds it as one thin vertical slice first:

1. a few datasets, acquired manually;
2. carried through every layer;
3. reconstructing one historical baseline.

Connectors and broader coverage follow once that slice passes. That is the
same approach v0.1 took with two policies.

**Not in v0.2:**

- a third policy;
- the policy interaction graph (v0.3);
- scenario costing (v0.4);
- Monte Carlo or sensitivity analysis (v0.5, per ADR-0008's sequence);
- Stats NZ microdata or IDI access.

## Tasks

Owners follow the v0.1 roles: GPT/Codex for sources and interpretation,
Claude Code for implementation, and the other model reviews.

### 1. The data layer

- **1.1 — Claude Code. Create the `data/` tree and `src/poltika/data/`**,
  exactly as `REPOSITORY_STRUCTURE.md`'s target architecture places them:
  - `data/raw/<organisation>/` holds immutable snapshots;
  - `data/processed/` holds machine-generated output;
  - `data/metadata/datasets/` and `data/metadata/variables/` hold the
    manifests and the dictionary.

  Move each directory's "target" entry to "instantiated" in the same PR.
- **1.2 — Claude Code. Manifest schema.** A Pydantic model for the eleven
  provenance fields in the provenance skill, plus a SHA-256 of the raw
  file. Validation fails on any missing field.
- **1.3 — Claude Code. Immutability guard.** A CI check fails if a
  committed raw snapshot or its checksum changes. A correction is a new
  snapshot version, never an edit. This extends the protected-path guard
  pattern.
- **1.4 — Claude Code. Dataset registry.** Lists every snapshot and its
  manifest, and resolves "dataset X as at vintage V".

### 2. Canonical variables

- **2.1 — Claude Code, reviewed by GPT/Codex. Data dictionary.** Each
  canonical variable in `src/poltika/semantics/` has:
  - an id, meaning and unit;
  - a frequency;
  - nominal or real, and the price base if real;
  - stock or flow;
  - a geography or population;
  - its valid period.
- **2.2 — Claude Code. Transformation registry.** Every raw → processed →
  canonical step is a named, versioned, pure function. The output records
  which transformation version produced it.
- **2.3 — Claude Code. Read interface.** Downstream code gets values by
  canonical id, date and vintage (`context.get("prices.cpi.all_groups",
  ...)`). It never sees a file, column or source format.

### 3. First datasets, acquired manually

Each dataset has a named consumer in Task 5 or Task 6, or it isn't
acquired.

- **3.1 — GPT/Codex. Identify the exact publications** for:

  | Area | Series |
  | --- | --- |
  | Prices | CPI, all groups |
  | People | Estimated resident population |
  | Economy | Nominal GDP |
  | Crown finances | Core Crown revenue, expenses, operating balance, net debt and finance costs |
  | Households | Household income distribution by type |

  The likely publishers are Stats NZ and the Treasury's Financial
  Statements of the Government and fiscal time series. Record the
  publication, table, vintage and any known revision practice for each.
- **3.2 — Pete or GPT/Codex. Acquire the snapshots**
  (`retrieval_method: manual_download`) and write their manifests. Claude
  Code does not download source data unless network access is granted (D3),
  and then only as a reviewed step.
- **3.3 — Claude Code. Transformations and mappings** from each snapshot to
  its canonical variables.

### 4. Validation

- **4.1 — Claude Code. Checks run on every snapshot:**
  - schema and types;
  - units against the dictionary;
  - missing and duplicate records;
  - declared ranges;
  - period continuity;
  - checksums.
- **4.2 — Claude Code. Revision handling.** Two vintages of the same series
  can coexist. The registry reports which observations changed between
  them.
- **4.3 — Claude Code. Ingestion tests in CI.** Each snapshot → canonical
  path is a regression test with frozen expected values. Those values are
  taken from the publication, not from the code.

### 5. Historical baseline

- **5.1 — GPT/Codex, with Pete deciding. Choose the reference date (D1)**
  and define the baseline:
  - revenue, expenses and operating balance;
  - net debt and finance costs;
  - nominal GDP and debt to GDP;
  - real and per-person views, using CPI and population.
- **5.2 — Claude Code. Baseline reconstruction.** A deterministic module
  produces the baseline for the chosen date. Each figure carries its full
  chain:

  `value → transformation → dataset → source → publication → vintage → retrieval date`
- **5.3 — GPT/Codex. Benchmark cases.** Hand-check the reconstructed
  figures against the published totals: the Financial Statements and
  Treasury's fiscal tables. Every difference is explained by a named
  transformation, or it is a finding under the Review Doctrine.
- **5.4 — Claude Code. Explanations.** The baseline gets the same kind of
  deterministic plain-language explanation as v0.1.5 results, tested
  against the figures.

### 6. Bridge to v0.1 (small)

- **6.1 — Claude Code. Real household types.** Run the existing WFF and
  Accommodation Supplement calculations for household types taken from the
  income-distribution data. The output is per-household results with the
  data's provenance attached, not a population costing (v0.4). The v0.1
  results stay byte-identical.

### 7. Connectors (after the manual slice passes)

- **7.1 — Claude Code. Stats NZ and Treasury connectors** as a second
  `retrieval_method`. They write the same raw snapshot and manifest as the
  manual path, so nothing downstream changes. A connector run that changes
  a snapshot creates a new vintage and never overwrites one.
- **7.2 — Claude Code. Scheduled refresh** that proposes new vintages as a
  PR for review and never merges them itself.
- The manual path stays, for sources without APIs.

### 8. Release

- **8.1 — Claude Code.** Write the CHANGELOG and `docs/releases/`
  limitations, and add a v0.2 release-gate test that maps each exit-gate
  item to a test. Pete tags `v0.2.0`.

## Sequence

| Sprint | Work |
| --- | --- |
| 1 | 1.1-1.4, 2.1-2.3, 3.1 |
| 2 | 3.2-3.3, 4.1-4.3 |
| 3 | 5.1-5.4, 6.1 |
| 4 | 7.1-7.2, 8.1 |

Sprint 1 needs no external data. The manual slice (sprints 1-3) passes the
exit gate on its own. Sprint 4 only changes how the snapshots arrive.

## Exit gate

- For the chosen reference date, the baseline figures in 5.1 are produced
  deterministically. Each one reconciles to its published total, or its
  difference is explained.
- Every material input traces from value to retrieval date. A test fails
  if any link is missing.
- Every raw snapshot has a complete, validated manifest and a fixed
  checksum. None has been edited since it was committed.
- No code outside `src/poltika/data/` reads a raw or processed file. An
  import-boundary test enforces this.
- The v0.1 and v0.1.5 results and release-gate tests are unchanged.

## Open decisions for Pete

- **D1: Which reference date?** Recommended: the latest year-end with
  audited Financial Statements of the Government, so the benchmarks are
  final published numbers.
- **D2: Scope.** Recommended: data only, with no third policy, as above.
- **D3: Network access.** Allow `www.stats.govt.nz`, `api.stats.govt.nz`
  and `www.treasury.govt.nz` in this environment's network settings for
  Task 7. Until then, snapshots are acquired outside it.
- **D4: Scope Doctrine wording.** `BUILD_PLAN.md`'s Scope Doctrine still
  says sensitivity analysis is "deferred to v0.2". ADR-0008's sequence puts
  it in v0.5. Recommended: follow ADR-0008 and leave the frozen doctrine
  text unchanged. This plan records that it is superseded, rather than
  editing the doctrine.
