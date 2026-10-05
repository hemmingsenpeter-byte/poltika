# Poltika household economic model: detailed v0.3 lane

**Date:** 26 September 2026
**Status:** Active supporting plan for the household economic model.
Originally approved 26 September 2026 with ADR-0015. ADR-0021 re-homes its
tasks under the sole master build order,
[BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md). Scope remains personal
income tax, Jobseeker Support, Sole Parent Support and Supported Living
Payment, with each supported slice established from primary sources.

**Starts:** Phase B's bounded household-model task can proceed on the merged
WFF/AS baseline after the relevant Phase A review checks. It does not wait
for a v0.2 tag, national microdata access, a universal registry, `NZState` or
all old foundations tasks. Each new policy still requires its own sourced
specification, reviewed mapping and retained Pete decisions before
implementation. Local "Phase 0" below means policy source scoping, not a
programme-wide infrastructure prerequisite.

**Programme mapping (3 October 2026, ADR-0021):**

| Existing task group | Active capability phase | Scope |
| --- | --- | --- |
| Local 0, 1, 2–5 | B | Source scoping, bounded semantics, shared household model, income tax, three main benefits, household graph, disposable income and incentives |
| Local 1b | B/C; population extensions E | Reuse delivered intake/conditional-answer work; finish only what the current analytical slice requires |
| Conformance, benchmark validation and analyst presentation | C | Bring assurance into the household analytical workflow; complete the existing workbench surface |
| Local 6 | E | Survey adapter and secure-environment population pipeline; 6.4 can support development checks earlier |
| Local 7 | Release closeout at demonstrated gates | Preserve versioned evidence and Pete's tagging authority; releases do not set the master sequence |

All task identifiers and historical progress below are retained. The old
ADR-0019 mapping to lanes 3A and universal foundations is historical; its
execution sequence is superseded. The review-debt cap remains suspended
under the retained P17 decision, subject to ADR-0020's review requirements.

**Next coding task:** local 1.1–1.3 only: the canonical household model and
reviewed mappings to the existing WFF and AS inputs. Every existing golden
household, spec case, golden result and result ID must remain byte-identical.
Keep today's request formats as adapters and retain meaningful
contradiction checks. New calculators and the graph follow their own
source/review gates; this task creates no national state or universal schema.

`BUILD_PLAN.md`'s doctrines apply unchanged: primary sources only, the
three test classes, protected values changed only through the test
doctrine, ambiguity escalated, and no external implementation as a source
of policy logic. Every statutory rule, rate, threshold and interaction
below is established by a phase's sourcing task. This plan names none of
them.

## Household capability this lane delivers

v0.2 runs two policies that don't feed each other (AS-10, WFF DEC-003).
v0.3 starts the **deterministic policy kernel**: one engine that turns a
household's state into its fiscal position under a policy configuration,

`household state → policy dependency graph → household fiscal position`

with source-derived relationships between calculations. A scenario compares
the same household under baseline and reform settings. Population and
fiscal estimates extend this analysis under the later Phase E/F gates;
they are not prerequisites for Pilot 1.

The target calculation shape is roughly:

`gross earnings → income tax → main benefits → WFF → AS → (Tier 2: childcare and supplementary assistance) → disposable income`

The actual order is whatever the source-derived edges (Phase 0.3) make
it. That shape is the aim, not an assumed rule. Phase B delivers:

1. **Personal income tax** on the income types the v0.2 household types
   have.
2. **The three core main benefits**: Jobseeker Support, Sole Parent
   Support and Supported Living Payment (Tier 1).
3. **One household model** with named, reviewed mappings to the existing
   per-policy input types, preserving today's request adapters and results.
4. **A household-level dependency graph** whose edges come only from the
   specifications, so one policy's output feeds another's input in a
   stated, explained order.
5. **Disposable income** for supported households, and with it the
   measures v0.2 couldn't offer (R3): effective marginal tax rates, and
   income-adequacy measures on a sourced definition.

Phase C brings conformance and benchmark validation forward: every rule in
the supported slice has golden, boundary, contradiction and regression
cases, linked to primary sources. The approved epistemic constitution and
ADR-0020 apply throughout. Semantic contracts grow only for the units,
periods, entities and variables current household calculations require;
an exhaustive registry, universal quantity wrapper or general evidence graph
does not block this lane.

The real-data pipeline remains local Phase 6, delivered under programme
Phase E. It runs inside the relevant approved secure environment and exports
only checked aggregates. Existing synthetic development machinery is reused
with its explicit label and limitations.

**Beyond this household lane:**

- dynamic national scenarios and `NZState` (programme Phase K);
- formal uncertainty propagation, Monte Carlo and behavioural mechanisms
  (Phase J), while current assumptions and unknowns remain visible;
- historical policy/data states and `as_of` replay (Phase I);
- wider revenue and firm domains (Phases H/L as analytical demand requires);
- the other household domains (Temporary Additional Support, Disability
  Allowance, childcare subsidies, NZ Super, Paid Parental Leave, student
  support, ACC levies, KiwiSaver and the rest). Phase H orders them by real
  analytical demand rather than implementing a coverage list mechanically.

## Phases

### Phase 0: policy source scoping (programme Phase B)

- **0.1 — GPT/Codex. Source-scope income tax.** Define the smallest
  supported slice: which income types, which tax year, which
  withholding or annual-assessment basis, and what is out of scope,
  each with primary sources. Record a v0.1-style source pack in
  `policy_specs/income_tax/sources.yaml`.
- **0.2 — GPT/Codex. Source-scope the three core main benefits**
  (Jobseeker Support, Sole Parent Support, Supported Living Payment). For
  each, record its eligibility gates, rate categories, partner and family
  treatment, and income abatement, with a v0.1-style source pack. Set the
  implementation order (proposed: Jobseeker Support, Sole Parent Support,
  Supported Living Payment), unless the sources show a dependency that
  changes it.
- **0.3 — GPT/Codex, Pete deciding. Record every interaction the
  specifications state:**
  - what counts as income for each income test;
  - what is taxable;
  - what each policy excludes.

  Each gets a decision record where the law is ambiguous. These become
  the graph's edges (Phase 4). Restate in the same form the ones the
  specifications already record:
  - WFF-08: a main benefit with family tax credit and Best Start, but
    normally not the in-work or minimum family tax credits;
  - the WFF "Earner and benefits" row;
  - WFF MB 1-2's allocation of main-benefit income into family scheme
    income;
  - AS's claimant-category thresholds by benefit ("Claimant rate class");
  - AS-10 and WFF DEC-003.

  Then add each new one from sources, including which government
  payments enter which income test, and whether and how each main benefit
  is taxed.
- **0.4 — Pete. Confirm each domain's supported slice (D1)**, and the disposable-income
  definition used for measures. It must be a sourced definition (for
  example an official statistical one), recorded as a decision, not
  assumed.
- **0.5 — Claude Code.** Apply the onboarding skill (W2.2) to plan each
  policy's tasks, with the W2.1 cost baseline as the estimate.

### Phase 1: shared household model (programme Phase B; ADR-0017)

- **1.1 — Claude Code. Canonical household model** in `semantics/`:
  persons, family and household, holding each fact once (partner status,
  children and their ages, income by type, housing costs, benefit
  receipt). It extends v0.2's population schema, and population records
  read it directly.
- **1.2 — Claude Code, reviewed by GPT/Codex. Per-policy mappings.** Each
  policy's input is derived from the household model by a named mapping
  function. The mapping for WFF and AS reproduces today's `WffScenario`
  and `AsScenario` exactly.
- **1.3 — Claude Code. Byte-identical proof.** Every golden household,
  spec case and golden snapshot runs through the new path with
  identical results and result ids. The existing request formats stay
  as adapters onto the household model.
- **1.4 — Claude Code.** Retire the Task 28.3 pairwise contradiction
  checks only where the single-fact model makes them impossible. Any
  check that still means something (for example two agencies' different
  definitions of the same concept) is kept and named.

### Phase 1b: intake questions and conditional answers (ADR-0016)

Built on WFF and the Accommodation Supplement first, so every Tier 1
domain is born with it. Each task below lists its subtasks, the owner,
and a "done when" a reviewer can check. The PR grouping follows the
working agreement: one PR per kind of review, review findings fixed in
the same PR.

- **1b.1 — Fact catalogues.** `policy_specs/<policy>/facts.yaml` for WFF,
  the Accommodation Supplement and the combined run. Each entry has an id
  matching the engine's `missing_facts`, a plain-language question,
  admissible values, the governing rule id, and optional per-component
  monotonicity with its rule id.
  - **1b.1a — Claude Code. Schema and completeness tests.** Done (#109):
    `FactEntry`/`FactCatalog`, the loader, and tests that every emitted
    id has an entry, every entry is emitted, domains match the engine
    fields, and rule ids exist.
  - **1b.1b — GPT/Codex. Wording review.** Check every question against
    its rule: it asks for exactly the fact the rule tests, it doesn't
    lead toward an answer, it names the period and person, and each
    admissible value reads as a plain answer. Record findings in
    `reviews/`, fix them in the same PR, then set `wording_status:
    reviewed`.
    *Done when:* all three catalogues are `reviewed`, and a review record
    names the reviewer and each change.
  - **1b.1c — Claude Code. Gate on wording.** A release-gate row fails if
    any catalogue a release ships is still `drafted`.
    *Done when:* the row exists and the v0.3 gate test runs it.
- **1b.2 — Conditional answers** (`scenarios/conditional.py`).
  - **1b.2a — Claude Code. Finite branches.** Done (#109): joint branches
    over finite missing facts, impact-ranked expansion, the 32-branch cap,
    per-component and WFF-total bounds, and `next_question`.
  - **1b.2b — Claude Code (schema, evaluation), GPT/Codex (declarations).
    Numeric ranges.**
    - Add `monotone: {<component>: {direction: increasing | decreasing,
      rule: <rule id>}}` to `FactEntry`, allowed only on numeric kinds
      (money, count).
    - GPT/Codex declares it only where a cited rule implies it (for
      example family tax credit decreasing in family scheme income above
      the threshold, WFF abatement rule). A declaration without a rule id
      fails the schema.
    - `resolve()` takes caller-supplied ranges (`{slot: (low, high)}`).
      For a component declared monotone in every ranged fact, it runs the
      endpoint corners and reports true bounds. Otherwise it runs the
      chosen points and labels them "values at these points, not bounds".
      With no range, the fact stays listed as missing with no branch.
    - A range with low above high, a negative money value, or a
      non-integer count is refused.
    *Done when:* ranges produce bounds only for declared components, and
    `Bounds` records which kind (true bounds or points) it holds.
  - **1b.2c — GPT/Codex (candidate values), Claude Code (branching).
    Unresolved parameters.**
    - Today the only candidate record is prose: `in_work_base` 2026-27 is
      `needs_review` at 7670, and its note says s 105(2) may reverse it
      to 5070. GPT/Codex adds a structured `candidates` list to that
      value row (each value with `source_id`, `locator` and the condition
      it depends on). That changes a protected file, so it goes through
      `doctrine/test-doctrine.md`.
    - Claude Code extends the loader to read `candidates`, and `resolve()`
      branches over them with a parameter override, one branch per
      candidate, each labelled a scenario assumption naming the
      condition. Nothing without a recorded candidate is branched.
    - The branch outcome stays `needs_review`. A candidate branch is never
      `calculated`, even if the rest of the run is.
    *Done when:* a household blocked only by the unresolved in-work base
    gets two labelled branches (7670 and 5070) and a range, and a
    parameter with no `candidates` still gives a bare `needs_review`.
  - **1b.2d — Claude Code. Rendering.** A plain-language summary of a
    `Resolution`: "Poltika can't give one figure without X. If X is …,
    the result is …", built from catalogue labels and branch values only,
    with the explanation-verification pattern v0.1.5 uses.
    *Done when:* every rendered figure is checked against its branch
    result by a test.
- **1b.3 — Claude Code. Differential and property tests.**
  - **1b.3a** Done (#109): every branch equals a direct engine run with
    that fact supplied, every branch explanation verifies, the base
    result is never changed, and the cap holds.
  - **1b.3b** Hypothesis: for each declared monotone component, any value
    drawn inside a range gives a result within the reported bounds, and
    the declaration itself holds (the result moves only in the declared
    direction across the fact's domain) on generated households.
  - **1b.3c** No conditional result is ever `calculated`: a test sweeps
    every golden household with each fact removed in turn and checks the
    blocked components' outcomes.
  - **1b.3d** Totals are summed only within one joint assignment: a test
    builds a household where the per-component extremes come from
    different assignments, and checks the total's bounds are narrower
    than the sum of the component bounds.
  - **1b.3e** Candidate branches (1b.2c) each equal a direct run with the
    parameter overridden to that candidate.
  *Done when:* all five run in CI.
- **1b.4 — Claude Code. Intake planner** (`scenarios/intake.py`).
  - **1b.4a** `next_step()`: given partial facts, the asked components
    and the declined facts, return `ready`, `ask` (with the next
    question) or `incomplete`. Order: finite facts that unblock an asked
    component, by impact; then numeric facts, in catalogue order; then
    the remaining finite facts. Ties go by specification rule order.
    (Implemented locally, with `Resolution.ranked` and
    `Resolution.unblocks` added to `conditional.py`.)
  - **1b.4b** `apply_answer()`: record an answer typed as the engine field
    requires. Finite facts are checked against the domain, attestations
    take yes (otherwise the fact is declined), counts take a whole number,
    and money takes a
    non-negative amount, and a partner's family scheme income needs the
    claimant's first. An inadmissible answer is refused, never coerced.
  - **1b.4c** "Don't know" is `declined`: never asked again, never
    defaulted, and distinct from never asked. When only declined facts
    block, the planner returns `incomplete` and the caller gets
    `resolve()`'s conditional answer.
  - **1b.4d** Tests:
    - the question order is deterministic (same input, same question);
    - for every golden household, removing its facts and answering the
      planner's questions from the golden values reaches `ready`, with a
      result identical to the golden run;
    - declining a fact gives `incomplete`, and the resolution matches a
      direct `resolve()`;
    - inadmissible answers are refused for each kind.
  *Done when:* those tests pass.
- **1b.5 — Claude Code. API and page.**
  - **1b.5a** `resolution` on calculation responses
    (`api/household.py`, and `api/wff.py` and
    `api/accommodation_supplement.py` for their own components): present
    only when something is missing. Existing fields and result ids are
    unchanged, so stored runs replay byte-identically.
  - **1b.5b** `POST /household/intake`: takes the household so far, the
    asked components and the declined facts, and returns the next
    question (id, catalogue wording, admissible values, rule id), `ready`
    or `incomplete` with the resolution. It is stateless: the caller
    sends everything each time.
  - **1b.5c** Answer route or field: an answer is validated with
    `apply_answer()`, and an inadmissible one gets a 422 naming the
    admissible values.
  - **1b.5d** The analyst page asks the questions first, then shows
    branches, ranges and the next question, labelled as conditional. The
    page and any LLM front end only phrase catalogue questions and map
    replies to admissible values, with confirmation. They never choose
    values or calculate (`doctrine/llm_boundaries.md`).
  - **1b.5e** API tests (every route, each status, a 422) and an
    acceptance test driving a golden household to `ready` through the
    routes.
  *Done when:* those tests pass and the OpenAPI schema lists the new
  route and field.
- **1b.6 — Claude Code. Population ranges.**
  - **1b.6a** For each `needs_review` household, the runner computes
    `resolve()` bounds (baseline and reform, same assignments). Bounds
    are computed only for those households.
  - **1b.6b** The fiscal summary reports three things, always separately:
    the calculated weighted total, the low-to-high weighted range from
    boundable `needs_review` households, and the unboundable weight. They
    are never added together.
  - **1b.6c** Explanations and the microsim page show the range with its
    household count, labelled synthetic until real data runs.
  - **1b.6d** Tests: the calculated total is unchanged from v0.2 on the
    synthetic population; the range brackets each household's own
    bounds, weighted; the three figures reconcile to the population's
    total weight.
  - **1b.6e** Performance: a scaling check against
    `docs/releases/V0_2_SCALING_MODEL.md`, with the extra cost reported.
  *Done when:* those tests pass and the run stays within the scaling
  model's budget, or the overrun is recorded.

**PR grouping for the rest of Phase 1b:**

1. Intake planner (1b.4), with 1b.3c.
2. Wording review (1b.1b), GPT/Codex.
3. Monotone declarations and candidate values (the GPT/Codex parts of
   1b.2b and 1b.2c): a protected-value PR.
4. Numeric ranges, candidate branching and rendering (the Claude Code
   parts of 1b.2b-1b.2d), with 1b.3b, 1b.3d and 1b.3e.
5. API and page (1b.5).
6. Population ranges (1b.6). This builds on v0.2's merged runner and
   doesn't wait for v0.2's release.

PRs 2 and 3 can be written while PR 1 is in review.

### Phase 2: income tax (v0.1 method)

Follow the `new-policy` skill's five PRs. Each subtask is one of them,
and the skill's table sets its exit check. Income tax is born on the
Phase 1 household model and with its Phase 1b fact catalogue.

- **2.1 — GPT/Codex. Sources and specification (PR 1).**
  `policy_specs/income_tax/sources.yaml` from 0.1; `specification.md`
  with rule ids (`IT-NN`) for the supported slice (income types, tax
  year, basis); a decision record for every ambiguity; out-of-scope
  cases listed, each mapped to `unsupported` with a category.
  *Done when:* every rule row cites a rank 1-2 source, and Pete has
  decided every decision record.
- **2.2 — GPT/Codex. Values and expected results (PR 2).**
  - `policy.yaml`: dated brackets and rates, each with `source_id`,
    `locator` and `review_status`, and a rate-status contract for any
    rate that can change mid-year, with candidate values (1b.2c).
  - `facts.yaml`: every input fact, with question, admissible values,
    rule id, and monotonicity where a rule implies it (tax is
    non-decreasing in taxable income).
  - `spec_cases.yaml`, hand-calculated with no code: each bracket
    boundary, $1 either side, zero income, and each out-of-scope case.
  - `benchmarks.yaml` from Inland Revenue worked examples.
  *Done when:* the evidence report has no problems, the currency report
  shows nothing due, and every bracket boundary has a case.
- **2.3 — Claude Code. Implementation (PR 3).**
  - `engines/simulator/income_tax.py`, reading the household model
    through a named mapping (1.2).
  - `record_step` calls and `STEP_TEMPLATES` entries for each step;
    reason codes and categories.
  - Unit, spec-case and benchmark tests; the fact-catalogue
    completeness test extended to income tax; golden households (single
    earner, two earners, each boundary).
  *Done when:* every spec case and benchmark passes, `verify()` holds for
  every result, and the catalogue test covers every emitted fact.
- **2.4 — GPT/Codex specifies, Claude Code implements. Interactions (PR
  4).** The Phase 0.3 edges income tax takes part in (for example which
  benefits are taxable income), as graph edges citing their rule. It
  lands with Phase 4 if the graph runner isn't ready.
  *Done when:* every edge cites a source, and existing WFF and AS results
  are unchanged.
- **2.5 — Claude Code. Release (PR 5).** Gate rows, CHANGELOG,
  limitations, the README coverage row, the maintenance line (W5.4) and
  throughput actuals (W2.5) in this plan's Progress table.
  *Done when:* the implemented slice's checks pass and any outstanding
  release rows are named. A release gate with skips remains unmet.

### Phase 3: the three core main benefits (v0.1 method)

The same slice for each benefit in Phase 0.2's order, each as the
`new-policy` skill's five PRs, pipelined (W2.4). GPT/Codex specifies the next
benefit while Claude Code implements the current one. Each benefit's
golden households cover single, couple and sole-parent cases, and at
least one where the benefit's result changes another policy's input.

- **3.1 — Jobseeker Support.** 3.1.1 sources and specification (`JS-NN`)
  → 3.1.2 values, `facts.yaml` and expected results (rate categories,
  partner and family rates, each abatement threshold $1 either side) →
  3.1.3 implementation → 3.1.4 interactions (AS claimant category, WFF
  main-benefit rules, taxable income) → 3.1.5 release.
- **3.2 — Sole Parent Support.** The same five steps (`SPS-NN`). 3.2.1
  starts when 3.1.1 is decided. The eligibility gates on the youngest
  child's age are finite facts in `facts.yaml`, never inferred from other
  ages.
- **3.3 — Supported Living Payment.** The same five steps (`SLP-NN`).
  3.3.1 starts when 3.2.1 is decided. Medical and capacity criteria stay
  asserted facts with catalogue questions; Poltika never assesses them.
- **3.4 — Claude Code. Cross-benefit checks.** A household can't receive
  two main benefits at once unless a specification says otherwise: a
  test over the golden households, and an intake question when the
  household model leaves it open.

For each benefit, *done when* is the skill's exit check for each of its
five PRs, with throughput recorded in the Progress table.

### Phase 4: household dependency graph (programme Phase B)

- **4.1 — Claude Code.** A graph of policy calculations per household.
  Each edge is one Phase 0.3 interaction, citing its decision record or
  rule id. There are no edges without a source.
- **4.2 — Claude Code.** Order the graph topologically. A cycle is refused
  (`unsupported`, with the cycle named) unless a specification defines
  how the law resolves it, in which case that resolution is implemented
  and tested as its own rule.
- **4.3 — Claude Code.** Carry outcomes along edges. A `needs_review` or
  `unsupported` input makes every dependent result the same, with the
  chain named in its reason. It is never zero.
- **4.4 — Claude Code.** Explain dependency chains: "this benefit fell by
  X because taxable income rose by Y (rule …), which …". Explanations are
  tested against the calculation, as in v0.1.5.
- **4.5 — Claude Code.** The combined runner becomes the graph runner.
  WFF and AS, which have no edge between them, keep byte-identical
  results.
- **4.6 — Claude Code. Calculated, not asserted.** Facts that WFF and AS
  take today as asserted inputs, and that a Tier 1 domain now calculates,
  come from the graph instead:
  - the AS claimant category (which benefit, or non-beneficiary);
  - WFF benefit-status and earner facts, as far as the specifications
    define them.

  An asserted value that contradicts the calculated one is a
  `needs_review` contradiction, as in Task 28.3, never silently
  overridden.

### Phase 5: disposable income and measures

- **5.1 — Claude Code.** Disposable income per household on the Phase
  0.4 definition, with its components listed and its coverage reported.
- **5.2 — Claude Code.** Effective marginal tax rates along an income
  path, now across tax and transfers. This replaces v0.2's per-policy
  withdrawal rates where every component is modelled, and resolves v0.2
  D9 through the household model's single income.
- **5.3 — GPT/Codex, Pete deciding.** Which income-adequacy measures to
  report, each on a sourced official definition, as decision records.
  None is invented.
- **5.4 — Claude Code.** Add those measures to the population analysis
  and explanations, with coverage.

### Phase 6: real-data pipeline (programme Phase E)

Tasks 6.1–6.3 serve representative population analysis. They are not Phase B
or Pilot 1 prerequisites. Their historical W3 references identify the
archived source of the workstream; current governance and source-derived
disclosure rules still apply. Task 6.4 may support earlier development
checks, with every output retaining the synthetic label.

- **6.1 — Claude Code. Secure-environment runner.**
  - 6.1a A runner entry point with no network access (it refuses to
    start if a socket can be opened) and no repository writes.
  - 6.1b The population path from configuration, never from the
    repository or a default.
  - 6.1c Aggregate-only export: the only writer takes checked tables
    (6.2). A test proves no household-level record can reach it.
  *Done when:* those tests pass in CI with a synthetic population.
- **6.2 — Claude Code, rules from W3.1. Output checks.** Minimum cell
  counts, rounding and dominance rules, implemented from W3.1's published
  rules with each rule cited. A table that fails is suppressed with a
  reason, never altered.
  *Done when:* each rule has a failing and a passing test table.
- **6.3 — Claude Code, reviewed by GPT/Codex. Survey adapter** onto the
  household model: a documented field mapping, with each unmapped or
  derived field named, and a fact left unknown (never defaulted) where
  the survey doesn't record it, so it flows to `needs_review` and to
  population ranges (1b.6).
  *Done when:* GPT/Codex has reviewed the mapping, and a round-trip test
  on synthetic survey-shaped records passes.
- **6.4 — Claude Code. Synthetic population** extended to income tax and
  the three benefits' facts, with every result keeping the synthetic
  label until real data runs.
  *Done when:* a population run covers every Tier 1 component.

### Phase 7: release closeout

- **7.1 — Claude Code. Release-gate test.** A later bounded alignment PR
  maps the existing executable rows to the B/C/E capability gates below,
  including the review-queue and 1b.1c wording rows. Retain the current
  skips until their capabilities are implemented and verified.
- **7.2 — Claude Code. Release documents.** CHANGELOG,
  `docs/releases/` limitations, the maintenance line per policy (W5.4),
  throughput actuals (W2.5), and the README coverage table.
- **7.3 — Pete.** Tags `v0.3.0`.

## Progress

The following table preserves the Phase 1b implementation record assembled
from 26 September 2026 onward, including contemporary local/PR states.
It is historical task evidence, not the current queue. Use
[PROGRAMME_STATUS.md](PROGRAMME_STATUS.md) and
[review_packets/review_queue.md](review_packets/review_queue.md) for live
status. In particular, the old review cap is suspended; v0.2 implementation
and reviews are complete while its release tag remains outstanding; and
#128's conditional-summary review was completed and closed by #152.

Pete authorised Phase 1b on 26 September 2026 after the queued-PR audit.
That work reused WFF/AS without waiting for a v0.2 release or new-policy
source scoping. Keep its completed work under the new programme.

| Task | State |
| --- | --- |
| 1b.1 | 1b.1a done (#109): catalogues for WFF (17 facts), the Accommodation Supplement (11) and the combined run (1), with completeness tests. Writing them found three emitted facts with no entry: `mc6a_veterans_payment`, `mc6b_disqualifying_payment` and `net_family_scheme_income_me3_attested`, the last a new non-branchable `attestation` kind. 1b.1b done (#112): GPT/Codex reviewed all 29 questions (`reviews/2026-09-27-pr109.md`), and all three catalogues are `reviewed`. 1b.1c done: `tests/acceptance/test_v0_3_release_gate.py`, started with the wording row (every shipped `facts.yaml` must be `reviewed`), a skip per exit-gate row whose phase isn't built, and the review-queue row. |
| 1b.2 | 1b.2a done (#109; #112 fixed contradictory hypothetical answers and re-ranks newly revealed facts under the cap). 1b.2b Claude Code part done: `FactEntry.monotone` (money and count only, each with a rule id), `resolve(ranges=...)` branching at each range's endpoints jointly with the finite facts, and `Bounds.kind` (`bounds` only where every ranged fact is declared monotone for the component, otherwise `points`), shown on the API and page. **No real catalogue declares monotonicity yet: GPT/Codex adds the declarations from cited rules.** Ranges aren't yet accepted by the API. 1b.2c (candidate values) waits on a structured `candidates` list from GPT/Codex. 1b.2d done: `scenarios/conditional_text.py` renders "Poltika can't give one figure without …", each answer's amounts, the ranges and the next question; `verify()` checks every figure against the branches and bounds. `resolution.summary` on the API (a failing verification is refused, never shown); "In words" on the analyst page. |
| 1b.3 | 1b.3a done (#109). 1b.3b done: Hypothesis checks that three candidate declarations hold against the engine (FTC never rises with family scheme income; AS never rises with weekly income, never falls with housing costs) and that any value inside a range stays within its bounds. These are test fixtures, not catalogue declarations. 1b.3c done: removing each supplied fact from every golden household never leaves a blocked component calculated. 1b.3d done structurally (the WFF total's range comes only from joint assignments); no v0.1 branch has a WFF total while the in-work tax credit is needs_review. 1b.3e waits on 1b.2c. |
| 1b.4 | Done (PR held under the review cap): `scenarios/intake.py` with `next_step()` and `apply_answer()`; `Resolution.ranked` and `unblocks` in `conditional.py`. Tests: each catalogued fact a golden household supplies is removed and restored through the planner to the exact golden result and step; determinism; asked components; declined gives `incomplete`; inadmissible answers refused per kind. An attestation takes only "yes" (one that can't be given is declined, or the planner would ask again). 1b.3c not yet added. |
| 1b.5 | 1b.5a, 1b.5b, 1b.5d and 1b.5e done: `/household/calculate` adds `resolution` when a component waits for a fact (branches with labelled assignments, bounds, next question; stored-run responses unchanged). `POST /household/intake` is stateless: the household as entered, the answers so far in order, the declined facts and the asked components; it returns `ask`, `ready` or `incomplete` with the calculation so far. An inadmissible answer, unknown fact label or missing child is a 422 naming the problem (1b.5c, as an `answers` field rather than a separate route). The analyst page's "Ask me first" asks the catalogue's questions one at a time with a "Don't know", then shows the result and the conditional answer; checked in Chromium on pilot case p11 (area unknown), both paths. |
| 1b.6 | Done: `scenarios/microsim/ranges.py` `population_ranges()` over a finished run (run_id, results and calculated totals unchanged). Each needs_review household is resolved under the baseline, and each branch's assignment rerun under the reform; a household is bounded for a component only when every branch is calculated in both runs and the cap isn't reached. Reports the calculated change, the weighted range of change (and of baseline amount) from bounded households, and the unboundable weight, reconciled with the unsupported weight to the run's total. `/microsim/runs` returns `fiscal_ranges`; the Fiscal tab shows them apart from the totals. On the synthetic development population nothing is boundable yet (every fact is asserted; the in-work and minimum family tax credits are unboundable), and ranges add about 1 s to a 6 s run. |

## Sequence

This is the bounded lane sequence under the master programme, not a second
programme order. Source research can proceed alongside the initial mapping
work; each new calculator waits for its own source and decision gates.

| Sprint | Work |
| --- | --- |
| 0 | Next coding task: 1.1–1.3 canonical household and reviewed WFF/AS mappings, with byte-identical results and IDs; source scoping 0.1–0.4 alongside it |
| 1 | Complete meaningful 1.4 checks; reuse Phase 1b; Phase 2 sources and specification |
| 2 | Phase 2 implementation; Phase 3 sources and specification (pipelined, W2.4) |
| 3 | Phase 3 implementation; Phase 4 |
| 4 | Phase 5; Phase C assurance and analyst workflow |
| 5 | Close demonstrated release gates through Phase 7; external Pilot 1 under programme Phase D |
| Later E | Phase 6 representative-population pipeline and survey/secure-environment work |

## Capability gates and retained release checks

The household gate below maps to programme Phase B; conformance and analyst
assurance extend it in Phase C. The population and secure-environment rows
belong to Phase E. A household-level Pilot 1 does not depend on those rows.

**Executable gate status:** `tests/acceptance/test_v0_3_release_gate.py`
still implements the original release rows: catalogue wording, explicit
skips for the unbuilt household/population/secure-environment capabilities,
and the review-queue check. This documentation migration changes none of
those tests and does not claim the capability gates are executable or met.
A later bounded PR must align the release checks with the new B/C/E gates,
retain independently reviewed expected values, and explain every remaining
skip. A green run containing those skips is not release acceptance.

- **Every modelled component** can say what it is missing: each
  `missing_facts` id has a catalogue question. An unresolved household
  gets branches or bounds instead of a bare `needs_review`, and the
  intake planner's questions reach a full calculation for every golden
  household.
- **Income tax and all three core main benefits** are specified,
  implemented, independently reviewed and benchmarked to v0.1's
  standard.
- **The kernel household** is a golden household built from the
  realignment example:
  - a couple aged 32 and 30;
  - children aged 1 and 4;
  - earnings of $48,000 and $15,000;
  - rent of $650 a week;
  - a verified AS statistical area unit (the AS spec forbids inferring
    an area from a city name such as "Auckland");
  - childcare of 25 hours a week;
  - cash assets of $5,000.

  It runs through the kernel to a disposable-income result. Every
  modelled component is calculated or explained, and components outside
  Tier 1 (childcare assistance) are `unsupported` with a named reason,
  never zero. GPT/Codex hand-calculates its expected values
  independently.
- **Every golden household** runs through the shared household model and
  the dependency graph. WFF and AS results are byte-identical to v0.2.
- **One policy's output feeds another's input.** For a household where
  that happens, the chain is calculated in source-derived order and
  explained, and the explanation is verified against the calculation.
- **Disposable income and effective marginal tax rates** are produced for
  supported households, with coverage reported. `needs_review` is never
  counted as zero.
- **Phase E: a population run** reports disposable-income changes by decile and
  household type for a reform, labelled synthetic until real data runs.
- **Phase E: the secure-environment runner** exports only checked aggregates, and a
  test proves no household-level record can leave.
- **No release-scope PR** is left without independent review (W1).
- **Permanent governing constraints:** the approved epistemic constitution,
  source/review requirements, unknown/outcome states, interim data-governance
  limits and applicable precision rules remain in force. Household inputs
  and outputs declare their needed units, periods, entities and evidence.
  The old requirement to finish universal registry/quantity infrastructure
  before this lane ships is superseded by ADR-0021's model-driven scope.
  The retained P3 decision specifies three significant figures for population,
  baseline and estimate displays, with ranges and full stored precision; this
  migration makes no display or stored-value change.
- **Phase C: every Tier 1 rule** has golden, boundary, contradiction and
  regression cases with conformance/benchmark evidence.

## Open decisions for Pete

- **D1:** Each Tier 1 domain's supported slice, from Phase 0's sourcing.
- **D2:** The disposable-income definition (0.4).
- **D3:** The income-adequacy measures to report (5.3).
- **D5 (decided 26 September 2026):** ADR-0016 accepted, with the
  32-branch cap and population-range reporting.
- **D6 (decided 2 October 2026):** ADR-0017 accepted (shared household
  model, Phase 1), with all three recommended answers: dated spells for
  income and benefit receipt, one family per household in v0.3, and
  today's request formats kept as adapters.
- **D4 (decided 26 September 2026):** v0.3 ships with all three core
  main benefits (W10 Tier 1). The original v0.3.x placement of Tier 2
  domains was redirected to ADR-0019's lanes 3C and 3D. ADR-0021 now places
  further coverage in Phase H, ordered by real analytical demand. The three
  core main benefits remain this household lane's scope.
