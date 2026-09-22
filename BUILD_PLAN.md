# Poltika v0.1 Build Plan

**Date:** 20 September 2026
**Status:** FROZEN — workflow and roadmap discussion closed. Week 0 Tasks 8
and 9 are complete.

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

Superseded its original capability-sequence framing per ADR-0008 (2026-09-21):
v0.1 through v1.0 are now a fully versioned sequence, defined in full in
`ROADMAP.md` (scope and exit gate per release) — this section states the
sequence and the dependency reasoning behind its order, not the detail.

v0.1 (deterministic foundation) → v0.1.5 (evidence intelligence /
pilotability) → v0.2 (authoritative data foundation) → v0.3 (policy
interaction graph) → v0.4 (scenario engine) → v0.5 (uncertainty and
assurance) → v0.6 (Discovery engine) → v0.7 (Hypothesis engine) → v0.8
(long-term NZ system model) → v0.9 (decision-intelligence product) → v1.0
(production hardening) → beyond v1.0, an unnumbered capability-track
sequence (Economic Digital Twin, Physical NZ, Adaptive Digital Twin,
National Decision Intelligence).

**Why this order, not another:** v0.2→v0.3→v0.4 is strictly
dependency-ordered — no historical reconstruction or scenario comparison is
possible without real data (v0.2) and a dependency graph to propagate a
parameter change through (v0.3) before scenarios can be compared (v0.4).
v0.5 (Assurance) sits before Discovery/Hypothesis, not after: it hardens the
deterministic core — backtesting, sensitivity, stress-testing the v0.1–v0.4
Simulator/Scenario engine — before anything exploratory or uncertain is
allowed near it, the same "deterministic correctness before probabilistic
sophistication" principle as the frozen Scope Doctrine, applied one level
up. v0.6 (Discovery) before v0.7 (Hypothesis) is forced by logic, not a
style choice: a hypothesis cannot be tested before Discovery has proposed a
candidate relationship to test it against — the Simulator promotion gate is
`Discovery → Hypothesis → evidence → validation → human approval → model
specification → tests → Simulator`, and nothing re-enters the hardened
Simulator without passing all of it.

The Stats NZ API connector and equivalents are pinned to v0.2 (the
data-foundation release) rather than left unpinned — this resolves the
original doctrine's deliberate vagueness about "whichever later phase needs
it" now that v0.2 concretely is that phase, not a reversal of the
underlying principle that automation follows real need.

**v1.0 definition (testable, not aspirational):**
Poltika v1.0 can ingest a structured package of material fiscal and policy changes
represented within its supported NZ policy domains, propagate those interventions
through an effective-dated policy interaction graph, and produce reproducible
multi-year fiscal, distributional and selected economic/social outcome scenarios
with explicit assumptions, uncertainty and source-level provenance.

("Supported domain" status to be formally defined before v1.0 scoping: presumably
= has a versioned POLICY_SPECS entry, passes its benchmark tests, has been through
fresh-context review.)

**North star (not a release gate):** a progressively improving executable digital
twin of the New Zealand policy system.

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
21. Add API — gated on the pure calculator passing acceptance

### Week 3 — Accommodation Supplement
22. Complete AS specification
22a. Identify and freeze the minimum authoritative external statistical
    datasets AS actually needs (e.g. Stats NZ Statistical Area Unit geography
    data underpinning the AS-05 Area 1-4 lookup), each with full provenance
    and retrieval_method: manual_download — see Data Acquisition Doctrine
23. Implement pure AS calculator (consumes canonical Poltika variables only)
24. Repeat test/review process
25. Stress-test POLICY_SPECS schema against AS's different structure
    (housing costs, asset test, geography)
26. Revise schema → v0.2
27. Migrate WFF's spec files to v0.2
28. Test WFF + AS interaction
    (API/integration path reused from WFF — no re-litigating the pre-API gate
    now that the path is validated)

### Weeks 4–5 — Poltika v0.1
29. Golden household test suite across both policies
30. Cross-policy deterministic scenarios
31. Full calculation provenance report
32. Scenario/version persistence
33. API integration
34. End-to-end acceptance testing
35. Demo: one real policy question, answered end-to-end

---

## Definition of Done for v0.1

- WFF + Accommodation Supplement both correctly modelled and benchmarked
  independently
- Cross-policy interaction verified
- Effective-dated, provenance-tagged POLICY_SPECS (schema v0.2, stress-tested
  by two structurally different policies)
- Three-layer testing in place, statutory values CI-protected
- Any interpretation ambiguity encountered has a recorded decision artifact
  with evidence considered, rationale, decision owner and date
- One real cross-policy household scenario answerable end-to-end, deterministically,
  with provenance
- Minimum required external statistical datasets frozen as versioned,
  provenance-tagged raw snapshots and registered as regression fixtures, with
  no live statistical API dependency (Data Acquisition Doctrine)
