# PR #218 independent integration clearance — 16 October 2026

## Verdict

**Independent GPT/Codex review clears `961d41873290c76fc8607f87a447d23f89b5573b`: no unresolved P1/P2 findings.** This is review clearance of that exact head, not merge acceptance or clearance of a later commit.

The CodeRabbit P3 is fixed: the queue links directly to the immutable review record in draft #222. Its inherited income-spell diagnostic P3 is accurately retained as an unpublished follow-up, not an integrated fix. Prior R1–R5 remain fixed.

## Inputs and review scope

- [PR #218](https://github.com/hemmingsenpeter-byte/poltika/pull/218).
- Previous reviewed head: `affda3298547ae9d2c8c2f0e9ddd58971f838197`; its substantive review is recorded in [the earlier review](2026-10-16-pr218-final-head.md).
- First integration: `df91333b6227d7aa98ceeebf013413e87ab99529`, parents `affda329` and `6a69274dd3958cc4263417f356d0f2336c6a8ce2` (#225 hosted CI and #223 web fix).
- Queue-only correction: `47d6a9d793506f448d5a0e0d68b08c69e770fb24`.
- Final integration: `961d41873290c76fc8607f87a447d23f89b5573b`, parents `47d6a9d` and `80e440c663fa32269f9be342ae5b61e03f942fae` (#226 licence).
- Current main observed: `80e440c663fa32269f9be342ae5b61e03f942fae`. GitHub reports the reviewed head `MERGEABLE`, with merge status `BLOCKED` while checks run.
- The user supplied a bounded integration checklist, explicitly distinguishing patch equivalence from a new derivation of household logic. This pass verified its assertions against Git objects and live GitHub evidence. A separate GPT/Codex reader independently checked the governance and conflict-resolution delta.

This review reuses the independently derived household contract and source review from the earlier passes. No statutory rule, source version, parameter, protected expectation or interpretation changes in these integrations. No new primary-source audit or legal review of #226 is claimed.

## Independently checked integration properties

1. The PR's diff over `src`, `tests`, `policy_specs` and `model_registry` has stable patch ID `a124d57b6ea400e109367b271d018edd23380261` for all three comparisons: `5ddd689..affda329`, `6a69274..df91333`, and `80e440c..961d418`. Household production paths, policy specifications, tests and registry are byte-identical to the reviewed household implementation.
2. `df91333` inherits its CI workflows and web code/tests byte-for-byte from `6a69274`. The additional source/test paths in the first-parent integration delta are main's web fix; they are not a new household implementation change.
3. The first merge preserves every line from both parents in `CHANGELOG.md` and `docs/decision_log.md`, in order. The second merge also preserves both parents. The final PR's own changelog delta is its 21-line household section, with no deletion; its decision-log delta is D39 and D40. Main's D41 and D42 remain intact.
4. The licence and package metadata inherited in the final merge match `80e440c` exactly. Task 6's changes remain alongside main's programme and repository-structure updates.
5. The two reviewer artifacts retain their historical scope and do not claim clearance of later heads. The probe script remains a reviewer artifact outside production, tests and fixtures. No test imports it.
6. The queue's immutable #222 link resolves to `05d71119a1dc1bc87e4ec710d20b87963ef335cb`. Its claim about `29ea434` being unpublished and outside the PR is accurate. The queue correctly records the `df91333` author and fresh-context passes without claiming they cover the later head.

No new discrepancy is proposed under the Review Doctrine. The inherited diagnostic P3 remains nonblocking and unchanged.

## Verification

Local checks were run in the isolated `df91333` worktree `/private/tmp/poltika-pr218-codex-merge-20261016`, using the existing locked development environment:

```sh
PYTHONPATH=src /private/tmp/poltika-int218-20261015/.venv/bin/python -m pytest -q \
  tests/acceptance/test_review_queue.py \
  tests/unit/scenarios/test_household_run.py \
  tests/unit/scenarios/test_household_roundtrip.py \
  tests/unit/scenarios/test_combined.py \
  tests/unit/engines/assurance/test_model_registry.py \
  tests/unit/api/test_web_static.py
```

Result: **194 passed, 1 skipped, 2 dependency deprecation warnings in 75.37 seconds; exit 0.** The same production and test files are byte-identical at `961d418`. This is supporting evidence, not a claim that those commands ran at the later head.

`git diff --check 80e440c...961d418` passed. The patch-ID, exact-path and parent-preservation comparisons above were checked directly against the final commit objects.

Successful exact-`df91333` CI was independently verified in [the test job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/38804665364/job/116662288730):

- Ruff passed; strict mypy passed for 107 source files.
- Default suite: **2,051 passed, 10 skipped, 2 deselected**.
- Installed artifact: **1 passed**, 2,062 deselected.
- Code replay: **1 passed**, 2,062 deselected.
- Web and pilot-image jobs, guards, source currency, links and security checks passed.

At the last live check of **`961d418`**, `test` and `web` were still `IN_PROGRESS`; pilot-image, guards, source currency, links, pip-audit, npm audit, Bandit and zizmor had passed. Report-only external links and scheduled issue publication were skipped. No final-head full-CI pass is claimed.

## Remaining acceptance gates

The [author delta preflight](https://github.com/hemmingsenpeter-byte/poltika/pull/218#issuecomment-6201932198) and [fresh-context reviewer pass](https://github.com/hemmingsenpeter-byte/poltika/pull/218#issuecomment-6202144616) name `df91333`. The [latest author handoff](https://github.com/hemmingsenpeter-byte/poltika/pull/218#issuecomment-6202157508) names `961d418`, but records only the new merge, patch equivalence and link check. Because the merge required conflict resolution, ADR-0020 requires renewed author/fresh-context coverage of the final head; the mechanical-main exception does not apply.

Claude retains acceptance and implementation ownership. Record those final-head passes, this independent clearance and green required CI before merging. The queue can cite this review as the independent clearance of `961d418`; any later commit needs the applicable renewed review. This reviewer changed only local review output and performed no PR edit or merge.
