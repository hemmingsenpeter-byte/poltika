# DEC-004 — final tax precision and missing independent benchmark

**Policy:** Personal income tax, D11 salary/wage slice.
**Date:** 2026-10-13
**Decision owner:** Pete
**Decision date:** none.
**Status:** open; `needs_review`. **Raised by:** GPT/Codex.
**Class:** AI hypothesis; not a new statutory rule.
**Discrepancy:** `MISSING_SOURCE`.

## Ambiguity

Q17 restricts the input to whole dollars. It does not decide how an exact
sub-cent table result becomes a final annual tax amount, or approve treating
an unrounded arithmetic component as the authoritative output. The numeric
packet must not silently choose either interpretation.

## Evidence considered

[ITA, dated 4 September 2026, BC 6(1),(2) and Schedule 1 Part A cl 1/Table 1](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
supports the exact sum of per-dollar band amounts. $15,603 gives $1,638.525
by hand. This check has not established a final quantisation/tie method.

[IRD's annual calculator](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income)
has the right basic-tax scope. On 13 October the linked public tool
returned HTTP 403 to the web reader and a request-verification screen in a
normal local headless-browser attempt; no tax result or PDF was obtained.
No challenge bypass was attempted. Published IRD payroll/FBT calculations
use different outputs; IR320's worked example is a transitional earlier
year/business case. Neither establishes this slice's output method or a
period-matched annual salary/wage benchmark. IR3G is excluded by Q18.

## Decision

No decision is invented. Candidate cases retain exact arithmetic strings
separately from the current expected outcome, `needs_review` with no value.
`benchmarks.yaml` has an empty benchmark list and names the missing evidence.
The packet is reviewable but BUILD_PLAN_v0_3 step 2.2 remains incomplete.

**Next evidence action:** retain a dated, period-matched official basic
annual-tax calculation with all inputs, output precision and artifact/hash;
independently compare it against the statute. If that establishes the
method without interpretation ambiguity, close the missing-source item by
reviewed evidence. If a choice remains, bring the competing sourced methods
to Pete. This does not reopen Q16–Q18 or request an IRD contact.
