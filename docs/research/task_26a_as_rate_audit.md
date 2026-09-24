# Task 26a: AS dated-rate audit

Author: GPT/Codex. Checked: 24 September 2026 (NZST).
Base: `18e1ca5`, after the per-policy provenance merge.
Status: research and discrepancy handoff, pending Claude's independent
source review and Pete's classification. Task 26a is not complete.

## Disposition

Do not populate the current IDs by multiplying published entry thresholds
by four. That would both mislabel rounded thresholds as statutory base
rates and assign one value to households for which MSD publishes different
thresholds. No policy values, protected expected values, or code are changed
by this audit. The existing `needs_review` protection remains in place.

Task 26a.1 explicitly requires stopping and flagging unsupported or
conflicting mappings rather than inferring a value. This is that handoff,
not a proposal to bypass it. The already-known assessment-week validation
bug is separate; fixing it alone will not make these parameter mappings safe.

## Primary-source checks

The source IDs below resolve in `policy_specs/accommodation_supplement/
sources.yaml`, with structured retrieval and version notes.

- Social Security Act 2018, versions 1 April and 4 September 2026:
  Schedule 4 Part 1 clause 1(d), and Part 7 clauses 1-3.
- Social Security Regulations 2018, versions 2 March and 4 September 2026:
  regulations 17-19. Regulation 17 constructs a base rate from applicable
  benefit rates and, in specified parent cases, a statutory maximum FTC
  amount divided by 52. Regulation 18(3) distinguishes the applicable
  Jobseeker-equivalent income level by household. Regulation 19 rounds
  the final AS amount, not an expressly stated intermediate threshold.
- MSD's four AS entry-threshold tables and non-beneficiary income table,
  each explicitly headed 1 April 2026. These are agency tables, not a
  replacement for the statutory definitions. The pages are live, not
  retained historical snapshots, and do not justify March values.

Official legislation was retrieved with the repository's documented
browser-user-agent method after the web tool returned 403. Dated versions
were checked separately from latest. No external policy engine was used.
No 28.2 date, future interval, or policy amendment is approved here.

## F1: base-rate household IDs collapse different published rows

Proposed classification: CODE_ERROR / SPEC_ERROR; priority high before
any rate population. Implementation owner: Claude Code; specification
follow-up: Codex, after review.

`src/poltika/engines/simulator/accommodation_supplement.py` uses
`_household_category()` both for statutory area caps and for
`_base_rate_parameter_id()`. The three cap categories are valid for caps,
but not sufficient for base-rate selection.

Published **rent/board entry thresholds**, NZD/week, at 1 April 2026:

| Actual household | Jobseeker | Sole Parent Support | Supported Living | Non-beneficiary |
| --- | ---: | ---: | ---: | ---: |
| Ordinary single, no children | 93 | No published row | 106 | 93 |
| Couple, no children | 158 | No published row | 180 | 158 |
| Couple, one or more children | 205 | No published row | 227 | 205 |
| Sole parent, one child | 168 | 168 | 184 | 168 |
| Sole parent, two or more children | 168 | 168 | 184 | 168 |

Sources: `as-msd-jobseeker-rates-2026`, `as-msd-sole-parent-rates-2026`,
`as-msd-supported-living-rates-2026`, `as-msd-rates-2026`.
This is a transcription of entry thresholds, not approved base parameters.

Reproduced on `18e1ca5`: for each of Jobseeker, Supported Living and
non-beneficiary, the childless couple and one-child sole parent select the
same suffix `no_dependent_children_couple_or_sole_parent_one_child`.
A couple with children and sole parent with two children both select
`with_dependent_children`. The table shows unequal thresholds in each pair.
No choice of a single value can make both households correct.

The repair needs a base-rate household selector distinct from the cap
selector. Existing partner/child facts distinguish the ordinary rows;
do not change the statutory area-cap grouping. The precise ID convention
and spec change need review before values are populated.

## F2: one non-beneficiary income-level ID cannot represent four levels

Proposed classification: CODE_ERROR / SPEC_ERROR; priority high before
population. Implementation owner: Claude Code.

The income-reduction lookup uses
`as_income_level_{scenario.claimant_category.value}`. For every ordinary
non-beneficiary it is therefore `as_income_level_non_beneficiary`.

`as-msd-income-2026` publishes the following **income thresholds**, identical
across Areas 1-4: single without children 693; couple without children 1066;
couple with children 1117; sole parent 906 (NZD/week). They are not the
separate area-dependent cut-out points. Regulation 18(3)(a)-(c) also
requires household-specific selection.

For an arithmetic diagnostic only, at income 1000 the un-imputed excess
over the published single threshold is 307, while for a childless couple
it is non-positive. Using 693 for both would apply a 76.75 reduction to
the couple that these table rows do not support. This is not an approved
fixture or a claim about a complete household's entitlement.

The income-level selector must distinguish these households independently
of the three area-cap categories. Do not silently load the single rate
under the existing universal ID.

## F3: published thresholds cannot be inverted into exact base rates

Proposed classification: SOURCE_CONFLICT / INTERPRETATION_AMBIGUITY;
priority high before population. Pete decides after sourced review.

For an ordinary single adult Jobseeker, Schedule 4 Part 1 clause 1(d)
and `as-msd-main-jobseeker-rates-2026` give 372.55 per week. Regulation
17(2)(c) uses the maximum benefit rate before abatement or deduction;
Schedule 4 Part 7 clause 3 then applies 25 percent. Exact arithmetic is
`372.55 * 0.25 = 93.1375`, whereas the AS table publishes 93.

Inverting the table gives `93 / 0.25 = 372`, not 372.55. Existing
benchmarks explicitly label such inverted values as assumptions for
conditional arithmetic checks. They must not be promoted into sourced
statutory base rates simply because they reproduce a published example.

This can affect a final amount: at qualifying costs 94.50, with no
income reduction and a nonbinding cap, exact-threshold arithmetic gives
`(94.50 - 93.1375) * 0.70 = 0.95375`, rounding up to 1. Using the published
93 threshold gives 1.05, rounding up to 2. This is a sensitivity diagnostic,
not a new protected expected entitlement.

The consulted Act, regulations, table, general-formula page and entry-
threshold page do not establish an intermediate rounding instruction
that reconciles these numbers. A targeted official-source search for
entry-threshold rounding did not establish one either. Do not infer
nearest-dollar, floor, or ceiling merely by matching some table rows.
Regulation 18(3)'s derived income levels also need their statutory
precision/rounding checked before promotion, rather than assuming that
the displayed whole-dollar levels settle it.

Possible resolutions to investigate, not decisions made here:

1. Retain exact statutory base construction and document why displayed
   agency thresholds differ, after confirming the legally operative method.
2. Establish an authoritative instruction for using the published entry
   thresholds and represent them as thresholds, not invented base rates.

DEC-001 does not decide this issue: it concerns fractional income excess
under regulation 18(2), not entry thresholds or regulation 18(3) levels.

## F4: supported claimant labels need a bounded rate subtype contract

Proposed classification: SPEC_ERROR / MISSING_SOURCE for unrepresented
combinations. No value is invented for a missing row.

The Jobseeker AS table separately publishes a 96 threshold for the
protected pre-15-July-2013 woman-alone category, versus ordinary single
93. `AsScenario` has no fact identifying that subtype. A blanket
`jobseeker_support` single rate would silently include it. Sole Parent
Support's table publishes only sole-parent rows; childless/couple values
cannot be manufactured for every syntactically accepted combination.

Resolve the verification/exclusion contract for such cases explicitly.
Do not infer normal-rate eligibility solely from a broad claimant enum.
An asserted general eligibility bundle is not documentation that the
rate-specific subtype was checked.

## Required handoff and completion conditions

- Claude independently re-fetches the cited sources before reviewing these
  conclusions; Pete confirms discrepancy classifications and decides the
  genuine precision ambiguity. No accepted DEC is created by this author.
- Claude repairs household selection and rate-subtype validation after
  the corresponding contract is reviewed. This work is not implemented in
  this Codex source branch.
- Codex then populates correctly named, effective-dated values and updates
  only permitted affected tests in the same value PR. Add the required
  assumption-free spec case only when the rate contract is resolved.
- Claude's already-tracked AS week-coverage fix remains a prerequisite
  for real module calculations; it depends on Pete's 28.2 decision.
- No test expectation is changed to claim that a real `calculated` case
  exists now. 26a.2, 26a.3 and 26a.4 remain pending.
