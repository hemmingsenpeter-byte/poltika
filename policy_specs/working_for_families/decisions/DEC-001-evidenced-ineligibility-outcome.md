# DEC-001: When an evidenced eligibility failure is $0 and when it is `unsupported`

**Policy:** Working for Families (with the Accommodation Supplement contract
cited for consistency; AS is not changed)
**Date:** 2026-09-25
**Decision owner:** Pete, delegated to Claude Code in session on 25 September
2026 ("just do it all yourself"); drafted by Claude Code.
**Status:** Recorded; open to the deferred GPT/Codex audit. Ratifies the
behaviour already implemented and tested: no code, parameter or protected
expected value changes.

## Ambiguity

The accepted WFF specification says: "Missing eligibility evidence, an
unverified income derivation, or unknown operative rate produces
`needs_review`; structurally outside-domain facts produce `unsupported`.
Neither becomes a numeric zero. A genuine, evidenced failure of an
eligibility test **may** yield zero for that component."

"May" does not say when an evidenced failure must be $0 and when it stays
`unsupported`. The v0.1 question set raised this as QS-5
(`review_packets/v0_1_question_set/q71_140_review.md`): should an evidenced
"not a full-time earner" give minimum family tax credit $0, or stay
`unsupported`? The whole-repo review of 25 September 2026 (PR #79) noted the
same gap more widely: Best Start gives $0 for an evidenced failure while
minimum family tax credit and in-work tax credit give `unsupported`.

## Evidence considered

- `policy_specs/working_for_families/specification.md`, the calculation
  contract paragraph quoted above (WFF-01/02/07/08), and its instruction
  that Tasks 11-15 must not represent out-of-domain households "as zero
  entitlement".
- `policy_specs/SCHEMA.md`: no field may default a missing fact to a value
  that yields entitlement, and "the eventual calculator must distinguish an
  in-scope zero from `unsupported`/`needs_review`".
- `policy_specs/accommodation_supplement/specification.md`: cash assets above
  the r 15 ceiling are "a genuine, evidenced *exclusion* ... `unsupported`,
  not a calculated zero" (confirmed by the PR #25 review). The AS contract
  already answers this question for AS.
- What each WFF input can express (`src/poltika/engines/simulator/wff.py`):
  - `BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT` means verified outside
    Best Start entitlement for the whole tax year. It is a separate value
    from `OTHER_COHORT_UNSUPPORTED` (entitlement exists but is outside the
    v0.1 branch), so it cannot describe a partly entitled child.
  - `minimum_family_full_time_earner_weeks: excluded` covers both "not a
    full-time earner for every week" and an ME 2(2)-(4)
    Commissioner-determined employment period or part-week case (the
    component's `me2_2_4_employment_exclusion` validation check). In the
    second case minimum family tax credit can be payable for part of the
    year.
  - `in_work_eligibility: excluded` covers a main benefit or Student
    Allowance period, an unpaid break, or not being a qualifying full-year
    earner, so in-work tax credit can be payable for part of the year.
  - An empty `children` list is outside the family-scheme membership domain,
    and a part-year child is itself an unsupported path
    (`part_year_child_eligibility`), so no children cannot establish no
    entitlement for the whole year.
- Protected cases that encode the current behaviour:
  `me2_employment_exclusion_unsupported_only_mftc` (WFF spec cases),
  `asset_ceiling_exceeded_is_unsupported` (AS spec cases), and the golden
  households' Best Start $0 results.

## Decision

1. A component is `calculated` with value 0 for an evidenced eligibility
   failure only when the verified facts establish no entitlement to that
   component for the **whole** assessment period, and the input recording
   the failure cannot also describe a case with partial or out-of-branch
   entitlement.
2. Where the recorded fact can also describe such a case, the component is
   `unsupported`, and its reason names the evidenced failure.
3. A qualifying household whose formula yields nothing is a calculated $0.
   Examples: income abated to zero, AS costs at or below the entry
   threshold, or income reduction to zero.
4. AS keeps its accepted contract: an evidenced exclusion (r 15 ceiling,
   no accommodation costs) is `unsupported`.

Applied to v0.1, this changes nothing:

- **QS-5:** minimum family tax credit with `excluded` full-time-earner weeks
  stays `unsupported`. The same value covers ME 2(2)-(4) and part-week
  cases, where $0 would be a false zero.
- **Best Start:** $0 when every child is `outside_best_start_entitlement`.
- **In-work tax credit:** `unsupported` when in-work eligibility is
  `excluded`.
- **No dependent child:** stays `unsupported`.

## Rationale

The specification forbids a false zero in the strongest terms ("Neither
becomes a numeric zero"; not "as zero entitlement") and only permits an
evidenced zero ("may"). Returning $0 from an input that can also describe a
partly entitled household would be exactly the false zero the contract rules
out. This rule uses the permission where the input makes it safe, as Best
Start's dedicated value does, and nowhere else. It matches the AS contract's
explicit choice, and it keeps every accepted, protected expected value.

Alternatives considered:

- **(a) Every evidenced failure is $0.** This needs inputs that separate a
  whole-year failure from the partial and out-of-branch cases they now share.
  The minimum family tax credit and in-work tax credit inputs do not, so it
  would create false zeros or require new inputs. That is a contract change
  for a later version.
- **(b) Every evidenced failure is `unsupported`, including Best Start's.**
  This discards an evidenced, whole-year $0 that the specification permits,
  and changes protected golden results for no correctness gain.
- **(c) A fourth outcome (for example `not_entitled`).** This is a schema
  and architecture change across both policies, the API and the store. It
  is worth considering after v0.1, not needed for correctness now.

A consumer that must tell "not modelled" from "evidenced ineligible" within
`unsupported` reads the reason; option (c) would make that
machine-readable.

## Confidence

medium: the rule follows directly from the accepted contract text and changes
no result, but "may" was not written with this rule in mind, and the
independent GPT/Codex audit of this record is still pending.
