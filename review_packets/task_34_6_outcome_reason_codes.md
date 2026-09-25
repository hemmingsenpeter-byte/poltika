# Review Packet: Task 34.6 outcome states and reason codes (ADR-0014) — 26 September 2026

**Label: author preflight.** Claude Code implemented this change and ran this
check, so it is not an independent or fresh-context review. GPT/Codex review
is pending (BUILD_PLAN.md Task 34.6).

## Review inputs

- **Diff.** Branch `feat/outcome-reason-codes`. The preflight ran on the
  working-tree diff against `5a73539`. The branch was then rebased onto
  `main` at `1efe0c3` (PR #75) and the checks were re-run there; see
  "Rebase onto PR #75" below. Record the final head SHA from the PR.
- **Decision.** `adr/0014-outcome-states-and-reason-codes.md`. Pete chose,
  on 26 September 2026: a headline plus reason code; the r 15 source check
  first; landing before the v0.1.0 tag.
- **Specification.**
  - `policy_specs/working_for_families/specification.md`, the outcome
    paragraph under "Approved Task 10 scoped calculation contract": "A
    genuine, evidenced failure of an eligibility test may yield zero for
    that component". An amendment note follows it.
  - `policy_specs/accommodation_supplement/specification.md`, the r 15 item
    and row AS-06: "exceptional asset-limit increases require separate
    facts".
- **Primary sources.** No new source was consulted. No rule, rate, threshold
  or value changed.
- **Commands** (worktree `/private/tmp/poltika-outcome-reason-codes`):

| Command | Result |
| --- | --- |
| `uv run --extra dev ruff check src tests` | All checks passed |
| `uv run --extra dev mypy --strict src` | no issues in 29 source files |
| `uv run --extra dev pytest -q` | 432 passed, 10 skipped, 2 deselected. The 10 skips are the PostgreSQL tests; the server binaries are not installed locally. |
| `uv run --extra dev pytest -q -m installed_artifact` | 1 passed |
| `-m code_replay`, and the PostgreSQL store and scenario route tests | **not run locally.** CI runs them. |
| `git diff --check` | clean |

## Author preflight

I authored the change and knew its rationale before writing this section.

### Expected behaviour (checklist)

- A missing or unverified fact is never `calculated` or `ineligible`. It is
  `needs_review` with `missing_input`, and `missing` names the request
  fields.
- `ineligible` appears only where the approved WFF specification supports an
  evidenced zero: Best Start when every child is verified outside
  entitlement. A formula zero (full abatement) stays `calculated`.
- The r 15 ceiling is not `ineligible`. It is `unsupported` with
  `unresolved_rule`, pending AS-06.
- No headline outcome or value changes except those Best Start relabels.
- In-work tax credit inherits family tax credit's blocker (MD 2(2)(c)).
- A combined-run disagreement is `conflicting_evidence`. It flags an
  `ineligible` result too; only `unsupported` is kept.
- Every blocked result has a resolution. A result without a code, or with
  inconsistent fields, cannot be constructed.

### Probes

| Probe | Result |
| --- | --- |
| Best Start: one child outside entitlement, one unknown | `needs_review`, `missing_input`, `children[].best_start_cohort` |
| One child outside entitlement, one other-cohort | `unsupported`, `outside_scope` |
| All outside entitlement, shared care unknown | `needs_review`, `missing_input` (the gate order is unchanged) |
| All outside entitlement, MC 6(a) excluded | `unsupported`, `outside_scope` |
| One child outside entitlement, one in the supported cohort | `calculated` 4041.00 |
| No children | all four `unsupported` / `outside_scope`; never `ineligible` |
| `/wff/calculate`, no cohort child | `{"outcome": "ineligible", "value": "0", "reason_code": null, "missing": [], "resolution": null}` |
| `/wff/calculate`, partnered, claimant 55000, no partner amount | family tax credit `needs_review`, `missing_input`, `["family_scheme_income.partner_amount"]`, with a resolution |
| Stored runs | `store.get_run` returns plain JSON and never rebuilds `ComponentResult`, so fetching an older run cannot fail validation |

**Golden fixture diff**, checked by script against the pre-change file:

- Scenario identities are unchanged.
- Three bound hashes changed: the WFF `policy.yaml`, the WFF
  `specification.md` and the AS `specification.md`.
- The result changes are the three new fields plus 10 relabels: g1, g2,
  g7, g8 and g9, `best_start` in both the final and the original WFF
  result, each `calculated` to `ineligible` with the same value "0".
- Nothing else changed.

**Relabelled protected expectations** (value unchanged in every case,
Best Start `calculated` "0" to `ineligible` "0"):

- **WFF `spec_cases.yaml`:** `single_ordinary_low_income`,
  `single_two_children_no_abatement`,
  `single_four_children_base_beyond_three`,
  `single_high_income_ftc_floors_to_zero`,
  `partnered_combined_income_drives_abatement`,
  `partnered_missing_partner_income_is_needs_review`,
  `mftc_zero_at_prescribed_amount`,
  `me2_employment_exclusion_unsupported_only_mftc`,
  `md14_15_protected_credit_excludes_ftc_and_iwtc_not_mftc_or_best_start`,
  `mc6b_disqualifying_payment_excludes_iwtc_mftc_not_ftc_or_best_start`,
  `in_work_eligibility_excluded_is_unsupported_not_needs_review` and
  `half_cent_precision_exact_decimal_result`.
- **`golden_households.yaml`:** g1, g2, g7, g8 and g9.
- **Interaction `spec_cases.yaml`:**
  `non_beneficiary_sole_parent_receives_both_with_no_income_leak`.

The statutory-value guard flags these files and the WFF `policy.yaml`.

### Findings (proposed classifications)

None of these is a confirmed code or test error.

| # | Finding | Proposed classification | Notes |
| --- | --- | --- | --- |
| P1 | Headline and code are not partitioned. `unsupported_period` and `unresolved_rule` appear under both `needs_review` and `unsupported`. | ARCHITECTURE_ISSUE (flag) | **Ruled:** kept and tightened. `unresolved_rule` is now `needs_review` only; `unsupported_period` stays under both (ADR-0014, Rulings). |
| P2 | The WFF `policy.yaml` `outcome_states` gains `ineligible` with no `policy_version` bump. | ARCHITECTURE_ISSUE (flag) | **Ruled:** WFF stays 0.1.0 (label only). AS moves to 0.1.2, because DEC-004/005 change its inputs and outcomes (ADR-0014, Rulings). |
| P3 | PR #75 (merged) added an `unsupported` result for verified $0 accommodation costs (s 65AAA) with no reason code. | INTERPRETATION_AMBIGUITY | **Decided:** `ineligible` $0 (DEC-005, s 65(1)(a)), by Claude Code at Pete's request. |
| P4 | The Task 35.3 demo was not regenerated. | (pending step) | It needs PostgreSQL and a clean commit after merge. The demo README carries a dated note. |
| P5 | The provenance `REPORT_FORMAT` stays `poltika-provenance/0.1`, although components gained fields. | ARCHITECTURE_ISSUE (flag) | **Ruled:** stays 0.1, since v0.1.0 is the format's first release (ADR-0014, Rulings). |

### Rebase onto PR #75

- `wff.py`: kept #75's MFTC reason text, using the `outside_scope`
  constructor.
- `accommodation_supplement.py`: kept #75's r 15 `>` comparison and reason
  text, with this branch's `unresolved_rule` code. Added a code and
  resolution to #75's $0-cost result (P3).
- The AS specification's step 1 notes the $0-cost code.
- The golden fixture was regenerated and checked again against `main`'s
  fixture. Commands and results are recorded in the PR description.

**Not verified:** the PostgreSQL tests and code replay (CI only), and any
legal content of AS-06's exceptional asset-limit increase (no source
consulted; open for GPT/Codex).

## Follow-up, 26 September 2026: decisions and rulings

Pete asked Claude Code to settle the open items ("fix these now"). The
decisions below were made by Claude Code at Pete's request. They are **not**
the GPT/Codex review, which remains pending.

**Sources checked on 26 September 2026.** Legislation was retrieved with the
recorded browser user-agent method, at the version as at 4 September 2026.
The MSD pages carry no version date.

| Source | Locator | Supports |
| --- | --- | --- |
| Social Security Act 2018 (`as-social-security-act`) | ss 65(1), 65AAA, 69(1)-(5) | DEC-004, DEC-005 |
| Social Security Regulations 2018 (`as-social-security-regulations`) | r 15(1)-(6), r 16, Schedule 8 Part 1 | DEC-004 |
| MSD Map `as-msd-assets` | "There are two exceptions" | DEC-004 |
| MSD Map `as-msd-lump-sum-impairment`, `as-msd-lump-sum-independence-allowance` (new catalogue entries) | "the cash asset limit is increased by the amount of the lump sum payment for 12 months" | DEC-004 |
| Income Tax Act 2007 (`wff-income-tax-act`) | ME 1(1)-(3) | WFF DEC-001 |

**Outcomes:**
- **DEC-004:** r 15 is `ineligible` $0 when `specified_lump_sum_status` is
  verified, `unsupported` when excluded, and `needs_review` when unknown.
  This adds a new AS input and moves AS to policy 0.1.2.
- **DEC-005:** $0 accommodation costs are `ineligible` $0.
- **WFF DEC-001:** MFTC stays `unsupported`. ME 1 pro-rates the credit by
  week, so it is not a $0.
- **P1, P2 and P5:** ruled; see the findings table and ADR-0014.

**Protected-file changes in this follow-up:**
- **AS `spec_cases.yaml`:** `asset_ceiling_exceeded_is_unsupported` is
  replaced by three cases (lump sum verified, excluded and unknown), and
  `zero_accommodation_costs_is_ineligible` is added.
- **AS `policy.yaml`:** version 0.1.2, the new input, and `ineligible` in
  `outcome_states`.
- **Interaction and golden YAML:** header comments only.

The golden fixture was regenerated and checked by script against `main`:
- **Results:** 10 Best Start relabels and nothing else.
- **Scenario ids:** all 9 changed (new input, new version).
- **Bound hashes:** 8 changed, the edited policy files and the three new
  DEC files.

## Deferred Codex audit

- Review the committed head of `feat/outcome-reason-codes` against
  `1efe0c3`. Check the contract in `src/poltika/engines/simulator/wff.py`
  (`ComponentResult.__post_init__`, `unresolved_parameter`) and each
  construction site's reason code.
- Re-derive the relabelled and new protected expectations independently:
  the 18 Best Start relabels, and the four new AS cases.
- Independently check DEC-004, DEC-005 and WFF DEC-001 against the sources
  above. In particular, check DEC-004's handling of how MSD's "limit is
  increased" reads against s 69(3)'s narrower text.
- Confirm or overturn the P1, P2 and P5 rulings.
