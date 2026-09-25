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
| P1 | Headline and code are not partitioned. `unsupported_period` and `unresolved_rule` appear under both `needs_review` and `unsupported`. | ARCHITECTURE_ISSUE (flag) | This follows from keeping the v0.1 headlines (Pete's choice). A later release could move the module-boundary period checks to `unsupported`; that would change protected labels. |
| P2 | The WFF `policy.yaml` `outcome_states` gains `ineligible` with no `policy_version` bump. | ARCHITECTURE_ISSUE (flag) | The precedent is the Task 34.4 `policy.yaml` change without a bump. No rule or value changed. The reviewer should confirm. |
| P3 | PR #75 (merged) added an `unsupported` result for verified $0 accommodation costs (s 65AAA) with no reason code. | INTERPRETATION_AMBIGUITY | Handled on rebase: it keeps `unsupported` and gets `reason_code: unresolved_rule`, with a resolution naming the pending decision. Under ADR-0014 it may be an evidenced zero (`ineligible`). **That is Pete's call and is not decided here.** |
| P4 | The Task 35.3 demo was not regenerated. | (pending step) | It needs PostgreSQL and a clean commit after merge. The demo README carries a dated note. |
| P5 | The provenance `REPORT_FORMAT` stays `poltika-provenance/0.1`, although components gained fields. | ARCHITECTURE_ISSUE (flag) | The change is additive only, before the release. The reviewer may prefer a version bump. |

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

## Deferred Codex audit

- Review the committed head of `feat/outcome-reason-codes` against `1efe0c3`.
  Check the contract in `src/poltika/engines/simulator/wff.py`
  (`ComponentResult.__post_init__`, `unresolved_parameter`) and each
  construction site's reason code.
- Re-derive the 18 relabelled protected expectations independently: is each
  an evidenced zero rather than a formula zero?
- Rule on P1, P2 and P5, and on P3 with Pete.
- Source research: AS-06's exceptional asset-limit increase, then a DEC for
  r 15.
