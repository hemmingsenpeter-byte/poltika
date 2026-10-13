# DEC-001: Gross entitlement, fractional income and payment precision

**Policy:** `supported_living_payment`
**Date:** 13 October 2026
**Decision owner:** Pete
**Status:** `open_pending_pete`; no interpretation or value approved.
**Classification:** `MISSING_SOURCE` for the computational precision/gross-up
method; `INTERPRETATION_AMBIGUITY` if choosing among competing conventions.
**Affected rules:** SLP-10–12; specification calculation steps 5–8.

## Ambiguity

D11 requests gross weekly entitlement for the established ordinary grant.
The Act's adult scheduled amount and the 2026 Order entry are `424.60`
per week. MSD separately publishes `424.60` after tax at M and `489.21`
before tax. Its deduction table labels income-test deductions as deductions
from the after-tax payment. A formula subtracting a scheduled-rate deduction
from the gross maximum would therefore mix different amount concepts.

Section 350 supplies a gross-up mechanism, but these sources do not supply
the applicable agreed tax calculation, fractional-money treatment and
rounding for each abated amount. Two-decimal presentation and whole-dollar
worked examples do not establish income flooring, intermediate or final
cent rounding. The rounded weekly cut-out table also cannot determine an
exact weekly zero or continued grant/payment status.

## Evidence considered

All listed evidence was checked on 13 October 2026; IDs resolve in
[the source catalogue](../sources.yaml).

- Social Security Act 2018, version 26 September 2026, Schedule 2 Income
  Test 1; Schedule 4 Part 3 cl 1(b) and mandatory own-effort disregard;
  ss 349–351. Section 350(3) increases the source payment by the amount
  needed so that its tax deduction leaves the original payment. Section
  351 treats MSD's tax payment as a benefit payment and income.
- Social Security (Rates of Benefits and Allowances) Order 2026, as made
  2 March 2026, cls 2, 4–5 and Schedule 1 Part 1: `424.60` replaces
  `411.80` for Part 3 cl 1(b) from 1 April 2026.
- MSD April 2026 rates, single 18+ without children, distinguish the
  `424.60` net-M and `489.21` gross columns.
- Income Tax Act 2007, version 4 September 2026, RD 11(3)(a), overrides
  RD 10(1) and requires the Commissioner, in consultation with the
  administering department's chief executive, to determine main-benefit
  PAYE tax. The dated section itself was checked, not its contents index.
- MSD SLP taxation guidance states that the benefit is taxable and clients
  receive a net payment; it links ss 349–352.
- MSD single 18+ deduction table describes two income-test bands and
  labels its deduction column after tax. The table is expressly an estimate.
- MSD personal-earnings Example 1 and weekly-income Examples 1–2 show
  whole-dollar reduction calculations. They do not state a general
  fractional-income or benefit-rounding method.
- MSD current cut-outs at 1 April 2026 explicitly round weekly income
  figures to the nearest dollar and direct annual comparison near the
  boundary. That is a cut-out presentation warning, not a benefit-payment
  rounding authority.

The verified Income Tax Act RD 11(3) authority must not be treated as an ordinary salary/wage PAYE
algorithm or an annual basic-tax formula without the relevant method.
Accommodation Supplement's r 19 rounding and DEC-001 apply to that policy;
they do not answer SLP's question.

## Decision

**Pending Pete. No rounding or gross-up convention is adopted.**

Keep gross entitlement absent with `needs_review` until the missing method
and interpretation are sourced, reviewed and recorded. This applies even
when chargeable income is explicitly zero: the documentary gross maximum
has not become an approved parameter or a general conversion rule.
Known outside-slice facts still take precedence as `unsupported`.

Required closeout: determine the tax method actually applicable to this
benefit/week, its inputs and rounding; establish fractional-income handling
and any intermediate/final rounding; source precise cut-out and payment
status treatment; independently reconcile supported amounts with a dated
official example. Pete records the accepted contract and rationale before
the values stage creates protected expectations or implementation starts.

Possible narrowing to a sourced monetary subdomain, or a deliberate model
Assumption, requires Pete's explicit recorded decision and clear output
labelling. This document neither makes that choice nor requests agency
contact or a broadened model. The blocker is confined to the affected
monetary claim; documentary drafting and review can continue.
