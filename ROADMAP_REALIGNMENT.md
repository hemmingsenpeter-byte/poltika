# Roadmap realignment plan

**Date:** 26 September 2026
**Status:** Approved 26 September 2026 with the recommended decisions
(D1 yes; D3 apply now; D4 a cap of five; D7 pipelining; D8 release v0.2
on the labelled synthetic population). D2 waits on the Phase 0 scoping,
and D5-D6 are due before v0.4.
**Decision record:** ADR-0015 (accepted).
**Detailed v0.3 tasks:** `BUILD_PLAN_v0_3.md`.

This plan fixes what a whole-roadmap review found on 26 September 2026:

1. no release owns policy coverage, although it is the critical path;
2. Discovery and Hypothesis (v0.6-v0.7) sit on the path to v1.0
   without being part of it;
3. real data depends on an access process nobody has started;
4. Monte Carlo at population scale will outgrow a per-household Python
   engine;
5. every policy added raises the yearly maintenance cost;
6. independent review has fallen behind implementation;
7. three design seams v0.3 must settle: a shared household model, a
   household-level dependency graph, and multi-year parameters.

Each workstream says what it fixes, its subtasks with owners, when it runs
and when it is done. Owners follow the v0.1 roles: GPT/Codex for sources,
interpretation and independent review, Claude Code for implementation, and
Pete for decisions and anything needing a person.

## Summary

| Workstream | Fixes | When | Blocks |
| --- | --- | --- | --- |
| W1 Review debt and cadence | 6 | Now, before any new implementation PR | The v0.2 release |
| W2 Policy coverage throughput | 1 | Now: 2.1-2.4 feed v0.3 | v0.3 |
| W3 Real-data access | 3 | Now: the application has a long lead time | Real v0.2 estimates; v0.3 exit |
| W4 Batch engine decision | 4 | Measure now; decide by v0.4 start | v0.5 Monte Carlo |
| W5 Maintenance budget | 5 | With v0.1.6 | Every later plan |
| W6 Shared household model | 7 | v0.3 Phase 1 | Adding a third policy |
| W7 Household dependency graph | 7 | v0.3 Phase 4 | Multi-policy scenarios |
| W8 Multi-year parameters | 7 | v0.1.6 Task 4.3 | v0.4 |
| W9 Roadmap reorder | 2 | On accepting ADR-0015 | Nothing: documentation |

## W1. Review debt and cadence

**Problem.** PRs #82-#100 (18 implementation and plan PRs) merged on
Claude Code's author preflight under Pete's recorded delegation. The
working agreement allows that, but the two-model review is what makes
Poltika's assurance claims true, and it has fallen behind.

- **W1.1 — Claude Code. Review queue.** Add
  `review_packets/review_queue.md`, listing every merged PR without an
  independent review: its number, scope, touched engine or statutory
  paths, and a risk rank. Engine-touching PRs (#94 preloaded parameters,
  #95 spec cache) and data-boundary PRs (#93) rank first.
- **W1.2 — GPT/Codex. Work the queue in risk order.** Use
  `review_packets/TEMPLATE.md`, classify findings under the Review
  Doctrine, and record each review in `reviews/`.
- **W1.3 — Owner by slice.** Fix findings through normal PRs. A finding
  against a merged PR is never resolved by editing history.
- **W1.4 — Pete. Cap review debt.** Amend the working agreement in
  `doctrine/development-doctrine.md`. Proposed wording: "When five or more
  merged implementation PRs await independent review, no further
  implementation PR merges until the queue is below five. Plan,
  documentation and review-fix PRs are exempt."
- **W1.5 — Claude Code. Enforce it in every release gate.** Add a row to
  each release-gate test (v0.1.5 and v0.2 now, later releases as they are
  planned) that skips, naming the PRs, while `review_queue.md` lists an
  open entry for that release. A skip rather than a failure keeps `main`
  green for review-fix PRs, and a green run with no skips still means the
  gate is met (the same convention as the v0.1.5 pilot rows).

**Done when:** the queue is empty or below the cap, the cap is in the
working agreement, and the gates check it.

## W2. Policy coverage throughput

**Problem.** Almost every later capability needs income tax and the main
benefits specified to v0.1's standard:

- disposable income;
- poverty and effective-tax-rate measures;
- v0.3's interactions;
- the v0.6 (was v0.8) revenue model.

v0.1 needed Tasks 1-35 and 58 merged PRs (#1-#81) for two policies. At that rate
coverage, not code, sets the pace.

- **W2.1 — Claude Code. Measure what a policy costs.** From the v0.1 git
  and review history, record per policy:
  - tasks, PRs and review rounds;
  - findings by class;
  - decisions escalated to Pete;
  - elapsed days;
  - where the time went (sourcing, specification, implementation, review).

  Output: `docs/research/policy_onboarding_cost.md`. It uses only
  repository history; nothing is estimated from memory.
- **W2.2 — Claude Code, reviewed by GPT/Codex. A policy onboarding
  skill.** Write `.claude/skills/new-policy/SKILL.md`, turning v0.1's
  sequence into one checklist:
  - source pack;
  - specification with rule ids;
  - `policy.yaml`;
  - spec cases;
  - benchmarks;
  - golden households;
  - evidence and currency reports;
  - explanation templates;
  - review packet.

  Each step names its owner and exit check. Anything v0.1 learned the
  hard way (rate-status contracts, period semantics, protected values)
  becomes an explicit step.
- **W2.3 — GPT/Codex, Pete deciding. Choose and scope the v0.3 domains.**
  From primary sources, define the smallest supported slice of:
  - individual income tax on employment and benefit income;
  - the main benefits needed to compute disposable income for the
    household types v0.2 already models.

  Which benefits, and which deductions the disposable-income definition
  needs, is decided here from sources and recorded as a decision (D2). It
  is not assumed in this plan.
- **W2.4 — Pete. Pipeline the work.** Agree that GPT/Codex sources and
  specifies policy N+1 while Claude Code implements policy N, so review
  and implementation overlap instead of queueing.
- **W2.5 — Claude Code. Track throughput.** Each build plan's progress
  table records tasks, PRs and elapsed days per policy, so W2.1's
  baseline is checked against reality every release.

**Done when:** the cost baseline and onboarding skill exist, the v0.3
domains are scoped and decided, and `BUILD_PLAN_v0_3.md` is approved on
that scope.

## W3. Real-data access

**Problem.** Real New Zealand estimates need survey unit records, which
are restricted. They can't be committed to this repository, access needs
an approved project, and results leaving a secure environment are checked
for confidentiality. Nothing in the roadmap starts that process, and a
synthetic population calibrated only on marginal shares will misstate
costs that depend on combinations such as income × children × tenure.

- **W3.1 — GPT/Codex. Document the access route from Stats NZ's own
  published guidance:** eligibility, project application, researcher
  requirements, costs, timelines, and the output-checking rules results
  must pass. Record it with dated sources in
  `docs/research/microdata_access.md`. Nothing about the process is
  asserted from memory.
- **W3.2 — Pete. Decide and apply (D3).** Whether to seek access, under
  which organisation, and for which project scope. Start early, because
  the lead time is the risk.
- **W3.3 — Claude Code. Secure-environment mode.** Poltika must run
  where the data lives:
  - no network;
  - no repository writes;
  - the population path read from configuration;
  - aggregate tables as the only export.

  Add a runner entry point that does exactly that, with a test proving
  no household-level record reaches the export.
- **W3.4 — Claude Code, rules from W3.1. Output checks.** Apply the
  published confidentiality rules (for example suppression or rounding
  of small cells) to every exported table before it leaves. The
  thresholds come from W3.1's sources, never from a default.
- **W3.5 — Claude Code, reviewed by GPT/Codex. Survey adapter.** Map
  survey records to the population schema (`semantics/population.py`),
  deriving each policy fact only by a reviewed rule. Where a fact can't
  be derived, it stays unknown, so the household reads `needs_review`.
  This extends v0.2 Task 2.3's mapping review.
- **W3.6 — Claude Code, optional until W3.2 lands. Joint calibration.**
  Extend the synthetic generator to published cross-tabulations
  (for example income by household type) where they exist. That narrows,
  but can't remove, the gap to real data. Every result keeps the
  synthetic label.

**Done when:** the route is documented, Pete has decided, and Poltika can
run inside a secure environment and export only checked aggregates. Real
estimates follow access, whenever it is granted.

## W4. Batch engine decision

**Problem.** A household takes about 4.8 ms for two policies, both runs
(v0.2 Task 7.4). Monte Carlo at population scale multiplies that by the
number of policies, years, draws and households. The v1.0 definition
needs uncertainty on multi-year results, so the engine's speed becomes a
design question before v0.5.

- **W4.1 — Claude Code. Scaling model.** Measure time per household per
  policy per year on the current engine, and project runs for 100,000
  households × {2, 5, 10} policies × {1, 10, 30} years × {1, 100, 1000}
  draws. Record in `docs/releases/` with the measurement method.
- **W4.2 — Claude Code. A one-component prototype.** Build a batch
  (vectorised) family tax credit calculation over a whole population.
  Differential-test it against the reference engine on every golden
  household, every spec case, and Hypothesis-generated households: equal
  outcome, value and reason code, or the test fails.
- **W4.3 — Claude Code drafts, Pete decides. ADR by the start of v0.4
  (D5).** It records one of:
  - (a) the per-household engine stays, and Monte Carlo is limited to
    what W4.1 shows is affordable;
  - (b) a batch engine is added for population runs.

  Under (b):
  - the per-household engine stays the reference and the only thing
    that explains a result;
  - every batch component is differential-tested in CI;
  - nothing ships from the batch path that the reference can't
    reproduce.
- **W4.4 — Claude Code.** If (b), schedule the batch engine in v0.4 for
  every component v0.4 covers.

**Done when:** the ADR is accepted before v0.4 implementation starts.

## W5. Maintenance budget

**Problem.** Every rate expires each 1 April (v0.1.6). Backtesting (v0.5)
and multi-year scenarios (v0.4) also need historical rates per policy per
year, each sourced and reviewed. The cost grows with every policy added.

- **W5.1 — Claude Code. Annual update runbook.** Write it from v0.1.6's
  actual steps:
  - the currency report;
  - sourcing new values;
  - specification review;
  - new intervals;
  - spec cases;
  - golden households for both years;
  - release.

  Output: `docs/releases/ANNUAL_UPDATE_RUNBOOK.md`, measured in tasks and
  days after the first cycle.
- **W5.2 — Claude Code. The currency report covers every policy
  automatically.** The workflow discovers `policy_specs/*/policy.yaml`
  instead of listing directories, so a new policy is covered on arrival.
- **W5.3 — Pete, with GPT/Codex. Backtest horizon (D6).** How many past
  years v0.5 backtests over. That fixes how many historical parameter
  years each policy must be sourced for. Set it before v0.4, so v0.4's
  multi-year work sources the same years once.
- **W5.4 — All plans.** Every future build plan carries a maintenance
  line per policy: yearly update effort from W5.1, and historical years
  from W5.3.

**Done when:** the runbook exists, the report is automatic, and the
horizon is decided.

## W6. Shared household model (v0.3 Phase 1)

**Problem.** Each policy has its own input type (`WffScenario`,
`AsScenario`). Facts such as partner status and children are held once
per policy and cross-checked pair by pair (`scenarios/combined.py`,
Task 28.3). With three or four policies that becomes every pair of every
shared fact.

The subtasks are in `BUILD_PLAN_v0_3.md` Phase 1:

- one canonical person, family and household model, holding each fact
  once;
- each policy's input derived from it by a reviewed mapping;
- the existing WFF and AS runs byte-identical through the new path;
- the pairwise contradiction checks retired only once every one of them
  is covered.

## W7. Household dependency graph (v0.3 Phase 4)

**Problem.** Once income tax and benefits exist, one policy's output is
another's input. The roadmap's v0.3 proposes a generic graph framework.
Built before those interactions are specified, it would be a speculative
abstraction (CLAUDE.md).

The subtasks are in `BUILD_PLAN_v0_3.md` Phase 4:

- the graph's edges come only from the specifications ("this policy's
  income test counts that policy's payment");
- the graph is ordered per household;
- a cycle is refused unless a specification defines how to resolve it;
- each dependency chain is explained.

## W8. Multi-year parameters (v0.1.6 Task 4.3)

**Problem.** `reference_period` is a single interval on the policy
schema, and both engines check against it. v0.4's multi-year scenarios
need every policy to hold several years.

- **W8.1** Keep v0.1.6 D2's design (one `policy.yaml`, a list of
  reference periods, one per year) and make it the schema for every
  policy, not a WFF and AS special case.
- **W8.2 — Claude Code.** v0.1.6 Task 4.3 implements it with a test that
  a household run for each year uses only that year's values and
  reference period.
- **W8.3 — GPT/Codex.** Review the schema change against
  `policy_specs/SCHEMA.md` before any third policy is written against it.

## W9. Roadmap reorder (ADR-0015)

- **W9.1 — Pete (D1).** Accept or reject ADR-0015.
- **W9.2 — Claude Code, on acceptance:**
  - rewrite `ROADMAP.md` v0.3-v0.9 into the new v0.3-v0.7 and move
    Discovery and Hypothesis under "Beyond v1.0";
  - update `BUILD_PLAN.md`'s Roadmap Doctrine;
  - update README, REPOSITORY_STRUCTURE and the v0.2 plan's references.
- **W9.3 — Claude Code.** Move the historical fiscal baseline and the
  Stats NZ and Treasury connectors into the v0.5 plan when it is written,
  with backtesting as their named consumer.
- **W9.4 — Claude Code.** Recast the v0.6 (was v0.8) scope as a
  transparent accounting model:
  - demography × participation × wages → revenue;
  - spending categories;
  - interest and debt;
  - exogenous, stated assumptions;
  - comparison with Treasury's published long-term projections.

  Behavioural and GDP modelling stay in the v2 track.

## Progress

| Item | State |
| --- | --- |
| W1.1 | Done: `review_packets/review_queue.md`. 17 open implementation rows, so the cap is reached. |
| W1.4 | Done: the cap is in `doctrine/development-doctrine.md`. |
| W2.1 | Done: `docs/research/policy_onboarding_cost.md`. About 25-30 merged PRs and 2-4 decision records per v0.1-shaped policy. |
| W4.1 | Done: `docs/releases/V0_2_SCALING_MODEL.md`. Deterministic runs stay practical. Population-scale Monte Carlo doesn't (days to years on one core). |
| W1.5, W5.2 | Done in a PR held behind the review cap. The gates' review rows skip, naming the open PRs, and the currency workflow discovers every `policy_specs/*/policy.yaml`. |

## Sequence

| Order | Work |
| --- | --- |
| Now | W1.1-W1.5, W2.1-W2.4, W3.1-W3.2, W4.1, W5.2, W9.1 |
| With v0.1.6 | W5.1, W8 |
| Before v0.3 implementation | W2.3 scoped and decided; `BUILD_PLAN_v0_3.md` approved; W1 below its cap |
| v0.3 | W6, W7, W3.3-W3.5, W4.2 |
| Before v0.4 | W4.3 decided, W5.3 decided |

## Open decisions for Pete

- **D1:** Accept ADR-0015's reorder? Recommended.
- **D2:** The v0.3 domains, from W2.3's sourced scoping: which income tax
  and which main benefits form the first slice.
- **D3:** Seek survey microdata access now (W3.2)? Recommended, because of
  the lead time.
- **D4:** The review-debt cap (W1.4): five merged implementation PRs
  proposed.
- **D5:** The batch engine (W4.3), by the start of v0.4.
- **D6:** The backtest horizon (W5.3), before v0.4.
- **D7:** Pipelining (W2.4): GPT/Codex specifies the next policy while
  Claude Code implements the current one.
- **D8:** Whether v0.2 releases on the synthetic population alone,
  clearly labelled, or waits for real data. Recommended: release on the
  synthetic population, so the machinery is gated and reviewed, and
  treat real estimates as a v0.2.x or v0.3 deliverable once W3 lands.
