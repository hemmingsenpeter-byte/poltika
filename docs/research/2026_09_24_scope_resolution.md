# v0.1 scope resolution: 24 September 2026

Decision owner: Pete. Recorded by GPT/Codex under Pete's explicit
instruction, "resolve and proceed", after the PR 46/48 findings were
presented. These are delegated modelling/scope choices, not a claim that
Pete personally selected each value or that independent review is waived.

## Task 28.2: selected dates and reporting

| Item | Decision |
| --- | --- |
| WFF assessment | Full tax year `[2026-04-01, 2027-04-01)` |
| WFF parameter lookup | `2026-06-01` |
| AS assessment week | `[2026-06-01, 2026-06-08)`; exclusive end |
| AS parameter lookup | `2026-06-01` |
| Reporting | Separate annual WFF components and weekly AS, each with period and lookup date |
| Conversion | None: no combined numeric total, annualised AS or implied WFF instalment |

The week is a scenario-design choice, not a statutory weekday convention.
It is after the April rate tables and before the 2 November Jobseeker
change. The evidence and remaining dated-source checks are in PR 41's
`docs/research/task_28_2_period_reconciliation.md`. Choosing June does not
verify the unfinished WFF tax year. Task 26b must keep the whole-year rate
gate and report `needs_review` if evidence does not cover the full year.
Unknown components are not zero and must not disappear into a WFF total.

## AS precision, selectors and scope

DEC-002 selects MSD's published rent/board entry thresholds and published
non-beneficiary income thresholds as an explicit v0.1 modelling convention.
Do not reconstruct a base rate by multiplying a table threshold by four.
The specification repair defines four rate-household categories, separate
from the three statutory cap categories, and an explicit ordinary-rate
verification input. This supersedes the defective missing-parameter names
once the repair is independently reviewed and implemented.

The legal equivalence of regulation 17(2)(f)'s annual-rate wording to its
siblings' maximum-rate wording remains unresolved; the table-based branch
does not evaluate that expression. Parent cases require a verified eldest
dependent child under 16 for the whole AS week. Known outside-domain cases
are `unsupported`; unknown facts are `needs_review`, not assumed ordinary.
No expansion into protected Jobseeker or special Supported Living subtypes.
Sole Parent Support is only supported for a sole parent with children.

Keep AS self-contained: cite its own dated MSD tables and, for any later
statutory derivation, its own FTC primary-source entry from PR 46. Do not
load WFF's policy at runtime or reuse its component output. A shared legal
rate does not imply an executable cross-policy dependency.

DEC-003 records the accepted modelling interpretation that identified
statutory WFF is excluded from AS income regardless of IRD/MSD payer.
This is not a cash-assets exemption or proof of individual payment facts.

## ADR-0012

Accept its existing narrow name-only coverage conclusion. The four opaque
names remain unconfirmed candidates, not verified gaps or required v0.1
features. No external body inspection or speculative implementation is
authorised. Claude owns the corresponding ADR status update; this record
provides the delegated acceptance and does not edit his ADR branch.
The new source-derived rate bugs remain real findings irrespective of that
earlier structural comparison.

## Execution order and acceptance

1. Independently review this contract and decisions; Claude updates
   ADR-0012 and the single BUILD_PLAN status PR from this record.
2. Accept/merge reviewed weekly validation (#43), then its wheel probe
   (#44). Recheck conflicts with #45. #45 is NOT clean for integration:
   its current line-297 empty-date assertion fails with #41's catalogue;
   Claude fixes it and Codex re-reviews before acceptance. #47 is separate.
3. Claude implements the reviewed AS selector/input/provenance repair and
   regression tests. Codex reviews it. Use AS policy revision `0.1.1` at
   coordinated adoption, schema `0.1`; do not silently change `0.1.0`'s
   meaning. This docs PR does not bump the executable policy early.
4. Only then does Codex populate the correctly named table parameters and
   update affected tests under 26a. Missing rates remain gated meanwhile.
5. The date selection unblocks 26b's source check and 28.3 contract drafting;
   neither task is marked done here. Continue the original dependency order.

No runtime values, protected expected results, code, database setup or
BUILD_PLAN statuses are changed in this decision/specification PR.
