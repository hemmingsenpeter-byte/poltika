# Changelog

## Unreleased (v0.2: static population microsimulation)

See `BUILD_PLAN_v0_2.md`. No calculated amount, protected expected value or
result identity changes.

- **Data layer** (Phase 1): immutable raw snapshots with an eleven-field
  provenance manifest and SHA-256; a registry that refuses a snapshot not
  matching its manifest; a versioned transformation registry; a canonical
  variable dictionary; `DataContext`, which returns values with their full
  lineage. A CI check fails if a committed snapshot or manifest is edited,
  and a test fails if anything outside `poltika.data` imports it.
- **Population schema** (Tasks 2.1-2.2): weighted households whose facts
  are scenario records, so a population household runs through the same
  path as a single one. Synthetic populations must carry the synthetic
  label.
- **Validation, weighting and reforms** (Phases 4-6): record checks with
  weighted status summaries; weighted totals, means and quantiles defined
  once; reforms as `set`/`add`/`multiply` overrides of the loaded
  parameters, labelled `scenario_assumption` in every trace. The engines
  accept preloaded parameters, so a population run loads each policy
  once. Results on the default path are unchanged.
- **Population runner** (Phase 7): every valid household runs under the
  baseline and the reform through `run_combined_household`, with per-
  component deltas that exist only when both runs calculated. Each run has a
  reproducible `run_id` and `results_sha256`. Caching the parsed
  `policy.yaml` by its hash (still checked on every call) makes a
  household about 80 times faster.
- **Analysis** (Phase 8): weighted winners and losers, deciles, household
  types, children, regions and AS areas, per-component fiscal totals with
  coverage, per-policy withdrawal paths, and parameter sweeps. Every table
  names its component set and unit, and reports what it left out.
- **Population explanations** (Task 9.1): a deterministic account of a
  run, rendered from recorded figures only, with `verify()` checking every
  figure against the run. The run records each assumed value with the
  baseline value and source it replaced.

## Unreleased (v0.1.6: keep v0.1 current)

See `BUILD_PLAN_v0_1_6.md`.

- **Source-currency report** (Task 2.1): a weekly workflow lists parameter
  values ending within 90 days, values not approved or with no end date,
  and cited sources with no structured check in 180 days, and opens an
  issue when anything is due. It fetches nothing.
  `python -m poltika.engines.assurance.currency <policy_dir>...` runs it
  locally.

## Unreleased (v0.1.5: the evidence and explainability bridge)

See `BUILD_PLAN_v0_1_5.md` for the plan and its progress table. No
calculated amount, protected expected value or result identity has changed
since v0.1.0.

- **Calculation steps:** every result's trace lists the arithmetic it
  performed, with the rule each step implements and its intermediate
  values.
- **Reason codes:** every result that is not calculated has a stable
  code. `unsupported` results are marked `evidenced_exclusion` or
  `not_modelled`; `needs_review` results name the facts they are waiting
  for.
- **Explanations:** each result gets a deterministic explanation rendered
  only from its trace (no LLM), and `verify()` proves it agrees with the
  calculation number for number. Every calculation route includes them
  (`/wff/calculate`, `/accommodation-supplement/calculate`,
  `/household/calculate`, `/scenarios`).
- **Evidence model:** every source has a type and authority rank. An
  evidence-coverage check runs in CI and fails on an unranked source, a
  parameter resting on guidance, or a rule without primary legislation.
- **Analyst page** at `/analyst`: pick a household, calculate, and open
  "Why?" for the steps, the facts asserted, and the rates and sources.
- **Pilot container:** a `Dockerfile` and `compose.yaml` (API plus
  PostgreSQL), smoke-tested in CI; `docs/pilot/GUIDE.md`.
- **Hardening:**
  - golden traces are frozen;
  - over 100 spec-case explanations are verified;
  - generated-household properties are tested;
  - evidence and explanation attack tests are added;
  - a protected-case metadata check is added.
- **Release records:** `docs/releases/V0_1_LIMITATIONS.md`, and
  `V0_1_BASELINE.md` (measured at v0.1.0).
- **Working agreement:** in `doctrine/development-doctrine.md`.

## v0.1.0 (25 September 2026)

Accepted by Pete (BUILD_PLAN.md Task 34.5).

v0.1 is a deterministic foundation: two New Zealand policies modelled from
cited primary sources, a combined household scenario, and provenance.

- Working for Families, 2026-27: family tax credit, minimum family tax
  credit and Best Start calculated inside a scoped domain. The in-work tax
  credit is `needs_review` until its 2026-27 base rate is confirmed (Task
  26b). Protected-credit, shared-care and part-year cases are
  `unsupported`.
- Accommodation Supplement, weekly: published MSD entry thresholds and
  income levels (DEC-002), statutory area caps and the 70% subsidy rate,
  asset imputation, and the non-beneficiary income reduction (DEC-001),
  with r 19 rounding. Homeowners, mixed-benefit couples and NZ
  Superannuation are `unsupported`.
- The WFF and AS interaction: a combined household runner that keeps each
  policy's native period, with no combined total and no income coupling
  (DEC-003). Conservative shared-fact checks downgrade disagreements to
  `needs_review`.
- Every component is `calculated`, `needs_review` or `unsupported`. A
  missing fact never becomes zero.
- Provenance: per-component traces and hash-bound artifacts, and
  per-policy and combined provenance reports that resolve sources, rules
  and decisions.
- Scenarios: canonical scenario and result ids, code identity, and an
  append-only PostgreSQL store (ADR-0013) with replay on retained
  artifacts, including on the retained code revision.
- API (FastAPI): per-policy routes, `/household/calculate`, and stored
  `/scenarios` routes (create, fetch, replay, re-run).
- Tests: spec, benchmark and regression layers, golden households, a
  frozen golden snapshot, an installed-artifact check and code replay, run
  in CI on every PR and push.
- Demo: `docs/demo/v0_1/`.
- Post-review fixes (PR #79; author-reviewed, merged on Pete's acceptance
  without a GPT/Codex audit):
  - storing the same household with its children in another order no longer
    returns 409;
  - each module's checks refuse a `policy.yaml` that changed after its
    parameters were loaded;
  - committed policy-file lookups are cached;
  - the statutory-value guard also lists the golden-results fixture and the
    source, specification and decision files;
  - Python is pinned to 3.12;
  - WFF DEC-001 records when an evidenced eligibility failure is $0 and when
    it is `unsupported`.
- Known limitation: no WFF total. The 2026-27 in-work tax credit base rate
  can be reversed early by Order in Council, so it stays `needs_review`.

## Scaffolding

- Seeded the Poltika repository structure
- Added doctrine, ADR, and policy-spec scaffolding
- Added baseline documentation and initial guardrails
