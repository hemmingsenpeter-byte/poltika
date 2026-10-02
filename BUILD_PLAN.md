# Poltika v0.1 Build Plan

**Date:** 20 September 2026
**Status:** FROZEN — workflow and roadmap discussion closed. Each task's
progress is recorded under it below; README.md's Current status says where
v0.1 stands.

---

## Roles

**Pete** — scope owner, final acceptance judge, decision-recorder for genuine
interpretation ambiguity (not a legal authority; draws on GPT's sourced research),
confirms discrepancy classification, manual message-bus between GPT and Claude
Code for all of v0.1 (not automated yet, by design).

**GPT (architect / source-grounded specifier)** — gathers and interprets primary
sources, drafts policy.yaml + specification.md, leads POLICY_SPECS schema design,
supplies interpretation research for ambiguity decisions, drafts the IP/provenance
ADR.

**Claude Code (repo-aware implementer / critic)** — repo-feasibility review of
schema, installs CI protection before implementation begins, builds each policy's
vertical slice, logs decision artifacts, assembles review packets.

**Fresh-context reviewer** — rotates between whichever model didn't do the work,
ideally a fresh session regardless. Given sources + spec + code + tests, never the
implementer's explanation. Independently derives expected behaviour before
comparing.

**Primary sources** (Acts, IRD/MSD/Treasury, published worked examples) — the only
ground truth. Neither model is authoritative on policy correctness.

---

## Development Doctrine (frozen)

primary sources → independent specification → implementation → independent
benchmarks → adversarial review → classified disagreement → documented resolution

---

## IP Doctrine (frozen)

Primary sources first. Independently derive implementation and tests before
looking at OpenFisca Aotearoa or any other prior art — with one narrow, explicit
exception: during Week 0 schema design (Task 3), after primary-source mapping
(Task 2) is done, a structural-only glance at OpenFisca Aotearoa is permitted
strictly to inform POLICY_SPECS entity/parameter shape. This exception never
extends to policy values, eligibility rules, abatement logic, or any
implementation detail, and never substitutes for Task 2's independent mapping.

Separately, and only after the WFF test suite is complete, inspect external
projects for structural/coverage concepts (categories only — e.g. what entities
or parameter types they found necessary), never for implementation or copied
values. Any gap found this way sends you back to primary sources to
independently derive the missing test. Log a one-line ADR confirming this
sequence was followed for both touchpoints.

---

## Data Acquisition Doctrine (frozen)

v0.1 depends on authoritative external data (Stats NZ, Treasury, IRD, MSD,
etc.), not on any live statistical API. The acquisition mechanism is
replaceable; the canonical data contract is stable:

authoritative source → manual acquisition → immutable/versioned raw snapshot
→ transformation + validation → canonical Poltika variables → simulator →
Assurance

Only the minimum datasets a given vertical actually needs are acquired — not
a full agency catalogue. Each raw snapshot carries full provenance (source
organisation, dataset/series, source URL/identifier, retrieval date,
observation/reference period, units, geography/population, retrieval method,
raw snapshot/version, transformation/version, canonical variable mapping).
v0.1's retrieval method is `manual_download`; a later `stats_nz_api` method
replaces it without changing the canonical variable or simulator interface.
The simulator never depends on a source-specific representation (API
response, CSV structure, endpoint) — only on canonical Poltika variables.
This is parameterisation/calibration from versioned data, not "training";
the LLM layer never memorises or calculates these values.

Frozen v0.1 datasets are also regression fixtures — same scenario + same
snapshot must yield the same deterministic result — and this lives inside
the existing Assurance/provenance architecture, not a parallel system.
Automated ingestion (Stats NZ API connector, scheduled refreshes, further
government-source connectors, schema-change detection, broader dataset
coverage) is a post-v0.1 capability-driven addition, not pinned to a version
number, that must slot beneath the same transformation/canonical/simulator/
Assurance layers unchanged.

---

## Scope Doctrine (frozen)

Deterministic correctness before probabilistic sophistication. No Monte Carlo,
no sensitivity analysis in v0.1 — deferred to v0.2.

---

## Architecture Doctrine (frozen)

Build the minimum abstraction demanded by two real policies (WFF + Accommodation
Supplement). Let implementation break POLICY_SPECS v0.1 and drive it to v0.2.
Do not prematurely design a universal policy DSL.

---

## Test Doctrine (frozen)

Three classes:
- **Spec tests** — hand-calculated from POLICY_SPECS, protected.
- **Regression tests** — prevent previously-working behaviour from changing.
- **Benchmark tests** — checked against independently published IRD/MSD/Treasury
  worked examples. This is what prevents AI-on-AI validation from being the only
  check.

Statutory expected-value changes are identified in PR CI, sourced, tested, and
reviewed before Pete merges — not changed to make a test pass. The mechanism
protects the *intent* — statutory expected values specifically — not every
numeric literal in a test file, and it is visibility plus independent review,
not a GitHub-enforced merge gate (see ADR-0007, which supersedes ADR-0005).
Claude Code determines the cleanest implementation (e.g. protected
benchmark/spec fixtures, or explicitly tagged statutory assertions) during
Tasks 7/9; this is an implementation decision, not an architectural one.

---

## Review Doctrine (frozen)

Disagreements are classified, not treated as pass/fail:
CODE_ERROR, TEST_ERROR, SPEC_ERROR, SOURCE_CONFLICT, INTERPRETATION_AMBIGUITY,
MISSING_SOURCE, ARCHITECTURE_ISSUE, REVIEWER_ERROR.

CODE_ERROR / TEST_ERROR route straight back to Claude Code.
INTERPRETATION_AMBIGUITY routes to Pete, with GPT supplying grounding research.
Every resolved ambiguity is recorded as a decision artifact: what was ambiguous,
what evidence was considered, who/what decided, when.

---

## Roadmap Doctrine (frozen)

Superseded its original capability-sequence framing per ADR-0008 (2026-09-21),
and its later release sequences per ADR-0014 and ADR-0015. Since ADR-0019
(29 September 2026) the order is Pete's master build order: 33 steps with
Phase 0 foundations and eight delivery phases, with a permanent layer and
a validation gate at every stage. It is
defined in `BUILD_PLAN_PROGRAMME.md` (what exists against each step, tasks,
month targets, gates, releases and decisions) and summarised in `ROADMAP.md`.
This section states the order and the reasoning behind it, not the detail.

v0.1 (deterministic foundation) → v0.1.5 (evidence and explainability) →
v0.1.6 (keep v0.1 current) → v0.2 (static population microsimulation), all
unchanged. Then:

- **Phase 0, foundations:** epistemic constitution and model governance;
  National Variable Registry and common schemas.
- **Phase 1, executable New Zealand:** deterministic statutory kernel;
  Evidence Intelligence and evidence graph; legislation conformance suite;
  validation framework and forward prediction ledger v0.
- **Phase 2, population and fiscal effects:** household microsimulation
  engine; fiscal and shared accounting spine; Historical NZ State Store.
- **Phase 3, baseline New Zealand:** National Baseline Engine; uncertainty
  and sensitivity framework; Causal Evidence Library; Historical Validation
  Laboratory.
- **Phase 4, first national system model:** National State Transition
  Engine; Canonical NZ Scenario Library; priority domain models.
- **Phase 5, federated New Zealand:** Federated Model Graph; continuous
  state estimation; Synthetic Population Programme; spatial and physical
  twin.
- **Phase 6, decision intelligence:** cost-of-delay engine;
  value-of-information engine; policy-space search and inverse solver;
  Pareto frontier engine.
- **Phase 7, national decision infrastructure:** Public NZ Futures
  Laboratory; policy and manifesto analysis interface; constraint-based
  negotiation sandbox; research and institutional APIs.
- **Phase 8, AI scientific layer:** natural-language policy interface; AI
  hypothesis discovery; AI model orchestration; AI explanation and research
  agent; autonomous research loop, with human gates.

Releases are tagged at gates: v0.3 (Phase 0 and the kernel's first lane),
v0.4 (Phase 1), v0.5 (Phase 2), v0.6-v0.7 and v1.0 (Phase 3), v1.x-v2.0
(Phase 4), v2.x-v3.0 (Phase 5), v3.x-v4.0 (Phase 6), v5 (Phase 7), v6
(Phase 8).

**Why this order, not another (ADR-0019):** each phase answers a harder
version of one question: "If New Zealand changes X, what happens, to whom,
when, through what mechanism, with what confidence, and compared with what
alternatives?" In short: what are the rules → who do they affect → what do
they cost → how does New Zealand work → why do outcomes change → what
happens under different futures → where are we wrong → what information
are we missing → what feasible choices exist → what are their trade-offs.

- **Foundations first.** The constitution, model governance and the
  variable registry come before further modelling, so every later model
  shares one meaning for each variable, unit, period, population,
  geography and identifier, and every quantity carries its value,
  uncertainty and evidence: X = (x̂, D_x, E_x).
- **Proof before impressive models.** The conformance suite, the
  validation framework and the prediction ledger are in Phase 1, so the
  external track record starts early.
- **Observed state before projection.** Accounts and a historical state
  store come before the baseline, and the baseline before causal claims
  about the future.
- **An integrated system before sophisticated parts.** A simple state
  transition engine runs New Zealand forward before domain models replace
  its parts, and each domain earns integration through validation.
- **A digital twin is earned, then used.** Poltika is called an
  operational national digital twin only at Phase 5's milestone. Decision
  intelligence follows it.
- **Value of information before search.** Poltika says when an answer
  hinges on poorly evidenced parameters before it searches large policy
  spaces, and it shows feasible trade-offs, never a single optimal answer.
- **Public infrastructure, then AI.** Only after the machinery has earned
  trust. AI operates the instrument; it is never the instrument.
- **The permanent layer throughout:** evidence and provenance, validation
  and benchmarking, forward prediction scoring, uncertainty and model
  risk, versioning and reproducibility, Māori data governance, privacy and
  security, human oversight, and model governance.
- **Every stage has a validation gate.** Poltika doesn't move from "built"
  to "trusted" because the code works.

Discovery and Hypothesis are the causal library's intake (Step 12), with AI
hypothesis discovery at Step 30, under the unchanged promotion gate
`Discovery → Hypothesis → evidence → validation → human approval → model
specification → tests → Simulator`. The Stats NZ API connector and
equivalents are pinned to Step 9, the historical state store, which first
needs them. Automation still follows real need.

**v1.0 definition (testable, not aspirational):**
Phase 3's milestone. For a structured package of changes inside its
supported kernel domains, Poltika v1.0 answers what happens (static, and
behavioural where the causal library holds a classified relationship), to
whom (by decile, household type, area and age on a graded population), when
(year by year, through the Crown accounts, against the national baseline),
through what mechanism (the evidence-graph chain to law and evidence), with
what confidence (evidence classes, propagated uncertainty, the population
grade, validation status, replay errors and the prediction ledger's
record), and compared with what alternatives (the baseline and other
scenarios). An independent analyst can reproduce and challenge the result
without the builders.

A "supported domain" has an approved specification, a complete
conformance matrix, an independent review and current values
(`BUILD_PLAN_PROGRAMME.md`).

**North star (not a release gate):** New Zealand's open, evidence-linked
policy intelligence infrastructure: a computational representation of how
policy, people, businesses, government and physical systems interact, used
to test interventions, discover trade-offs and learn from what actually
happens. People choose the objectives; Poltika measures consequences.

---

## Task List

### Week 0 — Policy Representation
1. Gather primary sources: WFF + Accommodation Supplement (legislation,
   regulations, IRD/MSD operational material, current parameters, official
   worked examples, effective dates). Record the dated Task 1 inventory in
   policy_specs/working_for_families/sources.yaml and
   policy_specs/accommodation_supplement/sources.yaml; Task 2 verifies and maps
   these sources before any policy rules or benchmark values are adopted.
2. Independently map both policies from source. Completed 21 September 2026:
   source-grounded rule, exception, effective-date, and cross-policy maps are in
   policy_specs/working_for_families/specification.md and
   policy_specs/accommodation_supplement/specification.md. Their Task 10/22
   review gates remain prerequisites for implementation, not Task 3 blockers.
3. Inspect OpenFisca Aotearoa's structural concepts only (not implementation) —
   the narrow pre-suite exception in IP Doctrine; schema shape only, after
   Task 2's independent source mapping is complete. Completed 21 September
   2026; the bounded inspection and Task 4 handoff are recorded in
   docs/research/task_3_structural_glance.md. The separate broader comparative
   review is not Task 3 or Task 16; ADR-0004 records its one-off timing
   decision and does not replace the later Task 16 check.
4. Derive minimal POLICY_SPECS v0.1 schema from both policies' actual
   requirements, including provenance fields for any external statistical
   datasets used (source organisation, dataset/series, source URL/identifier,
   retrieval date, observation/reference period, units, geography/population,
   retrieval method, raw snapshot/version, transformation/version, canonical
   variable mapping) — see Data Acquisition Doctrine. Completed 21 September
   2026 as a design draft in policy_specs/SCHEMA.md; Task 7 reviewed
   feasibility, not policy content approval.
5. Establish file structure: policy.yaml, specification.md, sources.yaml,
   benchmarks.yaml, spec_cases.yaml (ADR-0005 — hand-calculated spec-test
   expected values, loaded by Task 13 tests rather than hardcoded),
   decisions/*.md. Completed 21 September 2026 as unapproved scaffolds in
   both policy directories; no statutory expected values are recorded.
6. Version the schema itself (schema_version field), separately from policy
   version/effective dates. Completed 21 September 2026: both policy.yaml
   scaffolds declare schema_version "0.1" and leave policy_version null;
   legal effective dates remain distinct in the schema draft.
7. Claude Code repo-feasibility review of the schema; determine the concrete
   mechanism for statutory-value CI protection. Completed 21 September 2026:
   schema reviewed feasible in policy_specs/SCHEMA.md's Task 7 response.
   Original CI mechanism decided in ADR-0005 (CODEOWNERS + branch
   protection); not available on the repo's plan during Task 9, and
   superseded by ADR-0007 (PR visibility + Pete's review before merge,
   without CODEOWNERS or required review). ADR-0005 stays as the
   historical record; ADR-0007 is current.
8. Write IP/provenance ADR. Completed 21 September 2026: Pete accepted
   ADR-0006, linking ADR-0001/0003/0004 to the source-to-calculation
   provenance chain.
9. Install statutory-value visibility per ADR-0007. `.github/CODEOWNERS`
   removed (implied an enforcement the plan can't deliver — a false
   signal). `.github/workflows/statutory-value-guard.yml` kept and fixed
   (diffs from the actual merge-base, not a possibly-stale `base.sha`) as a
   visibility-only PR check, not a merge block. First attempt (test PR #3,
   21 September 2026) found the workflow didn't run at all — likely an
   account-level GitHub Actions hold, not a workflow bug, though GitHub
   never confirmed the cause directly. After Pete upgraded to GitHub Pro,
   PR #4 (opened independently by GPT/Codex) confirmed the underlying
   detection logic works — the workflow ran and correctly identified the
   changed `benchmarks.yaml` path — but PR #4 closed before its check run
   started, so that only proved detection, not that the warning is visible
   in time to inform a merge decision. Codex's review of PR #4 caught this
   distinction. **Closed 21 September 2026** after a follow-up test (PR
   #5) kept deliberately open until the check appeared: it went
   pending → pass while the PR was still open, and its annotation ("This
   PR changes protected statutory-value files...") was visible on the open
   PR before it was closed unmerged — confirming visibility-before-merge,
   not just detection. Pro also unlocked GitHub branch protection;
   enabled the baseline (no force-push, no branch deletion on `main`) but
   deliberately did not reinstate CODEOWNERS/required-review — Pete's
   explicit choice to stay with ADR-0007's visibility-plus-judgment model
   rather than silently reverting to ADR-0005 now that it's technically
   possible again. The operating rule stays manual: look at the PR diff and
   the guard workflow's result before merging.

### Weeks 1–2 — WFF Vertical Slice
10. Complete WFF policy.yaml + specification.md from source. Source-linked
    draft merged 21 September 2026 (PR #6) as a reviewed draft — `status:
    draft_pending_review`, `policy_version: null` — per Pete's explicit
    decision that merging a draft does not clear it for calculator
    implementation. Independent review found and the author fixed three
    issues pre-merge (complete-dollar abatement truncation, a missing-input
    status conflict, an interval/note contradiction on the temporary
    in-work rate); confirmed correct against full Act text, not just IRD
    guidance, for MD 1/3/10/13 and ME 1/3. Claude's subsequent full-text
    pass (commit `ad1a9a2`) checked MD 4-9/14 and MG 1-4. Pete accepted the
    narrow v0.1 input domain on 21 September 2026. Follow-up PR #8 records
    further checks of the 2025 rate Order and Budget Measures Act, Tax
    Administration Act s 80KW's extra-instalment exception, MG 4's protected
    Best Start boundary, MC 6(c)'s same-child payment exclusions, and
    correction of the repealed MB 14 inventory row.
    PR #8 independently reviewed (all four highest-risk new claims —
    s 80KW, the MB 14 repeal, MB 13's $5,000 exception, MC 6(c) — confirmed
    against full statute text, not just cited) and merged 21 September 2026
    as a further reviewed draft, `e67ae56`. PR #9 completed the MB/MC
    source-audit draft and was independently reviewed with no discrepancies
    in the provisions checked; Pete accepted its merge as a reviewed draft
    on 21 September 2026 (`038abfb`). PR #10 completed the source-linked
    calculation draft; PR #11 completed the temporary-rate contract and
    whole-spec independent review. Pete accepted the reviewed PR #11 revision
    (`bf70d1b`) on 21 September 2026. The scoped WFF specification is now
    `status: approved`, `policy_version: "0.1.0"`; Task 10 is complete.
    Approval does not clear `in_work_base`'s `needs_review` status or permit
    an unconditional full-year in-work result for an unverified interval.

    Task 10 closure subtasks (distinct from data Tasks 10a/10b):
    - **10.1 Statutory calculation contract — GPT/Codex.** Check the
      supported full-year MD/ME/MG/MF ordering, intermediate rounding, and
      protected-credit boundaries against dated primary text. Record each
      exact rule or an explicit `unsupported`/`needs_review` outcome in the
      source-linked draft. Done when no in-scope formula relies only on
      agency guidance or an unstated rounding/exception assumption. Author
      pass recorded 21 September 2026 in the Task 10.1 source/spec update;
      its interpretations were included in the independent review in 10.3.
    - **10.2 Temporary in-work rate — GPT/Codex.** Recheck the secondary-
      legislation register and specify the date-dependent treatment of the
      possible reversal Order. Done when `in_work_base` cannot silently
      produce a full-year result for an unverified interval; recheck again
      at implementation for each modelled date. Author pass recorded
      21 September 2026 in the Task 10.2 source/spec update; the official
      s 2 page showed no Order on that date, while the future interval remains
      unverified. The rate-status contract was independently reviewed in 10.3.
    - **10.3 Whole-spec independent review — Claude Code.** Derive the
      expected scoped behaviour from primary sources before reading the
      author response, then review the complete source map, policy draft,
      calculation sequence, status outcomes, and 10.1/10.2 diff. Classify
      discrepancies and return them for correction or Pete's decision.
      Done when findings are resolved and the reviewed revision is identified.
      **Done 21 September 2026** (PR #11, `docs/task10-temp-iwtc-rate`):
      no CODE_ERROR/SPEC_ERROR/SOURCE_CONFLICT found across the whole
      assembled document. One non-blocking finding recorded directly in
      `specification.md` — component-level exclusion conditions (MD 14/15,
      IWTC's direct-abatement pathway, ME 2(2)-(4), MG 4, s 80KW) are
      correct but prose-only and scattered; recommend giving each
      `policy.yaml` component a `validation_checks` list (per
      `ARCHITECTURE.md`'s module contract) when Task 12 starts, not before.
      Reviewed revision: PR #11 plus this review's own cleanup commit.
    - **10.4 Acceptance and release gate — Pete, with GPT/Codex drafting
      the approval change.** Pete accepts the supported domain, remaining
      unsupported cases, and any genuine interpretation decision after
      10.3. Only then assign `policy_version`, set `status: approved`, record
      the accepted revision and close Task 10. No calculator or statutory
      fixtures may consume the draft before this gate. **Done 21 September
      2026:** Pete expressly accepted the reviewed PR #11 revision and
      approved policy version `0.1.0` with its status outcomes intact.
10a. Identify the minimum authoritative external statistical datasets the WFF
    vertical actually needs (beyond the legislated rates already captured in
    sources.yaml/specification.md, if any) — GPT/Codex; manually acquire and
    freeze each as an immutable, versioned raw snapshot with full provenance
    (retrieval_method: manual_download) — Claude Code — see Data Acquisition
    Doctrine. **Complete 21 September 2026: no external statistical dataset
    required for WFF v0.1.** Every approved WFF rate/threshold traces to
    sourced legislation (Income Tax Act, the 2025 Tax Credit Order, amending
    Acts), not a Stats NZ/Treasury-style series; family-scheme income and
    eligibility are verified per-scenario inputs, not a shared dataset
    Poltika sources itself (`ARCHITECTURE.md`'s module contract already
    recorded "WFF has none identified so far" for `data_dependencies`). The
    dated in-work Order check is a policy-source verification, tracked via
    `sources.yaml`'s existing `order_check` provenance notes — not a reason
    to invent a statistical dataset or its own raw-snapshot machinery.
10b. **Not applicable to WFF — no action taken.** Building the
    transformation/validation layer now, with nothing to transform, would
    be exactly the premature abstraction Architecture Doctrine warns
    against. This task's actual construction is deferred to whichever
    policy first has a real snapshot to transform — expected to be
    Accommodation Supplement's Task 22a (Stats NZ Statistical Area Unit
    geography data), not built speculatively ahead of that need. Task 11
    is not blocked by this: WFF's parameter loader consumes `policy.yaml`'s
    already-approved parameters directly, which were never raw external
    data in the first place.
11. Build parameter loader (consumes canonical Poltika variables only, never
    a source-specific representation) — Claude Code implements, GPT/Codex
    gives fresh-context review (rotation reversed from Task 10: Claude Code
    is the author this time), Pete merges/accepts.
    - **11.1** Define the loader's interface to Task 12: requested policy,
      version, and modelled date in; typed parameter values or an explicit
      unresolved outcome out.
    - **11.2** Parse and validate `policy.yaml`: supported `schema_version`,
      `status: approved`, `policy_version`, units, source IDs, and
      non-overlapping effective intervals.
    - **11.3** Select values by effective date without silently substituting
      a missing interval or value.
    - **11.4** Preserve the `in_work_base` gate: `review_status: needs_review`
      must not yield an unconditional $7,670 value. Pass the dated
      Order-status requirement through to the calculator contract, not
      resolved inside the loader.
    - **11.5** Test valid, missing, overlapping, unapproved, and
      unresolved-rate cases; assemble the source/spec/diff/test review
      packet.
    - **11.6** Open the implementation PR for GPT/Codex's fresh-context
      review before Pete merges. **Complete, merged 21 September 2026
      (PR #13):** `src/poltika/policy/loader.py` +
      `src/poltika/semantics/schemas/policy_spec.py`, 24 tests (20 synthetic
      fixture cases plus 4 run directly against the real approved WFF
      `policy.yaml`, confirming `in_work_base` resolves to `needs_review`,
      never a silent $7,670). Two fresh-context review rounds from
      GPT/Codex found and Claude Code fixed five issues before approval:
      float used instead of exact `Decimal` for statutory amounts; no
      rejection of duplicate parameter IDs (would silently overwrite);
      `effective_to` wrongly required instead of schema-permitted
      open-ended; declared `source_catalog` ignored in favour of a
      hardcoded filename; and empty parameter value lists / free-text
      `value_type`/`unit` accepted instead of validated as closed,
      dimension-consistent enums per SCHEMA.md's Task 7 review response.
      Final GPT/Codex verdict: approved for merge, no remaining
      discrepancies. `pytest`/`ruff`/`mypy --strict` all pass.
12. Build pure `calculate_wff()` function. Add component-level
    `validation_checks` for the reviewed exclusion triggers identified in
    Task 10.3 (MD 14/15, the in-work direct-abatement path, ME 2(2)-(4),
    MG 4, and s 80KW); enforce the dated in-work Order status from sourced
    policy state, never a live network call from the deterministic core.
    **Complete 21 September 2026, PR #14 pending re-review:**
    `src/poltika/engines/simulator/wff.py` -- a pure function taking a
    `WffScenario` of canonical facts and a Task-11 `PolicyParameterSet`,
    returning per-component `calculated`/`needs_review`/`unsupported` with a
    reason for all four components (family tax credit, in-work tax credit,
    minimum family tax credit, Best Start); `total_annual_entitlement()`
    sums only when every component is `calculated`. `policy.yaml`'s
    `components[]` entries now each carry `validation_checks` naming their
    known exclusion triggers, closing the Task 10.3/10.4 obligation.
    GPT/Codex's fresh-context Task 12 review found three further issues,
    each independently verified against primary sources before fixing (see
    specification.md's "Task 12 fresh-context review findings" for detail):
    minimum family tax credit had no MC 6(b) check at all, though the
    official Act text (checked directly, 2026-09-21) confirms MC 6(b)
    excludes both in-work and minimum family tax credit; a Best Start child
    outside the narrow v0.1 birth cohort defaulted to a calculated zero
    instead of `unsupported`, though specification.md already said later
    cohorts "require separate review"; and a partnered household's
    `family_scheme_income` could be supplied as one unverified combined
    `Decimal` instead of going through specification.md's required
    per-person verification. All three fixed with dedicated types
    (`mc6b_disqualifying_payment`, `BestStartCohort`, `VerifiedIncome`) and
    targeted tests. A second re-review pass then found `VerifiedIncome`
    alone still couldn't distinguish a genuinely single claimant from a
    partnered claimant whose partner's income was never verified --
    `partner_amount is None` looked the same either way, so a partnered
    household could still produce a numeric result from the claimant's
    income alone. Fixed with an independent `PartnerStatus`
    (`SINGLE`/`PARTNERED`/`UNKNOWN`, defaulting to `UNKNOWN`) plus a
    `_partner_income_gap_reason()` check on family tax credit and Best
    Start. 70 tests (`tests/unit/engines/simulator/test_wff.py`, up from
    58): the ordinary full-year branch with hand-derived exact-decimal
    expected values (including the half-cent MD 13 case), every
    unsupported/needs_review trigger individually and in precedence
    combinations, the MD 2(2)(c) abatement-carryover interaction between
    family and in-work tax credit (including a caught-and-fixed bug where
    in-work tax credit would have silently assumed zero remaining abatement
    whenever family tax credit itself could not be calculated), the real
    approved WFF `policy.yaml`'s live `in_work_base` needs_review gate,
    rejection of structurally malformed negative income, and the
    missing-partner-income/unknown-partner-status cases above. A third
    re-review pass found `PartnerStatus.UNKNOWN` still let minimum family
    tax credit return a number, though specification.md's own text ties its
    MA 7 full-time-earner threshold to single (20 hours) vs partnered (30
    combined hours) status -- fixed with a direct `partner_status` check in
    `_minimum_family_tax_credit()`. 71 tests total, up from 70.
    `pytest`/`ruff`/`mypy --strict` all pass.
13. Build spec tests. **Complete, merged 22 September 2026 (PR #15):**
    `policy_specs/working_for_families/spec_cases.yaml`
    (`status: approved`) holds 23 independently hand-calculated cases
    per ADR-0005's design -- expected values loaded from this protected
    YAML file (one of `.github/workflows/statutory-value-guard.yml`'s
    watched paths), not hardcoded in Python. Each case's `source_note`
    records its by-hand derivation, computed via a standalone script
    separate from `wff.py` so the suite can actually catch an
    implementation bug rather than mirror one. Coverage: the ordinary
    full-year branch (1/2/4 children, partial/floored abatement, the exact
    half-cent MD 13 result), partnered combined income and the two
    partner-status gaps found during Task 12 review (missing partner
    income, unknown partner status), every household-wide gate
    (`eligibility_facts`, s 80KW), every component-specific exclusion
    trigger (MC 6(a)/(b)/(c), MD 14/15, ME 2(2)-(4), MG 4, shared care,
    in-work eligibility) individually, and the MFTC zero-at-threshold case.
    All cases run against the real approved `policy.yaml` via Task 11's
    loader; `in_work_tax_credit` is `needs_review` in most of them by
    design (the live `in_work_base` gate is a real legal fact, not a test
    gap) except where a higher-precedence exclusion already makes it
    `unsupported`. `tests/unit/engines/simulator/test_wff_spec_cases.py` is
    a thin loader/runner (no expected values in Python), parametrised one
    test per case, plus guard tests (non-empty file, unique IDs, and every
    case's `expected` block covering all four components) against a
    silently-truncated, duplicated, or incomplete fixture passing green.
    GPT/Codex's fresh-context review found two issues: the MD 14/15 case
    the coverage list claimed didn't actually exist in the YAML (fixed --
    `md14_15_protected_credit_excludes_ftc_and_iwtc_not_mftc_or_best_start`),
    and the runner only ever checked whichever component keys a case's
    `expected` block happened to include, so an incomplete block would
    have passed silently (fixed with the completeness guard above). A
    third pass caught the coverage note above understating the
    `in_work_tax_credit: unsupported` count as two cases when it's
    actually six; corrected in specification.md and this file. 96 tests
    total (up from 71). `pytest`/`ruff`/`mypy --strict` all pass. Pete
    recommended acceptance and delegated the final accept decision to
    Claude Code, which re-verified all of the above immediately before
    setting `spec_cases.yaml`'s `status: approved` -- see
    specification.md's "Task 13 acceptance" note.
14. Build benchmark tests (against independently published IRD examples).
    **Complete, merged 22 September 2026 (PR #16):**
    `policy_specs/working_for_families/benchmarks.yaml` (`status:
    approved`) holds 9 cases drawn from the four IRD pages
    `sources.yaml` already names as benchmark candidates (family tax
    credit, in-work tax credit, minimum family tax credit, Best Start),
    fetched directly (browser user agent, since a bare fetch 403'd) on
    2026-09-22. Every numeric `expected` value is copied verbatim from
    IRD's own stated worked-example result -- the opposite discipline from
    Task 13's spec_cases.yaml, where every value was self-derived; here the
    whole point is a third-party number, confirmed to be stated for
    2026-27 rates and as an annual (not weekly/fortnightly) figure before
    use. `tests/unit/engines/simulator/test_wff_benchmarks.py` is a thin
    loader/runner, plus guard tests (non-empty file, unique IDs, every
    `ird_source` resolves to a real `sources.yaml` entry, and the same
    all-four-components completeness check PR #15's review established for
    spec_cases.yaml).

    5 cases are numeric matches against a real published figure: Sarah's
    full family tax credit (2 children, no abatement), Jaimee's in-work
    tax credit (5 children, confirming the beyond-three-children $780
    formula against a real example), and three minimum family tax credit
    cases (Jeremy, Casey with mixed self-employment-plus-salary income, and
    Casey's later zero-entitlement example when her income rises mid-year
    above $36,604). 4 cases are scope-boundary demonstrations -- a real
    published scenario where the correct answer, per the already-reviewed
    v0.1 domain, is `needs_review`/`unsupported`, not IRD's stated number:
    Rahui and Claire & Laura's partnered examples give only a combined
    family income, never each partner's individually verified amount
    (demonstrating the Task 12 PR #14 partner-verification fix against a
    real example, not a self-authored one); Brooklyn's example is the
    direct-abatement pathway specification.md marks unsupported in v0.1;
    the Faraj family's example has a child (Azra) IRD states was born
    1 June 2026, partway through the 2026-27 tax year -- she does not
    qualify for the whole tax year, so the household gate makes all four
    components `unsupported`, not only Best Start as an earlier revision
    claimed (PR #16's second review round). Casey's self-employment-plus-salary eligibility was
    initially assumed out of scope by loose analogy with
    specification.md's own in-work tax credit domain paragraph (a v0.1
    scope decision, not an IRD rule -- IRD's in-work tax credit page
    itself says self-employment income qualifies); re-reading
    specification.md's minimum family tax credit domain paragraph directly
    showed no such exclusion exists there, so it was promoted to an
    in-scope case instead of dropped. All cases run against a synthetic
    fixture (real approved rates, but every parameter including
    `in_work_base` marked approved), the same design Task 12's
    `test_wff.py` already established, so the live rate-status gate
    (already covered by Task 13) doesn't mask whether a scope-boundary
    case is correctly excluded for its own, scenario-level reason. 108
    tests total (up from 96). `pytest`/`ruff`/`mypy --strict` all pass.
    **GPT/Codex's fresh-context review found three further issues, fixed
    2026-09-22:** several cases marked household-level exclusion-trigger
    facts `verified` without the cited IRD text stating them, while the
    header overclaimed everything uncovered was left unverified -- fixed
    with an explicit per-case `assumed_facts` list and a renamed
    `conditional_arithmetic_match` outcome kind, making clear these are
    conditional arithmetic checks, not unconditional verified entitlements
    (see specification.md's "Task 14 fresh-context review findings" for
    full detail); the Jaimee in-work tax credit case didn't flag that its
    own benchmarked rate is itself the live, unresolved Task 10.2 legal
    question; and two provenance statements were corrected (the "every
    value copied verbatim" claim, and the same self-employment
    misattribution above). A second review round then caught the Faraj
    whole-year-domain error described above, plus three partnered cases
    (Rahui, Claire & Laura, Faraj) that had put a published household
    income directly into `family_scheme_income.claimant_amount`,
    misrepresenting it as one person's individually verified amount --
    fixed to `family_scheme_income: null` in all three, the honest
    representation given neither partner's individual amount is actually
    known. Pete recommended acceptance and delegated the final accept
    decision to Claude Code, matching Task 13's pattern -- see
    specification.md's "Task 14 acceptance" note.
15. Build regression tests, including the frozen dataset-snapshot fixtures
    from Task 10b: same scenario + same snapshot must yield the same
    deterministic result — Claude Code implements, GPT/Codex gives
    fresh-context review, Pete merges/accepts (same rotation as Tasks
    11-14). Task 10b was closed N/A for WFF (no external statistical
    dataset needed), so the dataset-snapshot half of this task has nothing
    to build yet for WFF; it applies once Accommodation Supplement's Task
    22a introduces a real Stats NZ snapshot. What WFF's Task 15 does own:
    doctrine/test-doctrine.md's "Regression tests for known historical
    issues" — this project already has a documented list of exactly that,
    from Tasks 12-14's own review cycles.
    - **15.1** Inventory the known historical issues to protect against,
      each traceable to the PR/finding that caught it: the MD 2(2)(c)
      abatement-carryover bug where in-work tax credit would have
      silently assumed zero remaining abatement (Task 12, caught before
      review); the Best Start false-zero bug conflating "outside this
      narrow branch" with "verified zero" (Task 12, PR #14 first
      re-review); the two partner-income-verification gaps -- missing
      partner income, and unknown partner status blocking minimum family
      tax credit specifically (Task 12, PR #14 second and third
      re-reviews); the missing MD 14/15 spec case and the spec-case
      `expected`-block completeness gap (Task 13, PR #15); and the
      benchmark-specific scenario errors -- a household income mislabelled
      as one person's individually verified amount, and a child marked as
      qualifying for the whole tax year despite a stated in-year birth
      date (Task 14, PR #16 second round).
    - **15.2** Decide where these live: a new `tests/regression/`
      directory (already reserved, unpopulated, in
      REPOSITORY_STRUCTURE.md's target tree) holding one test per named
      historical issue, distinct from `spec_cases.yaml`/`benchmarks.yaml`'s
      per-policy-question framing. Reuse the existing scenario fixtures
      from those two files where the same scenario already exercises the
      issue, rather than duplicating fixture data; construct a new,
      minimal, targeted scenario only where no existing case isolates the
      specific defect.
    - **15.3** Implement one regression test per issue from 15.1, each
      named after and docstring-linked to its defect and originating
      PR/finding, asserting specifically the behaviour that was wrong
      before the fix (not a restatement of the general spec/benchmark
      case).
    - **15.4** Confirm explicitly, in the test file or its documentation,
      that Task 10b's dataset-snapshot-fixture requirement is intentionally
      not addressed here for WFF, and is not a gap.
    - **15.5** Test until satisfied, self-review anticipating GPT/Codex
      flags, open the PR for fresh-context review before Pete merges.
      **Complete, merged 22 September 2026 (PR #17):**
      `tests/regression/test_known_historical_issues.py` -- 9 tests, one
      per issue from 15.1. 4 reconstruct the minimal scenario directly
      (the calculator-logic bugs, none of which spec_cases.yaml/
      benchmarks.yaml happens to isolate on their own); 3 load the real
      case by id from `spec_cases.yaml`/`benchmarks.yaml` and either
      re-run it through `calculate_wff()` (the MD 14/15 case, confirming
      it still exists and still exercises the trigger) or check the
      specific scenario field that was wrong (the two benchmark
      authoring mistakes, where re-running the full case would just
      restate Task 14's own suite); 2 call the real, currently-shipping
      `test_wff_spec_case()`/`test_wff_benchmark()` functions directly
      with a deliberately truncated case and require them to fail loudly
      -- exercising the actual shipped guard rather than a
      re-implementation of it. `tests/conftest.py` (new) holds the
      shared fixtures/helpers this needed, extracted once three other
      files had each already defined a near-identical version rather
      than write a fourth copy -- those three files are otherwise
      untouched. `REPOSITORY_STRUCTURE.md`'s "Instantiated today" section
      was also corrected: it still claimed "nothing under `src/`... or
      `tests/`... exists yet" and "v0.1 is still in Week 0", both stale
      since Task 11. 117 tests total (up from 108).
      `pytest`/`ruff`/`mypy --strict` all pass. GPT/Codex's fresh-context
      review found two further issues, fixed same day: the income-
      provenance regression checked only the Rahui case, asserting
      without verifying that Claire & Laura and Faraj had "the same fix
      applied identically" (fixed to check all three by id); and the
      `REPOSITORY_STRUCTURE.md` update claimed `docs/` was entirely
      undone, missing that `docs/research/` already held two files from
      earlier session work (fixed, with the target-architecture tree
      annotated to distinguish it from the still-hypothetical
      `docs/{data_model,...}.md` files). Pete recommended acceptance and
      delegated the final merge decision to Claude Code, matching Tasks
      13/14's pattern.
16. External coverage-gap check (OpenFisca test names, strictly after suite
    completion) — return to primary sources for any gap found. **Complete,
    merged 22 September 2026 for WFF (PR #18, ADR-0009):** per ADR-0004,
    independently included both OpenFisca Aotearoa (commit `9d77ea7`) and
    `PolicyEngine/policyengine-nz` (commit `fbd186b`) as comparators, not
    OpenFisca alone. Structural-only (pinned-commit directory/file names;
    no file contents, test logic, or values read) -- OpenFisca Aotearoa's
    `family_scheme` test directory lists `best_start`, `eligibility`,
    `family_scheme`, `family_tax_credit`, `in_work_tax_credit`,
    `minimum_family_tax_credit`; PolicyEngine NZ has one consolidated
    `test_working_for_families.yaml` plus a separate Treasury-validation
    test file, and variable files for `best_start`/`family_tax_credit`/
    `in_work_tax_credit` with no separately named category found for
    either minimum family tax credit or partnered/combined-income
    verification at those paths. **No named-category gap found** -- every
    named category maps onto a category WFF's own suite already names
    somewhere across Tasks 12-15. Deliberately scoped no wider than that:
    a pinned list of file/directory names can show a category exists, not
    how deeply either comparator's tests exercise it, so no
    comparative-depth claim is made. GPT/Codex's fresh-context review
    (three rounds) caught an earlier revision overreaching into a
    comparative-depth claim, missing pinned commits/URLs, and misattributing
    OpenFisca's `family_scheme` category to PolicyEngine NZ as well --
    all fixed and independently re-verified. A legitimate clean result,
    not a shortcut -- see ADR-0009 for the full comparison, pinned commit
    URLs, and reasoning. Pete recommended acceptance and delegated the
    final merge decision to Claude Code, matching Tasks 13-15's pattern.
    Must be repeated independently for Accommodation Supplement once AS's
    own test suite is complete.
17. Independent adversarial review (fresh-context, no implementer explanation)
    — **Complete for WFF (PR #19, `review_packets/wff_task17.md`):**
    GPT/Codex reviewed the complete WFF vertical slice (Tasks 11-16, PRs
    #13-18) fresh-context, deriving expected behaviour from sources and
    specification.md before reading any implementer explanation, per the
    Roles section (Claude Code was the Tasks 11-16 implementer, so could
    not itself perform this review). Two findings recorded and classified
    (Task 18 below); PR #19 remains open as the standing review record, per
    Pete's instruction to keep it separate from the fix PR.
18. Classify discrepancies — **Complete for both Task 17 findings, MFTC fix
    merged 22 September 2026 (PR #20, commit `ec61213`).** Pete confirmed:
    **CODE_ERROR + TEST_ERROR** for the MFTC input gap; **ARCHITECTURE_ISSUE**
    for full-year rate binding. Neither required a policy-interpretation
    decision. `_minimum_family_tax_credit()` now gates on
    `family_scheme_income` (and partnered-income verification), matching
    `_family_tax_credit()`/`_best_start()`, confirmed against the operative
    Income Tax Act 2007 s ME 3 text (net family scheme income is legally
    derived from family scheme income). Three benchmark cases and one spec
    case corrected to match. Two review rounds on PR #20 (GPT/Codex): round
    1 found Jeremy's assumed family-scheme-income figure omitted IRD-stated
    child support (fixed, confirmed against IRD's family-income guidance);
    round 2 reported no remaining discrepancies in the narrowed MFTC scope.
    119/119 tests pass, Ruff and strict mypy clean. Pete recommended
    merging PR #20 "as the MFTC fix, not as closure of the Task 20
    architecture requirement"; Claude Code independently re-verified tests
    at the reviewed commit (`7ddf5f4`) and merged. The ARCHITECTURE_ISSUE
    finding is **not** resolved by this merge -- see Task 19/20 below.
19. Resolve ambiguities, record decision artifacts (where genuine ambiguity
    exists) — No interpretation ambiguity in either Task 17 finding, so no
    ambiguity decision artifact for those. One scoping decision was
    recorded instead: the fix PR (#20) initially added a generic
    reference-period-coverage guard directly to Task 11's loader, but this
    silently conflicted with `tests/unit/policy/test_loader.py`'s own
    already-reviewed design (`test_open_ended_final_interval_resolves`
    explicitly tests that Task 11 deliberately has no hardcoded date
    boundary at the loader level). Pete decided (22 September 2026): keep
    Task 11's open-ended-interval design as-is; the annual-period,
    policy/version, and rate-coverage checks move to Task 20 as **blocking
    acceptance tests** instead of a generic loader guard. The
    ARCHITECTURE_ISSUE finding stays open until those tests exist and
    pass — not resolved by PR #20.
20. Integrate into simulator — **Implemented for WFF, pending review.**
    Per Pete's Task 19 decision above and ARCHITECTURE.md's Simulation
    module contract, added `run_wff_module()`
    (`src/poltika/engines/simulator/wff.py`): combines Task 11's
    `load_policy_parameters()` and Task 12's `calculate_wff()` behind one
    call, enforcing the module contract's `validation_checks` — the
    existing schema-version/approval-status/`policy_version` gates
    `load_policy_parameters()` already raises for, plus the three
    module-specific invariants Task 19 assigned here rather than to Task
    11's general-purpose loader: (a) the requested modelled date falls
    within the policy's reviewed `reference_period`, not merely within
    some individual parameter's own interval — a foreign or mismatched
    date must not silently produce an annual result; (b) the loaded
    `PolicyParameterSet.policy_id` matches this module (`
    working_for_families`), not an unrelated or stale parameter set; (c)
    every parameter the calculation depends on is rate-covered for the
    *complete* reference period, not just individually resolved for the
    single requested date. Each invariant resolves to `needs_review` for
    all four `WffResult` components (never a silent zero), matching the
    calculator's own existing gate-failure pattern, rather than raising —
    only the pre-existing schema/status/version gates still raise, since
    those are unchanged, caller-level structural errors, not new
    module-boundary logic.

    Deliberately single-module: no cross-module `dependencies`
    (ARCHITECTURE.md notes those are v0.3's job).

    **Complete, merged 22 September 2026 (PR #21, commit `f0566e6`).**
    GPT/Codex's fresh-context review (two rounds) caught two further gaps
    in the first implementation, both independently reproduced before
    fixing: (1) the three module-boundary invariants above did not check
    that every parameter `calculate_wff()` needs is actually *declared* in
    `policy.yaml` at all — a policy.yaml missing one could pass all three
    invariants and then crash with a bare `KeyError` partway through a
    component calculation, reproduced directly against a synthetic
    single-parameter fixture; fixed by adding
    `_WFF_REQUIRED_PARAMETER_IDS` and a fourth module-boundary check
    confirming every one resolves before `calculate_wff()` runs, naming
    whichever are missing rather than crashing. (2)
    `requested_policy_version` defaulted to `None`, so an integration
    caller could silently omit it and bypass the policy_version half of
    the "matches what the caller requested" guarantee entirely (Task 11's
    `load_policy_parameters()` only checks a *supplied* version); fixed by
    making it a required keyword argument on `run_wff_module()` — no
    implicit "whatever's in the directory" fallback. Second review round
    reported no remaining discrepancies. Seven tests in
    `tests/unit/engines/simulator/test_wff_module.py` (all three original
    invariants including the mirror-direction interval case, the new
    missing-required-parameter regression, a behaviour-preservation smoke
    test, and confirmation the pre-existing `policy_version` mismatch
    raise is untouched). 126/126 tests pass (up from 119), `ruff`, and
    `mypy --strict` clean. Pete recommended merging, then recording
    acceptance; Claude Code independently re-verified tests at the
    reviewed commit (`ae8ac13`) and merged. **This closes the Task 17
    ARCHITECTURE_ISSUE finding (full-year rate binding)** — the three
    blocking acceptance tests it required now exist and pass.
21. Add API — gated on the pure calculator passing acceptance (now true:
    the Task 17-20 loop closed for WFF). **Complete, merged 22 September
    2026 for WFF (PR #22, commit `9e84864`), scoped to a source-checkout
    deployment -- see the future gate recorded below.** Introduces
    FastAPI + Pydantic v2 directly rather than a placeholder, per
    ADR-0010, which documents this as its own decision
    citing ARCHITECTURE.md's recorded long-term stack (commit `21dc905`)
    and the Streamlit-to-Next.js "go straight to the target" precedent.
    `fastapi`/`pydantic` added to `pyproject.toml`'s main dependencies;
    `httpx`/`uvicorn` under the `dev` extra only (not needed to run
    `TestClient`-based tests, no deployment target decided yet).
    `REPOSITORY_STRUCTURE.md` updated to add `src/poltika/api/` before
    creating it, plus the dependency-boundary table row (`api/` may
    depend on `engines/simulator/`/`common/`, never a caller-supplied
    policy directory path).

    One route (`POST /wff/calculate`, `src/poltika/api/wff.py`) wraps
    Task 20's `run_wff_module()` directly against the internally-pinned
    `policy_specs/working_for_families` directory -- never a
    caller-supplied path. The request model reuses `WffScenario`'s own
    `FactStatus`/`BestStartCohort`/`PartnerStatus` string enums directly
    as Pydantic field types (not re-declared), so the API's vocabulary
    cannot drift from the calculator's; `requested_policy_version` is a
    required field, no implicit default, mirroring Task 20's own
    explicit-version contract. The response's `ComponentResultResponse`
    shape is pinned explicitly --
    `{outcome, value: <decimal-as-string> | null, reason}` -- confirmed
    that Pydantic v2 serializes `Decimal` to a JSON string, not a float,
    preserving the exact-decimal precision specification.md's calculation
    sequence requires. `src/poltika/api/main.py` registers explicit
    exception handlers for `common.errors.PoltikaError` subclasses so a
    loader-raised structural error never collapses into a 200:
    `PolicyVersionMismatchError` -> 409 (caller-correctable), any other
    `PoltikaError` -> 500 (a deployed-data problem, not the caller's
    fault).

    Four tests in `tests/unit/api/test_wff_api.py` (FastAPI `TestClient`,
    reusing `spec_cases.yaml`'s own scenario blocks rather than
    hand-authoring new ones): a normal calculated result, a needs_review
    component that doesn't collapse to a zero/null-meaning-zero, a
    malformed request body (missing field + invalid enum value, asserts a
    4xx with per-field validation errors), and the `policy_version`
    mismatch case explicitly asserting 409 -- not left as prose-only
    documentation, since a loader exception silently becoming a 200 is
    exactly the failure mode this task's doctrine is most worried about.
    130/130 tests pass (up from 126), `ruff`, and `mypy --strict` clean.

    **Review depth, stated explicitly:** this task adds no new policy
    logic -- every calculated value still comes from
    `calculate_wff()`/`run_wff_module()`, already verified through Tasks
    12 and 17-20's full source-derivation and adversarial-review process.
    The API layer's only job is HTTP routing, request validation, and
    response serialization, so it does not get a Task-17-style
    fresh-context review; ordinary GPT/Codex code review (structure,
    error handling, schema correctness) is the stated, deliberate depth
    for this task, not a silently skipped decision.

    **PR #22 review round (GPT/Codex), two findings, both fixed:**
    (1) `WFF_POLICY_DIR` locates `policy_specs/` relative to this source
    file, which only resolves inside a source checkout --
    `pyproject.toml`'s `[tool.setuptools.packages.find]` only packages
    `src/`, so a normally `pip install`-ed wheel (confirmed by actually
    building one: `poltika/**` only, no `policy_specs/`) would fail to
    load `policy.yaml`. Fixing the packaging itself (e.g. moving
    `policy_specs/` under `src/poltika/`) is a deployment/packaging
    architecture decision beyond this task's single-module HTTP-wrapper
    scope, touching every existing reference to `policy_specs/`'s
    repo-root location -- **left open, explicitly documented as a known
    limitation** in `poltika/api/main.py`'s module docstring, not silently
    fixed. What this PR does add: a FastAPI `lifespan` startup check that
    fails loudly and immediately if `policy_specs/` is missing, rather
    than a confusing failure on the first request.
    (2) The 500 handler returned `str(exc)` verbatim, and
    `InvalidSourceCatalogError` in particular embeds absolute resolved
    filesystem paths -- confirmed directly. Fixed: the exception is now
    logged server-side (with traceback) but the response carries a fixed,
    generic detail message with no exception text.
    A third, non-bug scope finding was also addressed: the API's OpenAPI
    `description` and the route's docstring now state explicitly that
    every `"verified"` fact is the caller's own assertion, not
    independently confirmed by Poltika, and that a result is a
    conditional simulation, not a verified entitlement determination.
    Two new regression tests added (the leak fix, the startup-failure
    behaviour). 132/132 tests pass (up from 126), `ruff`, and
    `mypy --strict` clean.

    **Second PR #22 review round (GPT/Codex): accepted the path-leak fix
    and conditional-simulation wording, but flagged that Task 21's
    acceptance is scoped to a source-checkout deployment only** --
    `policy_specs/` is confirmed absent from a built wheel (see finding 1
    above), and the `lifespan` startup check only makes that failure
    clear, it does not make the API deployable from an installed
    artifact. Pete accepted PR #22 under that explicit scope and required
    recording the following as a **future gate, not yet scheduled as a
    numbered task**, before any deployment of this (or a later
    Accommodation-Supplement-extended) API outside a source checkout:

    1. Decide and implement how `policy_specs/` reaches an installed
       deployment (e.g. embedding it under `src/poltika/` as package
       data, a separate data-distribution mechanism, or a documented
       "mount policy_specs/ at deploy time" convention) -- an explicit
       packaging/deployment architecture decision, not a default to fall
       into.
    2. Add an installed-artifact test: build the wheel (`uv build
       --wheel`), install it into a clean environment separate from this
       source checkout, and confirm the API actually serves a
       `/wff/calculate` request successfully end-to-end -- not merely
       that the Task 21 startup check fails cleanly when the data is
       missing, but that when correctly packaged, the API actually works
       outside the checkout it was built in.

    Until both exist, this API must not be presented as deployable beyond
    a source checkout, regardless of what `pytest`/`ruff`/`mypy --strict`
    report -- none of those currently run against an installed artifact.

    **Deployment gate closed, 23 September 2026 (ADR-0011).** Presented
    Pete the three options this section named (embed under `src/`, a
    separate distribution artifact, a deploy-time mount convention) with
    the concrete blast radius of each (embedding would touch 12+ existing
    Python file references and three CI glob patterns); Pete chose the
    deploy-time mount convention. `policy_specs/` is deploy-time
    configuration, not package data -- supplied via the
    `POLTIKA_POLICY_SPECS_DIR` environment variable
    (`poltika.api.wff._wff_policy_dir()`), falling back to the source-
    checkout-relative default when unset, so local development and every
    existing deployment are unaffected. The Task 21 `_lifespan` startup
    check is unchanged -- only what feeds `WFF_POLICY_DIR` changed.
    `tests/installed_artifact/test_installed_artifact.py` (marked
    `installed_artifact`, excluded from the default fast suite via
    `pyproject.toml`'s `addopts`, run explicitly with `uv run pytest -m
    installed_artifact`) builds the real wheel, installs it into a
    throwaway venv with no source checkout on `sys.path`, and confirms
    `/wff/calculate` actually serves a request end-to-end -- independently
    verified twice: once via the committed test, once via a manual
    positive/negative sanity check (with the environment variable
    correctly unset, startup fails with the documented error; set, the
    request succeeds). This API may now be presented as deployable beyond
    a source checkout, given `POLTIKA_POLICY_SPECS_DIR` is set correctly.

    **Codex review finding on PR #26, confirmed and fixed:** the probe
    subprocess inherited the calling process's `PYTHONPATH`, so it could
    silently import `poltika` from the source checkout instead of the
    installed wheel -- reproduced directly by hand (setting
    `PYTHONPATH=<repo>/src` before running the probe against a real
    throwaway venv did exactly that). Fixed in two independently-verified
    layers: the parent test now strips `PYTHONPATH` from the probe's
    environment, and the probe itself asserts its own import resolves
    inside the throwaway venv before doing anything else, so any other
    leak path is caught too.

    **Complete, merged 23 September 2026 (PR #26, commit `be27227`),
    reconciled with the concurrently-developed Task 24.1 (PR #27,
    above).** Discovered mid-task that Claude Code and GPT/Codex were
    sharing the primary checkout rather than each in an isolated
    worktree -- Codex's own branch switch moved Claude Code's working
    directory without either side running that command directly. Claude
    Code's own work from that point on was built and verified entirely
    in a separate `git worktree`, never touching Codex's in-progress
    files. When both PRs were ready, merged PR #27 first, rebased PR
    #26 onto the result (clean, no conflicts -- the only file overlap
    was this document, in separated sections), and re-verified the
    combined state (189/190 tests, ruff clean, mypy --strict clean, the
    `installed_artifact` test passing explicitly) before merging PR #26.

    Immediately before merging, Claude Code independently re-verified
    `pytest` (132/132), `ruff`, and `mypy --strict` all pass, and that
    CI's `check-protected-paths` check was green, at the reviewed commit
    (`910c37b`). Merged as commit `9e84864`.

### Week 3 — Accommodation Supplement
22. Complete AS specification — **Complete, approved by Pete 22 September
    2026 (PR #24, commit `92a6acd`; `policy_version: "0.1.0"`).** Working
    from the already-complete
    Task 2 source map, directly re-checked the Social Security Act 2018
    (ss 65AAA-69, 423, Schedule 4 Part 7 cl 1-8) and Social Security
    Regulations 2018 (rr 15-19) official text. Resolved specification.md's
    s 423(3) $100-asset-step question directly from the Act text (complete
    hundreds, matching WFF's existing complete-dollar-excess convention).
    **Escalated to Pete, now decided (DEC-001, 22 September 2026):** r
    18(2)'s income-excess rounding -- confirmed the Regulations are
    genuinely silent on whether to round the excess before applying the
    25% reduction (unlike WFF's explicit "complete dollars" language),
    and MSD's own two pages disagree. Pete decided: apply the 25%
    reduction to the exact, unrounded excess (matching the
    student-partner worked example, not the general worksheet's
    floor-first convention) -- textually, r 18(2) omits the language MD
    13(3)(a) uses when the drafters do mean a complete-dollar floor, and
    r 19 already states the one place rounding happens (the final
    amount). Confidence: medium, not high -- `decisions/
    DEC-001-income-excess-rounding.md` records a residual verification
    risk (MSD's general worksheet reflects the opposite convention; find
    a second independently published fractional-excess example, or a
    direct MSD confirmation, before promoting this to a protected
    benchmark value in Task 24). `policy.yaml`'s now-stale
    `income_excess_rounding_convention_undecided` validation check
    removed -- resolved, not an open runtime gate any more. Confirmed
    AS-10's statutory basis exists (Schedule 3
    cl 8 cross-referenced against the Act's "WFF tax credit" definition)
    without resolving the full AS/WFF interaction (Task 28's job).
    Proposed a narrow v0.1 supported domain (single claimant or ordinary
    couple, rent/board tenure only, Jobseeker/Sole Parent/Supported
    Living/non-beneficiary categories) mirroring WFF's Task 10 narrowing
    pattern, with every named unsupported case (student, pension,
    mixed-benefit, joint-tenancy, community-spouse, homeowner, unverified
    area, asset exemptions, sub-letting/boarder accommodation income)
    required to resolve `unsupported`/`needs_review`, never a false zero
    or a silent default to Area 4. Also confirmed, directly against
    Schedule 4 Part 7 cl 1-3, that the area caps are **statutory** dollar
    figures, not just agency guidance as the Task 2 map's citation implied.
    **Task 25 finding, surfaced early rather than worked around:**
    `policy.yaml`'s `parameters` list is deliberately left empty --
    `ParameterUnit`'s enum has no weekly-dollar unit and no general-purpose
    fraction/rate unit outside WFF's "above threshold" wording, so every
    value this task verified lives in `specification.md`'s contract
    instead, ready to move into `policy.yaml` once Task 25/26 extends the
    schema. `policy.yaml`'s `status` moved `scaffold` -> `draft_pending_
    review` -> **`approved`**, `policy_version: "0.1.0"` assigned,
    matching WFF's Task 10/10.4 precedent -- domain scoping and ambiguity
    decisions were Pete's personal call (DEC-001), not delegated, and
    Pete personally accepted the whole scoped contract (specification.md's
    "Task 22 acceptance" note), the same pattern as WFF's Task 10.4. No
    code, test, or WFF file changed. GPT/Codex fresh-context review
    complete (PR #24, findings fixed). Immediately before accepting,
    Claude Code re-verified `pytest` (132/132), `ruff`, `mypy --strict`,
    and `load_policy_spec()` all pass at the reviewed commit (`d20c738`).
    Merged as commit `92a6acd`. This approval covers the scoped domain and
    calculation contract only -- `policy.yaml`'s `parameters` list stays
    empty pending Task 25/26's schema extension, and the residual DEC-001
    corroboration is still needed before Task 24 can treat the rounding
    convention as a protected benchmark rule.
22a. Identify and freeze the minimum authoritative external statistical
    datasets AS actually needs (e.g. Stats NZ Statistical Area Unit geography
    data underpinning the AS-05 Area 1-4 lookup), each with full provenance
    and retrieval_method: manual_download — see Data Acquisition Doctrine —
    **Closed N/A, 22 September 2026, matching WFF's Task 10a/10b precedent.**
    Checked `as-msd-areas` directly (the source already cited in `sources.yaml`
    as `kind: agency_geography`, not a statistical dataset): it is a complete
    named Statistical Area Unit -> Area 1-4 lookup table, but explicitly
    points users to MSD's own separate "area map tool" for the actual
    address-to-SAU resolution step -- that step is not on the page and not a
    published Stats NZ dataset either. This does not create a Data
    Acquisition Doctrine gap because Task 22's already-Pete-accepted
    `policy.yaml` input contract (`statistical_area_unit`, type
    `verified_area_1_to_4_classification`) requires the *caller* to supply an
    already-verified Area 1-4 classification -- Poltika's scoped v0.1 domain
    never performs address- or SAU-level geographic resolution itself, the
    same "verified fact in, never independently re-derived" pattern every
    other WFF/AS input already uses. No canonical Poltika geography variable,
    no `data/raw/` snapshot, and no Stats NZ dataset are needed for the
    domain as currently scoped. Per Data Acquisition Doctrine's "minimum
    necessary, not the full catalogue," acquiring one now would be
    speculative, not something this vertical actually needs to run or
    validate. **Revisit if a later task changes `statistical_area_unit` to
    accept a raw SAU code or address instead of a pre-verified Area
    classification** -- that would reintroduce the need for MSD's lookup
    table (already a cited source) and possibly a Stats NZ SAU boundary/
    concordance dataset for address-level resolution.
23. Implement pure AS calculator (consumes canonical Poltika variables only)
    — **Implemented, pending review, 23 September 2026.** Per Pete's
    decision (23 September 2026): resolved Task 22's flagged
    `ParameterUnit` gap with a narrow, additive schema extension inside
    this task rather than pulling Task 25/26 forward. Added exactly three
    new `ParameterUnit` members (`NZD`, `NZD_per_week`, `fraction`) --
    purely additive, no `schema_version` bump, WFF's existing
    `policy.yaml` still validates byte-for-byte unchanged (confirmed: all
    132 pre-existing tests still pass, plus 4 new tests asserting the new
    units resolve correctly and the dimension check still rejects a
    mismatch). `policy.yaml`'s `parameters` list populated with the 20
    values Task 22 independently verified (12 area caps, 2 asset
    ceilings, 2 asset-imputation thresholds, the imputation step/rate, the
    entry-threshold fraction, the income-reduction rate) -- deliberately
    still excludes the claimant-category base rates and the r 18(3) income
    level, which depend on dated MSD tables not yet independently
    recalculated (Task 24's job).

    `src/poltika/engines/simulator/accommodation_supplement.py`:
    `calculate_accommodation_supplement()`, mirroring `calculate_wff()`'s
    pure-function/`ComponentResult` pattern exactly (imports
    `ComponentResult`/`FactStatus` from `wff.py` rather than duplicating
    them, per Architecture Doctrine's "minimum abstraction demanded by two
    real policies" -- a plain import, no `wff.py` changes). Implements
    specification.md's approved 6-step sequence: household gate first
    (every named unsupported case), plain-case qualifying costs, the 25%
    entry threshold, the capped 70% cost-based amount, the DEC-001
    unrounded income reduction (non-beneficiary route only, per AS-08),
    and r 19's round-up-to-complete-dollar as the only rounding step.
    A parameter genuinely undeclared in `policy.yaml` (the normal, expected
    v0.1 state for the base rates/income level right now, unlike WFF's PR
    #21 bug) resolves `needs_review`, not `KeyError` -- built defensively
    from the start this time, per that earlier finding.

    21 new unit tests in `tests/unit/engines/simulator/
    test_accommodation_supplement.py`, mirroring `test_wff.py`'s Task 12
    scope: hand-calculated ordinary/capped/zero/non-beneficiary-reduction
    cases, every unsupported household-gate trigger, every unverified-fact
    needs_review case, and confirmation the real (not yet fully populated)
    policy.yaml resolves `needs_review` rather than crashing. 157/157
    tests pass (up from 132), `ruff`, and `mypy --strict` clean.

    **Review depth:** this task is calculator behaviour and an
    architecture-boundary schema change -- both categories Pete's
    Codex-review-reserve plan (22 September 2026) names as high-risk,
    warranting the one consolidated review, not self-review alone. Author
    preflight done per `.claude/skills/pr-review-preflight/SKILL.md`,
    found and fixed two self-flagged (not independently verified)
    judgment calls plus one test-coverage gap before requesting review
    (commit `9eac0c8`).

    **Complete, merged 23 September 2026 (PR #25, commit `53a4084`).**
    Pete reviewed personally (checked out the branch, ran the full
    suite/ruff/mypy independently, read the calculator end-to-end against
    specification.md, cross-checked every parameter ID against
    `policy.yaml`, and independently hand-recomputed three test cases
    rather than trusting the docstrings): parameter wiring, arithmetic,
    the narrow schema extension's scope, the "undeclared parameter ->
    needs_review" fix, and both self-flagged judgment calls all confirmed
    correct. One finding, spec-level not code-level: `specification.md`'s
    "Unsupported" list described the asset-ceiling-exceeded case as "a
    genuine, evidenced zero", contradicting the list's own header two
    lines above ("never a false zero") -- the calculator and its test
    were always correct (`unsupported`); only the wording was wrong.
    Fixed directly on `main` (commit `a14dfa8`, predates PR #25's own
    diff -- introduced during Task 22/PR #24, not this task). Immediately
    before merging, Claude Code independently re-verified `pytest`
    (158/158), `ruff`, and `mypy --strict` all pass at the reviewed
    commit (`78cbc1f`), confirmed CI green, and confirmed the doc fix and
    PR #25's diff don't conflict (PR #25 never touches
    `specification.md`). The two self-flagged judgment calls (sole-parent
    inference, exempt-asset `UNKNOWN` -> `unsupported`) and the deferred
    re-verification of the 20 populated parameter values remain correctly
    open per PR #25's own framing -- not closed by this review, tracked
    for Task 24/25.
24. Repeat test/review process — broken into subtasks 24.1-24.8 below (23
    September 2026), mirroring WFF's Task 13-20 sequence one-for-one,
    since AS's single-component structure makes the same granularity
    tractable as one task's worth of subtasks rather than eight separate
    numbered tasks the way WFF needed. **Owner/status per subtask below
    -- check this before starting any AS work, so Claude Code and
    GPT/Codex don't edit the same scope concurrently** (`review_packets/
    README.md`: "Do not have both models edit the same checkout
    concurrently").

24.1. Independent verification + spec/benchmark tests (spec_cases.yaml,
    benchmarks.yaml) — mirrors WFF's Tasks 13-14 combined into one
    subtask, since AS has one component, not four. **In progress,
    assigned to GPT/Codex, 23 September 2026** (Pete sent the goal
    directly). Scope: (a) independently re-verify all 20 statutory
    values already in `policy.yaml` against the Act/Regulations text --
    a genuine second look, not a re-read of Task 22/23's own prior work;
    (b) write `spec_cases.yaml` -- hand-calculated cases derived
    independently from specification.md's calculation sequence, covering
    the household gate's unsupported/needs_review triggers and both the
    beneficiary (no income test) and non-beneficiary (DEC-001 unrounded
    excess) paths; (c) search MSD's published worked examples for a
    second fractional-income-excess case to corroborate DEC-001's
    reading (Pete's explicit ask, PR #25 review) -- if found,
    independently recalculate and record in `benchmarks.yaml`; if not
    found, record that negative result in DEC-001's own "Confidence"
    section rather than leaving the gap silent. Does not touch
    `accommodation_supplement.py` or its existing unit tests. **Claude
    Code: do not edit `policy_specs/accommodation_supplement/` (any
    file, including `decisions/`) or `spec_cases.yaml`/`benchmarks.yaml`
    while this is in progress.**

    **Implemented, pending independent review, 23 September 2026.** The
    independent statutory pass found no discrepancy across the 20 populated
    values. Added 22 hand-calculated spec cases and 4 official-example
    benchmark/scope cases, each with an explicit single-component expected
    block and assumptions separated from published facts. The second-example
    search found no further fractional income excess: the additional official
    example found also uses an integral $57.00 excess. DEC-001 now records that
    negative result and remains medium confidence; its student-partner amount
    is not promoted to a protected numeric benchmark. The dated MSD
    benchmark tables exposed a Task 25 schema issue: entry thresholds vary by
    household category within a claimant category (for example, Supported
    Living Payment has different single/couple/parent thresholds), while the
    Task 23 calculator currently requests one `as_base_rate_<claimant_category>`
    parameter. Task 24.1 therefore keeps each dated benchmark threshold as an
    explicit per-case assumption and does not add a misleading global base-rate
    value to `policy.yaml`; Task 25 must resolve the parameter shape before the
    real policy can produce those ordinary numeric paths without assumptions.
    This is recorded, not fixed here, because 24.1 explicitly must not modify
    `calculate_accommodation_supplement()` or its existing unit tests.
    Isolated verification: 187/187 tests pass and Ruff is clean; strict mypy
    is clean when run against `src` and the two new runners.

    **Complete, merged 22 September 2026 (PR #27, commit `8c8c06a`).**
    Claude Code independently re-verified in a fresh, isolated worktree
    (not the shared checkout Codex used) rather than trusting the PR's
    own report: reproduced 187/187 passing, `ruff` clean, `mypy --strict`
    clean (without needing the `PYTHONPATH` workaround the PR description
    mentions -- that was specific to the shared checkout's polluted
    state, not this PR's content), and confirmed
    `calculate_accommodation_supplement()` and its existing Task 23 unit
    tests are genuinely untouched (empty diff). Reconciled with the
    concurrently-developed Task 21 deployment gate (PR #26, below): the
    only file overlap was this document, in clearly separated sections;
    merged PR #27 first, rebased PR #26 onto the result, and re-verified
    the **combined** state in the same isolated worktree (189/190 tests,
    190 = 187 + PR #26's 2 new tests + 1 `installed_artifact` test
    deselected by default) before merging PR #26 too -- both workstreams
    confirmed to coexist with zero interference, not merely assumed from
    the file-level non-overlap.
24.2. **Complete, accepted and merged 23 September 2026 (PR #28, GPT/Codex
    implementation, commit `06c8b78`).** Regression tests for six known
    historical issues from Tasks 22-24.1, matching WFF Task 15's discipline:
    the single-claimant 1-child/2-child Schedule 4 category boundary; r 15's
    deliberately different any-child asset threshold; UNKNOWN exempt-asset
    status remaining `unsupported`; the non-beneficiary zero floor; real
    undeclared base-rate and income-level parameters returning `needs_review`
    rather than `KeyError`; and DEC-001's exact fractional income-excess
    convention. Each regression independently reconstructs the relevant
    facts rather than importing a spec/benchmark case. AS YAML conversion and
    assumption helpers moved to `tests/conftest.py` at their third consumer.
    195 tests pass (plus the separately-invoked installed-artifact test),
    Ruff clean, strict mypy clean.

    **Pete's independent review** (own worktree, not from Claude Code's
    account): file-overlap claim checked directly against `gh pr diff`;
    195/1-deselected, Ruff, and strict mypy reproduced independently, not
    taken on trust; two of the six regressions hand-recomputed
    independently (`$74` DEC-001 exact-excess vs. the rejected `$75`
    floor-first figure; `$235` cl 2 area cap for a 1-child single
    claimant vs. cl 1's `$305`) -- both confirmed correct. **One finding:**
    `test_single_claimant_household_category_changes_at_two_dependent_
    children` asserted only on the private `_household_category()`
    helper's return value, never calling `calculate_accommodation_
    supplement()` -- the one test in the file (and, checked, the only one
    in the whole suite) not exercising behaviour through the public
    calculator, contrary to this file's own "make a previously observed
    mistake fail under its own durable, searchable name" purpose.
    Classified fixable-before-merge, not blocking.

    **Fix, Claude Code, isolated worktree, pushed to the PR branch same
    day:** converted the test to compare the resulting AS amount for a
    single claimant with 1 vs 2 dependent children against the correct
    Area 1 caps (`$235` cl 2, `$305` cl 1), the same way its neighbour
    (`test_one_child_single_uses_higher_asset_ceiling_but_cl2_area_cap`)
    already does. Re-verified independently after the fix: 195 passed,
    Ruff clean, strict mypy clean. Pete accepted and merged.
24.3. **ADR-0012 accepted 24 September 2026, narrowly** (Pete's delegation,
    recorded in PR #49): the name-only no-gap conclusion stands; the four
    opaque names remain unconfirmed candidates. Earlier status below.
    **Implemented 23 September 2026; proposed ADR-0012 pending independent
    review and Pete's acceptance.** Repeated ADR-0009's corrected WFF method
    after PR #28 merged: structural names only at pinned commits, with no
    external contents, test logic, values, or formulas read. Compared both
    OpenFisca Aotearoa (`9d77ea7`) and `PolicyEngine/policyengine-nz`
    (`fbd186b`). Every unambiguous AS category name maps to an existing
    Poltika spec, benchmark, regression, or calculator-test category. Four
    OpenFisca names (`_benefit_me`, `cutout`, `rebate`, `situation`) are too
    opaque to map from names alone and are recorded as candidates for Pete,
    not asserted as gaps. **Conclusion: no confirmed named-category gap
    found; no code or test changes needed.** No comparative-depth claim is
    made. See `adr/0012-task24-3-as-coverage-gap-check.md` for pinned URLs
    and the category table. Task 24.4 was not started here.
24.4. Independent adversarial review (fresh-context, no implementer
    explanation) of the completed AS vertical slice. Owner: whichever
    model did not do 24.1-24.3's implementation work, per the Roles
    section -- Codex did 24.1-24.3, so Claude Code, via a genuinely
    fresh-context subagent given only mechanical inputs (sources, spec,
    diffs, tests; no accumulated session context on the implementation),
    performed this one, mirroring Task 17's WFF precedent. **Complete,
    23 September 2026 (PR #31, `review_packets/as_task24_4.md`).**
    Covers Tasks 22-24.3 plus open PR #29 (reviewed here as its
    independent-review pass). 4 findings, none affecting any numeric
    calculation outcome: (1) MISSING_SOURCE/CODE_ERROR -- an uncited
    "s 65(1)(b)" citation in the asset-ceiling `ComponentResult.reason`
    text and a test docstring, where every other reference to the same
    rule cites r 15; (2) CODE_ERROR -- the asset-ceiling `unsupported`
    check sits outside `_household_gate_failure()`, so it cannot
    pre-empt an unrelated `needs_review` trigger the way the function's
    own docstring claims; (3) SPEC_ERROR -- `policy.yaml`'s
    `assessment.unsupported` list omits `asset_ceiling_exceeded`, which
    `components[0].validation_checks` includes (metadata drift, not read
    by the calculator at runtime); (4) SPEC_ERROR (cosmetic) --
    `decisions/README.md` still claims no decisions are recorded despite
    DEC-001 existing in the same directory. Both self-flagged judgment
    calls confirmed still correctly labelled; DEC-001's convention
    confirmed applied only at its one correct site; all spec/benchmark
    arithmetic independently re-derived and matches; `run_as_module()`
    (PR #29) confirmed structurally sound against `run_wff_module()`,
    no gap found. Findings #1 and #2 independently spot-checked by
    Claude Code (grep + direct reproduction) before opening the PR. No
    fix applied in this PR -- findings-only, kept as the standing review
    record per Task 17/PR #19's pattern. Awaiting Pete's classification
    (Task 24.5).
24.5. Classify discrepancies from 24.4 — **Complete, 23 September 2026,
    classification and fix accepted by Pete (PR #32, commit `14eea09`).**
    All 4 of PR #31's findings classified: finding 1 **MISSING_SOURCE +
    CODE_ERROR** (uncited "s 65(1)(b)" citation), finding 2 **CODE_ERROR**
    (asset-ceiling precedence gap), findings 3-4 **SPEC_ERROR** (policy.yaml
    list drift; stale decisions/README.md). None required a
    policy-interpretation decision -- all four are mechanical (a wrong
    citation string, a precedence ordering bug, and two internal-document
    drift issues), so Task 24.6 below has nothing to resolve. Fixed in PR
    #32: citation corrected to r 15 in both code and test; the r 15
    asset-ceiling `unsupported` check moved inside
    `_household_gate_failure()` so it can actually pre-empt an unrelated
    `needs_review` trigger, with a new regression test reproducing the
    previously-unexercised combination; `policy.yaml`'s
    `assessment.unsupported` list and `decisions/README.md` both
    corrected. 202 tests pass (201 + 1 new), Ruff clean, strict mypy
    clean; no numeric outcome changed anywhere. Author fix, not
    independently re-reviewed by a separate party before merge -- Pete
    explicitly accepted proceeding on that basis.
24.6. Resolve ambiguities, record decision artifacts (where genuine
    ambiguity exists) — **Complete, 23 September 2026: no genuine
    ambiguity found in any of Task 24.4's 4 findings**, so no decision
    artifact is needed (see 24.5). Distinct from Task 24.4's own two
    already-flagged, already-decided judgment calls (sole-parent reading;
    exempt-asset UNKNOWN handling), which the review confirmed remain
    correctly labelled and were not reopened.
24.7. Integrate `calculate_accommodation_supplement()` into a module
    entry point, mirroring Task 20's `run_wff_module()` pattern
    (validation_checks for policy identity, reference-period coverage,
    full rate coverage). **Implemented, Claude Code, isolated worktree,
    23 September 2026 (PR #29).** Adds `run_as_module()`; enforces the
    policy-identity, reference-period, and full-rate-coverage invariants
    generically over `spec.parameters` (no hardcoded AS parameter ids);
    deliberately does not duplicate WFF's "missing required parameter"
    invariant, since `calculate_accommodation_supplement()`'s own
    `_param_value()` already resolves an undeclared parameter to
    `needs_review` one layer down (Task 23's documented design). New
    `tests/unit/engines/simulator/test_as_module.py` mirrors
    `test_wff_module.py`'s Task 20 scope. No file overlap with Task 24.2
    (PR #28). **Complete, merged 23 September 2026 (PR #29, commit
    `e4deed1`).** Independent (non-implementer) review satisfied by Task
    24.4's fresh-context pass (PR #31, `review_packets/as_task24_4.md`),
    which explicitly scoped `run_as_module()`'s diff into its review and
    found it structurally sound against `run_wff_module()`, no gap --
    author preflight alone was not treated as sufficient, per
    `.claude/skills/pr-review-preflight/SKILL.md`. Re-verified in an
    isolated worktree against the post-#30/#31 `main` before merging:
    201 tests pass (195 + 6 new), Ruff clean, strict mypy clean.
24.8. Add an AS API route, mirroring Task 21's `run_wff_module()` ->
    FastAPI pattern (ADR-0010). **Implemented, Claude Code, isolated
    worktree, 23 September 2026 (PR #33).** Adds
    `src/poltika/api/accommodation_supplement.py`, mirroring
    `poltika.api.wff` exactly (`_as_policy_dir()`, same ADR-0011
    deploy-time mount convention; same 422/409/500 error mapping);
    registers alongside the WFF router in `main.py`, whose startup
    `_lifespan` check now covers both policy directories. Since the real
    deployed policy doesn't yet declare the base rates (see Task 25/26
    below), there is no request that legitimately produces `calculated`
    against the real policy yet -- tests instead confirm the real
    policy's actual current behaviour end-to-end (a clear `needs_review`
    naming the undeclared parameter) plus a real, fully-resolved
    `unsupported` outcome (the r 15 asset ceiling). 9 new tests
    (211 total), Ruff clean, strict mypy clean. Author preflight only at
    implementation time, same as PR #29.

    **Accepted and merged 24 September 2026 (PR #33, merge commit
    `e03e8f8`, merged after PR #34).** Independent review by GPT/Codex
    found two low-severity `TEST_ERROR`s -- the code was already correct,
    but the tests did not lock the claims in: no route-level test proved a
    fractional `Decimal` serializes as a JSON string, and the 500-handler
    test's fixture actually triggered `UnsupportedSchemaVersionError`
    before reaching the `InvalidSourceCatalogError` its docstring claimed
    to exercise. **Fix commit `79441c2` was written and pushed to the PR
    branch by GPT/Codex, the reviewer** (Pete confirmed authorship, 24
    September 2026) -- the commit's own git author (`GitHub Copilot`) and
    `Co-Authored-By: Claude Sonnet 5` trailer are inaccurate and do not
    reflect who wrote it; this entry is the authoritative record. Because
    the reviewer authored that commit, Claude Code checked it separately
    rather than treating it as covered by Codex's own review: raised the
    real `InvalidSourceCatalogError` directly (confirmed it fires and
    embeds the absolute path the 500 handler guards against leaking) and
    ran the full suite. Re-verified on `main` after merge: 212 passed (1
    deselected), Ruff clean, strict mypy clean. Pete accepted and merged.
25. Stress-test POLICY_SPECS schema against AS's different structure
    (housing costs, asset test, geography). **Complete, 23 September
    2026, Pete's decision on scope.** Checked all three named areas
    against the current `PolicySpec`/`ParameterSpec` schema: geography
    (`area_cap_<household_category>_<area>`) and the asset test
    (Task 23's `ParameterUnit` extension) already work within the
    existing schema; `assessment.membership_period: assessment_week`
    (distinct from WFF's `tax_year`, specification.md's own flagged
    concern) was already set correctly, stored in the schema's
    pre-existing untyped `assessment: dict[str, object]` field. The one
    confirmed gap was Task 24.1's base-rate finding (needs a
    household-category dimension) -- fixable with a compound
    parameter-id convention within the *existing* schema, mirroring
    `area_cap`'s already-established pattern, not a Pydantic model
    revision. **Conclusion: no `PolicySpec`/`ParameterSpec` schema
    revision is needed for AS.** Recorded in
    `policy_specs/accommodation_supplement/specification.md`'s "Note for
    Task 25" section (resolution appended, original note kept intact).
    Pete decided: close Task 25 on this finding; re-scope Task 26 from a
    schema revision to the targeted id-convention fix below.
26. **Re-scoped by Pete's Task 25 decision: rename `as_base_rate_*`'s
    parameter-id convention to carry the household-category dimension,
    not a schema (`PolicySpec`/`ParameterSpec`) revision.** Complete,
    Claude Code, isolated worktree, 23 September 2026 (PR #34, which
    also carries Task 25's `specification.md` resolution note).
    `_base_rate_parameter_id(claimant_category, household_category)`
    replaces the single-dimension `as_base_rate_<claimant_category>`
    construction in `calculate_accommodation_supplement()`, mirroring
    `_area_cap_parameter_id()`'s already-established
    `<primary>_<household_category>_<...>` pattern; `household_category`
    is now computed once, before the base-rate lookup, and reused for
    the area cap below it (previously computed separately, later). No
    real values are populated under either the old or new id -- both
    remain entirely undeclared, Task 22/23's documented gap, pending
    Task 24's independent recalculation of the dated MSD tables; this
    changes what string id is looked up, not any approved numeric fact.
    `policy.yaml`'s comment and `specification.md`'s calculation-sequence
    step 3 updated to describe the new id shape.
    `tests/conftest.py::as_parameters_for_case()`'s `base_rate`
    parameter-assumption mechanism updated to derive the compound id from
    a case's own `partner_status`/`dependent_children_count` (fails
    loudly if either is missing, rather than guessing); three regression
    tests and one unit-test fixture updated to match, including
    splitting one regression test that reused a single parameters object
    across two different household categories into two explicit ones.
    202 tests pass (no new test -- existing coverage already exercises
    the fix through the `calculated` outcomes it depends on), Ruff clean,
    strict mypy clean.

    **Accepted and merged 24 September 2026 (PR #34, merge commit
    `91c6faa`, merged before PR #33).** Independent review by GPT/Codex:
    clean, no findings. Claude Code additionally reproduced the
    highest-risk claim -- a partial-interval parameter under the new
    compound id -- and confirmed `run_as_module()`'s reference-period
    invariant resolves it to `needs_review` with the correct reason. The
    regression-test edits were checked against `doctrine/test-doctrine.md`:
    they change only parameter-assumption fixtures and the expected
    parameter-id string, no protected expected value or outcome
    assertion. No file overlap with PR #33. Re-verified on `main` after
    merge: 202 passed (1 deselected), Ruff clean, strict mypy clean. Pete
    accepted and merged.
### Refinement of Tasks 26a-35 (approved by Pete, 24 September 2026)

Tasks 27-35 were one-line placeholders written before either vertical
slice existed. This refinement breaks them into subtasks and adds two
prerequisite tasks (26a, 26b) that the end-to-end Definition of Done
cannot pass without. It changes no completed task, approved value, or
doctrine. Every subtask names its owner. "Pete decides" marks a scope or
interpretation call that the implementer must not resolve.

**Carried-forward open items** (tracked here so they are not lost; each
is owned by the task named):

- AS base rates (`as_base_rate_<claimant>_<household>`) and the r 18(3)
  income level are still undeclared in `policy.yaml`, so the real AS
  policy cannot currently produce a `calculated` result for any
  household -- Task 26a.
- WFF's `in_work_base` was last recorded `needs_review` (Tasks 10.2, 13);
  Task 10.2's contract requires Order evidence covering the whole
  completed modelled tax year, not a single date -- Task 26b. WFF's
  reference period is 2026-27 only (to 1 April 2027). Annual in-work
  calculations requiring `in_work_base` remain `needs_review` until the
  full-interval evidence requirement is met. That is not expected before
  the 2026-27 tax year completes. A scenario can still resolve
  `unsupported` earlier, for example when in-work eligibility fails.
  Tasks 29 and 35 plan around this; they do not assume it will clear.
- DEC-001 (AS income-excess rounding) remains medium confidence with no
  second fractional-excess example found (Task 24.1). Any golden
  household that depends on a fractional non-beneficiary excess must say
  so explicitly -- Task 29.
- ADR-0012's header still reads `Status: proposed` although PR #30 merged,
  and its four opaque OpenFisca names (`_benefit_me`, `cutout`, `rebate`,
  `situation`) await Pete's disposition; Task 24.3's entry above still
  says "pending independent review and Pete's acceptance" --
  Pete decides whether to accept ADR-0012 and what to do with the four
  names; Claude Code then records it (a docs-only change).
- Task 22a's revisit condition (a raw SAU code or address input would
  reintroduce a dataset need) stays live for any scenario-input design in
  Tasks 28-33.
- **AS module validation requires coverage of the whole reference period
  (CODE_ERROR, found in GPT/Codex's Task 28.2 research, PR #41; reproduced
  independently by Claude Code).** `_as_module_validation_failure()` copied
  WFF's annual rule, requiring each parameter value to span the whole
  `[2026-03-02, 2027-04-01)` reference period. AS is assessed per week, so
  a genuinely April-effective rate (the 1 April 2026 MSD tables) returns
  `needs_review` for every week. Owner: Claude Code. The fix checks
  coverage of the selected assessment week, and a boundary inside the week
  is never silently picked. WFF's full-year rule stays. The fix depends on
  28.2's week definition and must merge before 26a's rates run through the
  module. **Resolved, merged 24 September 2026 (PR #43).** `run_as_module()`
  takes an explicit `assessment_week` ([start, end), 7 days, no weekday
  convention). Reviewed by a fresh-context subagent standing in for
  GPT/Codex, on Pete's instruction to proceed without Codex input: approve,
  with six surviving boundary mutations, each now pinned by a test. PR #44
  added the AS route to the installed-wheel probe.

**Work split.** This follows the Roles section: GPT/Codex does source
work, specification text, and hand-calculated expected values; Claude
Code does repo implementation. Every slice is reviewed by the model that
did not author it, so the reviewer changes slice by slice rather than
per task.

| Owner | Authors | Reviews |
| --- | --- | --- |
| GPT/Codex | 26a (values plus the tests they change), 26b, 28.1, 28.3, 28.5's interaction spec cases, 29.1's proposed list, 29.2's hand calculations; research for 28.2 and 35.1 | 27, 28.4-28.5 code, 30, 31 (including 31.1's rule-ID mapping), 32, 33, 34.1's evidence, 35.3's wording; the Claude Code-authored slices in 34.3 |
| Claude Code | 27.2-27.3, 28.4, 28.5's runners and regression tests, 29.3, 30, 31, the 32.1 ADR draft, 32.2-32.4, 33, 34.1-34.2, 35.3-35.4; the ADR-0012 record | 26a, 26b, 28.1, 28.3, 29.2 (via a fresh-context subagent, per the Task 24.4 precedent); the GPT/Codex-authored slices in 34.3 |
| Pete | 27.1, 28.2, 29.1 approval, 32.1, 35.1, 35.2, ADR-0012, 34.4 classifications, every acceptance | -- |

**File ownership, so the two models never edit the same scope at once**
(`review_packets/README.md`): GPT/Codex owns `policy_specs/*/` policy
content (`policy.yaml`, `specification.md`, `sources.yaml`,
`spec_cases.yaml`, `benchmarks.yaml`, `decisions/`, and the golden
household file). Claude Code owns `src/`, the test runners,
`tests/regression/`, `REPOSITORY_STRUCTURE.md`, and
`policy_specs/SCHEMA.md` (27.2). There are two deliberate exceptions.
26a.3 lets GPT/Codex edit existing tests whose assertions the new values
change. 28.3 lets GPT/Codex edit both `specification.md` files. Each
model works in its own worktree. This file (BUILD_PLAN.md) is edited
only for status records, one PR at a time.

**Sequencing.** After approval of this refinement, 26a and 28.1 can
proceed independently (GPT/Codex source work; the earlier Codex usage
reserve was lifted by Pete on 24 September 2026). The date/interval decision in 28.2
must precede 26b; 26b records the outcome even if the rate remains gated.
28.3-28.4 need only 28.1 and 28.2. 28.5's cases that expect a
`calculated` AS result against the real policy, and all of 29, also need
26a and 26b. Then 29 → 30 → 31.6 → 32 → 33 → 34 → 35. Claude Code work that needs no
GPT/Codex input (each merge still requires the named independent review
and Pete's acceptance):

- 27.2-27.3, once Pete decides 27.1;
- 31.1-31.5, the per-policy trace, its tests and independent review.
  Because it changes calculator return types, merge it before 26a's
  test edits if review is available. Otherwise defer it until 26a merges;
  source research can proceed independently. Do not overlap test edits
  or bypass review. Complete this slice before 30;
- the 32.1 ADR draft;
- the ADR-0012 record, once Pete decides.

26a. **Populate AS base-rate and income-level parameters (new, prerequisite
    to 29-35).**
    - **26a.1 — GPT/Codex.** Independently recalculate, from the dated MSD tables
      already catalogued in `sources.yaml` (`as-msd-*-rates-2026`), the
      base-rate value for every supported claimant category × household
      category combination, plus the r 18(3) income level, citing the
      operative source for each. Where a table and the Act/Regulations
      disagree or a value is not published for a supported combination,
      stop and flag it (INTERPRETATION_AMBIGUITY or MISSING_SOURCE), never
      infer.
    - **26a.2 — GPT/Codex.** Add them to `policy.yaml` under the Task 26 compound-id
      convention, with effective intervals, units, and `source_id`s. This
      changes a protected path, so it goes through `doctrine/test-doctrine.md`'s
      statutory-value process, and the guard workflow result is checked
      before merge.
    - **26a.3 — GPT/Codex, same PR as 26a.2 so values and tests land together.** Update the tests that currently assert the real policy's
      base rate is undeclared (e.g. the Task 23/24.2 `needs_review`
      regressions, Task 24.8's API tests) so they record the new
      behaviour deliberately rather than just being flipped to pass. Add
      at least one spec case that produces `calculated` against the real
      approved policy with no parameter assumptions.
    - **26a.4 — Claude Code reviews (fresh-context subagent); Pete accepts.** Independent review of every new value against its source
      (not the author's workings); Pete accepts.

    **Status, 24 September 2026.** 26a.1's source audit merged (PR #46).
    Its fresh-context review confirmed that the Task 25/26 base-rate id
    reused the Schedule 4 cap grouping, which MSD's threshold tables split
    differently. That was a SPEC_ERROR, and Claude Code's own Task 25/26
    design error. It also found that the income level varies by household
    (r 18(3)). Pete delegated "resolve and proceed", and Codex recorded the
    resolution (PR #49):
    - DEC-002: use the published MSD entry thresholds and income levels
      directly, under four rate-household rows separate from the cap
      grouping, with fail-closed `ordinary_rate_status` and
      eldest-child-under-16 facts;
    - DEC-003: identified WFF is excluded from AS income whichever agency
      pays it.

    As a result, 26a.2 no longer populates `as_base_rate_*` values, as
    written above. It populates `as_entry_threshold_<claimant>_<rate_
    household>` and `as_income_level_non_beneficiary_<rate_household>`
    under AS policy `0.1.1`. Claude Code's code repair is PR #50, under
    fresh-context review; 26a.2's values follow once it merges.

    **Task 26a complete, merged 24 September 2026.** Claude Code did both
    parts on Pete's instruction to proceed without Codex input, with
    fresh-context subagent reviews standing in for GPT/Codex. Codex-owned
    files edited along the way: AS `policy.yaml`, `spec_cases.yaml` and
    `benchmarks.yaml`. Each PR flags this for Codex's later review.
    - **Selector repair (PR #50):**
      - four rate-household rows, separate from the cap selector;
      - published thresholds subtracted directly, with no old-id fallback;
      - fail-closed `ordinary_rate_status` and eldest-child-under-16 facts;
      - AS policy `0.1.1`.

      The fixture edits changed no expected value, which a script checked.
      The review found one fail-closed gate-order bug (a known unsupported
      case shown as `needs_review` when cash assets were unverified) and
      seven surviving mutations. All were fixed and re-checked.
    - **26a.2/26a.3 (PR #53):** 17 values were generated from MSD's
      1 April 2026 tables and verified one by one against the fetched tables
      by the reviewer. Three new spec cases run against the real policy with
      no assumptions ($75, $104, $47). The last two reproduce MSD's own
      published Nadiya and income-change examples. The non-qualified-partner
      rows are clarified: with children they use the ordinary row; without
      children there is no published row, so they are excluded.
    - **Verified on merged `main` (`c8316b2`):** 309 passed, the
      installed-artifact test passed, Ruff and strict mypy clean.
26b. **Recheck `in_work_base` for the v0.1 modelled interval(s) (new).** GPT/Codex;
    Claude Code reviews. Depends on 28.2's date/interval decision. Apply
    Task 10.2's existing rate-status contract in WFF's specification:
    record the dated Order check and the interval its evidence covers in
    `sources.yaml`'s `order_check` notes. An as-of check does not establish
    a rate for the rest of an unfinished tax year. Approve an ordinary
    full-year base only when evidence covers the entire completed,
    supported tax year, through the statutory-value process. An interval
    extending beyond the check remains `needs_review`; an Order commencing
    within it invokes the existing `unsupported` split-period path.
    A no-future-Order assumption cannot clear the gate or enter the
    assumption-free golden suite. Completion means a reviewed disposition,
    not necessarily rate approval. Task 35's question must respect it.

    **Disposition recorded 24 September 2026 (Claude Code, on Pete's
    instruction to proceed without Codex input; `sources.yaml`
    `task_26b_check`).** The official 2026 No 8 section 2 record still
    states "There is no secondary legislation made under this section
    currently on this website". The 28.2 interval is the full 2026-27 year,
    which extends beyond the check, so under WFF's Task 10.2 rate-status
    table the annual in-work base **stays `needs_review`**. `review_status`
    is unchanged. A targeted register search could not be repeated (the
    search URL returned 404), and the limitation is recorded. Recheck
    whenever the modelled interval or the check date changes.
27. **Re-scoped: settle the schema-version question (was "Migrate WFF's
    spec files to v0.2").** Task 25 concluded that no `PolicySpec`/
    `ParameterSpec` revision is needed for AS; both `policy.yaml` files and
    the loader are still `schema_version: "0.1"`, so there is no v0.2
    schema to migrate to. The Definition of Done still says "schema v0.2".
    - **27.1 — Pete decides. Decided 24 September 2026: option (a).**
      Schema stays `"0.1"`; the Definition of Done is amended below. The
      options were: (a) close the migration as moot and
      amend the Definition of Done to "schema v0.1, stress-tested by two
      structurally different policies (Task 25)"; or (b) define v0.2 as
      the stress-tested schema (Task 23's additive units plus the Task 26
      compound-id convention), bump both policies and the loader to
      `"0.2"`, and keep `"0.1"` loadable or reject it deliberately.
      Recommendation: (a). A bump would mark a change that already
      shipped without one, and "v0.2" already names a product release in
      ROADMAP.md, which invites confusion.
    - **27.2 — Claude Code (documents its own Task 23/26 changes); GPT/Codex reviews.** Whichever is chosen, bring `policy_specs/SCHEMA.md` up to
      date with what the code already accepts: the `NZD`,
      `NZD_per_week` and `fraction` units (Task 23), the compound
      parameter-id convention (`area_cap_*`, `as_base_rate_*`, Tasks
      25/26), and `assessment.membership_period` values in use
      (`tax_year`, `assessment_week`). **Complete, merged 24 September
      2026 (PR #38, merge commit `7b3f9c8`).** SCHEMA.md's "Schema as
      implemented" section. GPT/Codex review found no blocking issue; Pete
      accepted.
    - **27.3 — Claude Code; GPT/Codex reviews.** Apply the Definition of Done wording from 27.1. **Done
      in the refinement PR itself (24 September 2026).** Option (a) needs
      no migration.
28. **Cross-policy interaction: WFF + AS (refined).** The API/integration
    path is reused from WFF; the pre-API gate is not re-litigated.
    - **28.1 — GPT/Codex, primary sources only. Source-verify the
      interaction rules.** Starting from AS-10 and both specifications'
      cross-policy sections: (a) confirm, with operative citations, how
      Accommodation Supplement is treated in WFF family scheme income;
      (b) confirm how WFF is treated in AS chargeable income, separating
      the IRD-paid route (Schedule 3 cl 8, `as-msd-chargeable-income`)
      from any MSD-paid route, which both specifications say must not be
      collapsed; (c) establish from source which payment route applies
      to households in both supported domains (e.g. the AS beneficiary
      categories); (d) identify any other interaction that touches the
      supported domains, or record that none was found. Each unresolved
      point becomes an explicit `needs_review` gate or a DEC-00x decision
      artifact for Pete, never an assumption. **Research merged 24
      September 2026 (PR #48)**, after Claude Code's independent
      primary-source review. Its findings were resolved by DEC-003 (the
      MSD-paid route) and DEC-002 (r 17(2)(f)'s wording is left undecided;
      the table-based path doesn't compute that term). 28.3 drafting is
      unblocked.
    - **28.2 — Decided 24 September 2026 (Pete's "resolve and proceed"
      delegation, recorded in PR #49; research PR #41):** both lookup
      dates 2026-06-01; AS week [2026-06-01, 2026-06-08); WFF the full
      2026-27 year; results reported in native periods, with no combined
      total and no conversion. **Period and date reconciliation.** WFF is
      assessed per tax year (annual amounts) and AS per assessment week
      (weekly amounts). Decide how a combined result reports both: side by
      side in their native periods (recommended: no conversion rule is
      invented) or converted, in which case the conversion rule needs a
      source. Record the WFF tax-year interval, AS assessment week and
      applicable parameter lookup date(s) explicitly. Make this decision
      before 26b; it does not depend on the in-work rate being cleared.
      The dates must fall inside each policy's supported reference period,
      with the AS week before its 1 April 2027 amendment. Keeping annual
      and weekly results separate does not shorten WFF's evidence interval.
    - **28.3 — GPT/Codex; Claude Code reviews against the 28.1 sources.** Write the interaction contract into both
      `specification.md` files: which facts are shared (e.g. partner
      status and dependent children must agree between the two inputs),
      which outputs are excluded from the other policy's income, and
      which routes are gated.
    - **28.4 — Claude Code; GPT/Codex reviews.** Implement a combined household scenario runner: one set of
      canonical household facts in; `run_wff_module()` and
      `run_as_module()` results out; shared-fact consistency checks that
      return `needs_review` on disagreement, never pick one silently.
      This is the first `src/poltika/scenarios/` code, so update
      `REPOSITORY_STRUCTURE.md` before creating it. No dependency graph:
      that is v0.3.
    - **28.5 — split -- GPT/Codex hand-calculates the interaction spec cases (independent of the implementer); Claude Code writes the runners and regression tests.** Tests: hand-calculated interaction spec cases (e.g. a
      non-beneficiary household receiving both, proving neither
      payment enters the other's income; a gated route resolving
      `needs_review`), plus regression tests named for the specific
      leak each one prevents. Decide where cross-policy fixtures live
      and add that path to the statutory-value guard if it holds
      protected values.
    - **28.6 — cross-review -- Claude Code reviews 28.1/28.3 (sources, contract), GPT/Codex reviews 28.4/28.5 code; Pete accepts.** Fresh-context review by the non-implementer; Pete accepts.

    **Task 28 complete, 24 September 2026.** Claude Code did 28.3, 28.4
    and 28.5 on Pete's instruction to proceed without Codex input. Pete
    waived the cross-model rotation for Task 28 ("find the most obvious
    solution for these, accept and proceed"). Fresh-context Claude
    reviewers stood in for 28.6, and a GPT/Codex review remains welcome
    afterwards but is not a gate.
    - **28.3, the contract (PR #55; AS specification's "Task 28.3 WFF-AS
      interaction contract", with a WFF pointer).** The review corrected its
      claims of certainty: the partner, MC 6(b) and child checks are now
      conservative gates. It restored DEC-003's limits and left r 17(2)(f)
      unresolved. Pete's decisions:
      - two scenarios rather than one merged fact set;
      - community spouse not compared;
      - an existing `unsupported` is kept on a disagreement.
    - **28.4, the runner (PR #56; `src/poltika/scenarios/combined.py`, the
      first `scenarios/` code).** It keeps native periods, has no income
      coupling and no total, and adds the AS-claimant precondition fact. The
      shared-fact disagreements make components `needs_review`. Traces and
      the original module results are preserved. REPOSITORY_STRUCTURE.md
      gained a `scenarios/` dependency row, with a one-way no-cycle rule
      resolving a pre-existing table ambiguity.
    - **28.5, the cases (PR #57; `policy_specs/wff_as_interaction/
      spec_cases.yaml`, covered by the statutory-value guard's pattern).**
      Five hand-calculated cases, independently recalculated by the
      reviewer. They include a leak-sensitive household receiving both
      payments and a precedence case. There are regressions named for each
      income leak; injecting either leak into the runner fails them.
    - **Verified:** 336 passed, installed-artifact test passed, Ruff and
      strict mypy clean.
29. **Golden household test suite across both policies.** Unlike the
    per-policy spec cases, golden households run against the real
    approved policies with no parameter assumptions. Depends on 26a and 28.
    - **29.1 — GPT/Codex proposes the list; Pete approves.** Choose roughly 8-12 households
      spanning the supported domains, including: both policies
      `calculated`; one `calculated` and one excluded; the Schedule 4
      1-child/2-child household-category boundary; the partnered-income
      verification gates; one non-beneficiary with an income reduction.
      State for each why it is in the set.
    - **29.2 — GPT/Codex (independent of the 28.4/29.3 implementer).** Hand-calculate expected results independently of the
      implementation (author ≠ implementer, standalone workings as in Task
      13), in a protected YAML file watched by the statutory-value guard.
      Flag any case that relies on DEC-001's medium-confidence convention.
    - **29.3 — Claude Code.** A thin runner through the 28.4 scenario runner, with the
      same completeness guards (unique IDs, every component expected) as
      the per-policy suites.
    - **29.4 — Claude Code reviews the hand calculations via a fresh-context subagent (Task 24.4 precedent); Pete accepts.** Independent review of the hand calculations; Pete accepts.

    **Task 29 complete, merged 24 September 2026 (PR #59).** Claude Code did
    29.1-29.3 under Pete's delegation ("do all of this for me -- keep
    going"). There are nine households in
    `policy_specs/wff_as_interaction/golden_households.yaml`; the
    statutory-value guard now also watches `*/golden_households.yaml`.
    Expected values came from a standalone script over the policy files.
    The 29.4 fresh-context review recalculated all of them and approved. At
    its request, g6 was adjusted so that the one-child cl 2 cap binds. No
    household depends on DEC-001's convention.
30. **Cross-policy deterministic scenarios.** A scenario is a golden or
    ad hoc household plus modelled date plus requested policy versions.
    This task makes running one reproducible and identifiable. It adds no
    what-if parameter changes (v0.4).
    - **30.1 — Claude Code.** Define the scenario record: household facts,
      assessment periods and lookup dates from 28.2, requested
      `policy_version` per module, and an artifact manifest. Identify by
      content hash each policy file, source catalogue, applicable
      specification and decision artifact, plus the executable build and
      its dependency lock. Retain their bytes or retrievable immutable
      references with an explicit retention contract; a hash or version
      label alone is insufficient. A retained build or retained source
      revision with a reproducible build must support historical replay.
      For v0.1, a git commit SHA reachable from `main` (protected against
      force-push and deletion since Task 9), together with `uv.lock` at
      that commit, is an acceptable immutable reference for code and
      repository files. A separate artifact store is needed only for
      content not in git. The implementation must verify that the
      recorded hashes match the committed files actually used. A run
      made from an uncommitted or modified working tree cannot claim
      reproducibility from its HEAD commit alone. It must either retain
      those files or be recorded as non-reproducible.
    - **30.2 — Claude Code.** Canonical result serialization (stable key order,
      `Decimal` as string), and a scenario/result identity derived from
      the content hash of inputs plus the complete artifact manifest.
      Operational run IDs and timestamps sit outside the deterministic
      result payload. Source-only changes must change the manifest identity.
    - **30.3 — Claude Code.** Determinism tests: repeated runs and separate processes
      yield byte-identical output. Reordering inputs does not change the
      result.
    - **30.4 — Claude Code; GPT/Codex reviews all of Task 30.** Freeze the golden-household results as regression
      fixtures. An output change must be attributable to a named cause
      (parameter, rule, or code change), per ARCHITECTURE.md's
      change-attribution rule. No external dataset exists for v0.1
      (10a/22a); the retained artifacts and their hashes support replay.
      Hashes identify retained content; they do not replace snapshots.

    **Task 30 complete, merged 25 September 2026 (PR #60;
    `src/poltika/scenarios/record.py`).**
    - The scenario record, and an artifact manifest built from the run's own
      traces.
    - Code identity: commit, clean tree, `uv.lock` hash.
    - Canonical `scenario_id` and `result_id`.
    - `policy_files_committed`: every bound file equals its committed
      version. `reproducible` requires it together with a clean tree.
    - Determinism across processes.
    - 30.4 fixture `tests/fixtures/golden_results_v0_1.json`, with
      attribution of any change to the household's inputs, named policy
      artifacts, or code.

    The fresh-context review was cut off by the usage limit, so Claude Code
    reviewed it and found and fixed one gap (committed-file verification).
    An independent review afterwards is recommended.
31. **Full calculation provenance report.** Today a result carries its
    outcome, value and reason, but not which parameters and sources
    produced it (`ParameterResolution.source_id` exists in the loader but
    is not surfaced).
    - **31.1 — Claude Code drafts; GPT/Codex checks the rule-ID and source mapping against both specifications.** Define the provenance trace for each component: policy
      id, version and schema version; hashes identifying the artifacts
      used (the manifest later assembled in 30.1); every parameter
      used (id, value, unit, effective interval, `source_id`,
      `review_status`); every input used, with its verification status
      shown as the caller's assertion; specification rule IDs
      (`WFF-xx`, `AS-xx`) and any `DEC-xxx` applied; rounding steps; code
      version.
    - **31.2 — Claude Code.** Have the calculators emit that trace without changing any
      value or outcome. Preserve existing numerical and gating assertions;
      document any necessary response-shape changes. Existing tests check
      behavioural compatibility; 31.5 separately verifies trace correctness.
    - **31.3 — Claude Code.** Resolve each `source_id` against `sources.yaml` (title,
      URL, retrieval/check date), identifying the exact catalogue content
      used. Resolve rule IDs and decisions against the identified artifacts
      too; replay must not substitute current files. Location: `engines/assurance/`, per
      REPOSITORY_STRUCTURE.md ("provenance, regression, change
      attribution (v0.1)").
    - **31.4 — Claude Code.** Render the trace as machine-readable JSON plus a readable
      Markdown report. A UI is not required for v0.1.
    - **31.5 — Claude Code; GPT/Codex reviews; Pete accepts.** Per-policy tests
      and review land with 31.1-31.4, before that slice merges. Verify
      representative calculation paths record the actual parameters,
      inputs, sources, rules and rounding steps used, including calculated
      zero and gated paths. Every `calculated` value traces to a source;
      every used parameter has a resolvable `source_id`; every
      `needs_review`/`unsupported` result carries its reason. Check JSON and
      Markdown consistency and preservation of numerical/gating behaviour.

      **31.1-31.5 complete, merged 24 September 2026 (PR #40, merge commit
      `18e1ca5`).** Each `ComponentResult` carries a `ComponentTrace`
      (`engines/simulator/trace.py`). Recording wraps each component call,
      and the component functions are unchanged. `engines/assurance/
      provenance.py` builds the JSON and Markdown report. The loader binds
      hashes of `policy.yaml`, the source catalogue, `specification.md` and
      each `decisions/DEC-*.md` when it loads parameters. The report
      refuses a run whose bound files have changed, and refuses components
      from different scenarios. GPT/Codex's review found four issues, all
      fixed in `d3ed5d4` and confirmed on re-review:
      - F1: specification and decision files were read at report time
        rather than bound to the run.
      - F2: the report accepted components from different households.
      - F3: the r 19 wording overclaimed that no earlier step rounds.
      - F4: source-specific check evidence was omitted.

      Sources have no structured check-date field today, so the report
      shows `check_date` as not recorded rather than parsing free text. PR
      #41's `task_28_2_check.checked_on` fields are a follow-up for the
      report to read. **Done (PR #45, merged 24 September 2026):** a
      structured `checked_on` inside a mapping-valued check is reported per
      source; free text is never parsed. Merged without GPT/Codex's
      re-review of the final fix, on Pete's instruction to proceed without
      Codex input. PR #47 made `tests/conftest.py` strict-mypy clean. Verified on merged `main`: 249 passed, the
      installed-artifact test passed, Ruff and strict mypy clean.
    - **31.6 — Claude Code; GPT/Codex reviews; Pete accepts.** After 30, extend
      provenance tests to combined scenarios and their artifact manifests.
      Verify both assessment periods, interaction gates and report content
      are preserved. This adds combined coverage to the reviewed per-policy
      slice; it does not defer that slice's tests or review. **Done 25 September 2026:**
      `build_combined_provenance_report()` and `render_combined_markdown()`
      cover a scenario run's identities, reproducibility, manifest and
      disagreements, plus each policy's full report in its native period.
      The report refuses a manifest that does not match the files it
      verified, and a file changed after the run. Self-reviewed (usage
      limits); tests are mutation-checked.
32. **Scenario/version persistence.**
    - **32.1 — Pete decides; Claude Code drafts the ADR. Decided 24
      September 2026: option (a), PostgreSQL (ADR-0013, accepted; PR #39,
      merge commit `62884e5`).** Implementation starts with 32.2 in the
      approved sequence, after Task 30; no database scaffolding is added
      earlier. Storage: (a) PostgreSQL + SQLAlchemy 2
      + Alembic now, per ARCHITECTURE.md's recorded long-term stack and
      ADR-0010's go-straight-to-target precedent; or (b) an append-only,
      content-addressed file store behind a small repository interface,
      with Postgres deferred. The trade-off: (a) adds a database to local
      development, CI, and the ADR-0011 deployment convention; (b) is
      leaner but will be replaced.
    - **32.2 — Claude Code.** Model the immutable records: scenario, run (inputs,
      assessment periods, artifact manifest, result, provenance trace).
      Persist the artifacts from 30.1 or their retained immutable references
      and verify their hashes on retrieval. A run is never edited in place.
    - **32.3 — Claude Code.** Implement the store and migrations (if (a)).
    - **32.4 — Claude Code.** Tests: after current policy, source catalogue,
      specification/decision and code artifacts change, replay using the
      retained original artifacts reproduces the stored deterministic
      result and provenance exactly. Missing or hash-mismatched artifacts
      fail explicitly. A run requested against current artifacts creates a
      separate immutable run and reports drift, identifying changed
      artifacts even if monetary values stay equal. Never silently replace
      historical artifacts or overwrite the original run. Replaying after
      a *code* change means building the retained revision. The fast suite
      covers policy, source catalogue and specification changes. Code-change
      replay runs as an opt-in test, like `installed_artifact`, and is
      exercised at least once in 34.2.
      **Done 25 September 2026:** 32.2-32.3 in PR #63 (`ScenarioStore`,
      Alembic baseline, append-only content-addressed artifacts, hash checks
      on save and restore); code-change replay in PR #68
      (`tests/code_replay/`, run in CI), after the Task 34.3 review found
      it missing (F5).
    - **32.5 — GPT/Codex reviews.** Review; Pete accepts. **Pending:** Codex
      has not reviewed #63; covered by the GPT/Codex half of 34.3.
33. **API integration.** The per-policy routes (Tasks 21, 24.8) stay.
    - **33.1 — Claude Code.** A combined household route running the 28.4 runner and
      returning both modules' results plus the provenance trace, with
      the same caller-asserted-facts disclaimer as Task 21.
    - **33.2 — Claude Code.** Scenario routes: create, fetch, re-run (32).
    - **33.3 — Claude Code.** Consistent 422/409/500 mapping and no path or exception
      text in 500s (Task 21's finding), with tests at route level.
    - **33.4 — Claude Code; GPT/Codex reviews all of Task 33.** Extend the installed-artifact test (ADR-0011) to cover the
      combined route and persistence.
      **Done 25 September 2026 (33.1-33.4):** `/household/calculate` (PR
      #62); stored scenario routes create, fetch, replay and re-run (PR
      #64, `code_matches` added in #68); 404/409/422/503 and generic-500
      mapping tested at route level; the installed-artifact probe covers
      the combined route, migrations from the installed wheel, and stored
      scenarios. **Pending:** GPT/Codex review of Task 33 (34.3).
34. **End-to-end acceptance testing.**
    - **34.1 — Claude Code drafts; GPT/Codex verifies each row's evidence.** A traceability matrix: each Definition of Done bullet and
      the ROADMAP.md v0.1 exit gate, mapped to the test, review record, or
      decision artifact that evidences it. Any unevidenced bullet is a
      blocking gap. **Drafted 25 September 2026:**
      `review_packets/v0_1_traceability_matrix.md` (PR #65, updated in #68).
      D4's CI gap was closed by the Tests workflow (PR #66). **Every row
      was verified by GPT/Codex, 25 September 2026; all rows are evidenced.**
    - **34.2 — Claude Code.** An end-to-end test through the installed artifact:
      request → both modules → persistence → provenance report.
      **Done 25 September 2026 (PR #65):** the installed-wheel probe stores,
      fetches and replays a scenario and checks its provenance report
      against the stored manifest and the deployed file hashes.
    - **34.3 — cross-review -- GPT/Codex reviews the Claude Code-authored slices (28.4, 29.3, 30-33), a Claude Code fresh-context subagent reviews the GPT/Codex-authored slices (26a, 26b, 28.1, 28.3, 29.2).** A fresh-context adversarial review of the whole v0.1
      (both policies, the interaction, scenarios, and provenance) by the
      non-implementer, as in Tasks 17 and 24.4.
      Both reviewers inspect the complete end-to-end workflow and shared
      contracts as well as their assigned slices. A finding or fix touching
      a reviewer's own authored work requires the other model's independent
      check; ownership boundaries must not leave integration gaps unreviewed.
    - **34.4 — Pete confirms classifications; each fix routes to the slice's author.** Classify and resolve the findings under the Review
      Doctrine.
      **Claude half done 25 September 2026:** the Claude fresh-context review
      (`reviews/2026-09-25-task34-3-claude-fresh-context.md`) found 11
      findings (1 P1, 4 P2, 6 P3). Pete accepted the proposed
      classifications and fixes ("fix, accept and proceed"). Fixed in PR #67:
      F1 (beneficiary golden households and interaction cases: MD 14/15 and
      MG 4 protected months are `unsupported`; protected values changed with
      Pete's approval), F2 (protected-credit shared-fact gate), F3 (70% rate
      as a sourced parameter) and F7 (AS cases approved). Fixed in PR #68: F4,
      F5, F6, F8, F9 and F10. F11 (independence) routes to the GPT/Codex half
      of 34.3.
      **GPT/Codex half done 25 September 2026:**
      `reviews/2026-09-25-task34-3-codex.md` covers 28.4, 29.3, 30-33, the
      Claude 34.3 fixes, the F11 re-derivations (g2, g5, g6, g7, g9 and all
      five interaction cases, with no discrepancy), 34.1 row verification
      and the 35.3 wording (no change needed). There was one P3, C1 (missing
      review packets), which was resolved by adding
      `review_packets/task_28_3_interaction_contract.md`,
      `task_28_5_interaction_cases.md` and `task_29_4_golden_households.md`.
      Classification was accepted under Pete's delegation. **34.3 and 34.4
      are complete; 34.1 is verified.**
    - **34.5 — Pete.** Pete's acceptance of v0.1.
      **Accepted 25 September 2026:** Pete accepted v0.1 at `main`
      (`d307725`, including PR #79, whose GPT/Codex audit Pete waived).
35. **Demo: one real policy question, answered end-to-end.**
    - **35.1 — Pete decides; GPT/Codex proposes candidate questions inside both domains.** The question. It must sit inside both
      supported domains, and it must be chosen knowing 26b's outcome for
      the in-work tax credit. **Decided 25 September 2026 (Pete delegated:
      "do what you think is best"):** golden household g2, a couple with two
      children on $50,000 + $20,000 renting in Area 1 for $600 a week:
      "what WFF and AS does Poltika calculate, and does either reduce the
      other?" The in-work tax credit is reported as `needs_review` (26b).
      Beneficiary households were ruled out by the Task 34.3 F1 correction.
      No GPT/Codex candidate list was requested; Codex checks the wording in
      35.3.
    - **35.2 — Pete decides.** The demo surface: API plus the 31.4 report
      (recommended for v0.1), or a first Next.js screen per
      ARCHITECTURE.md's target stack. **Decided 25 September 2026
      (delegated):** the API plus the report, as recommended.
    - **35.3 — Claude Code runs and writes the walkthrough; GPT/Codex checks its limitations wording against both specifications.** Run it as a persisted scenario and produce its provenance
      report. Write a short walkthrough that states the result's
      limitations: conditional on caller-asserted facts, supported domain
      only. **Run and written 25 September 2026:** `docs/demo/v0_1/`
      (stored through `POST /scenarios` from clean commit `61564c3`;
      reproducible; replay `reproduced` and `code_matches`). GPT/Codex wording check done (no change needed; `reviews/2026-09-25-task34-3-codex.md`).
    - **35.4 — Claude Code.** Release: CHANGELOG, tag `v0.1.0`. The deferred v0.1.5 repo
      taxonomy rework starts after the tag, not before. **Done 25 September
      2026:** CHANGELOG finalised and `v0.1.0` tagged on the release PR's
      merge commit.

---

## Definition of Done for v0.1

- WFF + Accommodation Supplement both correctly modelled and benchmarked
  independently
- Cross-policy interaction verified
- Effective-dated, provenance-tagged POLICY_SPECS (schema v0.1, stress-tested
  by two structurally different policies -- Task 25 found no schema
  revision needed; amended from "schema v0.2" by Pete's Task 27.1(a)
  decision, 24 September 2026)
- Three-layer testing in place; statutory expected-value changes surfaced in
  PR CI and independently reviewed before merging (ADR-0007: visibility, not
  a merge gate) -- amended from "statutory values CI-protected", which
  predated ADR-0007, on Pete's delegation of 25 September 2026
- Any interpretation ambiguity encountered has a recorded decision artifact
  with evidence considered, rationale, decision owner and date
- One real cross-policy household scenario answerable end-to-end, deterministically,
  with provenance
- Minimum required external statistical datasets frozen as versioned,
  provenance-tagged raw snapshots and registered as regression fixtures, with
  no live statistical API dependency (Data Acquisition Doctrine) -- or,
  where a vertical needs none, a recorded determination to that effect
  (Tasks 10a and 22a both closed N/A; retained policy/evidence/build artifacts
  and their hashes support deterministic replay, Tasks 30 and 32) --
  amended by the Tasks 26a-35 refinement Pete approved on 24 September 2026
