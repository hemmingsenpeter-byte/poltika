# DEC-003 — SPS and SLP weekly-agreement first slice

**Policy:** Sole Parent Support and Supported Living Payment; this is their shared assessment-basis record.
**Date:** 2026-10-16
**Decision owner:** Pete
**Decision date:** 2026-10-16
**Status:** decided for coverage only; specifications remain `draft_pending_review`.
**Class:** Assumption — an explicit model coverage restriction, not a statutory eligibility rule.
**Affected rules:** SPS-11 and SLP-07.
**Authority:** [Q25 / D44, recorded on main](https://github.com/hemmingsenpeter-byte/poltika/blob/ed39fe700532b1d22b5a7ae2a3daa44963ce9cf6/docs/decision_log.md).

## Ambiguity

D11 requests gross weekly entitlement, but weekly payment does not establish
weekly income assessment. The drafts narrowed SPS and SLP to people with an
active one-week agreement without separately recording that coverage choice.
The question was whether to retain that first slice or require the ordinary
52-week path before implementation. This record resolves model scope only.

## Evidence considered

- `sole-parent-support-social-security-regulations-20261001` and
  `supported-living-payment-social-security-regulations-20261001`:
  [SSR, version 1 October 2026](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-10-01/),
  r 205(1), Schedule 6 item 1: the prescribed income-assessment period for
  SPS and SLP is 52 weeks. Schedule 6 item 2 separately prescribes one week
  for other benefits; this is not the authority for weekly SPS or SLP.
- Same dated Regulations, r 205(2)–(3): MSD may determine a one-week period
  with the person's agreement where 52 weeks would otherwise apply. Either
  party may end the agreement at any time by notice to the other.
- [SSA, version 26 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/),
  s 338(1)–(5), distinguishes the payable benefit week and instalment timing.
  Neither proves an income-assessment agreement.
- Pete's Q25/D44 chooses option (a), agreement-only now and a separately
  reviewed 52-week slice later. The cited assessment-basis provisions were
  rechecked on 16 October 2026; this is not a whole-policy currency check.

## Options and decision

1. **Selected:** retain the active r 205(2) agreement-only slice now; prepare
   the 52-week basis later as its own reviewed slice.
2. Commission and review the 52-week path before implementing SPS or SLP.

For the proposed `[2026-10-05, 2026-10-12)` week, the supported slice requires
an agreement covering the entire week, with dated evidence of its current
application and any notice ending it. A known 52-week basis, absent/ended
agreement or within-week basis change is `unsupported / not_modelled`.
Unknown or contradictory agreement/basis facts are `needs_review`; a known
coverage exclusion takes precedence. No missing fact or refusal has an amount.

Do not infer an agreement from a weekly bank payment, a stable earnings
pattern or the caller's preferred period. Do not divide annual income by 52,
annualise a weekly wage or apportion a spell to construct the required input.

## Rationale, limits and reopening

This keeps a bounded vertical slice while recognising that ordinary 52-week
recipients remain outside its coverage. It does not declare them legally
ineligible. Both specifications link to this one canonical decision.

Q25 records only the coverage choice. It approves no statutory interpretation,
rate, income preparation, gross-up, precision, benchmark or implementation.
SPS DEC-001/002 and SLP DEC-001 remain open; specification review and the
JS → SPS → SLP sequencing gates remain. A zero-income case is still nonnumeric.

Pete may reopen this choice or commission the separate 52-week path. That
requires its own source-linked input/period specification and independent
review; it cannot be implemented by silently assuming a weekly agreement.
