# DEC-003: Identified WFF income exclusion regardless of payer

**Policy:** Accommodation Supplement
**Date:** 2026-09-24
**Decision owner:** Pete; recorded by Codex under "resolve and proceed".
**Status:** Selected interpretation after independent source review in
PR 48; final artifact review and implementation acceptance remain required.

## Ambiguity

MSD's chargeable-income guidance names IRD-paid WFF. Does a verified WFF
credit paid by MSD instead lose the exclusion?

## Evidence considered

- Social Security Act 2018 Schedule 3 clause 8(1)(l): excludes credits or
  amounts received under Income Tax Act subparts MA-MG and MZ; no IRD-only
  payer qualifier. Source `as-social-security-act`.
  [Act, 4 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/).
- Tax Administration Act 1994 sections 80KN-80KO: MSD pays a WFF tax credit
  whose amount is linked to Income Tax Act provisions. Sections 80KP,
  80KK and 80KU preserve relevant transitional payment routes.
  [Act, 4 September 2026](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/).
  Source-map entry `as-taa-wff-payment-routes` is supplied by PR 48.
- `as-msd-chargeable-income` and PR 48's MSD administration guidance:
  agency payment route is not a different statutory credit.
- Claude independently checked the linked statutory chain on PR 48 and
  recommended recording this inference explicitly at high confidence.

## Decision and rationale

Interpret the exclusion by the credit's statutory legal basis, not its
payment mechanism. An identified WFF tax credit under the cited subparts
is excluded from AS chargeable income whether paid by IRD or MSD. Do not
apply that conclusion to every MSD payment or to unidentified amounts.

Verify payment identity, period and any history required by the component
contract. Income supplied already net of excluded credits must not be
reduced a second time. This is not an asset exemption or a direction to
derive weekly income from an annual WFF result.

Regulation 18 concerns non-beneficiaries; do not add an AS income test or
a generic payer gate to ordinary main-beneficiary cases. Transitional
MSD-paid WFF can matter to non-beneficiaries and must retain its evidence.

## Confidence

High, based on the independently checked cross-Act inference. Actual
claimant facts and exceptional instruments are not established by this
decision. It resolves AS-10's payer interpretation, not all WFF-AS rules.
