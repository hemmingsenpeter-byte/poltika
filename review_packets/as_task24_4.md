# Review Packet: Accommodation Supplement — Task 24.4 — 23 September 2026

Independent adversarial review (fresh-context, no implementer explanation
read first) of the complete Accommodation Supplement vertical slice, per
`BUILD_PLAN.md` Task 24.4. Covers the merged calculator + all three test
classes on `main`, plus open PR #29 (`run_as_module()` / `test_as_module.py`),
reviewed here as its independent-review pass.

## Review inputs

- Working directory: `/tmp/poltika-task24-4-review`, checked out at `main`
  commit `8f28a1b9` (2026-09-23).
- PR #29 diff (unmerged, reviewed in this pass): `/tmp/poltika-task24-4-review/PR29_DIFF.txt`.
- Primary sources: `policy_specs/accommodation_supplement/sources.yaml`;
  Social Security Act 2018 ss 65AAA-69, 423, Schedule 4 Part 7 cl 1-8;
  Social Security Regulations 2018 rr 15-19 (statutory text re-checked
  directly by the specification's own Task 22/24.1 author sessions, not
  independently re-fetched by this reviewer — see "Not independently
  verified" below).
- Specification/policy paths: `policy_specs/accommodation_supplement/specification.md`,
  `policy.yaml`, `spec_cases.yaml`, `benchmarks.yaml`,
  `decisions/DEC-001-income-excess-rounding.md`.
- Code: `src/poltika/engines/simulator/accommodation_supplement.py`
  (+ PR #29's addition of `run_as_module()`).
- Tests: `tests/unit/engines/simulator/test_accommodation_supplement.py`,
  `test_as_spec_cases.py`, `test_as_benchmarks.py`,
  `tests/regression/test_as_known_historical_issues.py`,
  PR #29's `tests/unit/engines/simulator/test_as_module.py`.

### Test command and output

Against `main` (8f28a1b9, PR #29 NOT applied):

```
$ uv run pytest -q
195 passed, 1 deselected in 33.14s
$ uv run ruff check src tests
All checks passed!
$ uv run mypy --strict src
Success: no issues found in 15 source files
```

Against `main` + PR #29 diff applied (separate scratch copy, `/tmp/poltika-pr29-check`,
same commit, dependencies freshly synced):

```
$ uv run pytest -q
201 passed, 1 deselected in 9.63s
$ uv run ruff check src tests
All checks passed!
$ uv run mypy --strict src
Success: no issues found in 15 source files
```

All commands actually executed (not asserted); PR #29's 6 new tests
(`test_as_module.py`) pass and no existing test regresses.

## Independent review

### Independently derived expected behaviour (from sources alone, before opening implementation)

1. **Supported inputs:** household eligibility bundle (s 66/s 67 incl.
   disability/care and Student Allowance branches/s 69), claimant category
   (Jobseeker/Sole Parent/Supported Living/non-beneficiary only — pension
   and mixed-benefit unsupported), tenure (rent/board only — homeowner
   unsupported), partner status (single/ordinary couple only — joint
   tenancy/community spouse unsupported), dependent children count,
   verified Area 1-4, weekly accommodation costs (plain-case only — no
   boarder/business-use income), cash assets, exempt-cash-asset status,
   weekly income (non-beneficiary route only).
2. **Unsupported triggers:** the twelve items specification.md's "Unsupported"
   list names, each tied to a specific statutory provision (ss 66, 67(b),
   67(d), 68, cl 6A, s 67(e)/Sched 5, mixed-benefit table, s 69, cl 4-6,
   unverified area, r 16/Sched 8, cl 7 b/c/d/f), plus the r 15 asset ceiling
   itself as a distinct, evidenced exclusion (not a scope narrowing).
3. **Calculation order:** (1) household/asset/area gate: unsupported before
   needs_review; (2) plain-case qualifying costs; (3) entry threshold = 25%
   × claimant-category base rate; (4) 70% of positive excess, capped by
   household category (cl 1/2/3) × Area 1-4; (5) non-beneficiary-only: add
   s 423(3) imputed income (floor complete $100 steps over the threshold),
   subtract 25% of the **unrounded** excess over the r 18(3) income level
   (DEC-001), floor the result at zero; (6) round the final positive amount
   **up** to the whole dollar (r 19) — the only rounding step.
4. **Two flagged judgment calls that must stay flagged, not silently
   promoted or contradicted:**
   (a) a single claimant with 1+ dependent children is read as "sole
   parent" for cl 1/2 purposes, since the v0.1 input contract has no
   separate "sole parent" fact;
   (b) `exempt_cash_asset_status == UNKNOWN` resolves to `unsupported`
   (not `needs_review`), because this branch does not attempt exemption
   determination at all, unlike every other unverified-fact check in the
   file.

### Discrepancies found

| # | Discrepancy | Classification | Notes |
|---|---|---|---|
| 1 | Fabricated/uncited statutory citation "s 65(1)(b)" for the assets-ceiling exclusion, in both runtime output and a test | MISSING_SOURCE (also a CODE_ERROR in the user-facing reason text) | `accommodation_supplement.py` lines 394 and 405 and `test_accommodation_supplement.py` line 278 all cite "s 65(1)(b)" as the source for the r 15 cash-asset ceiling exclusion. That citation string appears **nowhere** in `sources.yaml`, `specification.md`, or `policy.yaml` — every other reference to this same rule (policy.yaml's own comment above the `asset_ceiling_*` parameters, specification.md's calculation sequence step 1, and the `AS-06`/`AS-07` rule table) cites **r 15**, not any Act section 65. Reproduction: `grep -rn "65(1)" .` in the repo finds exactly these three lines and no supporting source entry. This is a `ComponentResult.reason` string an auditor/caseworker could read as an authoritative citation, and CLAUDE.md's "Ground truth" rule bars any statutory citation not derived from a cited primary source recorded in this project. The correct citation (per every other place this exact check is documented) is `r 15`, not `s 65(1)(b)`. Does not affect any numeric outcome — the check itself (cash_assets >= ceiling → unsupported) is correct; only the citation text is wrong. |
| 2 | Asset-ceiling `unsupported` exclusion is not part of `_household_gate_failure()`, so it cannot pre-empt an unrelated `needs_review` trigger the way every other unsupported condition can | CODE_ERROR | `_household_gate_failure()`'s docstring claims "`unsupported`... takes precedence over `needs_review`... matching `wff.py`'s `_household_gate_failure()` precedence discipline exactly" — but the asset-ceiling check is a separate `if` block in `calculate_accommodation_supplement()`, reached only *after* the gate function has already returned `None`. Reproduction (executed): `AsScenario(household_eligibility=FactStatus.UNKNOWN, claimant_category=JOBSEEKER_SUPPORT, tenure_type=RENT_CONTRIBUTIONS_OR_BOARD, partner_status=SINGLE, statistical_area_unit=AREA_1, weekly_accommodation_costs=200, dependent_children_count=0, cash_assets=8100, exempt_cash_asset_status=VERIFIED)` against the real approved parameters returns `needs_review` ("household_eligibility_facts ... unverified"), never reaching the fact that `cash_assets` (8100) is at the r 15 ceiling. specification.md step 1 explicitly lists the asset ceiling as part of the same household-gate step ("cash assets below the r 15 ceiling ... Any unverified or excluded condition returns unsupported/needs_review for the whole calculation, before any component-specific step"), and the file's own review-question framing (task prompt's question 2) is exactly this precedence rule. Both outcomes here are safe (neither is a silent zero), so this is not a numeric-safety bug, but the code's own precedence-discipline claim is false for this one trigger, and no existing test (spec case, benchmark, or regression) exercises the combination that exposes it. |
| 3 | `policy.yaml`'s `assessment.unsupported` list and its `components[0].validation_checks` list disagree by one item | SPEC_ERROR | `assessment.unsupported` (policy.yaml lines 24-36) lists 12 items and omits `asset_ceiling_exceeded`; `components[0].validation_checks` (lines 254-267) lists all 12 plus `asset_ceiling_exceeded` (13 items). specification.md's own prose "Unsupported" list (lines 207-245) explicitly includes the asset ceiling as a required trigger, so the component-level list is the one that matches the accepted contract and the code; the assessment-level list is the one that's incomplete. This is metadata/documentation drift inside a single approved file, not a calculation-affecting bug (the calculator does not read either list at runtime), but it is a genuine internal inconsistency in the one file that is supposed to be the machine-readable source of truth for the domain boundary. |
| 4 | `decisions/README.md` says "No interpretation decisions are recorded yet" while `DEC-001-income-excess-rounding.md` already exists in the same directory | SPEC_ERROR (cosmetic) | Stale boilerplate left over from before DEC-001 was added. No functional effect — DEC-001 itself is complete, dated, owned, and correctly reflected in specification.md and policy.yaml — but the directory's own index contradicts its contents, which is exactly the kind of drift `doctrine/review-doctrine.md`'s "required evidence" discipline is meant to keep from happening silently. |

### The two flagged judgment calls — checked, both correctly labelled

(a) **Single claimant + 1+ children = "sole parent"**: still an explicit,
un-promoted "self-review flag" comment in `_household_category()`
(`accommodation_supplement.py` lines 231-240), not asserted as settled fact
in specification.md or policy.yaml (policy.yaml's `dependent_children_count`
input note states the resulting household-category mapping as a fact but
does not claim a "sole parent" determination is itself verified — it
inherits the same reading the code flags). No test assumes a different
reading. Not contradicted, not silently promoted. Correctly flagged.

(b) **`exempt_cash_asset_status == UNKNOWN` → `unsupported`**: consistently
implemented (line 317 gate check), consistently documented (specification.md's
"Unsupported" list, policy.yaml's `exempt_cash_asset_unverified` item, and an
inline self-review-flag comment distinguishing it from every other
UNKNOWN-means-`needs_review` check in the same file), and independently
regression-tested (`test_unknown_exempt_cash_asset_status_is_unsupported_like_excluded`).
No promotion to policy.yaml/specification.md as unflagged settled fact, no
contradicting test. Correctly labelled.

### DEC-001 rounding convention — checked at every application site

The unrounded-excess convention is applied at exactly one place: the r 18(2)
income-excess step (`income_excess = total_income - income_level`, not
floored). The one other place a floor operation occurs — the s 423(3)
asset-imputation step (`complete_steps = ... ROUND_FLOOR`) — is a *different*
statutory provision ("every $100... over $X") that itself demands a
complete-unit floor, confirmed directly against s 423(3)'s text in
specification.md/sources.yaml, and is not governed by DEC-001 at all. No
other step rounds. The final r 19 round-up is the only other rounding
operation, applied once, at the end, matching r 19's own scope. Verified
against the spec-case hand-derivation (`non_beneficiary_fractional_income_excess_unrounded`,
which explicitly contrasts the unrounded $74 result against the rejected
floor-first $75) and the regression test
`test_dec001_uses_exact_fractional_income_excess_not_floor_first`; both
reproduce correctly by independent recalculation.

### `run_as_module()` (PR #29) — checked against the `run_wff_module()` pattern

`_covers()` and `_spans_reference_period()` are byte-for-byte identical in
logic (half-open `[from, to)` interval membership; "spans" requires
`value_effective_from <= reference_period.from_` and
`value_effective_to >= reference_period.to`, correct for half-open interval
containment) to `wff.py`'s versions. The three invariants — policy_id match,
modelled_date within reference_period, every *declared* parameter
rate-covered for the complete reference period, iterated generically over
`spec.parameters` rather than a hardcoded id list — are structurally
identical to `_wff_module_validation_failure()`. The one deliberate
divergence (no "is every parameter the calculator might look up actually
declared" check) is explained and justified in both the source docstring
and the test module docstring: `_param_value()` already turns an undeclared
AS parameter into `needs_review` one layer down, by design (unlike WFF's
PR #21 bug, where an undeclared parameter was always a fixture defect). I
independently re-derived the boundary tests (date exactly at
`reference_period.to`, parameter interval ending one day before it) and
confirm the implementation's half-open-interval reading agrees with
specification.md's own reference_period phrasing ("2026-03-02 to
2027-04-01"). Found no gap, no silently-skipped invariant, and no boundary
error. Ran clean (`git apply` in an isolated copy): 201/201 tests, ruff,
mypy --strict all pass with PR #29 applied.

### Benchmarks and spec cases — independently re-derived arithmetic

Recalculated all 4 numeric `spec_cases.yaml` cases and all 3 numeric
`benchmarks.yaml` cases by hand from the scoped formula in specification.md
and each case's own `parameter_assumptions`; all match the file's stated
`expected.value` (including the DEC-001-distinguishing fractional case:
$254.80 total income, $54.80 excess, $13.70 reduction, $73.975 pre-rounding,
$74 final — reproduced independently). The `AS_ALLOWED_PARAMETER_ASSUMPTIONS`
mechanism (`base_rate`, `income_level` only, asserted in
`tests/conftest.py::as_parameters_for_case`) keeps every synthetic input
labelled `source_id: test-case-assumption`, never disguised as a
`source_id: as-social-security-act`/`-regulations` entry, and the fourth
benchmark (`msd_student_partner_fractional_example_outside_scope`) is
correctly kept as `outcome_kind: scope_boundary` rather than promoted to a
numeric benchmark, matching DEC-001's own "not yet corroborated" caveat and
the Task 24.1 corroboration-search negative result recorded in both
`sources.yaml` and DEC-001 itself.

### Not independently verified (time/scope limits)

- Did not independently re-fetch legislation.govt.nz for ss 65AAA-69, 423,
  Schedule 4 Part 7, or Regulations rr 15-19 myself; relied on the
  specification's own recorded Task 22/24.1 direct-text quotations and the
  project's established browser-user-agent access method, as the task
  instructions' primary-source step directs deriving expectations from
  `sources.yaml`/`specification.md`/the spec_cases before opening code —
  it does not require a third independent re-fetch beyond the two the
  project has already recorded. The one exception is the "s 65(1)(b)"
  citation (finding #1), which I checked by confirming its absence from
  every source document already in the repo, not by fetching the Act to
  confirm what s 65(1)(b) actually says.
- Did not review `src/poltika/policy/loader.py`'s implementation in detail
  beyond confirming its `PolicyParameterSet`/`ParameterResolution` contract
  and interval-matching behaviour are consistent with what both `wff.py`
  and `accommodation_supplement.py` assume; it was in scope for WFF's
  Task 17 review, not re-reviewed line-by-line here.
- Did not review the FastAPI layer, `common/errors.py`, or any AS-adjacent
  module outside the explicitly listed files.
- Did not attempt to independently corroborate DEC-001's fractional-excess
  reading with a further external search — the task's out-of-scope note
  excludes OpenFisca/PolicyEngine, and DEC-001/sources.yaml already record
  a negative corroboration search as of Task 24.1; re-running that search
  was outside this review's remit.

## Author response

(none read prior to completing the independent section above, per
`review_packets/README.md`.)

## Resolution

Pending Pete's classification confirmation. No fix applied — per task
instructions, this review records findings only.
