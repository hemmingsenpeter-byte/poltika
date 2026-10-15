# DEC-002 — annual taxable-income and tax precision

**Policy:** Personal income tax, D11 salary/wage slice.
**Date:** 2026-10-08 (record raised).
**Decision owner:** Pete
**Decision date:** 2026-10-12 (Q17, D36).
**Status:** decided for input scope; output precision remains separately gated.
**Raised by:** GPT/Codex.
**Class:** Assumption (decided input scope); residual source gap in DEC-004.

## Ambiguity

Original 8 October AI-hypothesis question, retained for history:

The complete annual procedure for fractional taxable dollars, intermediate
precision, final rounding and ties remains unverified in the bounded check.

## Evidence considered

The reviewed [ITA Schedule 1 Part A cl 1/Table 1 and BC 6](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
give a table for each dollar and the basic-rate/liability relationship.
They do not establish in this check a complete procedure for fractional
taxable dollars, intermediate precision, final rounding and ties. Checks of
[TAA ss 22D, 22H, 22I, 92 and 92A](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/),
the [IRD yearly-tax calculator scope](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income)
and IR3G 2026 calculation pages (retrieved cover: August 2026) did not close
those gaps. That guide covers 2025–26, not the commissioned period.

## Decision

Pete decided Q17 on 12 October: accept **whole-dollar taxable income only**;
any non-integer input is `unsupported`. This is an **Assumption** about the
first slice, not a rule permitting taxpayer income to be rounded, floored or
truncated. Revisit the boundary if an official method is found. See
[D36](../../../docs/programme/2026-10-12-pete-approvals.md).

The decision removes the input-scope question. It does not specify cent
quantisation, ties or intermediate rounding. Whole-dollar income can give
sub-cent table arithmetic: $15,603 gives $1,638 + 3 × .175 = $1,638.525.
The new packet records exact conditional arithmetic only; adopting a final
tax amount still requires the source/output check in
[DEC-004](DEC-004-output-precision-and-benchmark.md). PAYE/FBT procedures
are not transferred. All currently supported numeric cases, including zero,
remain `needs_review` under the annual authority and review gates.
