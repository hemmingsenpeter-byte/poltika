# Reporting fixes — author preflight and deferred rotation

## Review inputs

Accepted base: `3bea73fba44f9173ecc4ee3d00be3aa22328b993`.
Original Claude handoff: `8a541368cc2dda4a0ef18df3288d28b1934bc701` on
`9451859c0a80c26ee02714cc843635a36f785351`.
Isolated original port/findings commit: `99c9aa0`.

Scope: five reporting production files, reporting tests, repository placement,
orientation and review evidence. No policy specification, rate, threshold,
protected fixture, existing engine, dependency, workflow or API route changes.
The original writer's construction directive and completion tracker are excluded.

Contract and original independent findings:
[review record](../reviews/2026-10-03-reporting.md). Approved precision:
[WFF specification](../policy_specs/working_for_families/specification.md),
annual exact-Decimal clause. Evidence classification:
[constitution Decision 4](../doctrine/epistemic-constitution.md). The supplied
economist-first master P3 requires three significant figures for population
displays; it is not merged programme adoption or a rounding rule for households.

## Author status and expected behaviour

GPT/Codex coordinator wrote the fixes after three separate GPT reviewers
recorded the original Claude defects. The coordinator knows the rationale;
this is **author preflight**, and further GPT checks are **same-model checks of
the fixes**. Neither substitutes for the required Claude rotation or ADR-0020
acceptance.

Before export, reject stale result/run/report identities, inconsistent household
coverage/deltas and substituted baseline hashes/date/version/evidence. Render
untrusted Markdown text literally and numeric charts within a finite supported
range. Preserve native units, unknown outcomes, exact household amounts, raw
derived Decimals and synthetic labels. Keep gaps in both chart exports and
reject colliding table identifiers clearly.

Missing WFF annual reference period remains explicit: retained records identify
WFF lookup dates and AS assessment weeks. Optional examples/paths are separately
supplied, with no inherited population-run identity. Non-overridden supplied
parameter resolutions cannot be independently verified from the retained run;
provenance remains partial. Hashes check consistency, not authenticated origin
or statutory truth. Uncertainty ranges remain unavailable until a retained
method and bounds exist. This is a draft library, not Task 24/Phase F acceptance.

## Verification before pinning

- Red regressions against archived `99c9aa0`: 75 failed, 25 passed; the failures
  exercise original integrity, precision, output and chart defects. A later
  native-unit case separately failed on that baseline and passed after its fix.
- Initial fixed reporting plus existing analysis/example/withdrawal checks:
  116 passed. Final focused run: 120 passed (101 reporting, 16 related,
  three orientation), no skips, two dependency deprecation warnings; 38.30s.
  Local log: `/private/tmp/poltika-reporting-fixes-final-tests-20261003.log`.
  Testing memo: `/private/tmp/poltika-reporting-fix-testing-20261003.md`.
- Whole `src tests` Ruff passed. Strict mypy over all production source passed,
  85 files. Scoped new reporting-test mypy passed with inherited imports silent;
  this does not claim the unchanged imported test tree typechecks.
- Local environment: Python 3.12.14 and the locked testing environment used in
  the original review, with `PYTHONPATH=src` selecting this worktree.

## Pinned author preflight and separate checks

Pending candidate SHA, separate read-only worktree, focused/default tests,
security probes and simplification recheck. No acceptance recommendation yet.

## Deferred Claude audit

Inspect the accepted-base-to-final-head diff, original findings and all
follow-up dispositions; check source-bound household precision and native units,
baseline context limits, retained/result/report consistency, output escaping,
numeric rejection, synthetic labels and missing uncertainty/integration gates.
Verify current main, exact-head CI and reviewer/acceptance authority before any
merge. Claude transmission permission remains pending; no attempted bypass.
