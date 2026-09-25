# ADR-0007: PR-visibility statutory-value protection (supersedes ADR-0005)

**Date:** 2026-09-21
**Status:** accepted (Pete)

## Context

ADR-0005 decided CODEOWNERS-gated required review, enforced via GitHub
branch protection, as the statutory-value CI mechanism. Installing it (Task
9) found that GitHub branch protection — the feature that turns CODEOWNERS
review into an actual merge block — requires GitHub Pro on a private
repository; this repo is on the Free plan. CODEOWNERS alone, without branch
protection, only auto-requests review as a soft suggestion; it enforces
nothing.

Pete's decision, for a small private repo: task-sized PRs, visible CI
results, and Pete's own judgment before merging are the operating model.
GitHub's mandatory-review/status-check gates aren't required to get a real
review record — PRs and workflow output already provide one.

## Decision

1. **The substantive safeguard is unchanged: independent, fresh-context
   review of policy meaning and benchmarks.** That review — not a GitHub
   approval-button click — is what actually catches a wrong statutory value.
   Nothing about the Review Doctrine or the fresh-context reviewer rotation
   changes.
2. **Test Doctrine's "protected by CI" wording is replaced.** Statutory
   expected-value changes are identified in PR CI, sourced, tested, and
   reviewed before Pete merges — not changed merely to make a test pass. See
   BUILD_PLAN.md's updated Test Doctrine text.
3. **ADR-0005 is superseded, not rewritten.** Its Decision/Mechanism/
   Consequences sections stay as the historical record of the original
   choice and why it didn't hold up; a status note at its top points here.
4. **CODEOWNERS is removed.** It implied an enforcement this plan can't
   deliver, which is worse than not having it — a control that looks like a
   gate but isn't one is a false signal.
5. **The PR guard workflow stays, reframed as visibility, not enforcement.**
   `.github/workflows/statutory-value-guard.yml` lists which protected value
   files (`benchmarks.yaml`, `spec_cases.yaml`, `policy.yaml`) changed in a
   PR, computed from the actual merge-base rather than the PR's base-branch
   tip at open time (fixing a real bug: `base.sha` can be stale if `main`
   moves after the PR branches, silently under- or over-reporting the diff).
   It does not block merge — nothing here can, without Pro.
6. **The operating rule is manual, not technical:** look at the PR diff and
   the guard workflow's result before merging. No subscription change is
   needed for v0.1.

## Consequences

- Task 7/9 in BUILD_PLAN.md point to this ADR, not ADR-0005, for the current
  mechanism.
- Nothing stops a direct push to `main` bypassing review entirely — that was
  already true under ADR-0005 too, since branch protection was never
  actually installed. This ADR is honest about that instead of claiming a
  gate that doesn't exist.
- If the plan ever changes (GitHub Pro, or moving to an org plan), branch
  protection and CODEOWNERS become available again — revisit then as a new
  decision, not an assumed reversion to ADR-0005's exact mechanism.
- Task 9 closes once the guard workflow has been fixed and demonstrated
  working on a real PR, not merely committed.

## Later path additions

The mechanism is unchanged; only the list of watched paths has grown, as
BUILD_PLAN.md asks when a new file holds protected values (Task 28.5):

- `policy_specs/*/golden_households.yaml` (Tasks 28.5 and 29).
- `tests/fixtures/golden_*.json`: the Task 30.4 frozen golden results and
  the v0.1.5 Task 7.2 golden traces. One environment variable regenerates
  each.
- A second, separately titled list for `policy_specs/*/sources.yaml`,
  `specification.md` and `decisions/`: not values, but the texts they are
  cited from and interpreted by, whose hashes every run binds (Task 31).
