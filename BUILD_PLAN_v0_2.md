# Poltika v0.2 Build Plan: static population microsimulation

**Date:** 26 September 2026
**Status:** Approved 26 September 2026, with the recommended decisions
below. ADR-0014 (accepted) moves static microsimulation into v0.2.
**Role (3 October 2026):** Active supporting release-completion plan under
[BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md), Phase A. Implementation
and review evidence are retained below; GitHub has no `v0.2.0` tag. Keep this
file live until Pete completes the release record, then archive an exact copy.
It does not determine the next modelling task or gate household work on tagging.
Earlier release sequencing and progress entries below are historical records;
[PROGRAMME_STATUS.md](PROGRAMME_STATUS.md) is the live execution state.


## What changes

| Release | Question |
| --- | --- |
| v0.1 | Can Poltika correctly calculate this household? |
| v0.1.5 | Can Poltika prove and explain why? |
| **v0.2** | **What happens across a modelled population if Working for Families or Accommodation Supplement settings change?** |

v0.2 runs the existing v0.1 engine across a weighted population. It runs
it twice, under current law and a reform, and aggregates the differences
into fiscal, distributional and household-type results. Every result has
the same evidence and reproducibility record a single household has.

**The rule that governs the whole release:** there is no second policy
engine. The v0.1 engines stay the only place statutory rules are
calculated. A microsimulation is many calls to them.

`BUILD_PLAN.md`'s doctrines apply unchanged:

- primary sources only;
- the three test classes;
- protected values changed only through the test doctrine;
- ambiguity escalated rather than resolved;
- the Data Acquisition Doctrine and the dependency boundary;
- external implementations never a source of policy logic
  (`doctrine/ip-doctrine.md`).

## Review of the proposed v0.2 specification

The v0.2 specification Pete pasted on 26 September 2026 (Modules A-Z, the
20 questions and the exit test) is the basis of this plan. Checking it
against the repository changes these points.

| # | Finding | Effect on this plan |
| --- | --- | --- |
| R1 | **It reorders the roadmap.** ADR-0008 put data in v0.2, the interaction graph in v0.3 and the scenario engine in v0.4, arguing that scenario comparison needs a dependency graph first. For WFF and the Accommodation Supplement that argument doesn't hold: their interaction is fixed by rule (R2), and the existing combined runner already handles it. | ADR-0014 (accepted) moves static microsimulation into v0.2. The historical macro baseline (GDP, debt, operating balance) moves to v0.3, beside the graph (since moved to v0.5 by ADR-0015). The proposal's reordering of later releases (behaviour at v0.4, graph at v0.6) is **not** adopted. It needs its own decision. |
| R2 | **No WFF-to-AS interaction exists in the modelled law.** AS-10 and DEC-003 exclude WFF tax credits from AS chargeable income, and IRD excludes Accommodation Supplement from WFF family income. The proposal's "AS interaction: -$110m" can't arise. | Module Q becomes an invariant test: a WFF-only reform leaves every household's Accommodation Supplement unchanged. The output states that there is no modelled interaction and cites the rule. |
| R3 | **Income tax and main benefits aren't modelled**, so there is no disposable income. | **No poverty or income-adequacy measures in v0.2 (Module O is dropped).** They need full disposable income and the official measures' own definitions. Module P is reported only as *WFF and AS withdrawal rates*, never as effective marginal tax rates. |
| R4 | **The 2026-27 in-work tax credit is `needs_review`** (the Task 10.2 rate-status contract), so a total WFF figure can't be calculated for 2026-27. Abatement falls on family tax credit first, then the in-work tax credit (WFF-03, MD 2). | Every population result reports its weighted coverage: calculated, `needs_review` and `unsupported`. `needs_review` is never counted as zero. The exit test reports the in-work tax credit's coverage honestly, and becomes complete once v0.1.6 adds 2027-28. |
| R5 | **Real survey unit records are restricted-access.** They can't be committed or run in CI. | v0.2 is built and tested on a **synthetic development population** calibrated to published aggregate tables, and every output is labelled as not an estimate for New Zealand. A real-microdata adapter is D2. |
| R6 | **Entitlement is not expenditure.** WFF and the Accommodation Supplement are paid only to people who claim. | The fiscal output is a *static entitlement cost at full take-up*, unless a sourced take-up assumption is registered. It is never labelled as spending. |
| R7 | **Reform values are assumptions, not law.** | Overrides are never written to `policy.yaml` and never marked `approved`. A run records its statutory baseline (hash-bound, as today) separately from its overrides, and every reform output says which values were assumed. |
| R8 | **Speed.** A combined household run takes about 200 ms today, mostly reloading the policy files. | The batch runner loads each policy once. Profile before adding Parquet, Polars or DuckDB (D6). |
| R9 | **The proposal's example figures** ($3.21b, $260m, 412,000 households) are illustrative. | None of them enters a test or a document as a fact. Population tests use tiny hand-calculated populations, invariants and published benchmarks. |
| R10 | **Attribution.** Splitting a cost by component or by group is exact: the parts add up. Splitting it across several parameters changed at once depends on the order they are applied. | v0.2 explains cost by component and by group. Attribution across parameters is only for single-parameter scenarios, until an order rule is decided. |
| R11 | **Treasury's TAWA** is a useful methodology benchmark. | Read it under `.claude/skills/clean-room-research/`, for concepts only. It is never a source of rules, values or code. |
| R12 | **Existing pieces cover part of the proposal.** The Task 32 scenario store and run records, `result_id`, the provenance report, the explanations and the analyst page are all reusable. | Extend them rather than build a parallel stack (Modules U, Y, Z). |

## Not in v0.2

- Poverty or income-adequacy measures (R3).
- Income tax, main benefits, or any policy beyond WFF and the
  Accommodation Supplement.
- Behavioural responses, labour supply, or take-up modelling beyond a
  registered assumption.
- Macroeconomic, GDP, inflation or debt modelling, including the
  historical fiscal baseline (moved to v0.3 by ADR-0014, then to v0.5 by
  ADR-0015).
- Monte Carlo, distributions or uncertainty ranges (v0.5). Deterministic
  sweeps are in scope.
- Calibration or raking of weights.
- The full policy interaction graph.
- LLM policy generation, Discovery, Hypothesis, agents or optimisation.

## Phases

Owners follow the v0.1 roles: GPT/Codex for sources and interpretation,
Claude Code for implementation, and the other model reviews.

### Phase 1: data layer (Claude Code)

The population and its calibration tables are datasets, so they need the
data layer first.

- **1.1** Create the `data/` tree and `src/poltika/data/` as
  `REPOSITORY_STRUCTURE.md` places them.
- **1.2** A manifest schema covering the eleven provenance fields, plus a
  SHA-256, vintage and transformation id.
- **1.3** An immutability guard: CI fails if a committed snapshot or
  manifest is edited or deleted.
- **1.4** A dataset registry, resolving "dataset X at vintage V".
- **1.5** A canonical variable dictionary and versioned transformation
  registry.
- **1.6** A read interface (`CanonicalContext`), so downstream code never
  sees a file.
- **1.7** An import-boundary test: nothing outside `poltika.data` imports
  it or reads `data/`.

### Phase 2: population schema (Module A)

- **2.1 — Claude Code.** Canonical `PersonRecord`, `FamilyRecord` and
  `HouseholdRecord`, plus `PopulationDataset` (records, weights, version,
  manifest). Every fact the v0.1 engines need is a field. An unknown fact
  is recorded as unknown, never as zero.
- **2.2 — Claude Code.** Adapters from a household record to the existing
  `ScenarioRecord` / WFF / AS inputs. A population record runs through
  exactly the path a single household does.
- **2.3 — GPT/Codex review.** Check the mapping against both
  specifications' input definitions: family, partner, dependent child,
  family scheme income, chargeable income and housing costs.

### Phase 3: synthetic development population (Module B)

- **3.1 — GPT/Codex.** Identify the published aggregate tables to
  calibrate against:
  - household and family composition, number and ages of children;
  - income distribution;
  - tenure and housing costs;
  - Accommodation Supplement areas;
  - total household counts.

  Record each table's publication, table and vintage.
- **3.2 — Pete or GPT/Codex.** Acquire them as manifest-tracked snapshots
  (Phase 1).
- **3.3 — Claude Code.** A seeded, deterministic generator. The same seed
  and snapshots give a byte-identical population. The population is itself
  a versioned dataset, with a report of how it matches each calibration
  table.
- **3.4 — Claude Code.** Labelling. Every output from a synthetic
  population carries "synthetic development population, not an estimate
  for New Zealand", from the API through to the analyst page.

### Phase 4: population validation (Module C)

- **4.1 — Claude Code.** Record checks: impossible ages, negative amounts,
  duplicate ids, orphan children, invalid structures, unknown AS areas,
  missing or non-positive weights. Each record is `valid`, `warning`,
  `needs_review` or `invalid`.
- **4.2 — Claude Code.** A coverage report: weighted and unweighted shares
  with enough facts for each WFF and AS component. For example, "x% of
  weighted households can be calculated for family tax credit".

### Phase 5: weighting (Module D)

- **5.1 — Claude Code.** Weighted totals, counts, means and quantiles,
  each defined once. The weighted-quantile definition is stated and tested.
  Unit tests use populations whose answers are known by hand.

### Phase 6: scenarios (Modules E, F)

- **6.1 — Claude Code.** A reform schema: baseline (law as at a date),
  plus overrides by parameter id with the operations `set`, `add` and
  `multiply`. It extends the Task 32 scenario store.
- **6.2 — Claude Code.** Validation before running:
  - the parameter exists;
  - the value type and unit match the schema;
  - money is not negative and rates are in [0, 1];
  - no parameter is overridden twice;
  - the date is inside the reference period.

  A request for an unmodelled policy is `unsupported`, never approximated.
  Whether a valid value is *sensible policy* is not Poltika's call.
- **6.3 — Claude Code.** Scenario provenance (R7). The baseline's hashes,
  the overrides and the reform parameter hash are recorded, and reform
  values are marked `scenario_assumption`.

### Phase 7: microsimulation runner (Modules G-I, U, X)

- **7.1 — Claude Code.** A batch runner. It loads each policy once and runs
  every household under the baseline and under the reform, through the v0.1
  engines. It is deterministic and order-independent, with a run id.
- **7.2 — Claude Code.** Per-household deltas by component. A household is
  `needs_review` if either run is.
- **7.3 — Claude Code.** A run record, extending Task 32. It holds:
  - the code identity and lock hash;
  - the policy hashes;
  - the population version;
  - the scenario;
  - a results hash.

  Rerunning it reproduces the hash.
- **7.4 — Claude Code.** Profile the full synthetic population. Optimise
  only what the profile shows (D6).

### Phase 8: analytics (Modules J-N, P, R)

- **8.1** Winners and losers: gain, loss, no change, `needs_review`. Report
  weighted counts, means, medians and extremes.
- **8.2** Income deciles, on the basis chosen in D3.
- **8.3** Household types: sole parent, couple with children, number of
  children, renter or owner, working or not.
- **8.4** Geography: Accommodation Supplement areas, and regions where the
  population carries them. Tables only.
- **8.5** Static entitlement cost (R6): baseline, reform and delta by
  component, which add up exactly to the total.
- **8.6** WFF and AS withdrawal rates for chosen households along an income
  path. This shows cliffs and high-withdrawal zones (R3 wording).
- **8.7** Deterministic sweeps: one parameter over a list of values, one
  run each.

All Claude Code. Every figure carries its coverage (R4).

### Phase 9: explanation and assurance (Modules S, T, V, W)

- **9.1 — Claude Code. Population explanations.** Deterministic, tested
  against the figures like v0.1.5's. They cover:
  - the cost by component and group (R10);
  - the size and make-up of the affected population;
  - the rule and source behind each driver;
  - what was assumed.
- **9.2 — Claude Code, reviewed by GPT/Codex. Invariant tests:**
  - an identity reform changes nothing;
  - a WFF-only reform leaves Accommodation Supplement unchanged (R2);
  - a higher family tax credit rate never lowers any household's family
    tax credit;
  - ineligible households are unaffected;
  - doubling every weight doubles every total.
- **9.3 — GPT/Codex. Hand-calculated population cases.** Small
  populations with independently calculated totals, deciles and winner
  counts.
- **9.4 — GPT/Codex, Claude Code. Cross-validation report.** Compare
  modelled recipients and entitlement with published programme figures.
  Every difference is explained: synthetic population, take-up, scope.
  None is tuned away.

### Phase 10: interface (Modules Y, Z)

- **10.1 — Claude Code.** API routes under the existing scenarios API:
  - create a scenario;
  - run a simulation;
  - fetch its fiscal, distribution, household and explanation results.
- **10.2 — Claude Code.** Analyst page tabs, extending v0.1.5's page:
  - Overview
  - Distribution
  - Households
  - Areas
  - Fiscal
  - Evidence
  - Methodology

  The synthetic label shows on every tab.
- **10.3 — Claude Code.** CHANGELOG, `docs/releases/` limitations and
  methodology, and a v0.2 release-gate test. Pete tags `v0.2.0`.

## Progress

| Task | State |
| --- | --- |
| Phase 1 (1.1-1.7) | Done. `src/poltika/data/`, `data/`, `semantics/variables.py`, the `data-snapshot-guard` workflow and `tests/unit/data/`. Raw snapshots are committed rather than gitignored, so the registry can verify them. No real dataset yet: the dictionary is empty until 3.1 names the publications. |
| 2.1-2.2 | Done. `semantics/population.py` and `scenarios/population.py`. One family per household (the family is the household's facts). Facts use the stored scenario-record form, so the adapter is `record_from_plain`, moved from `store.py` to `record.py`. |
| 2.3 | Independently reviewed by GPT/Codex, 27 September 2026 (`reviews/2026-09-27-pr117.md`): mapping matches both policies' input contracts as declared synthetic assumptions; no actionable findings. A12 names the eldest-child-under-16 assertion. |
| 4.1 | Done. `scenarios/microsim/validation.py`: invalid, needs_review, warning and valid, with weighted summaries. A dependent-child count mismatch is a warning, not an error, because WFF and AS define a dependent child differently. 4.2 (component coverage) is built from run results in Phase 7. |
| 5.1 | Done. `scenarios/microsim/weighting.py`: the weighted quantile is the lower inverse of the weighted distribution, with no interpolation. |
| 6.1-6.3 | Done. `scenarios/microsim/reform.py`, plus an optional preloaded `parameters` argument on `run_wff_module`, `run_as_module` and `run_combined_household`. It is refused for another date or version, and every v0.1 result is byte-identical on the default path. Reform values are `scenario_assumption` with no source, in every trace. A reform isn't yet stored through the Task 32 store: it is recorded in the Phase 7 run record. |
| 7.1-7.3 | Done. `scenarios/microsim/runner.py`. Parameters are loaded once per policy, date and version. Per household and component it keeps the outcome, value and code. `run_id` hashes the population, reform, code and policy files, and `results_sha256` the results. Both reproduce on rerun. WFF (per tax year) and AS (per week) keep separate units (D8). Tests are invariants on the golden households: an identity reform gives zero deltas; a threshold rise never lowers family tax credit and is bounded by the policy values; a WFF-only reform leaves AS unchanged (R2). |
| 7.4 | Done. The profile showed re-parsing `policy.yaml` was about 90% of run time (`load_bound_policy_spec` runs twice per household). The parse is now cached by the file's SHA-256, which is still read and checked on every call, and each caller gets a deep copy. Measured: about 4.8 ms per household for both runs, roughly 8 minutes for 100,000 households. No new dependency is needed (D6). |
| 8.1-8.5, 4.2 | Done. `scenarios/microsim/analysis.py`: winners and losers, deciles, household types, dependent children, regions, AS areas, and per-component fiscal totals with coverage. A household's change is the sum of a named, single-unit component set, calculated only when every member is. So a family tax credit reform is measurable while the in-work tax credit is `needs_review`, and a partial set is never called total WFF. Every table reports what it left out. |
| 8.6-8.7 | Done. `scenarios/microsim/withdrawal.py`: per-policy withdrawal paths (WFF on the claimant's family scheme income, AS on weekly income) and deterministic sweeps. A combined WFF and AS withdrawal rate needs a stated mapping between the two income definitions (D9). The WFF path clears `net_family_scheme_income`, which can't follow the path, so minimum family tax credit reads `needs_review` along it. |
| 3.1-3.2 | Author record, 27 September 2026 (Claude Code, local machine with Stats NZ access): `docs/research/v0_2_task_3_1_calibration_tables.md`. Five Stats NZ snapshots with manifests (HES year ended June 2025, 2018 Census national highlights, household net worth 2024, two births release pages), their four registered transformations, 54 canonical variables, and `tests/unit/data/test_real_snapshots.py`. HES Table 5 counts people, not households. Gaps: household counts by AS area and claimant category. Independent GPT/Codex review open. |
| 3.3-3.4 | Mechanics done: `scenarios/microsim/synthetic.py` and its CLI. Every New Zealand quantity is a required `SyntheticSpec` input with no default: shares, bands, households represented, and all 16 asserted facts. `sources` must name where the targets came from. The generator rules are stated (independent marginals, equal weights, couple income split, gross income as family scheme income, AS weekly income as gross over a stated divisor) and reported with each population, along with a calibration report of target against generated shares. The output always carries the synthetic label. **Waiting on 3.1-3.2** for a real spec. The tests use a toy spec labelled as made up. **Real spec, 27 September 2026:** `data/metadata/populations/nz_synthetic_development.v1.yaml`, derived by `scenarios/microsim/calibration.py` (CLI `calibrate_cli`) from the Task 3.2 snapshots, with rules D1-D7 and assumptions A1-A11 (A10-A11 named after review) stated in its `sources` and `docs/releases/V0_2_POPULATION_METHODOLOGY.md`. A test regenerates it and compares. All 49 calibration rows within 3 points; the release gate's real-population row runs (FTC exit scenario, AS unchanged, explanation verified). |
| 9.3 | Done, GPT/Codex, 27 September 2026: `tests/acceptance/test_v0_2_independent_population_cases.py` adds fixed, source-checked expectations for unequal weights, fractional-dollar abatement, tied deciles, gains, losses, zero entitlement and unresolved coverage. Derivations and independent review of the original author cases are in `reviews/2026-09-27-pr117.md`. |
| 9.4 | Claude Code half done, 27 September 2026: `scenarios/microsim/crossval.py` and `crossval_cli.py` write `docs/releases/V0_2_CROSS_VALIDATION.md` from the baseline run against Inland Revenue WFF statistics (2025 tax year) and MSD Benefit Fact Sheets (June 2026 quarter), acquired as snapshots with a standard-library `data/xlsx.py` reader. Modelled/published: FTC families 0.75, FTC entitlement 0.78, children 0.56, Best Start families 0.13, AS recipients 0.18; every gap is explained (in-work non-beneficiary scope A6, one Best Start cohort, synthetic population, different year), none tuned. A test regenerates the report. GPT/Codex half open. |
| 10.1-10.2 | Done. `api/microsim.py`: population, parameters, runs and a run fetch, keeping a process's runs in memory. A rerun reproduces `run_id` and `results_sha256`. Durable run storage is later. The population is operator-set (`POLTIKA_POPULATION_PATH`), never caller-supplied, and a request naming one is rejected. `api/microsim_page.py`: `/analyst/microsim` with the seven tabs and the label on every tab. Checked in Chromium against a toy population: run, tabs, error display. 10.3 (release) waits on the real population and the Phase 9 cross-model checks. |
| 9.2 | Done: `tests/acceptance/test_v0_2_release_gate.py`, one test per exit-gate row on a toy population, including the plan's invariants (identity reform, no family tax credit loss from a higher threshold, out-of-scope households stay out, doubling weights doubles cost, AS unchanged). Writing it found a real generator bug: equal weights like 1000/300 were recurring decimals, so weighted totals drifted in the last digits. Weights are now six-decimal and sum exactly to `represents`. A committed spec under `data/metadata/populations/` is picked up by the gate's real-population row, which skips until 3.1-3.2 land. |
| 10.3 | Done, except the tag: `docs/releases/V0_2_LIMITATIONS.md`, the methodology page and CHANGELOG. The exit run reproduces: family tax credit +$130,098,302.73 a year over weight 444,485.48, AS 0.00, `verify()` clean, `results_sha256` stable on rerun. Pete confirmed on 27 September 2026 that GPT/Codex cleared every v0.2 row, and the release gate now passes with no skips of its own. **Ready for Pete to tag `v0.2.0`.** |
| 9.1 | Done. `scenarios/microsim/explain.py`. The run now records each overridden parameter with its baseline value, source and locator. The explanation covers the label, the assumed values and their baseline sources, what ran, cost by component with coverage (largest first), winners and losers, the top gaining household type, and why AS didn't move for a WFF-only reform. `verify()` recomputes every figure from the run and checks it appears in its sentence. |

## Sequence

| Sprint | Work |
| --- | --- |
| 1 | Phase 1, 2.1-2.2, 3.1 |
| 2 | 2.3, 3.2-3.4, Phase 4, Phase 5 |
| 3 | Phase 6, Phase 7 |
| 4 | Phase 8, 9.1-9.2 |
| 5 | 9.3-9.4, Phase 10 |

## Exit gate

In one reproducible run on the synthetic development population, with no
code edited, Poltika takes this scenario:

> raise the family tax credit abatement threshold from the 2026-27 value
> in `policy.yaml` to $50,000.

It produces:

- affected households, winners and losers;
- impact by income decile, household type and Accommodation Supplement
  area;
- the static entitlement cost by component;
- the Accommodation Supplement interaction (none, with the rule that makes
  it none);
- weighted coverage, including the `needs_review` share (R4);
- an explanation of the main drivers, with the governing rules and
  sources;
- the population's methodology and synthetic label;
- a reproducibility record whose rerun gives the same results hash.

Also:

- The invariant, hand-calculated and cross-validation checks in Phase 9
  pass or are explained.
- The v0.1 and v0.1.5 results and release-gate tests are unchanged.

Of the proposal's 20 questions:

- **Answered, for the synthetic population:** 1-13 and 15-20.
- **Answered as WFF and AS withdrawal rates only:** 14 (R3).

Real New Zealand estimates wait for D2.

## Open decisions for Pete

- **D1: Adopt ADR-0014?** It moves static microsimulation into v0.2 and
  the historical macro baseline into v0.3. Nothing later changes.
  Recommended.
- **D2: Microdata.** Synthetic only in v0.2 (recommended), or start a
  Stats NZ access process for real survey microdata now. That needs an
  approved project and can't be committed to this repository.
- **D3: Decile basis.** Which income ranks households? Recommended: gross
  household income from the population record, stated on every output.
  Equivalisation waits for a sourced scale.
- **D4: Tax year.** Build on 2026-27, with in-work tax credit coverage
  gaps reported, then add 2027-28 when v0.1.6 lands. Recommended.
- **D5: Network access** for Stats NZ and Treasury hosts, so calibration
  tables can be fetched here. Until then they're acquired outside.
- **D6: New dependencies** (Parquet, Polars, DuckDB) only if the Phase 7
  profile needs them. Recommended.
- **D8: Accommodation Supplement annual figures.** WFF results are per tax
  year and AS results per week. The runner never adds them. An annual AS
  or combined fiscal figure needs a stated annualisation method (a weekly
  amount times 52, or the number of weeks in the year). That is a
  methodology choice to record, not something to assume. Until it is
  decided, fiscal tables report AS per week, in its own column.
- **D9: A combined withdrawal rate.** WFF uses family scheme income, and
  the Accommodation Supplement chargeable weekly income. A single income
  path through both needs a stated mapping between those definitions,
  which is an interpretation question for the specifications. Until it is
  decided, withdrawal rates are reported per policy.
- **D7: Scope Doctrine wording.** `BUILD_PLAN.md` says sensitivity
  analysis is "deferred to v0.2". This plan does deterministic sweeps only.
  Ranges and distributions stay in v0.5. Record that here rather than
  editing the frozen text. Recommended.
