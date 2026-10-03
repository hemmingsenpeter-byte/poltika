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

First candidate `8235506ca8fb1b211b847a805e95d57f2956ac7b` was inspected in
separate detached author checkout
`/private/tmp/poltika-reporting-author-preflight-20261003`. Complete accepted-base
diff, whitespace, whole src/tests Ruff and strict mypy (85 source files) passed.
Its wheel built offline and was installed offline in the temporary testing
environment so isolated child-process tests used the correct package.

Default suite at that fixed head: **1,380 passed, 22 skipped, two deselected**,
two dependency deprecation warnings, 792.05s; exit 0. Opt-in installed-artifact
and code-replay tests were excluded by the repository default. PostgreSQL and
deferred/pilot skips remain limitations, not a zero-skip release claim. Log:
`/private/tmp/poltika-reporting-default-tests-8235506.log`.

The separate same-model security check resolved the original injection/hang/
stale-ID probes, with 101 reporting tests and 48 additional numeric cases passed,
but found R12/P2: unbounded fixed-point expansion before hashing. This was
recorded before fixing in `60e15af`; it prevents clearing `8235506`.

R12 correction uses compact exact Decimal strings for storage/exclusions,
bounded fixed-point display with exact/scientific fallback, and rejects chart
numeric range errors before hashing. Sixteen bounded regressions failed at
archived `8235506` (allocation guards prevented billion-character output) and
passed after correction. Working-fix focused run: **136 passed, no skips**,
two dependency warnings, 38.29s. Whole src/tests Ruff and scoped eight-file
reporting-test mypy passed. A final pin and targeted security/simplification
rechecks follow; the earlier broad result does not cover this formatting delta.
No acceptance recommendation yet.

### Corrected code pin and targeted author verification

Corrected code head: `3a10771bc3dfdb27002ed03286cb61cd36d93809`.
The separate author checkout was pinned to that head. Complete accepted-base
whitespace check, whole src/tests Ruff and strict mypy (85 files) passed.
Focused reporting/analysis/example/withdrawal/orientation checks exited 0:
**136 passed, no skips**, two dependency warnings, 40.16s. Log:
`/private/tmp/poltika-reporting-final-3a10771-tests.log`.

The corrected wheel built and installed offline. From `/private/tmp`, Python
`-I` imported reporting from the temporary environment's site-packages,
preserved an invented exact half-cent amount, parsed SVG, retained its synthetic
warning, stored a billion-exponent Decimal compactly and rejected its chart.
This is an installed-library smoke check, not the excluded full artifact/API/
database/code-replay suite.

Separate same-model security delta check at this head found no remaining
blocker: guarded exponent/hash ordering, compact exclusions/all three exports,
literal Markdown, stale report identity and explicit population HalfUp under
ambient ROUND_DOWN passed; 52 targeted tests passed (7.56s). Probe/log:
`/private/tmp/poltika-reporting-r12-security-probe.{py,log}`.

The separate same-model contract check at `8235506` found no actionable findings,
with 82 focused regressions passed. Genuine baseline/reform/source/date probes,
the real household half-cent, exact storage/population display, Scenario class
and synthetic warnings passed. A real mixed-date run retained identical baseline
and reform signatures; differing future signatures need dated rows or a guard,
not a speculative schema now. Final same-model contract/simplification delta
check at `3a10771` found no actionable findings or remaining blocker, with
21 resource/precision tests passed (0.65s). Exact compact storage, bounded
presentation and chart range validation before hashing passed; earlier 82-test
results were not rerun or represented as final-pin evidence. Local record:
`/private/tmp/poltika-reporting-contract-review-3a10771.md`.
No live Vega/browser or external benchmarking is established. The recorded
findings are resolved within the draft scope; Claude review and ADR-0020
acceptance remain prerequisites, with no Task 24/Phase F completion claim.

Initial draft #154 at documentation head
`10e5e122e8fd97b4d896abe390b0c0c164e5fa67` has production and test files
identical to `3a10771`. All four exact-head checks passed: test, pilot-image,
immutable snapshots and protected paths. The
[test run](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37093544795)
finished at 03:40:33 UTC on 3 October 2026. This evidence belongs to that head;
later documentation updates still require their own latest-head checks.

## Deferred Claude audit

Inspect the accepted-base-to-final-head diff, original findings and all
follow-up dispositions; check source-bound household precision and native units,
baseline context limits, retained/result/report consistency, output escaping,
numeric rejection, synthetic labels and missing uncertainty/integration gates.
Verify current main, exact-head CI and reviewer/acceptance authority before any
merge. Claude transmission permission remains pending; no attempted bypass.
