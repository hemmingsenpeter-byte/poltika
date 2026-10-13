# DEC-001 — gross SPS entitlement and statutory-side abatement

**Policy:** Sole Parent Support, D11 single established-grant slice.  
**Date raised / source check:** 13 October 2026.  
**Decision owner:** Pete. **Decision date:** none.  
**Status:** open; `needs_review`. **Raised by:** GPT/Codex.  
**Classification:** `MISSING_SOURCE`; scope/meaning choice also requires Pete.

## Ambiguity and missing authority

The accepted output is gross weekly entitlement. The statutory SPS table
contains an amount that the official operational tables label after tax at M.
Income Test 1 reduces the applicable rate; the official deductions page places
that deduction against after-tax payment. The complete method connecting an
abated statutory-side amount to the requested gross amount remains unverified.
The maximum-rate gross observation alone cannot establish the abated curve.

## Evidence considered

- `sole-parent-support-social-security-act-2026-09-26`:
  [SSA s 17; Schedule 2 Income Test 1; Schedule 4 Part 2 cl 1](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/).
  The ordinary table amount is $521.52 a week subject to Income Test 1.
- `sole-parent-support-rates-order-2026`:
  [Order cls 2–5 and Schedule 1 Part 1](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/36/en/2026-03-02B/)
  replace $505.80 with $521.52 from 1 April 2026; they do not insert $606.69.
- `sole-parent-support-msd-rates-2026`:
  [MSD April table, SPS section](https://www.workandincome.govt.nz/products/benefit-rates/benefit-rates-april-2026.html)
  reports $521.52 after tax at M and $606.69 before tax. This is operational
  corroboration, not a complete gross method or approved parameter set.
- `sole-parent-support-msd-deductions`:
  [MSD deductions](https://www.workandincome.govt.nz/on-a-benefit/tell-us/income/deduction-tables/sole-parent-support)
  distinguishes gross earnings from deduction against after-tax payment;
  it expressly describes its printed table as an estimate.
- [SSA ss 349–351](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/)
  identify the separate tax-payment mechanism. Under s 350, MSD may pay tax
  separately; subsection (3) derives the amount by grossing up the payment
  under the appropriate specified provision. Section 351 treats tax paid
  under that mechanism as benefit received and income of the person.
- `sole-parent-support-income-tax-act-interactions`:
  [ITA RD 11(3)(a)](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
  requires the Commissioner, in consultation with the administering department,
  to determine main-benefit PAYE tax despite RD 10(1). The operative
  determination, applicability to this slice, and complete numeric method
  were not verified in this check.

## Decision

None. Retain the gross-output requirement and a missing-source gate. The draft
does not silently change D11 to a net output, choose M for every recipient,
derive main-benefit tax from a wage table or subtract net abatement from gross.

## Resolution required

Obtain the applicable Commissioner/MSD determination or equally authoritative
published method for the reference week, including how abatement, tax amount,
zero limits and precision combine. Independently derive a full gross example.
Pete then confirms the sourced gross meaning and any supported-slice choice;
numeric specification and cross-model review remain separate gates. If the
output scope changes, record that change explicitly rather than relabelling
the statutory-side amount. Unknown gross entitlement is never zero.

## Rationale and confidence

The sources distinguish statutory-side rate, gross benefit income and cash
payment. An incorrect conversion would distort later taxable-income/WFF
inputs and withdrawal measures. Confidence is high in the documented source
distinction; no confidence is assigned to an unverified numeric gross method.
