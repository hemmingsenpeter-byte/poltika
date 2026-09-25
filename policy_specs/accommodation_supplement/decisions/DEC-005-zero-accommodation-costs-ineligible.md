# DEC-005: Verified $0 accommodation costs are an evidenced $0

**Policy:** Accommodation Supplement
**Date:** 2026-09-26
**Decision owner:** Pete. Recorded by Claude Code, which Pete asked to decide
it on 26 September 2026 ("fix these now"). GPT/Codex review is pending (Task
34.6).
**Status:** Implemented in policy 0.1.2 (ADR-0014).

## Ambiguity

The v0.1 question set (QS-6, PR #75) made verified $0 weekly accommodation
costs `unsupported` rather than a calculated $0. Under ADR-0014, is that an
evidenced $0 (`ineligible`), or can it not be determined?

## Evidence considered

The Act is at the version as at 4 September 2026, retrieved on 26 September
2026 (`as-social-security-act`).

- **Section 65(1)(a):** a person is entitled to an accommodation supplement
  if, among other things, they "ha[ve] accommodation costs".
- **Section 65AAA:** accommodation costs, "for a person and a period", are
  the rent, board or ownership payments that MSD is satisfied are paid or
  required for the premises. A verified $0 for the assessment week means
  there are no accommodation costs for that period.
- **Section 69(3A):** MSD must refuse a grant that would be payable at a rate
  of zero. This is a second, independent route to the same result.
- **Specification** step 1 and row AS-01 already require accommodation costs.

## Decision

Verified $0 weekly accommodation costs are `ineligible`, value 0. The check
keeps its position in the household gate. Only the outcome label changes
from `unsupported`.

## Rationale

A requirement of entitlement is verified as not met. That is the ADR-0014
definition of an evidenced zero, and nothing in the Act provides an
exception.

## Confidence

High.
