# Programme verification — 3 October 2026

Testing was performed by a separate GPT/Codex testing lead; no tracked file
in the shared `main` checkout was modified. This record describes observed
checks, not release acceptance or a complete security audit.

## First-cycle evidence — historical baseline and pinned PR heads

The following observations precede #150's merge. They remain evidence for
their exact recorded revisions, not a rerun or fresh CI result on newer main.

### Repository baseline

At `e52f5d35913fbb4b81c7b64c6caf6d446c158759`:

- Ruff passed; strict mypy passed on 80 source files; evidence coverage passed.
- Full default pytest: 1,262 passed, 22 skipped, 2 deselected, one environment
  setup failure. The temporary environment used `--no-install-project`, and
  the identity test's child process clears `PYTHONPATH`; it could not import
  `poltika`. This was a resolved REVIEWER_ERROR, not a code fix.
- The baseline wheel was installed into the isolated environment. Focused
  rerun of `test_identity_is_the_same_in_a_separate_process`: one passed.
  All 1,263 runnable selected tests passed across the run and rerun; the
  original single run is not described as green.
- Thirteen skips: missing local PostgreSQL binaries. Eight: deferred/unbuilt
  v0.3 rows including #128 review. One: missing external pilot. Installed
  artifact/code replay are separately selected, not implied by default pytest.

The locked dev environment fixed stale shared dependencies without changing
main. Docker and PostgreSQL are unavailable locally; their tests require CI.

### Existing hosting PR #140

At exact `ffa05168a34b29192ba1bff08622bd1328fe4c59`, an isolated snapshot's
existing installed-artifact test passed: built wheel installed in a fresh venv,
correct import origin, and WFF, AS and combined-household API probes. Its
PostgreSQL sub-probe was unavailable locally. No actionable finding in the
hosting addition; no CI or acceptance clearance is inferred.

### Security fix and negative probes

At `941cbc18a9c0dc9f4d96bc27726f778d05d56e8b`, separate probes verified:

- All action references immutable; tokens restricted; no checkout credential
  persistence; guard scripts and full-history checkout preserved.
- Read-only PR report; issue-only non-PR publisher without checkout/install
  or repository-code execution; explicit `GH_REPO` outside a git checkout.
- Stub `gh` issue create/update/no-due/list-error paths pass, with no external
  issue writes. Due counts 0/1/12 produce the expected advisory output.
- Bandit retains medium findings and blocks high severity, scanner errors,
  empty scans and malformed reports. An unsafe synthetic workflow makes
  pinned zizmor fail with exit 14. Real workflow scan has zero findings.
- Currency CLI ran without GitHub tokens: AS Due(0), WFF Due(3), exit 0.

Local Bash 3.2 cannot execute Ubuntu's `mapfile`; discovery was inspected
and the exact due/output branch executed separately. Hosted scheduled issue
publication was not exercised. Subsequent `f483fb90` changes only this PR's
review documentation; workflows remain identical to the tested revision.

Latest GitHub head `f483fb90b6bc98c12639b8f35c1caf073ead4ff5` has successful
test, pilot-image, both guards, links, pip-audit, source-currency, Bandit and
zizmor checks. The scheduled external-links and issue-publisher jobs correctly
skip on a PR. The test workflow includes PostgreSQL, installed-artifact and
retained-code replay, covering those local limitations.

### Separate final document checks

Fresh reviewer of #143 `75eb7a9..82990da` and #138 `e34e681..d868564` reports
no actionable findings. Complete diffs, issue YAML/form references, private
visibility/issues enabled, actual tooling, release-gate doctrine, tiers and
promotion safeguards were checked. Both whitespace checks passed. This is
fresh same-model review of GPT/Codex fixes, not independent Claude acceptance.

At the recorded heads, both PRs also have successful test, pilot-image and
guard checks: [#138 test](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37083113350)
and [#143 test](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37083111237).
The workflow includes the PostgreSQL and installed-artifact checks unavailable
locally. Passing CI does not clear delegated acceptance.

The source-scoping draft has its separate dated source check in #148.
All pending cross-model, policy, milestone, pilot and acceptance gates remain.

## Second-cycle evidence — 3 October 2026, after #150 merge

This dated update is written from actual recorded Claude results, fixed
source-review artifacts and the coordinator's PR-state handoff. It is not
a new independent review or broad test run by the PM writer.

### Actual Claude review and delegated merge

`/private/tmp/poltika-pr128-claude-review.json` records a completed read-only
Sonnet review: Approve, no outstanding findings; the four conditional-summary
findings were verified fixed. It inspected formatting, verifier/caller and DOM
boundaries but ran no test/lint commands. The acceptance record identifies
the reviewed code head as `948fb24`; later changes before merge were docs only.

`/private/tmp/poltika-pr150-opus-acceptance.json` records actual Tier A
acceptance and squash merge of PR #150 at 01:38:42 UTC. Accepted PR head:
`ea872403acdd3e3a37a15040161d4fb847332f12`. Merge on main:
`3bea73fba44f9173ecc4ee3d00be3aa22328b993`. Opus checked PR checks and
the ancestor/up-to-date condition, used no admin bypass, and left the branch.
Its compare/run-list calls were unavailable; it used live refs, the local
ancestor check and `gh pr checks`. It explicitly left #128 queue closure for
a separate documentation PR.

Draft #152 now targets main at `2404ab47fc17b5c685382155cf616e5b014e92ee`.
Its local checks record **7 passed/7 skipped** and a separate same-model
document check has no findings. Those are not zero-skip release evidence.
The #128 row remains open on main until the closure PR is accepted and merged.
Actual Sonnet review of #152 has not run: automatic approval review rejected
the new invocation because the private payload's transmission to Anthropic
lacked explicit destination consent. The bounded permission request is pending;
authorised local checks continue. No whole-goal blocked state is inferred.

### Baseline PRs: actual review, refreshed acceptance still pending

`/private/tmp/poltika-baseline-claude-review.json` records completed actual
read-only Sonnet review of #138/#142/#143 with no blocking findings. This
is separate from the first-cycle same-model checks. The review verified
the intended token/job boundaries, governance/release wording and evidence
promotion contract; it did not independently rerun live CI, authenticate
action SHAs or exercise merge conflicts. All three were behind main after
#150 at the coordinator's second-cycle handoff. Base refresh, review of
any new diff, latest-head CI and Opus acceptance remain required. The old
green-check statements above apply only to their recorded heads.

### Source drafts and limits

- #151 final draft head: `50f13f44533cdab2939dd80e37538c8313ecb774`.
  The [separate source check](https://github.com/hemmingsenpeter-byte/poltika/blob/50f13f44533cdab2939dd80e37538c8313ecb774/reviews/2026-10-03-core-benefit-source-scope.md)
  found P2/SPEC_ERROR in the JS category label. Correction `b238820` was
  inspected by the separate checker and resolved; catalogues stayed unchanged.
  Its 9/10/10 entries validate. The independent retrieval was by another
  GPT/Codex agent: it is a same-model check, not Claude rotation or Pete D1.
- #148 final draft head: `0db2bfaf787280a6cda252f6fa7e9287ba107ef7`.
  The [fresh same-model source check](https://github.com/hemmingsenpeter-byte/poltika/blob/0db2bfaf787280a6cda252f6fa7e9287ba107ef7/reviews/2026-10-03-income-tax-source-scope.md)
  remains limited to the recorded source head `cd2f116`; later draft changes
  only record review/tracking. Claude review and Pete D1 remain pending.

Neither draft creates approved specifications, monetary parameters, protected
cases or runtime engines. Period/rounding/payment and supported-slice gaps
remain. Migration #144–147 remains unmerged; its stack and existing owners are
preserved. The main-baseline suite, local PostgreSQL/Docker and code-replay
limits above are not silently replaced by these source/document checks.

The planning check also identified an existing household writer in
`/Users/peterhemmingsen/poltika-p1-household` on `build/p1-household`, with
uncommitted household/mapping files, roundtrip/semantics tests and pass1/pass2
documents. This ownership state is retained from the coordinator's planning
handoff, not a new code audit by this PM writer. Reconcile/review that increment
before assigning another household/model/mapping writer; golden parity and
source-derived mapping acceptance are still required.

### Local evidence identities

These session files were read and their results retained above; they are not
portable repository artifacts or a fresh review of the revised PM draft.

| Local file | SHA-256 |
| --- | --- |
| `/private/tmp/poltika-pr128-claude-review.json` | `80e2a55413a208180d32e0cda5e0eb119da3173dbf06c4b81713f14ddf83a74b` |
| `/private/tmp/poltika-pr150-opus-acceptance.json` | `31bb9a15cacf2d4039865af24794fccf81eaac207dd7b33117ec0966e80b0dc8` |
| `/private/tmp/poltika-baseline-claude-review.json` | `ca0b0574109fb6476aad922a0f4b62883a9bae4e422471ea9907b4a7141e92eb` |
