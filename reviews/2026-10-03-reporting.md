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

Pending follow-up fixes and pinned verification. Missing uncertainty ranges,
decision dependencies and reporting/workbench acceptance remain explicit gates.
