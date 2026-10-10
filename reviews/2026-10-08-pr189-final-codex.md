# PR #189 final-source Codex recheck — 8 October 2026

No new actionable P1 or P2 findings at `5be777c3abf7f0e533e1025a31d52de45d461ecf`.
The original eight P2 findings retain their dispositions in the PR-branch
record `reviews/2026-10-08-pr189.md`. The GPT/Codex review of Claude's
scenario experience is complete. The owning Claude session subsequently
recorded its fresh-context cross-model review of the Codex fixes as clear.
Both model scopes now have review evidence with no unresolved P1/P2 at the
frozen source head. The owning session retains stack integration and merge
authority; a later semantic change needs renewed review.

## Review inputs

- Reviewer: GPT/Codex, with two fresh-context GPT reviewers, 8 October 2026.
- PR: https://github.com/hemmingsenpeter-byte/poltika/pull/189.
- Base: `e5d87c3eba19540cfe499bfab86a87a9018d884a`.
- Frozen head: `5be777c3abf7f0e533e1025a31d52de45d461ecf`.
- Original findings/fixes: `82b8f1c` → `17bf1bd` → `1496de4` → `9c6a254`.
- Contracts: `BUILD_PLAN_B0_1_WEB.md` B0.1.3/B0.1.4, ADR-0023,
  Epistemic Constitution, architecture/structure, and the frozen
  `v1_blocks.py`, `v1_scenarios.py` and Workbench contracts.
- Scope: final scenario forms/workspace, schemas, formatting, provenance,
  retained definitions/exports, reruns and static/development routing;
  the existing #187 review supplies predecessor coverage.
- Label: independent GPT/Codex recheck of Claude-authored work;
  supporting same-model recheck of previous Codex fixes. The root saw the
  earlier rationale; the fresh reviewers derived expectations first.
- GitHub CI at this head: every executed check succeeded, including
  Python, web, image and security. Report-only external links and the
  scheduled issue publisher were skipped.

## Independently derived expected behavior

1. Confirmation captures all checked options and exactly the request later
   submitted; edits and late responses cannot approve different inputs.
2. Edit-as-new preserves retained options or household facts, dates and
   versions. Reruns create a new run; exports read the selected stored run.
3. Missing and unresolved quantities keep their outcomes. Household Rule
   strings stay exact; population aggregates display three significant
   figures while retaining/exporting full stored precision.
4. Known blocks validate their bodies; unknown types render a notice.
   Units, periods and provenance remain inspectable. Deep routes keep real
   IDs; legacy JSON and household requests still reach FastAPI.

## Discrepancies and disposition

No new reproducible CODE_ERROR, TEST_ERROR or other blocking discrepancy
was found. This does not reclassify the earlier eight findings or imply
that a same-model recheck meets the cross-model rotation.

The actual read-only Claude/Sonnet CLI attempt returned `is_error: true`,
`Not logged in · Please run /login`, session
`aa98d550-8fa5-4b5c-ac0e-e5553ea81e09`, with no model usage or verdict.
It supplied no review clearance. No login/account change or interaction
with the other Claude session was attempted. The owning session needs a
fresh-context review of `10291cf`…`5be777c`, including the Codex fix
`17bf1bd` and follow-ups, before clearing the remaining queue gate.

A later request to run a separate authenticated Claude reviewer was rejected
by automatic approval review: the CLI could transmit repository contents
and the prompt to an external service, and that destination/payload was not
sufficiently authorized. It did not execute. No workaround was attempted;
the owning Claude session retained the pending cross-model gate at that time.

## Subsequent cross-model clearance

At 04:07 UTC on 8 October 2026 the owning Claude session posted its actual
fresh-context `poltika-reviewer` result for `10291cf`…`9c6a254`:
[PR #189 clearance](https://github.com/hemmingsenpeter-byte/poltika/pull/189#issuecomment-6051987408).
It checked all eight fixes and reported no unresolved P1/P2. The remaining
`9c6a254`…`5be777c` delta is review and queue metadata, covered by this Codex
final-head check. This later review closes the previously pending Codex-fix
gate; the failed CLI attempts above remain historical evidence.

Claude listed three non-blocking P3 follow-ups: null household facts should
read “Not recorded”; the reform description stays stale after an option edit;
population table money cells omit the currency symbol. These remain with
the owning frontend session; this documentation PR changes no frontend.
Claude cleared an earlier head of #192
([comment](https://github.com/hemmingsenpeter-byte/poltika/pull/192#issuecomment-6051987821));
the current #192 head needs its own final-head confirmation.

Pete's subsequent acceptance instruction authorises advancing this review
record and the gated policy-specification work. It does not choose a pending
policy interpretation or override the stack's ownership and CI gates.

## Documentation update preflight

Author preflight, GPT/Codex: independently read the two linked Claude
comments, checked their scope against the frozen #189 head, and retained
the original verification results and failed-attempt history. The #189
queue row is moved into the six-column review table and marked reviewed,
with no outstanding P1/P2 (as of 8 October; superseded by the 9 October section below).
The branch's main integration was conflict-free (as of 8 October; superseded by the 9 October section below).
Only this record and the review queue change in this follow-up. Whitespace
checks pass, and the existing review-queue acceptance tests pass (2 tests).
This preflight does not review its own semantic change independently.

## Verification

Frozen checkout: `/private/tmp/poltika-codex-pr189-frozen-check`.

```sh
PYTHONPATH=/private/tmp/poltika-codex-pr189-frozen-check/src \
  /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q \
  tests/unit/api/test_v1_workspace_regressions.py \
  tests/unit/api/test_v1_household_definition.py \
  tests/unit/api/test_web_static.py \
  tests/unit/scenarios/test_reform_record.py
```

Exit 0: **71 passed, 1 skipped** (the optional built-export copy scan;
`web/out` is not built in this checkout). Shared installed dependencies
were reused; the explicit PYTHONPATH selects the frozen source.

Focused Vitest with existing dependencies and `--maxWorkers=1`: **87 passed
in 10 files**, covering ReformBuilder, HouseholdBuilder, WorkspaceView,
NewScenarioPage, ScenarioWorkspacePage, API schemas/client/scenarioService,
BlockRenderer and formatters. No install or Playwright. `git diff --check
e5d87c3 5be777c` passed.

Full pytest, a new frontend build, browser execution and Render deployment
were not run locally. Final-head CI supplies the broader checks. No source,
statutory expected value, owned branch or Claude worktree was changed.

_Generated by GPT/Codex._

## Subsequent conflicted integration, 9 October 2026

The completed review above remains evidence for frozen `5be777c`. Codex has
prepared and pushed merge `473e9d15194ce83b22751a0e1b4e41949d7ff353`, parent
`5be777c`, integrating current main `26cd8a6dde236f5c3df93602979f5f85de283643`.
It resolved nine conflicts from the stacked squash merges, retaining the
reviewed confirmation, definition/export, rerun and precision implementation.
`git diff 5be777c 473e9d1 -- web src tests .github/workflows Dockerfile` is
empty. The only old-head tree delta is three catalogue-preflight lines from
main; duplicate Docker COPY directives introduced by the automatic merge
were removed. No protected statutory path/value changed.

This is a Codex-authored conflict resolution, so ADR-0020's mechanical-update
exemption does not apply even though the executable tree is identical. Fresh
author preflight, Claude final-head review and current CI remain required.
Do not infer that the old queue clearance covers this new integration. Keep
the three legitimate P3 follow-ups above. Merge this review record before
#189, and merge #188 before #189, through the authorised Claude owner.

On `473e9d1`: 105 focused Python tests passed with 7 skips (6 initially
missing PostgreSQL binaries on PATH; one optional built-export scan). A
separate required-PostgreSQL run with the supported UTF-8 locale and loopback
permission passed 20 persistence/replay/rerun tests. Its first sandbox run
had 12 socket-permission setup errors and 8 passes; it was retried after
that precise cause was identified. Ruff passed; WFF/AS evidence reports had
no problems. Strict mypy was interrupted under severe host contention and
was not a pass. Serial frontend verification on `473e9d1` passed 112 tests in 17 files
with one worker, TypeScript, backend OpenAPI equality and regenerated-schema
equality. No new build or install was performed. Required CI remains a
separate current-head gate. No deployment or release is claimed.
