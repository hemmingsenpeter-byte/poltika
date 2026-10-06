# Income-tax source scope — author preflight and review handoff

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex source-writer agent, coordinated by GPT/Codex project manager.
- Base: prepared programme migration `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Scope: Programme Task 7 / detailed household lane local 0.1.
- Draft PR: #148, stacked on migration #147.
- Separate result: [fresh same-model source check](../reviews/2026-10-03-income-tax-source-scope.md),
  at source head `cd2f116`; source files remain unchanged in later tracking commits.
- Label: author preflight and subsequent fresh same-model source check;
  independent cross-model review and Pete D1 remain pending.

## Mechanical review inputs

- [Source catalogue](../policy_specs/income_tax/sources.yaml): dated official
  legislation, IRD and Parliament entries with pinpoints and explicit limits.
- [Scope proposal](../docs/research/task_0_1_income_tax_scope.md).
- Contracts: `BUILD_PLAN_v0_3.md` local 0.1, source-first/IP/test doctrine,
  `SourceCatalog` in `src/poltika/semantics/schemas/source_catalog.py`, and
  existing WFF/AS supported periods. No external policy engine was inspected.

The author knows the proposal rationale. A separate checker derives the
source-scope criteria before reading it. That check does not clear the
GPT/Claude reviewer rotation or approve a statutory interpretation.

## Expected contract

The pack identifies proposed income types, reference year, calculation basis
and exclusions from primary sources. It distinguishes dated source retrieval
from legal commencement and proposed law from enacted law. Unknown income,
credits, rounding, annualisation and future enactment remain unresolved.
No source inventory or basic-tax scope alone authorises a final tax assessment
or complete disposable-income result.

## Author checks and limits

- Existing `SourceCatalog.model_validate` accepts all 12 unique entries;
  source dates, locators, coverage and pending-review metadata are present.
- `git diff --check` passes; placement is recorded in the repository map.
- No production code, existing policy artifact, protected expectation,
  dataset, dependency or existing test is changed.
- Discovery in the source-currency workflow uses `policy.yaml`; the new
  source-only directory is not promoted into an executable policy.
- No full-Act audit, rounding rule or numerical calculator benchmark is
  claimed. No runtime parameter or statutory expected result is created.
- Existing default-suite/lint/type evidence applies to unchanged production;
  the checker validates this catalogue and the changed documentation separately.

## Deferred independent review

Inspect the exact final PR head and its primary source locators. In particular,
verify BB 1/BC 1–8, Schedule 1 applicability, the 2026–27 annual-rates instrument,
ordinary earnings/main-benefit classifications, proposed exclusions and the
separation of annual basic tax from PAYE/credits/levies. Review the D1 options
without treating the author's recommendation as an accepted slice.

Keep the proposed year gated until enacted authority is independently verified.
Pete's D1 and the later specification, values/cases, implementation, interaction
and release PR gates remain outstanding. The programme task is not Done.

## 5 October 2026 source refresh — author preflight

Refresh base: `main` at `1e185f7652bebce693a9c709cb716b4a9bcfdf5a`.
The earlier check is historical and does not cover this changed head. The
author knew the proposal rationale; a new final-head Claude pass is required.

Expected contract: source-only catalogue, complete main-benefit inventory,
explicit unsupported classes, rank-4 Bill context and unresolved annual-rate,
rounding and implementation gates. Findings recorded before fixing:

- P3 `SPEC_ERROR`: incomplete main-benefit inventory. SSA Schedule 2
  (a)(i)–(vii) and ITA YA 1 (a)–(b) were re-read; youth payment, young parent
  payment, emergency benefit and equivalent assistance now stay unsupported.
- P3 `MISSING_SOURCE`: independently unreproduced Parliament progress content
  now has an explicit browser-retrieval limitation; enactment remains gated.
- P3 `SPEC_ERROR`: missing Bill context added from its explanatory note and
  cls 3, 133(1), (3). The ordinary table is not replaced; this is rank-4
  proposed-law context and adopts no rate or protected expected value.
- Rounding question: searched provisions/pages and outstanding TAA/method/
  calculator research are explicit. Unsearched material is not claimed verified.

NZ Legislation's official dated SSA/ITA HTML (4 September 2026) and Bill
344-1 latest text were retrieved on 5 October with `curl --fail --location
--user-agent 'Mozilla/5.0'`; catalogue pinpoints record the source checks.
No external policy engine was accessed.

Checks completed, exit 0: `git diff --check`; existing `SourceCatalog`
validation (12 unique entries, source-only pack, Bill rank 4, annual rates
`needs_review`, unsupported benefit classes explicit); and
`PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/python -m pytest -q tests/acceptance/test_programme_authority.py`
(10 passed). Numerical implementation, protected values, rounding approval,
independent final-head review and CI remain separate gates.

## 6 October 2026 review-record closeout — author preflight

The independent [Claude review of source head `4e739475`](https://github.com/hemmingsenpeter-byte/poltika/pull/148#issuecomment-5990307031)
and separate fresh reviewer pass are now recorded in the existing review
file. Its historical (a)(i)–(iv) inventory and hash claim are explicitly
limited to `cd2f116`; the current catalogue retains (a)(i)–(vii)/YA 1 (a)–(b).
No catalogue, parameter or expected value is changed by this closeout.
The note links the review record and later Q5 scope commission.

The author knows the source rationale. Checks actually run on the prepared
delta, exit 0: `git diff --check`; existing `SourceCatalog.model_validate`
(12 unique sources, no executable `policy.yaml`); targeted changed-document
relative-file/anchor checks. This is author preflight, not a fresh independent
review. Later main integration, the final commit and current CI must be
checked separately; a final reviewer pass is recorded in the PR without
editing its already committed review evidence again.

### Current follow-up verification — 6 October 2026

Merged `origin/main` at `f9c69d8e3384f0753be482c5ee4a6564cfa5d8ea`
without rewriting history. Current checks exited 0: `git diff --check`;
`SourceCatalog.model_validate` (12 unique source entries; no executable
policy); targeted relative-file/anchor checks (10 links); and
`PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/python -m pytest -q tests/acceptance/test_programme_authority.py`
(10 passed). These are author checks. Final Claude source re-derivation,
current CI and latest-main integration remain gates.
No review-queue row was changed before #170 merged.
