# DEC-004: Cash assets over the r 15 ceiling are an evidenced $0

**Policy:** Accommodation Supplement
**Date:** 2026-09-26
**Decision owner:** Pete. Recorded by Claude Code, which Pete asked to decide
it on 26 September 2026 ("fix these now"). GPT/Codex review is pending (Task
34.6).
**Status:** Implemented in policy 0.1.2 (ADR-0014).

## Ambiguity

When cash assets exceed the r 15 ceiling, is Accommodation Supplement an
evidenced $0 (`ineligible`), or can it not be determined? Row AS-06 of the
specification says "exceptional asset-limit increases require separate
facts", but no source in the repo said what those increases are. Until now
the result was `unsupported`, "not a calculated zero".

## Evidence considered

All legislation is at the version as at 4 September 2026, retrieved on 26
September 2026 with the recorded browser user-agent method. The MSD pages
carry no version date and were retrieved on 26 September 2026.

- **Social Security Act 2018, s 65(1)** (`as-social-security-act`): a person
  is entitled to an accommodation supplement if they have accommodation
  costs, **meet the assets requirement** in regulations under s 423, and are
  not excluded.
- **Social Security Regulations 2018, r 15(1)**
  (`as-social-security-regulations`): cash assets "must not exceed" $16,200
  or $8,100. Regulation 15(2) makes this subject only to s 69(2), (2A) and
  (2B): the partner's assets count, including in community-spouse cases, and
  s 67(c) is preserved. Neither r 15 nor Schedule 8 Part 1 mentions an
  increase to the limit.
- **Act s 69(3) and (5):** for 12 months after A, or A's spouse or partner,
  receives a *specified lump sum payment*, s 69(1)'s refusal power for
  unrealised assets does not apply to it. A specified lump sum payment is an
  ACC impairment lump sum or an Independence Allowance lump sum. Nothing in
  the Act raises the r 15 limit in terms, and no other "exceptional" power in
  the Act relates to AS assets.
- **MSD Map, "Assets - non-beneficiaries"** (`as-msd-assets`): a
  non-beneficiary whose cash assets exceed the limit "cannot get
  Accommodation Supplement. There are two exceptions": a lump sum paid for
  impairment, and a lump sum payment of an Independence Allowance.
- **MSD Map, the two exception pages** (`as-msd-lump-sum-impairment`,
  `as-msd-lump-sum-independence-allowance`): "the cash asset limit is
  increased by the amount of the lump sum payment for 12 months from the
  date the payment is received", for the client, partner or dependent
  child. The pages cite Act s 69 and Regulations r 15.

## Decision

AS-06's "exceptional asset-limit increases" are MSD's two lump-sum
exceptions. A new input, `specified_lump_sum_status`, records whether one
applies. It is consulted only when cash assets exceed the ceiling:

| `specified_lump_sum_status` | Outcome when cash assets exceed the r 15 ceiling |
| --- | --- |
| `verified` (no such lump sum received in the 12 months up to the assessment week) | `ineligible`, value 0: s 65(1)(b) fails |
| `excluded` (one was received) | `unsupported`, `outside_scope`: the increased limit is not modelled |
| `unknown` | `needs_review`, `missing_input` |

## Rationale

The Act and MSD agree that assets over the limit mean no entitlement, and
MSD names exactly two exceptions. The statute frames the lump-sum rule
differently from MSD. Section 69(3) disapplies a refusal power for A or A's
partner, while MSD raises the limit and includes a dependent child. The
`verified` fact asks about all three people, so a $0 under this decision
holds under either reading. An exception that applies is reported as
`unsupported`, never guessed.

## Confidence

High that a verified ceiling breach with no lump sum is a $0 entitlement.
Medium on how s 69(3) and MSD's "limit is increased" relate. That question
only matters for the `excluded` path, which stays `unsupported`.
