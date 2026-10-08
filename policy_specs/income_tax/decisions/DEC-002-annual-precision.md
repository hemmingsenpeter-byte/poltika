# DEC-002 — annual taxable-income and tax precision

**Status:** open; `needs_review`. **Owner:** Pete. **Raised:** GPT/Codex,
8 October 2026. **Class:** AI hypothesis; proposed discrepancy `MISSING_SOURCE`.

The reviewed [ITA Schedule 1 Part A cl 1/Table 1 and BC 6](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
give a table for each dollar and the basic-rate/liability relationship.
They do not establish in this check a complete procedure for fractional
taxable dollars, intermediate precision, final rounding and ties. Checks of
[TAA ss 22D, 22H, 22I, 92 and 92A](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/),
the [IRD yearly-tax calculator scope](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income)
and March 2026 IR3G calculation pages did not close those gaps.

This is a bounded negative finding, not a claim that no official rounding
rule exists. PAYE or FBT worksheet conventions have different output scope
and are not transferred. No floor-to-dollars, nearest-cent, truncation,
intermediate rounding or exact-fraction convention is selected by this draft.
Decimal arithmetic is a transport/implementation requirement, not legal
authority for a rounding choice.

**Effect:** all numeric results remain gated, including whole-dollar and
known-zero examples; no parameter/expected-result fixtures are supplied.
**Smallest Pete action:** commission/identify a dated official annual basic-tax
method or obtain authoritative clarification, then decide only after the
source and independent review establish the procedure. See PETE_QUEUE Q17.
