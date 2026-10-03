# Programme status

**As of:** 2 October 2026.

This is the live tracking file named by ADR-0020. It maps every step of
`BUILD_PLAN_PROGRAMME.md` (the master build order, ADR-0019) and each task
of Steps 1-10 to a status, an owner, a PR and a blocker. Steps 11-33 are
scope only until each gets its own plan, so each has one row.

The other tracking files are `docs/decision_log.md` (Tier A and B
decisions) and `PETE_QUEUE.md` (open Tier C items, cited here as Q1, Q2 and
so on). The plans stay the source of what each task means and when it is
done. This file records where it stands.

**Who updates it, and when.** Every PR that changes a task's state updates
that task's row in the same PR: status, PR number and blocker. The author
of the PR does it, whichever agent that is. A row is never marked Done
without a merged PR. Where a task's state can't be told from the
repository, the row says "Not started" and names no PR.

## Legend

| Status | Meaning |
| --- | --- |
| Done | Merged, and the task's "done when" is met. |
| In flight (other session) | Another session has the work in a worktree or PR. Don't plan or duplicate it. |
| In progress | Being built in a worktree now. |
| Planned | Taken by a session, not started. The blocker column says what it waits on. |
| Blocked | Cannot start until a named item outside the session clears. |
| Pete | Waiting on a decision or action only Pete can take. |
| Not started | Nobody has it yet. |

Owners are Claude Code, GPT/Codex or Pete, as in the plan.

## Professional baseline (ADR-0020)

Not a step of the programme. It is the engineering baseline ADR-0020
sets, kept apart so it doesn't read as programme progress.

| Item | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| B1 | ADR-0020: delegated acceptance | In progress | Claude Code | #139 (open) | Merge |
| B2 | Ruleset on `main` and squash-only auto-merge | Pete | Pete | None | PETE_QUEUE Q1 (needs the repository owner's shell) |
| B3 | Dev tooling: import-linter, pre-commit, Makefile, coverage | In progress | Claude Code | None yet | B1 |
| B4 | Security CI: Dependabot, pip-audit, CodeQL, lychee | In progress | Claude Code | None yet | B1; new jobs join the ruleset's required checks only after Q1 |
| B5 | Governance files: CODEOWNERS and the like | In progress | Claude Code | None yet | B1 |

## Releases

| Release | Steps | Status | Owner | Blocker or deadline |
| --- | --- | --- | --- | --- |
| v0.1, v0.1.5 | Done | Done | | |
| v0.2 | 7.1 | Ready to tag | Pete | Pete tags `v0.2.0` (`BUILD_PLAN_v0_2.md` 10.3; GPT/Codex cleared every row on 27 September 2026) |
| v0.1.6 | Lane 3B | Not started, except the source-currency report (v0.1.6 2.1, #92) | GPT/Codex sources, Claude Code implements | Calendar-bound: the 2027-28 year must be in by 1 April 2027 (M6); needs the 2027-28 values to be published; 2.2 needs Pete's network access |
| v0.3 | Steps 1, 2, 3A, 5.1 for Tier 1 | In progress (Phase 1b mostly done) | Claude Code, GPT/Codex | PETE_QUEUE Q5 (D1-D3) gates Phases 2-5 |
| v0.4 | Steps 4, 5, 6, 3C | Not started | | After v0.3 |
| v0.5 | Steps 7, 8, 9, 3D | Not started | | After v0.4; IDI is PETE_QUEUE Q3 |
| v0.6 | Steps 10, 11, 3E | Not started | | |
| v0.7 | Steps 12, 13 | Not started | | |
| v1.0 | Gates 1-13 plus outside-analyst hardening | Not started | | Phase 3 milestone, claimed on validation evidence |

# Phase 0: Foundations

## Step 1: Epistemic constitution and model governance

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 1.1 | Epistemic constitution | Done | Claude Code drafted, Pete approved | #136, #137 | Follow-ups: a class in each dataset manifest (Step 2); `DEC-*` records classed for Pete's confirmation |
| 1.2 | The AI gate | In flight (other session) | Claude Code, GPT/Codex reviewing | None yet (branch `prog/ai-gate`) | |
| 1.3 | Precision rule (P3) | Planned | Claude Code | None | 2.6 (quantity type) |
| 1.4 | Māori data governance, privacy and security | Pete | Pete; GPT/Codex sources | None | PETE_QUEUE Q2. Interim rule P5 holds meanwhile |
| 1.5 | Model governance and model registry | In flight (other session) | Claude Code drafts, Pete approves | None yet (branch `prog/model-governance`) | |
| 1.6 | Mechanical never-build checks | In flight (other session) | Claude Code | None yet (branch `prog/never-build-checks`) | |
| 1.7 | `evidence-classes` skill | In progress (review fixes) | Claude Code authored; GPT/Codex reviewed/fixed | #138 (open) | Promotion exception clarified; final-head review/CI and delegated acceptance pending |

## Step 2: National Variable Registry and common schemas

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 2.1 | Registry covers every variable a model reads or writes | Planned | Claude Code, GPT/Codex reviewing | None | 2.2-2.5 supply its unit, period, entity and geography types |
| 2.2 | Units and price bases | In progress | Claude Code | None yet | |
| 2.3 | Time periods | In progress | Claude Code | None yet | |
| 2.4 | Populations, entities and identifiers | In progress | Claude Code | None yet | |
| 2.5 | Geography | Planned | Claude Code; GPT/Codex sources concordances | None | Geography types first (no blocker). Dated concordances need GPT/Codex sourcing |
| 2.6 | Quantity type X = (x̂, D_x, E_x) | Planned | Claude Code | None (a parked 29 September draft is on `claude/step2-quantity`, not for review) | 2.2, 2.3, 2.4 |
| 2.7 | Shared household model (ADR-0017; v0.3 Phase 1) | Planned | Claude Code | None | GPT/Codex review of 1.2's mappings |
| 2.8 | State schema v0 | Planned | Claude Code drafts, GPT/Codex reviewing | None | 2.1. The P19 scope is Tier A under ADR-0020 |
| 2.9 | Every shown or stored number is a quantity | Planned | Claude Code | None | 2.6 |
| 2.10 | Registry checks | Planned | Claude Code | None | 2.1 |

# Phase 1: Executable New Zealand

## Step 3: Deterministic statutory kernel

Lane 3A follows `BUILD_PLAN_v0_3.md`. Its Phase 1 is task 2.7. Its Phase 6
(secure runner and survey adapter) is task 7.6.

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 3A, v0.3 0.1-0.3 | Phase 0 scoping: source packs for income tax and the three core main benefits; the stated interactions | Not started | GPT/Codex, Pete deciding ambiguity | None | No `policy_specs/` pack for either exists yet |
| 3A, v0.3 0.4 | Confirm each domain's slice, the disposable-income definition and the income-adequacy measures (D1-D3) | Pete | Pete | None | PETE_QUEUE Q5; waits on 0.1-0.3 |
| 3A, v0.3 0.5 | Plan each policy's tasks with the onboarding skill | Not started | Claude Code | None | v0.3 0.1-0.2 |
| 3A, v0.3 1b.1-1b.6 | Delivered fact catalogues, conditional answers, intake planner, API/page, population ranges and release gate; conditional-summary follow-up in progress; 1b.2b, 1b.2c and 1b.3e remain below | In progress (review fixes) | Claude Code original author; GPT/Codex independent review and fixes | #109, #112, #121, #125, #126, #127, #128; #150 draft follow-up | #128 review found four P2 errors; #150 fixes tested and independently Claude-reviewed at948fb24; latest-head CI, delegated acceptance and integration pending; assurance row stays open |
| 3A, v0.3 1b.2b | Monotone declarations in the real catalogues | Not started | GPT/Codex | None | Cited rules; none declared yet |
| 3A, v0.3 1b.2c, 1b.3e | Candidate values and their checks | Blocked | GPT/Codex, then Claude Code | None | A structured `candidates` list from GPT/Codex |
| 3A, v0.3 Phase 2 | Income tax | Not started | GPT/Codex sources, Claude Code implements | None | v0.3 0.1; PETE_QUEUE Q5 |
| 3A, v0.3 Phase 3 | Jobseeker Support, Sole Parent Support, Supported Living Payment | Not started | GPT/Codex sources, Claude Code implements | None | v0.3 0.2; PETE_QUEUE Q5 |
| 3A, v0.3 Phase 4 | Household dependency graph | Not started | Claude Code | None | Phases 2-3; shares node ids with Step 4 |
| 3A, v0.3 Phase 5 | Disposable income and effective marginal tax rates | Not started | Claude Code | None | PETE_QUEUE Q5 (the disposable-income definition) |
| 3A, v0.3 Phase 7 | Release (exit gate, then Pete tags) | Not started | Claude Code; Pete tags | None | Phases 1-6; tagging is Tier C |
| 3B | Dates: multi-year parameters (M1), 2027-28 (M4-M6), historical years | Not started | GPT/Codex sources, Claude Code implements | None. Lane tasks are v0.1.6 1.1-1.2, 2.1-2.3, 3.1-3.3, 4.1-4.5, 5.1 | v0.1.6 2.1 is Done (#92). The plan records no state for the rest. 2027-28 needs published values and the 1 April 2027 deadline; 2.2 needs Pete's network access; historical years wait on P11 (PETE_QUEUE Q7) |
| 3C | NZ Superannuation, childcare support, KiwiSaver interactions, Paid Parental Leave | Not started | GPT/Codex sources, Claude Code implements | None | Each domain follows the five-PR `new-policy` structure; needs Step 1.5 and Step 2 entries |
| 3D | Student support, ACC, Temporary Additional Support, Disability Allowance, other MSD assistance, Child Support | Not started | GPT/Codex sources, Claude Code implements | None | After 3A and 3C |
| 3E | GST, company tax, other tax regimes, regulatory costs, Crown classifications | Not started | GPT/Codex sources, Claude Code implements | None | Company tax needs a firm state (2.4); classifications need 8.1 |

## Step 4: Evidence Intelligence and evidence graph

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 4.1 | Graph schema | Not started | Claude Code | None | Shares node ids with the household graph (3A Phase 4); VARIABLE nodes need Step 2 |
| 4.2 | Built from what exists | Not started | Claude Code | None | 4.1 |
| 4.3 | Queries in both directions | Not started | Claude Code | None | 4.2 |
| 4.4 | Change impact | Not started | Claude Code | None | 4.3 |
| 4.5 | Click-through in the API and page | Not started | Claude Code | None | 4.3 |
| 4.6 | Completeness review | Not started | GPT/Codex | None | 4.2 |

## Step 5: Legislation conformance suite

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 5.1 | Coverage matrix per rule id | Not started | Claude Code | None | |
| 5.2 | Backfill WFF and AS cases | Not started | GPT/Codex | None | Through the test doctrine |
| 5.3 | Portable fixtures | Not started | Claude Code | None | Registry variable ids (Step 2) |
| 5.4 | The harness | Not started | Claude Code | None | 5.3 |
| 5.5 | Publication as an independent executable standard | Pete | Pete (P6); GPT/Codex checks the IP Doctrine | None | PETE_QUEUE Q4 (P6) |

## Step 6: Validation framework and prediction ledger v0

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 6.1 | The validation case | Not started | Claude Code | None | Registered variables (Step 2) |
| 6.2 | Model scoring | Not started | Claude Code | None | 6.1; 1.5 |
| 6.3 | Benchmark comparators | Not started | Claude Code | None | 6.1 |
| 6.4 | Ledger v0 | Not started | Claude Code | None | 6.1; PETE_QUEUE Q4 (P7, public timestamp) |
| 6.5 | First ledger entries | Not started | Pete picks, Claude Code registers | None | 6.4; a genuinely predictive output; PETE_QUEUE Q4 (P7) |

# Phase 2: Population and fiscal effects

## Step 7: Household microsimulation engine

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 7.1 | Tag `v0.2.0` | Pete | Pete | None | Ready to tag (PETE_QUEUE Q8) |
| 7.2 | Confidence grade on every population and run | Not started | Claude Code | None | Criteria from P4 |
| 7.3 | Public-data calibration | Not started | Claude Code, GPT/Codex reviewing | None | 7.2 |
| 7.4 | Validation against published aggregates | Not started | Claude Code | None | 6.1 |
| 7.5 | Kernel domains' facts join the population | Not started | Claude Code | None | Each domain landing (Step 3) |
| 7.6 | Secure-environment runner, output checks, survey adapter | Not started | Claude Code | None | 1.4 constraints (PETE_QUEUE Q2) |
| 7.7 | IDI and Longitudinal Business Database access | Pete | GPT/Codex, then Pete | None | PETE_QUEUE Q3 (P12) |
| 7.8 | Results by decile, household type, area and age | Not started | Claude Code | None | 7.2 |

## Step 8: Fiscal and shared accounting spine

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 8.1 | Source the Crown classifications | Not started | GPT/Codex | None | |
| 8.2 | Sector accounts in the state schema | Not started | Claude Code | None | 2.8 |
| 8.3 | Crown accounts on the spine | Not started | Claude Code | None | 8.1, 8.2 |
| 8.4 | Map kernel outputs to Crown lines | Not started | Claude Code | None | 8.3; lane 3E |
| 8.5 | Multi-year scenarios | Not started | Claude Code | None | |
| 8.6 | Batch engine (W4.2 prototype, W4.3 ADR) | Not started | Claude Code (P10 is Tier A under ADR-0020) | None | None; due by M4 |
| 8.7 | Static fiscal scoring | Not started | Claude Code | None | 8.3, 8.5 |
| 8.8 | Reconciliation with the Crown's statements | Not started | Claude Code | None | 8.3 |

## Step 9: Historical NZ State Store

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 9.1 | Connectors | Not started | Claude Code, GPT/Codex reviewing mappings | None | |
| 9.2 | State snapshots | Not started | Claude Code | None | 2.8 |
| 9.3 | As-of queries | Not started | Claude Code | None | 9.2 |
| 9.4 | Gaps are explicit | Not started | Claude Code | None | 9.2 |
| 9.5 | Validation against sources | Not started | Claude Code | None | 6.1, 9.2 |

# Phase 3: Baseline New Zealand

## Step 10: National Baseline Engine

| Task | Title | Status | Owner | PR | Blocker |
| --- | --- | --- | --- | --- | --- |
| 10.1 | Population engine | Not started | Claude Code | None | Step 9 |
| 10.2 | Economy as exogenous, sourced Assumptions | Not started | GPT/Codex, then Claude Code | None | |
| 10.3 | Crown baseline on the spine | Not started | Claude Code | None | Step 8 |
| 10.4 | Reproduce He Tirohanga Mokopuna 2025 | Not started | Claude Code, GPT/Codex reviewing | None | 10.1-10.3 |
| 10.5 | Uncertainty that grows with the horizon | Not started | Claude Code | None | 10.3; Step 2 (D_x) |

## Steps 11-33 (scope only)

Each gets its own detailed plan when it starts.

| Step | Title | Phase | Status | Owner (provisional; set by each step's plan) | PR | Blocker |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | Uncertainty and sensitivity framework | 3 | Not started | Claude Code | None | Step 2 (D_x), batch engine (8.6) |
| 12 | Causal Evidence Library | 3 | Not started | Claude Code, GPT/Codex | None | Published studies, each reviewed |
| 13 | Historical Validation Laboratory | 3 | Not started | Claude Code | None | Steps 6, 9 |
| 14 | National State Transition Engine | 4 | Not started | Claude Code | None | 2.8, Step 13 |
| 15 | Canonical NZ Scenario Library | 4 | Not started | Claude Code, Pete | None | PETE_QUEUE Q4 (P20) |
| 16 | Priority domain models | 4 | Not started | Claude Code, GPT/Codex | None | PETE_QUEUE Q4 (P13) |
| 17 | Federated Model Graph | 5 | Not started | Claude Code | None | Step 16 |
| 18 | Continuous State Estimation | 5 | Not started | Claude Code | None | Steps 6, 9 |
| 19 | Synthetic Population Programme | 5 | Not started | Claude Code, Pete | None | PETE_QUEUE Q2, Q3 (microdata access, Māori data governance) |
| 20 | Spatial and physical twin | 5 | Not started | Claude Code | None | Steps 2.5, 16 |
| 21 | Cost-of-delay engine | 6 | Not started | Claude Code | None | Phase 4 |
| 22 | Value-of-information engine | 6 | Not started | Claude Code | None | Steps 11, 12 |
| 23 | Policy-space search and inverse solver | 6 | Not started | Claude Code | None | PETE_QUEUE Q4 (P14) |
| 24 | Pareto frontier engine | 6 | Not started | Claude Code | None | Step 23 |
| 25 | Public NZ Futures Laboratory | 7 | Not started | Claude Code, Pete | None | Phase 7 trust gate |
| 26 | Policy and manifesto analysis interface | 7 | Not started | Claude Code | None | Phase 7 trust gate |
| 27 | Constraint-based negotiation sandbox | 7 | Not started | Claude Code | None | Phase 7 trust gate |
| 28 | Research and institutional APIs | 7 | Not started | Claude Code | None | Phase 7 trust gate |
| 29 | Natural-language policy interface | 8 | Not started | Claude Code | None | `doctrine/llm_boundaries.md`; Step 1.2 |
| 30 | AI hypothesis discovery | 8 | Not started | Claude Code | None | Step 12 |
| 31 | AI model orchestration | 8 | Not started | Claude Code | None | Step 1.5 |
| 32 | AI explanation and research agent | 8 | Not started | Claude Code | None | Step 4 |
| 33 | Autonomous research loop, with human gates | 8 | Not started | Claude Code, Pete | None | Steps 18, 30 |
