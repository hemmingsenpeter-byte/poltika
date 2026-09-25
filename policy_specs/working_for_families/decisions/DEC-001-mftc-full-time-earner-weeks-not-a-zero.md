# DEC-001: MFTC with unverified 52 full-time-earner weeks is not a $0

**Policy:** Working for Families
**Date:** 2026-09-26
**Decision owner:** Pete. Recorded by Claude Code, which Pete asked to decide
it on 26 September 2026 ("fix these now"). GPT/Codex review is pending (Task
34.6).
**Status:** Confirms the current behaviour. No code, value or expectation
changes.

## Ambiguity

The v0.1 question set (QS-5, PR #75) escalated this question. When
`minimum_family_full_time_earner_weeks` is `excluded` (the claimant is not a
full-time earner for every week, or an ME 2(2)-(4) case applies), is the
minimum family tax credit an evidenced $0? The specification says an
evidenced failure of an eligibility test "may yield zero".

## Evidence considered

Income Tax Act 2007, s ME 1, version as at 4 September 2026, retrieved on 26
September 2026 (`wff-income-tax-act`):

- **ME 1(2):** the credit is `(prescribed amount − net family scheme income)
  × weekly periods ÷ 52`.
- **ME 1(3)(c):** "weekly periods is the number of periods of 1 week in the
  entitlement period for which the person is a full-time earner."

## Decision

`excluded` stays `unsupported`, with reason code `outside_scope`. It is not
`ineligible`.

## Rationale

The credit is pro-rated by the number of full-time-earner weeks. Not being a
full-time earner in *every* week establishes a part-year amount, which the
v0.1 branch does not calculate. It does not establish a $0. Only a
verified count of zero full-time-earner weeks would give $0, and that would
be a formula zero (`calculated`), not an eligibility failure. The v0.1 input
contract has no such fact.

## Confidence

High.
