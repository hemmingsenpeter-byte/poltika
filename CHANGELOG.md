# Changelog

## Unreleased (MAP-01 fix; Pete's 13 October decisions on B4, Q19, Q2 and Q3)

- Household validation rejects overlapping benefit spells for one person,
  and the AS mapping refuses a week where a covering spell sits beside any
  other receipt (MAP-01, P2 from the #207 mapping review; decision log
  D37). Previously a whole-week `NO_BENEFIT` spell plus a one-day Jobseeker
  Support spell mapped to `NON_BENEFICIARY`. No fixture or calculated amount
  changes; a mid-week change of benefit still leaves the category unknown.
- Q19 (5): `to_wff` refuses a claimant or partner main-benefit spell inside
  the tax year when a whole-year no-benefit assertion (in-work eligibility,
  MC 6(b)) is verified. Dates only, nothing apportioned. In a combined pair the
  assessment-week spell stays with the existing per-component check, so every
  fixture result is unchanged.
- Q19 (1): the AS stock unit `NZD` has no period; `cash_assets` is the
  caller's balance for the assessment week. Q19 (2): the adapter's first-N AS
  child marking is labelled a round-trip device, not membership.
- B4: AS DEC-004 records that s 423(3) counts complete $100 steps, as the
  engine already does. The boundary proposal's B1–B3 notes are fixed.
- Pete's 13 October decisions are recorded (`docs/programme/2026-10-13-pete-approvals.md`,
  D38): Q19 and B4 move to Done; Q2 and Q3 stay parked with named triggers.
  No calculated amount changes.

## Unreleased (pilot data notice, research briefs, #213 review follow-ups)

- Web: a notice under the header on every page says the shared pilot holds
  synthetic or public non-personal data only, and that anyone with the login
  can see every stored scenario (PETE_QUEUE Q20; `docs/pilot/HOSTING.md`).
- `review_packets/research_briefs_20261012.md`: GPT/Codex briefs for Q2 (Māori
  data governance), Q3 (IDI access route) and Q19 parts 1, 2 and 5 (household
  mapping readings). They ask for sourced readings only, with no outreach or
  application.
- Q12 done: 91 merged remote branches were deleted after re-checking their
  tips, and 12 clean merged local worktrees were removed. PETE_QUEUE and the
  dated record now show what is done and what remains, including the Render
  setup found for Q15.
- #213 review P3s: current-state docs now show ADR-0018 as accepted, and a
  test covers a code change together with a population change. No
  calculated amount changes.

## Unreleased (Pete's 12 October 2026 decisions recorded; replay code identity)

- Pete's decisions on Q2–Q5, Q7 and Q9–Q22 are recorded in
  `docs/programme/2026-10-12-pete-approvals.md` and decision log D35–D36.
  Nine questions move to Done, ten carry their decision and the remaining
  action, and Q23 tracks the real-phone check of B0.1.6. ADR-0018 is
  accepted.
- Task 14 replay (Q21 (d)): `verify_manifest` decides `identical` or
  `drifted` from inputs and results only, and reports a different code
  identity as `ReformVerification.code_changed`. A new commit that reproduces
  every amount is `identical`. No calculated amount changes.
- `reviews/2026-10-12-q12-branch-verification.md` lists the 91 verified
  branches approved for deletion, with their tip SHAs.

## Unreleased (#211 review follow-ups and 360px re-measure, 12 October 2026)

- `POST /api/v1/scenarios/{id}/runs` maps a stored reform that no longer
  validates to the coded 503 `scenario_storage_unavailable` (it was a bare
  500), like the other retained-data sites; regression test added.
- Web, from a Chromium and WebKit re-measure at 360px: the Audit tab's run
  manifest notes wrap (a SHA-256 widened the page to 475px), and `summary`
  toggles are at least 24px tall. A source-link 24px test is added.
  `review_packets/review_queue.md` gains a GPT/Codex row for the WFF/AS
  boundary proposal. No calculated amount changes.

## Unreleased (batched follow-ups to #209 and #210, 12 October 2026)

- Task 14 follow-ups: tests for real-input drift, code-identity drift, an
  option-count mismatch, the results fallback and migration 0003 down/up over
  a 0002 row; a population id change is labelled `population_id` (it was
  `population_population_id`). `api/v1_scenarios.py` maps `ValidationError`
  to 503 only where retained data is re-validated (`_retained_data()`), with
  a regression test. Web: WCAG 2.2 SC 2.5.8 24px targets for the header link,
  provenance buttons, Technical-tab links and household radios, plus #209
  review tests. `review_packets/wff_as_boundary_cases_proposal.md` is an
  unreviewed proposal that adds no protected values. No calculated amount
  changes. Parked question: PETE_QUEUE Q21 (d).

## Unreleased (Task 14 reform run manifest and replay check, 12 October 2026)

- Task 14, first increment: `scenarios/reform_manifest.py` builds a typed
  manifest for each reform run (law baseline date, per-option reform and
  population identity, code identity, policy artifact hashes, overridden
  assumptions, units, limitations). Migration 0003 adds a nullable
  `reform_run.manifest_json`; `ScenarioStore.save_reform_run` stores it and
  `verify_reform_run` reruns the options and reports `identical`, `drifted`
  (naming what changed) or `not_retained` (a run stored before 0003; never
  backfilled). `POST` run responses carry the manifest and the audit tab shows
  it. The reform `run_id` hash inputs are unchanged (pinned by a test). No
  calculated amount changes. Parked questions: PETE_QUEUE Q21, Q22.

## Unreleased (web accessibility and responsive polish, 11 October 2026)

- Task B0.1.6: axe checks over Home and the empty, loading, error and
  unavailable states; the drawer's navigation landmark is named "Primary menu";
  larger touch targets below `md`, a wrapping header, a capped drawer and a
  scrollable chart region named after its metric (decision log D34); one-line
  explanations on empty states. No API, Python or calculated-amount change.

## Unreleased (CI fork guard and runner isolation runbook, 11 October 2026)

- Audit #191 A1: self-hosted CI jobs skip pull requests from forks, and a new
  hosted `fork-pr-gate` job fails them (decision log D33). Required check names
  are unchanged. `docs/programme/RUNNER_ISOLATION_RUNBOOK.md` describes moving
  the runner to a dedicated macOS user (Pete's action, Q13), and
  `docs/pilot/HOSTING.md` states what data the shared-login pilot may hold
  (Q20). Verification of A1–A7: `reviews/2026-10-11-audit-191-verification.md`.
  No calculated amount changes.

## Unreleased (household semantics and shared household model, 11 October 2026)

- Task 5: `semantics/unit_binding.py` binds every unit and period that a
  `policy.yaml` declares to the semantics registries, enforced by a test over
  every policy. `UnboundPolicyUnitError` names an unregistered unit or a
  cross-period use.
- Task 6 (ADR-0017 1.1–1.3): `semantics/household.py` and
  `scenarios/household_mappings.py`, a household with facts held once and dated
  spells, mapped to the existing WFF and AS scenarios. A spell is never scaled
  across periods. A round trip over the golden households and spec cases gives
  identical results and result ids.
- Task 12: a WFF/AS conformance matrix and 27 non-numeric API conformance tests.
- Review records for #193 (independent source review) and #195. No calculated
  amount, protected value or result identity changes.

## Unreleased (web Models/Data, accessibility, charts and deploy prep, 11 October 2026)

- Task B0.1.5: dataset detail pages show coverage (half-open period wording),
  units, geography and source; "used by" reads Not recorded because no model
  declares its datasets; the Source Archive state comes from the API
  (ADR-0022). Model detail gains a Status row. Both catalogues and both detail
  pages are tested.
- Task B0.1.6 (partial): full `jsx-a11y` lint, axe checks in Vitest on the
  Models, Data and scenario pages (colour contrast is not checked in jsdom),
  and an accessible SVG metric chart for calculated options (decision log
  D31). New dev dependencies: `axe-core`, `eslint-plugin-jsx-a11y`.
- Task B0.1.7 prep: `docs/web/FRONTEND.md`, the `POLTIKA_DATABASE_URL` step in
  `docs/pilot/HOSTING.md`, and a PostgreSQL restart-persistence test. No
  deployment. No calculated amount, protected value or result identity changes.

## Unreleased (web scenario experience, 10 October 2026)

- Task B0.1.4: the public OpenAPI request-body schema names for the legacy
  `/scenarios`, `/wff/calculate` and `/household/calculate` endpoints change to
  Pydantic's `*-Input` variants (`Reform-Input`, `Override-Input`,
  `OptionRequest-Input`, `CreateScenario-Input`, `WffCalculationRequest-Input`,
  `AsCalculationRequest-Input`, `HouseholdCalculationRequest-Input` and
  `VerifiedIncomeRequest-Input`), because `Reform` is now also returned. Request
  shapes are unchanged: each `-Input` schema equals the previous one once the
  names are normalised. No calculated amount changes.

## Unreleased (Dependabot paused, 10 October 2026)

- `.github/dependabot.yml`: `open-pull-requests-limit: 0` for all three
  ecosystems, at Pete's instruction (decision log D27). Version-update PRs stop
  until the limits are restored. Tooling only; no calculated amount changes.

## Unreleased (campaign-policy and NZ Budget analysis roadmap, 9 October 2026)

- Documentation-only product-scope refinement under the sole ADR-0021 master
  programme: C14a verified claim-to-scenario intake, optional D16a
  campaign-policy household pilot, F24a repeatable NZ Budget analysis using
  validated representative fiscal/distributional reporting, and I29a
  historical Budget as-of replay. Public/research presentation stays at
  O 51; no party/plan ranking, automatic statutory promotion or LLM numerical
  authority. See [use-case specification](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md).
- Updated ROADMAP, PROGRAMME_STATUS, frontend supporting plan, architecture,
  repo map, README and decision record. No engine, source value, database
  migration, API or runtime capability changed; no release/pilot gate is met.

## Unreleased (web shell, 7 October 2026)

- Task B0.1.3 (ADR-0023): `web/`, the first web frontend. Next.js (App Router,
  TypeScript strict, Tailwind) built as a static export and served by FastAPI
  from the same image (`api/web.py`, `POLTIKA_WEB_DIR`): Home with a search over
  the supported analyses, Scenarios, Models and Data pages, declarative
  navigation behind capabilities, central formatters and shared loading, error,
  empty and unavailable states. Types are generated from the API's OpenAPI
  document (`scripts/development/dump_openapi.py`); CI fails on drift. The
  Dockerfile gains a Node build stage, CI a `web` job, `security.yml` an
  `npm audit` and Dependabot the npm ecosystem. A `GET` is answered with a page
  only when its `Accept` header prefers `text/html` on a declared UI route; API
  clients and every existing route are unchanged. No calculated amount, protected
  value or result identity changes.

## Unreleased (passive source-preservation archive, 6 October 2026)

- ADR-0022 and `src/poltika/data/acquisition/`: a passive,
  content-addressed archive of what authoritative sources published, starting with
  Stats NZ (`scripts/ingest/stats_nz.py`, `data/source_archive/`). Exact bytes,
  canonical source metadata and one record per retrieval, with content and metadata
  change detected independently; optional advisory OpenRouter enrichment, stored
  apart and marked non-authoritative. Evidence only: nothing in the governed data
  path reads it, `DatasetManifest` and `DatasetRegistry` are unchanged, and no
  calculated amount, protected value or result identity changes. Programme Step 27 is
  not started or complete.

## Unreleased (programme migration, 3 October 2026)

- ADR-0021 establishes the economist-first, pilot-driven master build order;
  ADR-0019 sequencing is superseded while compatible principles remain.
- Exact historical planning snapshots, reconciled live status, agent instructions
  and household/maintenance lanes establish one active programme. Existing code,
  policy amounts, protected expectations, source/data snapshots and API semantics
  are unchanged. Release/pilot evidence remains distinct from implementation.

## Unreleased (v0.3: tax, benefits and the household graph)

See `BUILD_PLAN_v0_3.md`. No calculated amount, protected expected value or
result identity changes.

- **Exact unit rescaling:** retain every Decimal digit regardless of the caller's precision; refuse a repeating or non-finite result instead of rounding.

- **Entities and identifiers** (Programme Task 2.4): `semantics/entities.py`
  defines the seven entity types, an identifier scheme registry (household
  IDs from the existing validator; person, family, firm and sector unassigned
  with reasons; Crown and New Zealand fixed IDs) and `Population` definitions.
  No amount changes.

- **Mechanical never-build checks** (Programme Task 1.6, and the test part of the interim rule P5): release-gate tests that every population result carries its label, no output schema scores or ranks a party or plan, no user-facing page claims an unreached milestone, and no output is disaggregated by ethnicity or iwi. The validation-grade row skips until grades exist (Task 7.2). Tests only; no amount changes.
- **Conditional-summary corrections** (independent review of #128): preserve
  exact Decimal amounts, distinguish evidenced exclusions from missing model
  coverage, describe only evaluated cases and retain branch-limit caveats.
  Verification checks the complete fixed sentences and figure inventory.
  Analyst range wording follows the same certainty limit. Review findings
  remain open until the follow-up is accepted and integrated.

- **Delegated acceptance** (ADR-0020): Claude Code accepts and merges
  engineering work under three tiers; Tier C decisions stay with Pete in
  `PETE_QUEUE.md`, and Tier A and B decisions are logged in
  `docs/decision_log.md`. Merges are squash merges.
- **Programme status** (ADR-0020): `PROGRAMME_STATUS.md` tracks every programme step and task with status, owner, PR and blocker; `BUILD_PLAN_PROGRAMME.md`'s Progress table points to it.
- **Supply-chain, security and link checks** (ADR-0020): Dependabot (uv and
  GitHub Actions, weekly, grouped), `pip-audit` of the locked dependencies,
  Bandit for Python (high-severity gate, every finding retained) and zizmor
  for actions (all findings gate), with immutable action pins and read-only
  report execution, an offline lychee check of markdown links and anchors, and the
  source-currency report now runs on pull requests (report only). CI only; no
  amount changes.
- **Governance files** (Tier A, docs): `.github/CODEOWNERS`, `SECURITY.md`,
  `CONTRIBUTING.md`, issue forms under `.github/ISSUE_TEMPLATE/` and
  `docs/releases/RELEASE_CHECKLIST.md`. No amount changes.
- **Units and price bases** (Programme Task 2.2): `semantics/units.py` gives
  every unit a dimension, scale and price basis, rescales by scale only, and
  refuses any other conversion (nominal to real) without a named, sourced rule.
  `PriceBasis` moves there and is still importable from `variables.py`.
- **Time periods** (Programme Task 2.3, `semantics/periods.py`): period types
  (tax year, assessment week, quarter, calendar year, point in time, year ended
  June), a frozen half-open `Period`, and named period relations with sources.
  The AS week inside the WFF year is registered; annual/weekly value conversion
  is refused (v0.2 D8). No amount changes.
- **Analyst workbench backend** (ADR-0018, proposed): `GET /workbench/registry`
  lists every instrument under `policy_specs/` with its parameters (current
  value, unit, effective dates, review status), sources and decisions, so a
  new instrument spec appears with no code change (it is runnable only if the
  engines model it). `POST /workbench/check` shows what each override of a
  reform would do, or why it is refused, before a run. `POST /workbench/results`
  runs one or two options against the status quo and returns a headline and
  Fiscal, Households and Assumptions & provenance tabs as generic table blocks;
  `POST /workbench/export.xlsx` and `/workbench/export/{table}.csv` write the
  same blocks, with the run ID on every sheet. No amount changes. Nothing is
  added across units, the in-work tax credit stays `needs_review`, and there is
  no total row. Worked examples run the golden households under a reform
  (`scenarios/microsim/worked_examples.py`). Adds `openpyxl`.
- **Hosted pilot, password protected**: the pilot image refuses to start
  without `POLTIKA_ACCESS_PASSWORD`, then asks for it on every page and
  route (HTTP Basic; `/healthz` stays open for health checks). It listens
  on `$PORT` and includes the synthetic development population. Hosting
  steps are in `docs/pilot/HOSTING.md`. Local runs from a checkout are
  unchanged.
- **Hosted pilot, hardened for outside use**: every response carries
  security headers; request bodies over 64 KiB get 413; and population
  runs are computed one at a time (429 while busy).
- **Fact catalogues** (Task 1b.1, ADR-0016): every fact the WFF, AS and
  combined engines can report missing has a plain-language question and
  its admissible answers, in `policy_specs/<policy>/facts.yaml`. The
  wording was reviewed by GPT/Codex in PR #109.
- **Conditional answers** (Task 1b.2, first part): a household with
  missing yes/no or category facts gets engine-computed branches ("if X,
  then …"), ranges per component, and the most useful next question,
  instead of a bare `needs_review`. The blocked result itself is
  unchanged.
- **Intake planner** (Task 1b.4, `scenarios/intake.py`): before a run, it
  returns the next question for the components asked about (`ask`),
  `ready`, or `incomplete` when only declined facts block. Answers are
  checked against the catalogue and typed as the engine field requires.
  "Don't know" is a declined fact, never a default. Removing any fact from
  a golden household and answering the planner's questions restores that
  household's exact result.
- **Questions first, in the API and the analyst page** (Task 1b.5):
  `/household/calculate` adds a `resolution` when a component is waiting
  for a fact: each possible answer's result, the ranges, and the most
  useful next question. `POST /household/intake` returns the next
  question, `ready`, or `incomplete`, with the calculation so far. The
  analyst page's "Ask me first" asks one question at a time, with a
  "Don't know" that leads to the conditional answer.
- **Numeric ranges** (Task 1b.2b): a missing amount or count can be given
  a range. The household is rerun at both ends, and a component's range
  is labelled true bounds only where the fact catalogue declares it
  monotone in that fact, with a rule id; otherwise it is values at those
  points. No catalogue declares monotonicity yet: that is specification
  content for GPT/Codex. Property tests check declarations against the
  engine.
- **The conditional answer in words** (Task 1b.2d): "Poltika can't give
  one figure without …", then each possible answer's amounts, the ranges
  and the next question. Every figure is checked against the calculation
  before it is shown. A v0.3 release-gate test starts with the check that
  every shipped question catalogue has reviewed wording (Task 1b.1c).
- **Population ranges** (Task 1b.6): a population run now reports, beside
  the calculated totals, the range of change from households waiting on a
  fact (each possible answer rerun under the baseline and the reform) and
  the weight that can't be bounded. The three are never added. The run's
  identity and calculated totals are unchanged.

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
- **Synthetic population generator** (Tasks 3.3-3.4): a seeded,
  deterministic generator from a spec in which every New Zealand quantity
  and every asserted fact is an explicit input, with a calibration report
  and the synthetic label.
- **Stats NZ calibration data** (Tasks 3.1-3.2, #111): five Stats NZ
  snapshots with manifests, four registered transformations and 54
  canonical variables.
- **The synthetic development population** (Task 3.3, #113):
  `data/metadata/populations/nz_synthetic_development.v1.yaml`, derived by
  `scenarios/microsim/calibration.py` from those variables, never
  hand-written. Every rule (D1-D7) and assumption (A1-A11) is in its
  `sources` and `docs/releases/V0_2_POPULATION_METHODOLOGY.md`. On it, the
  exit scenario (family tax credit abatement threshold raised to $50,000)
  gives a static full take-up family tax credit change of $130.1m a year
  over 444,485 weighted households, with AS unchanged and the in-work tax
  credit `needs_review`.
- **Cross-validation** (Task 9.4, #114): the baseline against Inland Revenue's
  WFF statistics and MSD's Benefit Fact Sheets, read with a standard-library
  xlsx reader. `docs/releases/V0_2_CROSS_VALIDATION.md` reports each ratio
  with its reasons; nothing is tuned.
- **Population API and page** (Tasks 10.1-10.2): `/microsim/population`,
  `/microsim/parameters`, `/microsim/runs` and `/analyst/microsim`, over
  an operator-set population file. The page shows Overview, Distribution,
  Households, Areas, Fiscal, Evidence and Methodology tabs, with the
  synthetic label on every one.
- **Release documents** (Task 10.3): `docs/releases/V0_2_LIMITATIONS.md`
  and the methodology page.
- **v0.2 release-gate test** (Task 9.2): one test per exit-gate row,
  including the invariants. Equal synthetic weights are now exact to six
  decimal places and sum to the total represented, so weighted totals are
  exact.

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
