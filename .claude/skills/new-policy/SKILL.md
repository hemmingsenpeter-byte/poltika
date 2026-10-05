---
name: new-policy
description: Use when starting, planning, splitting into PRs, or reviewing the onboarding of a new NZ policy domain into Poltika (income tax, a main benefit, a domain selected by BUILD_PLAN_PROGRAMME.md Phase B or H), or a policy's annual update. Sets the standard five-PR structure, the file set, the owners and the exit check for each step, and the lessons v0.1 learned the hard way. Supersedes the planned policy-rule-implementation skill.
---

# New policy onboarding

Historical origin: `ROADMAP_REALIGNMENT.md` W2.2 and W2.6 (archived).
Current scope/order comes from `BUILD_PLAN_PROGRAMME.md` Phases B/H and the
active detailed lane, never from the archive. A new policy joins the deterministic
policy kernel. It is not a standalone calculator. It reads the shared
household model, and its links to other policies are graph edges that cite
a rule.

`BUILD_PLAN.md`'s doctrines apply unchanged: primary sources only, the three
test classes, protected values changed only through `doctrine/test-doctrine.md`,
ambiguity escalated to Pete as a decision record, and no external
implementation as a source (`doctrine/ip-doctrine.md`, the
`clean-room-research` skill).

## The five PRs

One PR per kind of review, not one per task. v0.1 averaged about 15 PRs per
policy, largely from follow-up PRs. Five is the standard, and up to eight
is fine for a large domain (split PR 3 by component).

| PR | Author | Contents | The reviewer checks | Exit check |
| --- | --- | --- | --- | --- |
| **1. Sources and specification** | GPT/Codex | `policy_specs/<policy>/sources.yaml`; `specification.md` with rule ids (`XX-NN`); `decisions/DEC-*.md` for every ambiguity; the supported slice and what is out of scope | Interpretation against the law | Every rule row cites primary legislation or a rank 1-2 source (`evidence.py`). Every ambiguity has a decision Pete has made. |
| **2. Values and expected results** | GPT/Codex | `policy.yaml` (dated intervals, `source_id`, `locator`, `review_status`); `facts.yaml` (a question, admissible values, rule id and any monotonicity for every input fact, ADR-0016); `spec_cases.yaml` hand-calculated independently of any code; `benchmarks.yaml` from official worked examples | Every number against its source (the protected-value process) | The evidence report has no problems. The currency report shows nothing due. Cases cover each boundary. |
| **3. Implementation** | Claude Code | The engine module in `engines/simulator/`; the household-model mapping; `record_step` calls and `STEP_TEMPLATES` entries; reason codes and categories; unit, spec-case and benchmark tests; golden households | Code against the approved specification and cases | Every spec case and benchmark passes. `verify()` holds for every result. Golden snapshots are regenerated through the protected-value process. |
| **4. Interactions** | GPT/Codex specifies, Claude Code implements | Graph edges to existing policies, each citing a rule or decision; interaction spec cases and golden households | Each edge against its cited rule | Every edge cites a source. Outcomes propagate (`needs_review` is never zero). Existing results are unchanged unless an edge says otherwise. |
| **5. Release** | Claude Code | Release-gate rows, CHANGELOG, `docs/releases/` limitations, the README coverage table, the maintenance line (W5.4) and throughput actuals (W2.5) | Checklist | The gate passes, or skips only for named reasons. |

PR 1 for the next policy can be written while PR 3 of the current one is
in review (W2.4 pipelining).

## Rules that keep the count down

- **Review follow-ups go in the same PR, before merge.** A finding on an
  open PR is fixed by pushing to that PR. A new PR is only for a finding
  against something already merged.
- **Don't open a PR per task.** Group the plan's tasks into the five PRs
  above. A task that doesn't fit any of them is a sign the plan needs
  another look, not a sixth PR.
- **Scaffold first.** Start PR 1 and PR 2 from the existing policies' file
  shapes (`policy_specs/accommodation_supplement/` is the fuller example).
  Don't invent a new layout.
- **Shared patterns after the third policy, not before.** Once three
  policies repeat a pattern (thresholds, abatement, rounding, period
  proration), extract it into a small reviewed library in a separate PR.
  Before that, repetition is cheaper than a speculative abstraction
  (CLAUDE.md).
- **One annual-update PR per policy per year**: new intervals, spec cases,
  benchmark refresh and golden re-runs together, reviewed against that
  year's official tables (W5.1 runbook).

## Review depth by risk

The working agreement (`doctrine/development-doctrine.md`) sets it:

- **Full independent review:** PR 1 (interpretation), PR 2 (protected
  values), and any engine, loader or graph code in PR 3 or PR 4.
- **Light independent check:** tests-only, documentation-only and
  generated-file changes. The reviewer confirms the scope matches the
  label.

## What v0.1 learned (make these explicit steps)

- **A missing fact is never zero.** Unknown gives `needs_review` with
  `missing_facts`, and every such id needs a `facts.yaml` entry, so the
  intake planner can ask for it and conditional answers can branch on it
  (ADR-0016). Out of scope gives `unsupported`, with category
  `evidenced_exclusion` or `not_modelled`.
- **Rate-status contracts.** A rate that can change mid-year (an Order in
  Council, a pending amendment) stays `needs_review` until the whole
  period is confirmed (WFF Task 10.2). Record the check date.
- **Periods are `[from, to)`**, and a module refuses a date outside its
  reviewed reference period.
- **Separate thresholds by category are separate parameters** (AS
  claimant-category tables). Don't collapse them.
- **Rounding is a rule, with a decision record where agencies differ**
  (AS DEC-001).
- **Asserted versus calculated.** If another domain can calculate a fact,
  take it from the graph. A contradicting assertion is a `needs_review`
  contradiction, never a silent override.
- **Never infer a fact from a proxy** (an AS area from a city name, an
  eligibility from an age alone).
- **Record throughput.** The plan's progress table records PRs, review
  rounds, decisions and days for the policy (W2.5).
