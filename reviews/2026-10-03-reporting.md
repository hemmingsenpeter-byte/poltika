# Reporting handoff review — 3 October 2026

## Fixed review inputs and authority

Original Claude-authored handoff: base
`9451859c0a80c26ee02714cc843635a36f785351`, head
`8a541368cc2dda4a0ef18df3288d28b1934bc701`. Separate GPT/Codex security,
testing and simplification reviewers inspected that fixed head. The coordinator
recorded the expected contract before implementation inspection. This is an
independent GPT review of the original Claude code, not acceptance of a Pass 1
status narrative. Subsequent coordinator fixes require author preflight and the
applicable Claude rotation/ADR-0020 acceptance.

The isolated follow-up starts from accepted main
`3bea73fba44f9173ecc4ee3d00be3aa22328b993`. It ports only the reporting code,
tests and deliberate repository-map placement; the other branch's construction
directive and programme completion claims are excluded.

Mechanical inputs: BUILD_PLAN.md; ARCHITECTURE.md; REPOSITORY_STRUCTURE.md;
doctrine/{review,test,development,epistemic-constitution,llm_boundaries}.md;
approved WFF specification, annual precision clause; the supplied economist-first
master Task 24/Phase F and P3/P5/D8/D9; existing retained population/result,
validation, parameter and code-identity contracts. No external policy engine was
inspected and no statutory expected value was changed.

## Expected behaviour, recorded before the code review

- Consume retained deterministic results without rerunning a policy engine.
  Check their population, result and input identities before analysis.
- Derive narrative and charts from the report tables; detect stale content
  identities before export. Hash consistency does not authenticate caller input.
- Preserve unresolved outcomes and coverage, native WFF-year/AS-week units,
  exact household annual amounts and full stored derived Decimals. Population
  displays use three significant figures. Never invent uncertainty bounds.
- Bind supplied baseline provenance to retained artifacts, dates, versions and
  baseline evidence. Optional examples/paths without run identity remain clearly
  separately supplied context, not results of this population run.
- Keep synthetic status visible, including standalone charts; generated
  households use the constitution's existing Scenario evidence class.
- Escape untrusted output text and reject unrenderable numeric ranges promptly.
  Implemented draft capability does not establish Phase F or release acceptance.

## Findings recorded before fixes

All classifications below are proposed under the review doctrine.

| ID | Severity/classification | Location at original head and reproduction | Expected vs actual |
|---|---|---|---|
| R1 | P2 CODE_ERROR | report.py:684, caller title containing an img/onerror and script; facts, labels and notes share the boundary | Markdown preserves active HTML and Markdown syntax; it must render untrusted text literally. Ordinary HTML/SVG text escaping passed. |
| R2 | P2 CODE_ERROR | charts.py:156, validated one-household population weight `5e-324`; direct overflow/nonfinite probes | SVG does not complete within a two-second watchdog because span/5 becomes zero; Vega can emit Infinity/NaN. Reject unsupported numeric conversion/ranges without zero substitution or an unbounded loop. |
| R3 | P2 CODE_ERROR | report.py:561, change an FTC reform amount/delta while retaining results_sha256; replace run metadata | Changed fiscal figures retain the old results digest; synthetic false/foreign run metadata can be presented. Verify results digest, run identity, population metadata, validation and household coverage. |
| R4 | P2 CODE_ERROR | report.py:581 and tables.py:572, pass apply_reform(actual_baseline, actual_reform), or a real loader set from changed sources.yaml bytes | Reform baseline threshold and stale source artifacts are accepted as complete provenance. Reconcile supplied baseline context to retained hashes/date/version and override evidence; do not claim unsupported origin verification. |
| R5 | P2 CODE_ERROR | report.py exporters, dataclasses.replace a generated Sentence or Table under the old report_id | All three exports accept changed report content under stale report identity. Validate the canonical report digest and references before export; a freshly forged digest does not prove truth. |
| R6 | P2 CODE_ERROR | charts.py:133, line rows `(1,10),(2,None),(3,12)` | Vega filters the gap out and joins its endpoints while SVG breaks the line. Retain invalid path rows so line output preserves the gap. |
| R7 | P2 CODE_ERROR | tables.py:149/195/271/499, actual golden g2 with claimant income increased by 1 returns FTC `7472.225`; average 1/3 | Household display rounds to `7472.23`; stored averages/shares are quantized; population display uses fixed cents. Preserve household precision and raw arithmetic, distinguish population presentation. |
| R8 | P2 CODE_ERROR | charts.py:116/339, standalone chart from the genuine synthetic fixture | Both standalone exports omit the synthetic warning. Carry visible synthetic context through table/chart exports. |
| R9 | P2 CODE_ERROR | report.py:450 | `synthetic` is emitted as an evidence class. Constitution Decision 4 classifies generated households as Scenario; synthetic is separate status. |
| R10 | P3 CODE_ERROR | report.py tables lookup, path labels `a-b` and `a b` | Colliding slugs overwrite table identities and later produce an unrelated chart-hash failure. Reject duplicate identifiers explicitly. |
| R11 | P3 TEST_ERROR | test_tables_and_charts.py:45 | A reused comprehension variable introduces a strict-mypy error in new tests. Rename it; do not fix unrelated inherited test errors in this change. |

R4 also covers fabricated period/version labels. Optional worked examples and
paths lack population-run identity; stamping them with that run's source ID is
unsupported. They must be separately labelled, not silently reconciled.

The line-gap inference is supported by the official
[Vega-Lite invalid-data documentation](https://vega.github.io/vega-lite/docs/invalid-data.html):
filtering null path rows connects remaining valid points. No browser renderer was
executed during the original review.

## Original verification and limits

- Testing lead: 35 focused reporting/analysis/example/withdrawal tests passed,
  no skips; Ruff passed; strict mypy on five reporting production files passed.
  Reporting plus tests mypy found R11 and four errors in unchanged imported tests.
- Security reviewer: 19 reporting tests passed; bounded injection/hang/digest
  probes reproduced R1–R3. No network/filesystem/secret access introduced.
- Simplification reviewer: real loader/reform source substitutions, exact
  household half-cent and standalone chart warnings reproduced R4/R7–R9.
- Retained local evidence: `/private/tmp/poltika-reporting-testing-20261003.md`,
  `poltika-reporting-probes-20261003.{py,log}`,
  `poltika-reporting-p3-probe-20261003.{py,log}`,
  `poltika-reporting-security-probe.py`,
  `poltika-reporting-subnormal-probe.py`. These are local observations, not
  portable public CI artifacts.

No full suite, live browser, national population validity, uncertainty method,
workbench integration, external benchmark, policy source promotion, Phase F
acceptance or merge approval is established. Claude destination permission is
pending following automatic approval review's rejection of private payload
transmission for a prior review; no bypass or new Claude call is made here.

## Author response and resolution

### Follow-up security finding, recorded before its fix

At coordinator candidate `8235506ca8fb1b211b847a805e95d57f2956ac7b`, the separate
same-model security checker found **R12 — P2 CODE_ERROR** at tables.py:153/165
and charts.py:64: fixed-point serialization expands arbitrary finite Decimal
exponents before chart range rejection. `Decimal('1e1000000')` expands into
1,000,001 characters; a guarded probe confirmed that `1e1000000000` requests
over one billion output characters before hashing/range checks. The guard
prevented that allocation; no billion-character allocation was attempted.

Expected: compact exact storage and bounded presentation, plus chart numeric
validation before hashing. Local evidence:
`/private/tmp/poltika-reporting-candidate-expansion-probe.py`. That check also
ran 101 reporting tests and 48 additional numeric rejection probes successfully,
and found the original injection/hang/stale-identity defects resolved. R12 blocks
clearing this candidate; subsequent fixes need pinned re-verification.

The coordinator's follow-up addresses R1–R11 with literal Markdown text,
finite/range-checked bounded charts, retained-input/result and export-content
checks, baseline artifact/date/version/override reconciliation, exact household
display and unquantized stored averages/shares, population presentation, visible
synthetic chart context, Scenario classification and explicit duplicate rejection.
Optional paths also reject native-period mismatches. Supplied examples/paths have
their own context labels, and unchecked baseline fields retain partial status.

Separate testing lead: final focused 120 passed, no skips (101 reporting,
16 related, three orientation); whole src/tests Ruff and scoped new-test mypy
passed. Protected expectations were unchanged. Red regressions were recorded
against the original port before fixes. Pinned security/simplification rechecks,
author preflight and broad verification follow below; this response is not
independent acceptance of coordinator-written code.

Missing uncertainty ranges, annual WFF period evidence, decision dependencies
and reporting/workbench acceptance remain explicit gates.

R12 follow-up: compact exact Decimal storage and exclusion weights prevent
exponent expansion; fixed-point display falls back to compact notation at an
output-size boundary, and chart values are range-checked before hashing. The
boundary controls presentation size, not statutory input validity. Sixteen
bounded regressions failed on `8235506` and passed after correction; the focused
working-fix checks passed 136 tests with no skips. Final pinned checks are
recorded below. The separate author preflight's earlier default-suite result (1,380
passed/22 skipped/two deselected at `8235506`) is preserved separately, not
mislabelled as final-delta verification.

Corrected code pin `3a10771bc3dfdb27002ed03286cb61cd36d93809`: separate pinned
author preflight passed 136 focused tests, no skips (40.16s), whole Ruff and
strict mypy over 85 production files. Corrected offline wheel build/install and
isolated reporting-library smoke passed. Separate same-model security delta
check found no remaining blocker, with 52 targeted tests and guarded compact
exponent/exclusion/all-export probes passed. R12 is resolved in that check;
it does not establish authenticated origin or cross-model acceptance.

Separate same-model contract check at `8235506` found no actionable findings,
82 focused regressions passed. Its real mixed-date probe retained identical
baseline/reform amounts; no current numerical loss was demonstrated from the
override table's undated key. Distinct future signatures require a dated-row
contract or explicit guard. Final same-model contract/simplification check at
`3a10771` found no actionable findings or remaining blocker in the corrected
Decimal delta. Its 21 targeted resource/precision tests passed (0.65s); it
confirmed exact compact storage, bounded exact/population display and chart
range checks before hashing. Earlier 82-test results were not rerun or treated
as final-pin evidence. Local record:
`/private/tmp/poltika-reporting-contract-review-3a10771.md`.

These checks resolve the recorded findings within this draft library scope.
They do not supply the required cross-model Claude review, ADR-0020 acceptance,
live browser rendering, reporting/workbench integration or missing policy/source
decisions. No Task 24/Phase F completion is claimed.
