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
