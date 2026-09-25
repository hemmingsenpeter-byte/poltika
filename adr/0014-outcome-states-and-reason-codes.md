# ADR-0014: Outcome states and reason codes

**Date:** 26 September 2026
**Status:** accepted. Pete asked for the change and chose each option below on
26 September 2026. Drafted and implemented by Claude Code (BUILD_PLAN.md Task
34.6). GPT/Codex review is pending.

## Context

Every component result was `calculated`, `needs_review` or `unsupported`, with
a free-text `reason`. Pete asked for more precision. `needs_review` should mean
that Poltika cannot produce a defensible answer because information required to
determine the result is missing, ambiguous or unresolved. It should never mean
"probably zero" or "the calculation failed". An evidenced zero ("assets $1 over
a hard limit") is a different statement from an unknown amount ("assets
unknown"). A result that cannot be calculated should say exactly what prevents
it and what information would resolve it.

He proposed eight statuses: CALCULATED, INELIGIBLE, NEEDS_REVIEW,
MISSING_INPUT, CONFLICTING_EVIDENCE, INVALID_INPUT, UNSUPPORTED_PERIOD and
UNRESOLVED_RULE.

Three facts shaped the design:

- v0.1's protected files hold about 250 `needs_review`/`unsupported`
  expectations. These are the spec cases, benchmarks, golden households and
  the golden-result fixture.
- About 30 results are "outside the modelled domain", such as shared care,
  homeowners and protected credits. None of the eight statuses covers them.
- The approved AS specification says an r 15 asset-ceiling failure is
  `unsupported` and "not a calculated zero" (a PR #25 review finding). Its
  AS-06 row says "exceptional asset-limit increases require separate facts".
  The calculator does not collect that fact, and no source in the repo says
  what the increase is.

## Options

1. **A flat list.** `outcome` is exactly one of the eight statuses, plus one
   for out-of-scope cases. Every protected expectation is relabelled.
2. **A headline plus a reason code.** The headline `outcome` is
   `calculated`, `ineligible`, `needs_review` or `unsupported`. Each
   `needs_review`/`unsupported` result also carries a `reason_code`,
   `missing` and `resolution`.

## Decision

Option 2, chosen by Pete. It matches his own definition, in which
NEEDS_REVIEW covers "missing, ambiguous, or unresolved". His AS example also
reports unknown assets as NEEDS_REVIEW. The headline says whether there is a
number, and the reason code says why not.

**Headline outcomes.**

| Outcome | Value | Meaning |
| --- | --- | --- |
| `calculated` | the amount (can be 0 after abatement) | The facts and encoded rules produce an answer. |
| `ineligible` | always 0 | The facts establish that an eligibility test fails: an evidenced zero. |
| `needs_review` | none | A required fact or rule cannot be resolved now. |
| `unsupported` | none | The case or period is outside what Poltika models. |

**Reason codes** (`needs_review` and `unsupported` only):

| Code | Meaning | Headline |
| --- | --- | --- |
| `missing_input` | A required fact was not supplied or is unverified. `missing` names the request fields. | `needs_review` |
| `conflicting_evidence` | Two supplied facts disagree (the combined runner's shared-fact checks). | `needs_review` |
| `invalid_input` | The request is inconsistent with itself, such as a lookup date outside the assessment week. | `needs_review` |
| `unresolved_rule` | A rule or rate is not reviewed or not encoded, such as `in_work_base`'s rate status or an undeclared AS row. | either |
| `unsupported_period` | Poltika has no reviewed rules for the period. | either |
| `outside_scope` | The case is outside the modelled domain. | `unsupported` |

The v0.1 headlines stay unchanged, so two codes appear under both headlines.
The Task 20/24.7 module-boundary period checks were accepted as
`needs_review`, while a parameter with no interval for the date resolves
`unsupported`. The r 15 ceiling (below) stays `unsupported`. A fact the
caller can supply or correct is always `needs_review`, and an out-of-scope
case is always `unsupported`.

Every `needs_review`/`unsupported` result also has a `resolution`, which says
what would resolve it or that no caller input can. "Known" facts are not a
separate field: the provenance trace already records every input each
component read, with its value.

`ComponentResult.__post_init__` enforces the contract. A result with a
missing code, a missing resolution, a value where none belongs, or `missing`
facts under any code but `missing_input` cannot be constructed.

**Reclassification: only one, the one the approved specification already
supports.** WFF specification.md says "a genuine, evidenced failure of an
eligibility test may yield zero for that component". Best Start with every
child verified outside Best Start entitlement becomes `ineligible` $0 instead
of `calculated` $0. This relabels 12 WFF spec cases, 5 golden households and
1 interaction case. Every value is unchanged.

**The r 15 ceiling is not reclassified yet (Pete's choice: source-check
first).** It stays `unsupported` with `reason_code: unresolved_rule`, and its
resolution names the pending AS-06 check. GPT is asked to source AS-06's
exceptional asset-limit increase. If a decision artifact then establishes
that no increase can apply to the modelled case, or adds the fact that rules
it out, r 15 becomes `ineligible` $0.

The verified $0 accommodation-cost exclusion (s 65AAA, added by PR #75) is
handled the same way. It stays `unsupported` with `reason_code:
unresolved_rule`, and whether it is an `ineligible` $0 is left to Pete.

Other exclusions that could be read as ineligibility keep their current
outcome: MC 6(a)/(b) disqualification, a household with no dependent child,
and the s 66 social-housing exclusion. Whether each is an evidenced $0 for
the modelled period is an interpretation question that this ADR does not
resolve. Reclassifying any of them needs its own decision artifact.

**Timing (Pete's choice):** this lands before the v0.1.0 tag, so the changed
contract needs GPT/Codex review before Pete's 34.5 acceptance.

## Consequences

- The API response for each component adds `reason_code`, `missing` and
  `resolution`, and `outcome` may be `ineligible`. The scenario record's
  result payload and the provenance report (JSON and Markdown) carry the
  same fields. This changes result identities (`result_id`) for new runs.
  The golden-result fixture is regenerated. Its diff is the new fields plus
  the Best Start relabels, and nothing else.
- `WffResult.total_annual_entitlement()` counts an `ineligible` zero.
- The combined runner's shared-fact findings each carry a code. When several
  kinds apply, the result carries the most serious code
  (`conflicting_evidence`, then `unsupported_period`, then `missing_input`).
  The reason text lists every finding, and the resolution covers each kind.
  A disagreement now flags an `ineligible` result too, because its evidence
  is in dispute. Only `unsupported` is kept.
- The WFF `policy.yaml` `outcome_states` list gains `ineligible`, with no
  `policy_version` bump. This follows the Task 34.4 precedent of changing
  `policy.yaml` without a bump, since no rule or value changes. The reviewer
  should confirm that this is acceptable.
- The Task 35.3 demo run predates this ADR. Re-running it needs PostgreSQL
  and a clean commit after merge.
