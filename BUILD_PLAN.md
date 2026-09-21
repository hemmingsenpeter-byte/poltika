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
    draft in PR #6; independent legal/content review and Pete's acceptance
    remain open. The draft is not an executable policy specification.
10a. Identify the minimum authoritative external statistical datasets the WFF
    vertical actually needs (beyond the legislated rates already captured in
    sources.yaml/specification.md, if any); manually acquire and freeze each
    as an immutable, versioned raw snapshot with full provenance
    (retrieval_method: manual_download) — see Data Acquisition Doctrine
10b. Build the transformation/validation layer mapping frozen raw snapshots
    to canonical Poltika variables; register each frozen snapshot as a
    regression fixture
11. Build parameter loader (consumes canonical Poltika variables only, never
    a source-specific representation)
12. Build pure `calculate_wff()` function
13. Build spec tests
14. Build benchmark tests (against independently published IRD examples)
15. Build regression tests, including the frozen dataset-snapshot fixtures
    from Task 10b: same scenario + same snapshot must yield the same
    deterministic result
16. External coverage-gap check (OpenFisca test names, strictly after suite
    completion) — return to primary sources for any gap found
17. Independent adversarial review (fresh-context, no implementer explanation)
18. Classify discrepancies
19. Resolve ambiguities, record decision artifacts (where genuine ambiguity exists)
20. Integrate into simulator
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
