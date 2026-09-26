# What a policy cost in v0.1

`ROADMAP_REALIGNMENT.md` W2.1. This is measured from repository history
only (git log, `policy_specs/`, `review_packets/`, `reviews/`) on
26 September 2026. Nothing here is estimated from memory. It is the
baseline that v0.3's policy plans (income tax, main benefits) are
estimated against and checked against (W2.5).

## v0.1 as a whole

| Measure | Value | How it was counted |
| --- | --- | --- |
| Build-plan tasks | 35 (Tasks 1-35) | `BUILD_PLAN.md` task list |
| Merged PRs to the v0.1 release | 58 (#1-#81) | merge commits naming PR numbers up to #81 |
| Calendar span | 20-26 September 2026 | first commit to the v0.1.0 release PRs |
| Review packets | 15 | `review_packets/*.md` |
| Independent review records | 2 | `reviews/` (Task 34.3, Claude fresh-context and Codex) |

The calendar span is short because the work was AI-assisted, so elapsed
days are a weak measure of cost. The better measures are PRs, review
packets, decisions escalated to Pete, and protected-value changes: those
are the steps that need sourcing, a second model or a person.

## Per policy

| Measure | Working for Families | Accommodation Supplement | WFF-AS interaction |
| --- | --- | --- | --- |
| Commits touching `policy_specs/<policy>/` | 31 | 32 | 5 |
| Decision records escalated to Pete | 2 | 4 | 0 (resolved in AS DEC-003) |
| Specification rule rows | 9 | 11 | n/a |
| Spec cases | 23 | 26 | 5 |
| Official benchmarks | 9 | 4 | n/a |
| Golden households | n/a | n/a | 9 |
| PR titles naming the policy (rough) | 9 | 19 | 9 |

The PR-title count is a keyword match on merge messages, and some PRs
touched both policies. Read it as "the Accommodation Supplement took
about twice the PRs of WFF", not as an exact split.

## What the history says about cost

- **Sourcing and interpretation dominate.** Six decision records, the
  WFF rate-status contract (Task 10.2), the AS rate-contract resolution
  and the Task 26a rate audit were all interpretation work that needed
  Pete or a second model. Implementation PRs were comparatively cheap.
- **The policy with more cases per rule cost more.** The Accommodation
  Supplement (claimant categories, areas, assets, rounding) needed more
  PRs and decisions than WFF, despite a similar number of rule rows.
  v0.3's benefits are likely to be closer to the Accommodation Supplement
  in shape than to WFF, and income tax closer to WFF. W2.3's scoping
  should confirm that from sources.
- **Independent review was the scarce step.** Two review records exist
  in `reviews/`. Most review happened inside review packets or PR
  threads. W1's queue and cap make that step visible and bounded.
- **Interaction work is separate.** The WFF-AS interaction had its own
  sources, spec cases and golden households (Tasks 28-29). Every pair of
  interacting policies in v0.3 will need the same, which is why v0.3
  Phase 0.3 records every interaction first.

## Planning figure for v0.3

A v0.1-shaped policy costs roughly 25-30 merged PRs, 2-4 decision records
and one review cycle per slice (58 PRs over two policies plus their
interaction). Treat it as a starting estimate. v0.3's progress tables
record the actual figures (W2.5), and the next plan uses those instead.
