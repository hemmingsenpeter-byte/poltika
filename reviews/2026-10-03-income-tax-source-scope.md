# Income-tax source scope — fresh same-model check

- Date: 3 October 2026, Pacific/Auckland.
- Reviewed head: `cd2f1162be5aaa9ca43fe7505e0f7410791b09db`.
- Base: prepared migration `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Author: GPT/Codex source-writer agent.
- Reviewer: separate GPT/Codex source/evidence checker with a fresh context.
- Result: no actionable discrepancy or P1/P2 finding in this bounded draft.
  This is not independent Claude rotation, statutory approval or Pete D1.

The reviewer derived Task 7/local 0.1 requirements before reading the draft:
source-linked income types, period, annual/withholding basis and exclusions;
dated catalogue metadata; no executable parameters or approved amounts;
unverified enactment and unknown income/rounding/interaction facts gated.

## Independently checked sources

The dated official locators in the catalogue were read independently:

- Income Tax Act 2007, 4 September 2026: BB 1; BC 1–8; CE 1; CF 1; CW 33;
  DA 2; LC 13; MA 3; RD 3; YA 1; YD 1; YE 1; Schedule 1 Part A clause 1/Table 1.
  The official latest header also identifies 4 September 2026.
- Taxation (Budget Measures) Act 2024: ss 2(5), 37(1), 37(4).
- Annual Rates Act 2026 No 8: s 3 establishes the 2025–26 annual rates.
- Social Security Act 2018, 4 September 2026: Schedule 2, paragraph (a)(i)–(iv).
- Bill 344-1, IRD status and Parliament progress: retrieved proposal/select
  committee status and the recorded introduction-date difference agree.
- IRD annual calculator scope, individual rates, taxable income, IETC and
  IR340 April 2026 cover/printed p3: stated scope and update dates agree.

The [catalogue](../policy_specs/income_tax/sources.yaml) retains the exact
primary URLs, versions and pinpoints. No numerical calculator result or
future-year enactment is inferred. The population/WFF artifacts confirm that
grouping income and family-scheme income are not individual annual taxable income.

## Verification and limits

- `git diff --check 422b055..cd2f116`: passed.
- Current `SourceCatalog.model_validate(yaml.safe_load(...))`: passed, 12
  unique sources, required stated metadata present; bill/status entries rank 4.
- Source/note hashes match the committed head; note link resolves; worktree clean.
- No full-Act/future-year audit, statutory rounding, benchmark expectation,
  approved slice, annualisation or income mapping is claimed.

Claude's independent review and Pete D1 remain pending. The source pack is
preparation for onboarding, not evidence that the income-tax capability is done.
