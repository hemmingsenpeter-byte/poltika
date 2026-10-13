# Task 7 numeric income-tax packet — draft handoff

**Author:** GPT/Codex, 13 October 2026.
**Base:** `7342e528ad67b58984de5711ba2d195bdef97c67`.
**Review state:** author preflight and supporting GPT check; independent
Claude full primary-source review remains pending. Final head and actual
verification results are recorded in the draft PR. This packet grants no
acceptance or merge clearance.

## Commission and expected behaviour

BUILD_PLAN_v0_3 step 2.2 requires dated source-linked values, intake questions,
hand-calculated boundaries and official benchmarks. D11 commissions ordinary
annual salary/wage taxable income for one whole-year ordinary NZ resident
individual, 2026–27. Q16–Q18/D36 decide the authority/input/IR3G questions.

- Whole-dollar input only, as an Assumption; never round an input to fit.
- Known outside-slice facts are `unsupported` before unresolved facts/gates.
- Otherwise supported inputs, including zero, remain `needs_review` with no
  numeric value while authority, source and approval gates remain unresolved.
- Authority/approval gates are server-owned; no intake answer clears them.
- Candidate arithmetic is exact decimal per-dollar band summation. It is
  distinct from final tax precision and from independent benchmark evidence.
- No conversion, engine, graph edge, API or existing protected-value change.

The author already knows the rationale; this is an **author preflight**
contract, not an independently derived reviewer verdict.

## Reviewable artifacts and ownership

| Artifact | Content / reviewer action |
| --- | --- |
| [specification](../policy_specs/income_tax/specification.md) | IT-01–08, source-linked formula, outcome/trace contract and applied Q16–18 |
| [policy](../policy_specs/income_tax/policy.yaml) | Nine candidate values, all `needs_review`, no policy version; review each number and interval |
| [facts](../policy_specs/income_tax/facts.yaml) | Nine drafted inputs and monotonicity; `income_tax` scope added to the existing catalogue enum only |
| [cases](../policy_specs/income_tax/spec_cases.yaml) | 47 cases; 17 exact hand-arithmetic candidates kept separate from current gated outcomes |
| [benchmarks](../policy_specs/income_tax/benchmarks.yaml) | Empty official benchmark list; retained gap and rejected candidates |
| [sources](../policy_specs/income_tax/sources.yaml) | Original observations retained, 13 October candidate source/gate checks added |
| [DEC-001–004](../policy_specs/income_tax/decisions/DEC-004-output-precision-and-benchmark.md) | Q16–18 decided; new residual output/benchmark missing-source item remains open |

The catalogue scope extension permits parsing this draft. No runtime engine,
resolver or intake registration is added. The unit-binding discovery test now
checks income tax's `policy.yaml` rather than listing it as absent.

## Evidence and remaining gates

The official current ITA index still identifies 4 September 2026; Schedule 1
Part A cl 1/Table 1 and BC 6 supply the candidate band arithmetic. The 2024
Budget Measures Act ss 2(5), 37(1),(4) supplies applicability from 2025–26.
The dated annual-law gate is separate: official IRD status checked 13 October
reports select committee as at 12 October, so Q16 remains `needs_review`.

Q17 does not decide a final cent/tie method ($15,603 gives $1,638.525 exactly).
Q18 excludes IR3G entirely. The correct-scope official calculator returned
403/request verification; no numeric result/PDF was retained. FBT/PAYE and
transitional business examples cannot close this annual-output gap. No
external policy implementation was consulted.

Evidence report: nine ranked parameter sources, eight primary-source rule
rows, no problems, **zero approved values**. Currency report: **nine due**,
because every value is `needs_review`. These results do not satisfy step 2.2's
exit gate. Tasks 7, 9–11 and Gate B are not declared complete.

Claude's next review must independently rederive primary-source rules,
numbers, input/refusal boundaries and precision limits at the final head.
Pete retains protected-value/interpretation acceptance. After missing evidence
is reviewed and annual assent/application/period coverage verified, use a
reviewed values update before Claude's separate engine PR.
