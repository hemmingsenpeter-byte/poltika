# Claude Code repo closeout execution plan

**Date:** 3 October 2026  
**Coordinator:** Claude Code  
**Base snapshot:** `main` at `3bea73fba44f9173ecc4ee3d00be3aa22328b993`

## Objective

Collapse the current open-PR topology into one clean, current `main`, activate the
economist-first programme, preserve the high-throughput ("monkey with a hammer")
execution doctrine, and unblock the next v0.3 implementation wave.

This is a coordination plan, not authority to bypass Poltika's gates. Use
ADR-0020 for acceptance authority, the review doctrine for review depth, the
epistemic constitution for truth/provenance constraints, and the development
doctrine for build-speed trade-offs.

## Operating mode

Use the high-throughput build approach once PR #153 lands:

- breadth before elegance;
- front-load useful implementation and defer non-blocking polish;
- parallelise independent bounded modules;
- provisional internals are acceptable behind stable typed contracts;
- tests and regression protection come before polish;
- make technical debt explicit and machine-visible;
- refactor at real integration boundaries;
- prefer bounded replacement of poor internals over prolonged repair;
- keep runnable vertical slices moving;
- never trade away statutory correctness, legal interpretation discipline,
  source provenance, evidence classes, reproducibility, uncertainty semantics,
  protected expected values, common schemas or deterministic calculation.

If the economist-first migration touches `doctrine/development-doctrine.md`,
preserve the high-throughput section from PR #153. Do not let an older stacked
branch overwrite it.

## Ground rules

1. Work from live GitHub state, not stale tracker wording.
2. Before touching a PR, refresh its base and derive the expected behaviour from
   the governing docs before reading the author rationale.
3. For each PR: exact-head diff check, required review, latest-head CI, then
   acceptance/merge under ADR-0020. Never use admin bypass.
4. Where a PR is stacked, merge its dependency first, retarget to `main`, update
   the branch, rerun exact-head review/CI, then merge.
5. Do not silently resolve statutory, evidential or policy-definition ambiguity.
   Preserve the unknown and escalate through the existing authority path.
6. Do not transmit private repository material to an external model/provider
   unless the user has explicitly authorised that destination and scope.
7. Tier C remains Pete-only. Do not decide Q1-Q8 on Pete's behalf.
8. Keep `PROGRAMME_STATUS.md`, `review_packets/review_queue.md` and
   `PETE_QUEUE.md` truthful after each state change.

## Execution order

### Phase A — close review debt and establish the execution doctrine

#### A1. PR #152 — close PR #128 assurance

- Refresh only if `main` moved.
- Re-run the exact-head document/diff checks.
- Complete the remaining independent review and delegated acceptance gate.
- Confirm all required CI is green.
- Merge.
- Confirm the #128 row is actually closed in the review queue and no release gate
  still names #128 as outstanding.

**Done when:** #152 is merged and the #128 assurance row is closed on `main`.

#### A2. PR #153 — live-status reconciliation + high-throughput doctrine

- Rebase/refresh onto the post-#152 `main`.
- Resolve tracker conflicts against actual GitHub state, not the old branch text.
- Preserve the full high-throughput build-mode section.
- Re-run latest-head CI and light independent documentation review.
- Merge.

**Done when:** current tracker state and the high-throughput doctrine are both on
`main`.

### Phase B — clear the professional-baseline backlog

Handle these as independent work, but merge sequentially so every final head is
based on the latest `main`.

#### B1. PR #138 — evidence-classes skill

- Refresh against current `main`.
- Review the updated diff.
- Run latest-head CI.
- Complete delegated acceptance and merge.

#### B2. PR #142 — security CI

- Refresh against current `main`.
- Preserve the intended dependency/static-analysis/source-currency isolation.
- Confirm no workflow change weakens protected-path, snapshot or statutory-value
  enforcement.
- Run security/static-analysis negative-path checks plus normal CI.
- Complete delegated acceptance and merge.
- Record any new required-check names that Q1 will eventually need.

#### B3. PR #143 — governance files

- Refresh against current `main`.
- Re-check CODEOWNERS, SECURITY, CONTRIBUTING, issue forms and release checklist
  against the now-current CI names and acceptance doctrine.
- Run latest-head CI and delegated acceptance.
- Merge.

#### B4. PR #140 — Task 21 / hosting documentation closeout

- Refresh against current `main`.
- Preserve the useful `POLTIKA_POLICY_SPECS_DIR` hosting documentation unless
  current architecture makes it incorrect.
- Re-run the installed-artifact verification if the refreshed diff or packaging
  path warrants it.
- Merge or, if superseded, close with a precise replacement reference.

**Done when:** #138, #142, #143 and #140 are either merged or explicitly closed as
superseded, with no useful change stranded off `main`.

### Phase C — activate the economist-first programme

The stack is #144 -> #145 -> #146 -> #147. Partial adoption is not the target.

#### C1. PR #144

- Refresh onto current `main`.
- Reconcile conflicts with #153; retain the high-throughput doctrine and truthful
  live status.
- Run independent review and exact-head CI.
- Merge.

#### C2. PR #145

- Retarget from `docs/programme-adr-archive` to `main`.
- Refresh onto the post-#144 head.
- Run independent review and exact-head CI.
- Merge.

#### C3. PR #146

- Retarget from `docs/programme-master` to `main`.
- Refresh onto the post-#145 head.
- Run independent review and exact-head CI.
- Merge.

#### C4. PR #147

- Retarget from `docs/programme-references` to `main`.
- Refresh onto the post-#146 head.
- Run independent review and exact-head CI.
- Merge.
- Verify the economist-first master, roadmap, detailed household lane and live
  status now agree on the same execution order.

**Done when:** #144-#147 are all merged, the economist-first programme is
canonical on `main`, and no active root plan still gives the superseded order
operational authority.

### Phase D — land the new operating model and source scopes

#### D1. PR #149 — programme-management operating model

- Retarget onto the post-migration `main`.
- Reconcile all status references with live GitHub state.
- Preserve the one-writer / specialist-review / isolated-worktree model and the
  high-throughput parallelisation intent.
- Run final-main CI and independent review.
- Merge.

#### D2. PR #148 — income-tax source scope

- Retarget onto current `main`.
- Independently review the source catalogue and scope against dated primary
  sources.
- Verify enactment/current-period separation, rounding questions and unresolved
  interpretation are explicit.
- Do not adopt statutory values or a supported slice merely because they appear
  in the draft.
- Merge the source-research increment once the research itself is sound.

#### D3. PR #151 — three core benefits source scope

- Retarget onto current `main`.
- Independently review Jobseeker Support, Sole Parent Support and Supported
  Living Payment source catalogues against dated primary sources.
- Re-check the recorded household-versus-person restriction issue, payment
  period, income basis, partner rules and any future commencement separation.
- Keep unsupported or unresolved questions explicit.
- Merge the source-research increment once the research itself is sound.

#148 and #151 can be reviewed in parallel after the migration is canonical.

**Done when:** #149, #148 and #151 are merged and Q5 can be presented to Pete
using reviewed source material rather than draft branch assumptions.

## Phase E — reconcile invisible/in-flight work

The existing tracker has claimed work in flight for items that do not currently
have visible remote branches/PRs, including:

- Step 1.2 — AI gate;
- Step 1.5 — model governance/model registry;
- Step 1.6 — mechanical never-build checks;
- Step 2.2 — units and price bases;
- Step 2.3 — time periods;
- Step 2.4 — populations/entities/identifiers.

For each item:

1. Check local worktrees/branches.
2. If real work exists, push it to a named remote branch and open a bounded PR.
3. If no real work exists, correct `PROGRAMME_STATUS.md`; do not leave
   "In flight" or "In progress" without reviewable artefacts.
4. Preserve the dependency order needed for quantity type, variable registry,
   shared household model and state schema.

The parked `claude/step2-quantity` branch is not automatically authoritative.
Review whether it still fits the economist-first programme before reviving it.

**Done when:** every claimed in-flight task is either represented by a visible
PR/branch or truthfully marked planned/not started.

## Phase F — clear near-term evidence and release housekeeping

### F1. Issue #130 — source currency

Resolve or deliberately reclassify the genuine due items:

- WFF `in_work_base` remains `needs_review`;
- cited WFF parameter sources without structured currency checks;
- remaining AS/WFF informational sources without structured checks where the
  new source-currency design requires them.

Do not convert "needs review" to a value without primary-source evidence.

### F2. v0.2 tag

The `v0.2.0` tag does not currently exist. Tagging is Tier C (Q8), so prepare
the exact recommended commit and command for Pete but do not create the tag
without Pete's action/authority.

### F3. Main ruleset

Q1 remains Pete-only. After #142 is merged, provide Pete the exact current
required-check names and ruleset commands. Do not silently change repository
administration settings.

## Phase G — prepare the next real build wave

Once #148/#151 are reviewed and merged, prepare Q5 for Pete with concise options
and evidence for:

1. each Tier 1 domain's supported slice;
2. the canonical disposable-income definition;
3. the income-adequacy measures.

Do not start implementations whose semantics depend on an unresolved Q5 choice.

After Q5 is decided, execute the v0.3 statutory build in high-throughput mode:

- income tax;
- Jobseeker Support;
- Sole Parent Support;
- Supported Living Payment;
- shared/canonical household facts and mappings;
- household dependency graph;
- disposable income;
- effective marginal tax rates/incentive measures;
- real-catalogue monotonicity declarations;
- structured candidate values and their checks;
- release/assurance integration.

Parallelise independent policy modules once their shared contracts are fixed.
Keep one source/specification reviewer distinct from the implementation author.

## Near-term Pete items

Do not block Phase A-D on later Tier C items unless their named gate is reached.

- **Q1:** main ruleset / squash-only auto-merge — near-term repository hygiene.
- **Q5:** v0.3 D1-D3 — required before Phases 2-5 implementation semantics.
- **Q6:** Claude review-skill wording — low-risk consistency fix; propose exact
  edits if permissions permit.
- **Q8:** v0.2 tag — release housekeeping.
- **Q2:** Māori data governance — required before Māori/microdata outputs.
- **Q3:** IDI application — later microsimulation/synthetic-population gate.
- **Q7:** historical horizon — due by November 2026 for the state-store lane.
- **Q4:** deferred programme choices — raise only at their named steps.

## Stop / escalate conditions

Stop the affected lane and escalate rather than guessing when any of these occur:

- conflicting primary sources;
- genuine legal interpretation ambiguity;
- a proposed protected statutory value or expected-result change;
- uncertainty over whether a value is Fact, Rule, Estimate, Assumption,
  Scenario or Model output;
- a breaking change to a shared schema/identifier/quantity contract;
- a Tier C decision;
- a need to transmit private repository contents externally without explicit
  destination approval;
- a failing protected-path/snapshot/statutory-value guard that cannot be
  explained by the bounded task.

Other independent lanes should keep moving where safe.

## Completion criteria

This coordinator plan is complete only when all of the following are true:

- #128 assurance debt is closed;
- #153's status reconciliation and high-throughput doctrine are on `main`;
- #138, #142, #143 and #140 are merged or explicitly superseded;
- #144-#147 are integrated and the economist-first programme is canonical;
- #149 is integrated;
- #148 and #151 are on `main` as reviewed source research;
- every tracker "in flight"/"in progress" claim has a visible artefact or has
  been corrected;
- issue #130's due source-currency items have a clear disposition;
- Q5 is ready for Pete with reviewed evidence and concrete options;
- Q1/Q8 have exact current actions prepared for Pete;
- `PROGRAMME_STATUS.md`, `review_packets/review_queue.md` and
  `PETE_QUEUE.md` agree with live GitHub state;
- all merged work passed the required latest-head CI/review gates;
- the repo has one authoritative programme and no stale stacked migration left
  pretending to be active authority.

At that point, stop treating repository cleanup as the main job and move the
majority of AI coding capacity onto the v0.3 executable policy/model build.
