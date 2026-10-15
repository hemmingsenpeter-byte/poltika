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

The shipped-catalogue wording gate now explicitly skips an unbuilt draft
policy with a named reason. Already modelled catalogues still fail on
unreviewed wording, even if their policy status is changed to draft (negative
probe). This adds an unmet-gate skip; it does not declare Phase B accepted.

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

## Dated source and arithmetic recheck — 15 October 2026

This is an **author evidence follow-up**, not independent Claude review.
Observed PR head: `a6d16675872b50944c0ee92c79564eab9131ccdd`.
Observed current main: `63359fecfe3b6659476528da021ea0ade0023537`;
merge base: `7342e528ad67b58984de5711ba2d195bdef97c67`.
No merge/rebase was performed. Main's intervening #221 changes frontend and
status/release records; no income-tax source, decision or numeric contract
changed. Claude remains integration owner. GitHub's reviews and inline
comments endpoints returned no entries for #219; its only issue comment was
CodeRabbit's draft-review skip. There is no reported Claude finding to mark
resolved or approval to infer.

The checker derived the following table from primary statutory text before
comparing the draft arithmetic. Same-model reconstruction is supporting
evidence and cannot clear the independent cross-model gate.

| Source, version and locator | 15 October observation and limit |
| --- | --- |
| [ITA core, 4 September 2026](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1512313/), BB 1; BC 2–6, 8 | Annual enactment, taxable-income basis and basic liability remain distinct from credits/terminal tax. BC 6(2) supplies the zero path. |
| [ITA Schedule 1, same version](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1523173/), Part A cl 1/Table 1 | All five bands/rates match. General rates exclude the special categories in cls 2–14. The root URL redirects to the first Act part: use this dated parts URL for the actual table. |
| [ITA employment, same version](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/sections/DLM1512779/), CE 1(1)(a); [year provisions](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1520573/), YE 1(2)–(5) | Salary/wage classification and standard April–March endpoints confirmed. Non-standard years and other employment items remain outside this slice. |
| [2024 Budget Measures Act as enacted, 4 June 2024](https://www.legislation.govt.nz/act/public/2024/19/en/2024-06-04/), ss 2(5), 37(1),(4) | Table replacement starts 1 April 2025 and applies for 2025–26 and later income years; it is not the annual taxing Act for 2026–27. |
| [TAA, 4 September 2026](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/), s 92A(1),(2) | Commissioner may assess at basic rates before annual enactment, with adjustment for different enacted annual rates. This does not clear Pete's Q16 project gate. |
| [IRD Bill status](https://www.taxpolicy.ird.govt.nz/bills/2026-fbt-simplification-tax-bill), labelled as at 12 October; [Parliament progress](https://bills.parliament.nz/v/6/ae9d3517-66d6-4a30-c155-08df0eed0d02?Tab=history&lang=en), published 1 October; [Bill 344-1](https://www.legislation.govt.nz/bill/government/2026/344/en/latest/), cl 3 | Latest positive observations identify select committee; Parliament now reproduces in the web reader, with no completed Royal Assent date. NZ Legislation still labels its text Introduction 10 September 2026. No enacted 2026–27 instrument was verified. Retain `needs_review`; recheck currency before approval. |
| [IR3G 2026](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir1---ir99/ir3g/ir3g-2026.pdf?modified=20260331185539), August 2026 cover, pp 7, 43–44 | Fresh bytes match the previously retained PDF hash `4b0f2ffbc831c0aa88235d2c0ce986fa80b234be8f3fb6ac17ee1ab377f71b99`. The printed year is 2025–26; disputed threshold is still $78,101. Q18's `SOURCE_CONFLICT` and complete benchmark exclusion stand. |
| [IRD yearly calculator scope](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income), page updated 1 April 2025, “Gather your information” and tool link | Correct basic-tax scope remains confirmed; linked public tool fails in the web reader. No numeric output, year selector or PDF observed. Official benchmark and final-output precision gates remain unmet. |

The introduction-date conflict (Parliament 9 September; IRD/NZ Legislation
10 September) is preserved. Parliament's displayed 2098 submission deadline
is anomalous and unused. Current consolidation metadata is not a completed
audit of incorporated/unincorporated amendments and commencement/application
across `[2026-04-01, 2027-04-01)`. No complete future-period assurance is
inferred. Whole-period coverage remains `needs_review`.

Independent hand arithmetic, **candidate only**, in NZD before quantisation:

| Taxable income | Exact table sum |
| --- | --- |
| 0; 1 | 0; 0.105 |
| 15,599; 15,600; 15,601 | 1,637.895; 1,638; 1,638.175 |
| 53,499; 53,500; 53,501 | 8,270.325; 8,270.50; 8,270.80 |
| 78,099; 78,100; 78,101 | 15,650.20; 15,650.50; 15,650.83 |
| 179,999; 180,000; 180,001 | 49,277.17; 49,277.50; 49,277.89 |
| 15,603; 200,000 | 1,638.525; 57,077.50 |

Derivation: `15,600 × .105 = 1,638`; add `37,900 × .175 = 6,632.50`,
then `24,600 × .300 = 7,380`, then `101,900 × .330 = 33,627` for the
cumulative endpoints. One dollar below subtracts the current band's rate;
one above adds the next band's rate. No simulator produced these numbers.
All 17 numeric cases match, including `15600.00` as an integral transport.
All remain `needs_review` without an authoritative value. Zero is known,
unknown remains missing, fractional input is refused under Q17, other years
and income categories are outside scope, and `unsupported` precedes pending
authority/missing income. No protected case/value was changed.

The remaining decision is **final output representation**, not reopening
Q17's whole-dollar input scope. At income $15,603, exact arithmetic is
$1,638.525: retaining that as an explicitly unrounded component, or applying
a sourced final monetary rule, would produce different representations.
An assumed nearest-cent rule would itself still require a tie convention
($1,638.53 versus $1,638.52 under the usual half-up/half-even examples).
These are illustrations of the unresolved choice, not sourced NZ rounding
options or proposed expectations. Recommended next action: retain DEC-004's
gate until a period-matched official result and method are checked. If
Pete commissions an explicitly assumed unrounded component, record that
separate output Assumption and keep the missing official-benchmark gate;
it cannot be labelled an official rounded tax assessment.

No new statutory decision, protected-value approval or numeric benchmark is
requested by this source update. Q16–Q18 stand. Next: Claude independently
reviews the final numeric draft; official benchmark/final precision and a
complete dated authority/application/period check precede promotion.

Verification of this bounded working diff (source selection `PYTHONPATH=src`,
existing `/Users/peterhemmingsen/Poltika/.venv/bin/python`):

```sh
python -m poltika.engines.assurance.evidence policy_specs/income_tax
python -m poltika.engines.assurance.currency --as-of 2026-10-15 policy_specs/income_tax
python -m pytest -q tests/unit/policy/test_decision_records.py \
  tests/unit/policy/test_fact_catalogs.py tests/unit/policy/test_case_metadata.py \
  tests/unit/engines/assurance/test_evidence.py \
  tests/unit/semantics/test_unit_binding.py
git diff --check
```

All exit 0: **76 tests passed**; evidence has nine ranked values, eight
primary-source rule rows, no problems and zero approved values; currency
has **nine due**, plus five informational sources lacking structured
checks. A separate YAML comparison against the hand-derived table above
confirmed 47 cases, 17 numeric candidates, no numeric authoritative
expectation, nine `needs_review` parameter values, 14 unique source entries
and zero official benchmarks; packet relative links resolve. No new numeric
fixture, implementation test or source approval was introduced. This is
working-diff evidence; a subsequent commit/integration needs its exact-head
author preflight and independent Claude review before acceptance.
