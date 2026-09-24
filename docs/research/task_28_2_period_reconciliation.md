# Task 28.2: assessment periods and dates

Research author: GPT/Codex. Checked: 24 September 2026 (NZST).
Base revision: `499f54d` (PR #37 merged).
Status: independently reviewed by Claude Code on PR #41; Pete's decision not yet recorded.

This note supplies the evidence and outstanding choices for Task 28.2.
It does not select a demo date, approve a reporting mode, complete Task
26b, change a parameter, or resolve Task 28.1's income interactions.
Pete has removed the usage reserve. Source tasks remain subject to their
own prerequisites, including the 28.2 decision before 26b.

## 1. Distinguish the periods

| Item | WFF | Accommodation Supplement |
| --- | --- | --- |
| Approved calculation domain | Stable household and qualifying facts for the full 2026-27 tax year | Scoped claimant and household facts for an assessment week |
| Policy reference interval | `[2026-04-01, 2027-04-01)` | `[2026-03-02, 2027-04-01)` |
| Result basis | Annual amounts, per component | Weekly AS amount |
| Current module argument | `modelled_date`, a parameter lookup date inside the reference interval | `modelled_date`, currently a single lookup date, not an explicit week interval |
| Separate evidence date | Date on which sources and the Order record were checked | Date on which operative provisions and dated tables were checked |

These are repository contracts from the approved specifications and
`policy.yaml` files, not a claim that the legislation universally limits
all households to these domains. End dates in the table are exclusive.
The selected AS week needs explicit start and end dates; a lookup date
alone does not identify it. No statutory Monday-to-Sunday convention has
been established by this research.

## 2. Evidence checked

Source IDs resolve in each policy's existing `sources.yaml`; the new
`task_28_2_check` fields record date, version, locator and scope.

| Source | Checked provision or page | Finding and limit |
| --- | --- | --- |
| `wff-income-tax-act` | Official 4 September 2026 consolidation, MD 3(1)-(5), MF 4(1)-(4) | Entitlement uses an entitlement-period formula; instalments have a separate statutory calculation and display treatment. This check does not expand the approved full-year-only calculator. |
| `wff-ird-rates-2026` | IR271 April 2026 revision, page 1 heading | Explicit payment year: 1 April 2026 to 31 March 2027. The chart is guidance, not proof of a future uninterrupted in-work rate. |
| `wff-ird-family-tax-credit` | Annual entitlement and weekly/fortnightly payments sections | Guidance distinguishes annual entitlement from instalments and instalment rounding. Dividing an annual output is not enough to establish a particular payment schedule. |
| `wff-iwtc-increase-act-2026` | Sections 2(43)-(45), 106/MF 4L | The early reversal mechanism and 1 April 2027 backstop remain relevant. MF 4L concerns instalments; this research does not perform Task 26b's register search. |
| `as-2025-amendment` | Section 2; Schedule 1, clauses 104-105 | The cost-rule change starts 2 March 2026; transitional treatment includes weekly application and a pending-application exception. A date does not by itself clear all eligibility gates. |
| `as-msd-qualifying-costs`, `as-msd-rate-method` | Opening paragraphs | MSD describes a calculation based on weekly qualifying costs, with the new settings from 2 March 2026. |
| `as-msd-rates-2026` | Non-beneficiary table heading | Weekly table dated 1 April 2026. This is not evidence for a 2 March effective start; numerical derivation remains 26a. |
| `as-2026-amendment` | Section 2; Schedule 2, new clauses 131-132 | AS homeowner changes apply from 1 April 2027. The separate Jobseeker changes start 2 November 2026; do not describe all of this Act as commencing in April. |

Official legislation was retrieved using the repository's documented
browser-user-agent method after web-tool retrieval failed. IRD and MSD
guidance was retrieved separately. Live MAP pages without revision dates
are identified as such; they are not historical snapshots. Once Pete
chooses exact dates, operative-version coverage must be checked for those
dates before implementation acceptance. No unchecked future interval is
declared legally verified here.

## 3. Compatible dates and reporting choices

The existing WFF scope supplies only the full interval
`[2026-04-01, 2027-04-01)`. Choosing a week in a completed earlier tax year
would need another reviewed WFF policy version; it is not an option within
the present domain. Choosing a past date inside 2026-27 does not shorten
the WFF assessment to that date.

An AS week for a combined scenario must fall wholly inside the relevant
reviewed policy and parameter intervals. The 1 April 2026 tables examined
here make an ordinary week after that date a candidate for 26a's work;
they do not establish rates for March. Avoiding a date boundary is a test
design choice, not a statutory rule. The current fixtures' 1 June 2026
lookup date is a possible anchor, not an approved assessment week.
Any other selection needs the same dated-source checks. No exact week or
lookup dates are selected by this note.

A week wholly before 2 November 2026 avoids the additional check of
Jobseeker eligibility facts against the changes commencing that day.
This is a sequencing consideration, not a new limit on AS policy scope:
on or after that boundary, the asserted claimant category needs checking
against the amended eligibility rules.

| Reporting choice for Pete | Consequence |
| --- | --- |
| Keep native periods | Show WFF annual components and the dated weekly AS result separately. No mixed-period total or implied payment schedule. This is the existing build-plan recommendation, still awaiting Pete's choice. |
| Convert for comparison | Requires an explicit purpose, units, interval, rounding and source-backed contract under 28.2. A weekly equivalent is not automatically an actual instalment; multiplying one AS week does not verify a year's entitlement. Additional work is required before implementing this choice. |

Whole-year WFF income and the chosen week's AS income must retain their
distinct verified definitions and periods. Neither annual income divided
by 52 nor weekly income multiplied by 52 supplies the other policy's
input without independent justification. Payment-route exclusions and
shared-fact reconciliation remain Tasks 28.1 and 28.3.

## 4. Implementation finding for Claude

Proposed classification: CODE_ERROR (Pete confirms). Existing on `main`,
not introduced by PR #40.

`src/poltika/engines/simulator/accommodation_supplement.py`:
`_as_module_validation_failure()` requires each resolved parameter's
selected value to span the complete policy reference period. It uses
`_spans_reference_period()` copied from WFF's annual validation, even
though the approved AS specification explicitly distinguishes its weekly
assessment from the reference period ("Note for Task 25").

Reproduction on `499f54d`: using the real AS specification and parameter
set, mock only the first cap's effective start from 2 March to 1 April
2026, keeping its existing value and end date. Validate a 1 June 2026
lookup. The module returns `needs_review` because the value does not span
the reference period starting 2 March; its reason even calls this a
"full-year rate". This is a synthetic interval diagnostic, not a proposed
change to that statutory cap.

Consequently, adding genuinely April-effective base rates in 26a can
leave real June module runs gated. Do not backdate rates or silently
shorten policy scope to make this pass. Claude should align AS validation
with the accepted assessment-week contract, with a focused regression for
an interior valid week and invalid/boundary coverage. Keep WFF's full-year
guard intact. Route and sequence that change with 26a/28.4 after review;
no calculator code is changed in this research handoff.

## 5. Consequences for later tasks

- 26b: evaluate evidence over the full selected WFF interval. A pre-year-end
  check cannot approve the ordinary annual in-work base. An applicable
  earlier reversal invokes the existing split-period `unsupported` path.
  Other eligibility exclusions keep their own outcomes; not every
  household reaches the rate gate.
- 29: select households within the accepted periods and record each WFF
  component outcome. No parameter assumptions may clear the annual rate
  gate. AS numeric runs still depend on 26a and resolution of the weekly
  validation finding above.
- 35: a calculated FTC component and calculated AS result can support a
  question about those components, subject to interaction verification and
  Pete's acceptance criteria. They cannot be presented as a complete WFF
  total if another component is unresolved. Do not assume the demo or
  release gate has thereby been accepted.

## 6. Review and decision record

| Subtask | Status |
| --- | --- |
| Read approved domains and date restrictions | Research recorded above |
| Verify statutory boundaries and separate agency guidance | Bounded checks recorded; final selected-date coverage remains to verify |
| Identify compatible intervals and lookup-date requirements | Recorded; exact AS week and lookup dates not selected |
| Document reporting choices and conversion requirements | Recorded |
| Explain consequences for 26b, golden households and demo | Recorded |
| Claude independently reviews research and the AS finding | Reviewed on PR #41; source-check scope recorded below |
| Pete selects assessment periods, lookup dates and reporting | Pending |
| Codex records Pete's decision and any selected-date follow-up | Pending |
| Claude checks the recorded contract and feasibility | Pending |
| Pete accepts 28.2 | Pending; 26b not started |

Claude independently fetched both AS amending Acts and the MSD table,
confirmed the date constraints, and reproduced the AS validation finding.
The review did not independently refetch WFF MD 3/MF 4 or the IR271 heading;
those checks remain author-verified, not independently source-verified.
The review's reserve-wording and file-location corrections are incorporated
here. Claude owns the AS implementation fix after Pete selects the week.

Decision fields to complete after review: WFF interval; AS week start and
exclusive end; WFF and AS lookup dates; reporting mode; source-check date
and any remaining evidence gaps; Pete's acceptance date. This is a scope
decision record, not a newly resolved statutory interpretation artifact.
