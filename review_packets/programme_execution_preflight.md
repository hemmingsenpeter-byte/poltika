# Programme execution — author preflight

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex project manager, appointed by Pete's current goal.
- Base: prepared migration `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Scope: coordination practice, current tracker and dated first/second-cycle verification;
  no new roadmap, doctrine, acceptance delegation or model implementation.
- Label: author preflight; separate fresh same-model document check applies
  only to the first-cycle diff identified below. The second-cycle update
  awaits its own fresh review; Claude acceptance/migration integration remain pending.

The author knows the operating rationale. Reviewers derive their contract
from the user goal, master programme, doctrine and ADR-0020 before comparing
the complete diff and the records linked from it.

## Expected contract

Only one live tracker/master remains. Distinct development roles fit the four
available concurrent slots; no author check becomes independent approval.
Remote PR/head/CI evidence is represented accurately. No open PR, code-only
asset, skipped release gate or unverified policy source becomes Done. Existing
worktrees and the prepared #144–147 migration are preserved. Reserved sources,
values, decisions, resources, publication, tags and merge authority remain intact.

## First-cycle verification — historical snapshot

- Focused programme-authority, orientation-example and review-queue acceptance
  checks pass in the locked isolated Python environment.
- All 58 task IDs remain exactly once in order; 12 local Markdown targets resolve.
- `git diff --check` passes. All changes are tracker/map/docs/review evidence;
  production, policy, tests, dependencies and data are untouched against base.
- #138/#142/#143 final-head applicable CI is green; their separate review
  checks passed. Recheck remote
  SHAs before any acceptance; documentation is not a merge permission.
- Baseline full-run plus identity-rerun distinction and local environment skips
  are retained in `reviews/2026-10-03-programme-verification.md`.

No new tests are added for a reversible documentation/tracking increment.
Main-only CI does not run on the stacked draft base. The final exact head and
normal checks must be reviewed after retargeting onto integrated main.

## First-cycle separate check — historical scope

A fresh GPT/Codex reviewer independently derived the contract before the
author narrative and checked `422b055..687ed4d`. No actionable findings.
Task IDs, local links, exact remote PR heads/CI, draft stack state and the
unchanged tested source/workflow content were confirmed. The checker did
not rerun broad suites or audit statutory sources. Subsequent first-cycle
changes only record this check and the draft PR number. Claude acceptance
remained pending at that snapshot.

## Second-cycle author preflight — 3 October 2026

This writer knows the operating rationale and is not the independent reviewer.
Mechanical prior PM head: `14476d03c9f0de8af52788f7cf3bd8f91187ad04`.
The bounded update changes only `docs/programme/EXECUTION.md`,
`PROGRAMME_STATUS.md`, `reviews/2026-10-03-programme-verification.md` and
this packet. The exact handoff head is returned by `git rev-parse HEAD`.

Expected contract: preserve all 58 task IDs/order and the A–P gates; retain
first-cycle checks with their original revisions; record only actual #150
acceptance/merge; distinguish #152's draft closure from a main queue change;
label #148/#151 source checks as same-model with Claude/Pete gates pending;
require refreshed heads/CI/Opus acceptance for #138/#142/#143. Preserve the
unmerged migration stack and existing workers. Reconcile/review the uncommitted
`build/p1-household` increment before assigning another household/model/mapping
writer; ADR-0017 mapping/parity requirements remain acceptance gates.

Inputs are the actual Claude JSON results identified and summarised in the
verification record, fixed source-review artifacts at #148 `0db2bfaf` and
#151 `50f13f44`, and the coordinator's bounded second-cycle state. They are
evidence of those reviews only, not review of this new PM diff.

Second-cycle writer checks exited 0:

```sh
PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/python -m pytest -q tests/acceptance/test_programme_authority.py tests/acceptance/test_orientation_examples.py tests/acceptance/test_review_queue.py
git diff --check
```

The focused run had **15 passed**, no skips, in 7.91 seconds, with two existing
Starlette/anyio deprecation warnings. This checks programme authority,
orientation examples and the queue reader; it does not establish release gates.
Mechanical comparison to `14476d03` preserves all 58 task IDs/capabilities and
A–P phase order. The master, architecture/map and acceptance/sequence ADRs
are byte-identical; exactly the four authorised documentation paths changed;
all 12 relative Markdown targets resolve. Production, policy, tests, live
review queue, dependencies and data remain untouched. The committed archive
is checked separately at handoff, preserving the tested file contents.

No broad test, new policy-source audit or live CI rerun is claimed.
The final diff requires a fresh reviewer; the `422b055..687ed4d` check above
does not cover it. Retargeting/reconciliation onto main and latest-head CI
remain acceptance prerequisites; nothing here grants merge authority.

External reviewer permission is pending for new bounded Claude review and
delegated-acceptance runs. The attempted #152 Sonnet pass was rejected by
automatic approval review because the private payload's external destination
lacked explicit consent. No #152 Sonnet review/acceptance or landed #128
closure is claimed. Local authorised writing/checks continue.
