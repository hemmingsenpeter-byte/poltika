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
document check has no findings; the seven retained skips are unbuilt capability
rows. The coordinator's latest live check records all four latest-head CI
checks **SUCCESS**: test, pilot-image and both guards. The
[#152 test run](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37087917287)
finished at 02:01:40 UTC; guard runs are
[37087917283](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37087917283)
and [37087917310](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37087917310).
No file/head change followed that check. #152 remains OPEN/DRAFT; successful
CI is not zero-skip release evidence or source/acceptance approval.
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

The same ownership handoff records substantial unmerged implementation
drafts on `build/p1-income-tax`, `build/p1-benefits`, `build/p1-reporting`
and `build/p1-sim-analysis` in their corresponding `poltika-p1-*` worktrees.
The coordinator's 02:14 UTC check on 3 October 2026 found reporting clean at
committed `8a541368cc2dda4a0ef18df3288d28b1934bc701`, with household, tax,
benefits and simulation-analysis still uncommitted at `9451859`. The earlier
collective uncommitted label was a P3 factual discrepancy; it is corrected.
These are branch-local, unaccepted observations; this writer performed no
code audit/tests of them. Source drafts #148/#151 keep their separate state.
The simulation-analysis owner owns both existing snapshot test files;
additive household snapshot/trace parity must wait for a pinned owner
handoff and use an unoccupied path. No capability is marked Done from this
inventory, and older Not started rows do not authorise overlapping writers.

### Local evidence identities

These session files were read and their results retained above; they are not
portable repository artifacts or a fresh review of the revised PM draft.

| Local file | SHA-256 |
| --- | --- |
| `/private/tmp/poltika-pr128-claude-review.json` | `80e2a55413a208180d32e0cda5e0eb119da3173dbf06c4b81713f14ddf83a74b` |
| `/private/tmp/poltika-pr150-opus-acceptance.json` | `31bb9a15cacf2d4039865af24794fccf81eaac207dd7b33117ec0966e80b0dc8` |
| `/private/tmp/poltika-baseline-claude-review.json` | `ca0b0574109fb6476aad922a0f4b62883a9bae4e422471ea9907b4a7141e92eb` |

## Third-cycle reporting and coordination evidence — 3 October 2026

This additive handoff preserves the first- and second-cycle records and their
evidence hashes. It records a new reporting review/fix cycle and a bounded
draft-coherence check; it is not a fresh independent review of this revised
PM document, programme adoption or reporting acceptance.

The original reporting author was Claude. Independent GPT/Codex review used
the source, architecture, test and review contract before inspecting the
implementation and author rationale at
`8a541368cc2dda4a0ef18df3288d28b1934bc701` (base
`9451859c0a80c26ee02714cc843635a36f785351`). The original owner checkout
`/Users/peterhemmingsen/poltika-p1-reporting` remains untouched. Review found
discrepancies in retained-result reconciliation, metadata/provenance,
precision, export identity and charts. Passing the original focused tests did
not resolve those findings or establish Task 24/Phase F completion.

The finding-first isolated port is
`99c9aa0e01431180058f448a8df4d752bc0eddca` on accepted main
`3bea73fba44f9173ecc4ee3d00be3aa22328b993`. The coordinator's GPT/Codex fixes
and separate testing work are pinned at
`8235506ca8fb1b211b847a805e95d57f2956ac7b` on
`codex/reporting-review-fixes`; no reporting PR number exists at this handoff.
The retained tests exercise exact household amounts, population display
precision with full stored Decimal values, stale IDs/deltas, retained metadata,
separately supplied examples/paths, literal Markdown, chart numeric limits,
unknown-outcome gaps, synthetic warnings and native units. Protected statutory
expected values were not changed.

The locked local environment is
`/private/tmp/poltika-testing-e52f5d3-venv`, with `PYTHONPATH=src` for source
assets. The final focused command was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/pytest -q -p no:cacheprovider tests/unit/scenarios/reporting tests/unit/scenarios/microsim/test_analysis.py tests/unit/scenarios/microsim/test_worked_examples.py tests/unit/scenarios/microsim/test_withdrawal.py tests/acceptance/test_orientation_examples.py
```

At the first fix candidate it exited 0 with **120 passed, no skips**, and two
dependency deprecation warnings in **38.30 seconds**. Whole `src/` and `tests/`
Ruff checks passed;
the coordinator also reported strict mypy passing all **85 production source
files**. The reporting tests' scoped strict mypy check passed separately; it
does not establish that all inherited test files type-check. Detailed local
testing evidence is retained in
`/private/tmp/poltika-reporting-fix-testing-20261003.md` and its named logs.
Subsequent security review found new P2 resource defect R12: extreme Decimal
exponents can expand into very large fixed-point strings before a chart guard.
The finding is retained in reporting review commit `60e15af`; candidate
`8235506` is not cleared. A bounded resource fix and additional regression
handoff are underway. Broader pinned-suite verification and the wheel build
remain underway at this handoff. The earlier 120-pass result does not resolve
R12, and these local checks are not green CI evidence.

Separate same-model checks of the GPT/Codex fix candidate remain incomplete,
with R12 unresolved at this recorded handoff. They cannot supply the cross-model
review of their author or Claude acceptance.
The pinned reporting review and author preflight retain the missing annual
WFF reference period, uncertainty bounds and unverifiable complete baseline
parameter resolutions as limits. Task 24/Phase F, source/Pete decisions,
fresh-context review and ADR-0020 acceptance remain gated.

The read-only coordination check compared open drafts #153
(`ce7c5921a5cb1b613c944f7a46b5e1f73b8369d6`), #152
(`2404ab47fc17b5c685382155cf616e5b014e92ee`) and #149
(`40cc0505a2896c7136f43b3e218d88e4dc1b1222`). #153 and #152 overlap the
3A1b tracker status and #128 review-queue row from the same accepted base:
#153 retains pending assurance; #152 proposes closure. Merge #153 first and
refresh #152, or, if #152 is accepted first, refresh #153 to preserve that
closure. Refresh the later PM/migration tracker with actual accepted outcomes
while leaving these dated records historical. Each refreshed head still needs
its required checks and acceptance; this check approves none of the drafts.

The check also distinguished Pete's authorised current working sequence from
unmerged migration adoption. Draft #153 is not doctrine authority. Its phrase
that speculative abstractions “may wait” needs the owner's reconciliation
with AGENTS.md's prohibition on introducing them. No #153 owner file was
changed, and no source, ownership or ADR-0020 gate was relaxed.

### Corrected reporting pin and initial draft CI

The first-candidate paragraphs above are historical. Corrected code pin
`3a10771bc3dfdb27002ed03286cb61cd36d93809` is published in
[draft #154](https://github.com/hemmingsenpeter-byte/poltika/pull/154).
Initial documentation head `10e5e122e8fd97b4d896abe390b0c0c164e5fa67` and
final review-record head `9b6413c8135491b4cd6dd75cc8256eb74648cb15` have source
and test files identical to that code pin; only verification documents changed.

The separate pinned author preflight passed **136 focused tests, no skips**,
two dependency warnings, 40.16s; whole src/tests Ruff and strict mypy over
85 production files also passed. Log:
`/private/tmp/poltika-reporting-final-3a10771-tests.log`. The corrected wheel
built/installed offline and an isolated installed-library smoke passed. It
does not claim the full opt-in artifact/API/database/code-replay suite.

The earlier default-suite run at `8235506` exited 0 with **1,380 passed,
22 skipped, two opt-in tests deselected**, two dependency warnings, 792.05s.
Log: `/private/tmp/poltika-reporting-default-tests-8235506.log`. This belongs
to the earlier candidate and is not final Decimal-delta verification.
All 16 bounded resource regressions failed before R12's fix and passed after.
Separate same-model security delta review found no remaining blocker at
`3a10771`, with 52 targeted tests and guarded exponent/export probes passed;
local log: `/private/tmp/poltika-reporting-r12-security-probe.log`.
The same-model contract checker found no actionable findings at `8235506`
with 82 tests, then no remaining blocker in the final `3a10771` delta with
21 resource/precision tests (0.65s). The earlier 82 tests were not rerun or
represented as final-pin evidence. Local record:
`/private/tmp/poltika-reporting-contract-review-3a10771.md`.

At initial #154 documentation head `10e5e122`, all four exact-head checks
passed: test and pilot-image
([run 37093544795](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37093544795)),
immutable snapshots
([run 37093544762](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37093544762))
and protected paths
([run 37093544827](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37093544827)).
The test job finished at 03:40:33 UTC, 3 October 2026. Latest-head checks for
the final documentation update were pending at that handoff. Subsequently,
all four checks passed at final head `9b6413c`; its
[test run](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37094271115)
finished 03:53:53 UTC. The downloaded exact-job log
`/private/tmp/poltika-reporting-ci-9b6413c-test.log` records default suite
**1,409 passed, nine skipped, two deselected**, two warnings, 442.50s;
installed-artifact **one passed/1,419 deselected**, two warnings, 17.35s;
code replay **one passed/1,419 deselected**, two warnings, 14.88s. Neither
test deselection nor the nine default skips is a zero-skip release claim.
These hosted checks cover their declared PostgreSQL/artifact/replay scopes,
without establishing live Vega rendering or workbench/report acceptance.
Claude rotation
and ADR-0020 acceptance remain pending; no gate or task row is changed. Task 24
remains behind prerequisites 21–23, with no Phase F completion claim.

### Security-CI refreshed handoff

#142's local force-free merge `7ab7cbb92ec4a4cf1297485ba61b9392db1abed6`
has parents `f483fb90` and exact accepted main `3bea73f`. The subsequent
documentation-only head `94f08fc4b541e14cf054b408b13399b972fbe5ee` is published
on `infra/security-ci`. Complete authored/main change payloads survive;
ten non-shared authored blobs and all seven main-only files were checked
byte-for-byte. Both shared documents preserve both sides, with no conflicts.

Separate same-model security/contract review found no actionable finding,
with seven report-reader and four isolated publisher probes passed expected
exits. Bounded author preflight passed 15 existing probe groups and seven
currency tests/no skips (1.46s), whole src/tests Ruff and strict mypy over
80 source files. Cached offline zizmor 1.30.1 returned exit 0/empty findings;
its unsafe fixture returned expected exit 14. Fresh cached Bandit 1.9.4 and
the exact workflow reader returned exit 0, with 11,677 scanned lines, zero
errors, 35 low/four medium/zero high findings. The backlog remains unresolved.
Local commands/results and environment limits are retained in
`/private/tmp/poltika-pr142-refresh-preflight-20261003.md`; preservation and
separate-check evidence are in
`/private/tmp/poltika-pr142-base-refresh-20261003.md` and
`/private/tmp/poltika-pr142-refresh-security-20261003.md`.

No broad-suite, live advisory/link, hosted issue, PostgreSQL, Docker,
installed-artifact or replay verification was repeated locally. Latest-head
CI and ADR-0020 acceptance remain pending at publication. Historical Sonnet
review is not a new review of this head; no new Claude call or merge occurred.
