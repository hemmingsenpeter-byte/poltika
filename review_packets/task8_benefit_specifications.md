# Task 8 benefit specifications — draft handoff

**Author/source writers:** GPT/Codex, 13 October 2026.
**Base:** `7342e528ad67b58984de5711ba2d195bdef97c67`.
**Review state:** author preflight plus supporting fresh-context GPT check;
independent Claude full primary-source final-head review remains pending.
Exact published head and actual checks are recorded in the draft PR.
No acceptance, protected-value approval or implementation clearance is given.

## Commission and expected behaviour

Task 8 / v0.3 sources-and-specification steps 3.1.1, 3.2.1 and 3.3.1, under
Pete's D11 and the 6 October restricted-capacity clarification. Pete asked
for all three drafts now. They share a completed proposed reference week,
`[2026-10-05, 2026-10-12)`, checked 13 October. The dates are a project scope
choice. No benefit week-to-year conversion or receipt apportionment is made.
The author knows the drafting rationale; this is **author preflight**, not
the independent reviewer rotation.

| Draft | Commissioned slice | Rules / unresolved monetary method |
| --- | --- | --- |
| [Jobseeker](../policy_specs/jobseeker_support/specification.md) | Single existing ordinary grant, 25+, no dependent children; excludes legacy transfer rate | JS-01–11; gross conversion and income/payment precision DEC-001/002 |
| [Sole Parent](../policy_specs/sole_parent_support/specification.md) | Single existing ordinary principal-caregiver grant; ordinary child/care route, active weekly assessment agreement | SPS-01–18; gross authority and weekly precision DEC-001/002 |
| [Supported Living](../policy_specs/supported_living_payment/specification.md) | Single adult existing restricted-work-capacity s 34 grant, no children; active weekly assessment agreement | SLP-01–13; gross entitlement and precision DEC-001 |

- Unknown grant, income, relationship, child, basis or source facts cannot
  become zero, an exclusion or an administrative determination.
- Known coverage exclusions precede `needs_review`; per-person s 18 and the
  deliberately narrower household coverage limit remain distinct.
- Ordinary payable state and a covering grant are separate asserted facts.
- Gross entitlement, scheduled rate, withheld tax and actual cash payment
  remain distinct; no result while monetary/source/approval gates are open.
- All interpretation text is draft. No `policy.yaml`, `facts.yaml`, protected
  expected cases, engine, household adapter or graph edge is added.

## Primary evidence and material gaps

SSA's current consolidation is 26 September 2026. The earlier 4 September
catalogue entries and original check dates remain for history. Author
comparisons found the scoped benefit provisions unchanged; the updated
CYPFA definition is recorded separately. SSR remains 4 September. The 2026
Order commenced/applies to benefits payable from 1 April under cls 2–4.
Amendment Act 2026/54 commences Part 1 on 2 November and Part 2 on 1 April
2027; no post-commencement coverage is claimed.

Schedule 4 prints $372.55 (JS), $521.52 (SPS) and $424.60 (SLP adult), matching
MSD's net-M observations. The published gross maxima are respectively
$426.12, $606.69 and $489.21. Income-test deductions apply on the statutory
side. SSA ss 349–351 and ITA RD 11(3) establish the tax-dependent gross-up
authority, but the operative determination and complete precision method
were not verified. Subtracting statutory deductions directly from the gross
maxima would be unsupported. The drafts explicitly stop there.

SPS/SLP normally use a **52-week income basis**, despite weekly payments;
r 205(2) permits an MSD/person weekly agreement, terminable under (3).
Their proposed weekly sub-slices require that active agreement. SLP's s 34
own-effort disregard is mandatory up to its sourced limit; SPS childcare
disregard is discretionary. Inputs must carry resolved provenance and apply
the relevant adjustment exactly once. No generic disregard is invented.

Official MSD deduction examples can corroborate a deduction substep, but do
not independently benchmark these requested gross outputs. Full gross
benchmark and precision evidence remain `MISSING_SOURCE`, named in each
decision. Pete owns any residual interpretation choice; an evidence-backed
source update can resolve a missing-source item if no choice remains.

## Review and next steps

Review the full source catalogues, statutory rule rows, period/slice refusal
contracts and decision records against dated primary legislation. The
supporting GPT check cannot approve GPT-authored policy content. Claude must
perform the full source re-derivation at the final head.

The detailed lane's decision order remains Jobseeker → Sole Parent →
Supported Living. Concurrent commissioned drafting does not approve the
later slice or clear those stage gates. Resolve gross-up/precision sources
and interpretations before the separate values/facts/cases/benchmarks PR;
only then may Claude implement an independently accepted slice. Task 8 and
Gate B remain incomplete; Tasks 9–11 still need the connected reviewed work.
