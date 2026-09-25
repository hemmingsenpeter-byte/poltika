# Task 34.3: fresh-context adversarial review (Claude reviewer)

> **Disposition (Task 34.4), 25 September 2026.** Pete accepted the
> proposed classifications and fix routing ("fix, accept and proceed"),
> including the protected-value changes for F1. F1, F2, F3 and F7 are fixed
> in the PR that adds this record; F4-F6 and F8-F10 follow in a second PR;
> F5's matrix wording is corrected there. F11: the GPT/Codex half of 34.3
> should re-derive the 28.3, 28.5 and 29.2 slices (at least the beneficiary
> and couple households) before `v0.1.0`.

- **Scope:** the slices assigned to GPT/Codex: 26a, 26b, 28.1, 28.3 (with
  DEC-003) and 29.2. Also the end-to-end workflow and shared contracts:
  request, both modules, `scenarios/combined.py`, `record.py`, `store.py`,
  `api/` and `engines/assurance/provenance.py`.
- **Checkout:** `/private/tmp/poltika-343` at `1c69613` (main). It was read
  only. Nothing was edited, committed or posted.
- **Test run:** `uv run --extra dev pytest -q -p no:cacheprovider` gave
  372 passed, 9 skipped and 1 deselected. The 9 skips are all the
  PostgreSQL store and scenario-route tests, because no server binaries are
  installed here.
- **Reviewer:** Claude, in fresh context, as the Task 34.3 stand-in reviewer
  for the Codex-assigned slices.
- **Authorship.** BUILD_PLAN records that Claude Code actually authored
  every one of these slices under Pete's delegation. This review therefore
  comes from the same model family as the author. It is not the cross-model
  check the plan intended (see F11).

Classifications use the frozen Review Doctrine taxonomy (BUILD_PLAN.md
"Review Doctrine"): CODE_ERROR, TEST_ERROR, SPEC_ERROR, SOURCE_CONFLICT,
INTERPRETATION_AMBIGUITY, MISSING_SOURCE, ARCHITECTURE_ISSUE and
REVIEWER_ERROR. All classifications are proposed. Pete confirms them in
34.4.

---

## Findings

### F1 (P1): beneficiary golden households assert that protected FTC and protected Best Start do not apply, which contradicts MD 14 and MG 4

- **Proposed classification:** TEST_ERROR, for the protected fixture facts
  and expected outcomes. There is a linked REVIEWER_ERROR: the 29.4 review
  and the 28.5 review both missed it.
- **Location:**
  - `policy_specs/wff_as_interaction/golden_households.yaml`: lines 45 and
    50 (the `&wff_single_earner` anchor, inherited by
    `g5_supported_living_couple_two_children` at line 171 and
    `g6_sole_parent_support_best_start_child` at line 202).
  - `policy_specs/wff_as_interaction/spec_cases.yaml`: line 39 (the
    `&wff_sole_parent` anchor), used by `sole_parent_support_beneficiary_consistent`
    at line 69.
  - The frozen snapshot `tests/fixtures/golden_results_v0_1.json`: g5 at
    line 318 and g6 at line 397.

**Statutory text.** I read it directly from the official Income Tax Act
2007 Part M, latest version, fetched with the recorded browser user agent;
the URL is `wff-income-tax-act`.

- MD 14(1): a person receives protected family tax credit for a calendar
  month if, in that month, they
  - (a) have no partner, receive a main benefit, and derive family scheme
    income below the MD 13(3)(a)(i) amount ($44,900); or
  - (b) have a partner, receive a main benefit, and derive combined family
    scheme income below $44,900.
- MG 4(1) is the same test for protected Best Start, measured against the
  MG 3(2)(a) amount ($79,000).
- MD 14(2) and MG 4(2) annualise the income under MB 2.

**Approved WFF contract.** `working_for_families/specification.md` steps 2
and 5 say:

- "An established MD 14/15 protected month is `unsupported` for this
  component."
- "An established MG 4 protected month is `unsupported` for this
  component."

**Task 28.1 research.** `docs/research/task_28_1_wff_as_interactions.md`,
under "Main-benefit facts constrain WFF component branches", says:

> "a beneficiary example cannot be made into an ordinary calculated FTC
> demo simply by declaring protected-credit applicability absent. This is a
> fixture-design constraint for Task 29".

**What the fixtures do.**

- **g6:** the AS claimant receives Sole Parent Support in the week
  [2026-06-01, 2026-06-08). WFF is single, with family scheme income of
  $28,000, below both $44,900 and $79,000. On these facts, MD 14(1)(a) and
  MG 4(1)(a) apply for June, unless June's annualised income is at least
  $44,900, which nothing suggests. The fixture nevertheless asserts
  `ftc_iwtc_protected_or_direct_abatement: verified` (verified *not* to
  apply) and `best_start_protected_credit: verified`. It then expects FTC
  `calculated 7921` and Best Start `calculated 4041`.
- **28.5 case `sole_parent_support_beneficiary_consistent`:** the same
  pattern. It is Sole Parent Support with income of $30,000, and expects
  FTC `calculated 7921`. It is described as "consistently described".
- **g5:** a Supported Living Payment couple with combined income of
  $40,000, below $44,900. MD 14(1)(b) applies if the WFF person is the
  benefit recipient. The AS claimant may be the partner, so for g5 this is
  a conservative contradiction rather than a certain one.

**Reproduction.** I ran the combined runner exactly as the golden test
does:

```
g6 as-is:              contradictions=()  FTC calculated 7921   Best Start calculated 4041
g6 MD14/MG4 = excluded: contradictions=()  FTC unsupported       Best Start unsupported
                        ("MD 14/15 protected family-tax-credit case applies -- needs its own specification ...")
g5 as-is:              contradictions=()  FTC calculated 14375
g5 MD14/MG4 = excluded: FTC unsupported
```

**Effect.** The dollar amounts might coincide with the true entitlement,
because abatement is zero below the thresholds. That is not something
this project may assume: the approved contract routes these months to
`unsupported` precisely because the monthly protected-credit pathway is
unspecified. These households are protected statutory expected values.
Task 35.1's demo question could well be chosen from them, and the golden
suite is cited as D2 evidence in the traceability matrix.

**Suggested fix.** This routes to the fixture author; Pete confirms.

- Set `ftc_iwtc_protected_or_direct_abatement: excluded` and
  `best_start_protected_credit: excluded` for g6 and for the Sole Parent
  Support spec case.
- Change their FTC and Best Start expectations to `unsupported`, and
  either do the same for g5 or document why g5's benefit is the partner's.
- Alternatively, replace them with beneficiary households whose income is
  at or above the thresholds, if such a household is coherent.
- Refreeze `golden_results_v0_1.json`, attributing the change to "fixture
  facts corrected (MD 14/MG 4)".
- Because this changes protected paths, it goes through the
  statutory-value guard process.
- If Pete wants beneficiary FTC to be calculable, that is a new
  INTERPRETATION_AMBIGUITY or specification task for the MD 13(3)(b)
  protected-month pathway. It is not a fixture edit.

### F2 (P2): the 28.3 contract and the runner have no shared-fact gate for MD 14 or MG 4

- **Proposed classification:** SPEC_ERROR, because the contract drops a
  28.1 research finding. The runner omission follows from it as a
  CODE_ERROR.
- **Location:**
  - `policy_specs/accommodation_supplement/specification.md:493-513` (the
    shared-fact table).
  - `policy_specs/working_for_families/specification.md:344-362`.
  - `src/poltika/scenarios/combined.py:123-134`.

**The gap.** The 28.1 research listed MD 14-15 and MG 4 as main-benefit
constraints next to MC 6(b) and MD 8. The contract turned only in-work
eligibility and MC 6(b) into gates. As a result, the following combination
passes with zero contradictions (reproduced in F1):

- AS asserts a main benefit in the week;
- WFF asserts `ftc_iwtc_protected_or_direct_abatement` or
  `best_start_protected_credit` as `verified` (meaning it does not apply);
- WFF family scheme income is below $44,900 or $79,000.

For a single household this contradiction is as certain as the MC 6(b)
one the contract already accepts, subject only to the MB 2 annualisation
of that month's income.

**Suggested fix.** Add a conservative row to the contract. If AS has a
main-benefit category and WFF asserts either protected-credit fact
`verified`, flag it when WFF's verified family scheme income is below the
relevant threshold, or unconditionally as a conservative gate. Implement
it in `shared_fact_contradictions()` with a regression test named for the
leak. Pete accepts the contract change.

### F3 (P2): the 70% subsidy rate is hard-coded, not a sourced and effective-dated parameter, while an unused 25% fraction stays approved

- **Proposed classification:** SPEC_ERROR together with CODE_ERROR. This is
  a provenance gap.
- **Location:**
  - `src/poltika/engines/simulator/accommodation_supplement.py:642`, which
    reads `min(Decimal("0.7") * excess, area_cap)`.
  - `policy_specs/accommodation_supplement/policy.yaml:213`, which declares
    `entry_threshold_rent_board_fraction`.

**The 70% rate.** Schedule 4 Part 7 cl 1-3 set 70%. I re-read it from the
latest consolidation and it is correct. But it is the only statutory rate
in either calculator that is a literal: a `grep` for `Decimal("…")` in
`engines/simulator/` finds only this one. It has:

- no `source_id`;
- no effective interval;
- no entry in the provenance trace's `parameters`;
- no mention in `_AS_CALCULATION_RULES`.

So a `calculated` AS value's provenance report never names the rate that
dominates it. That falls short of Task 31.5's "every calculated value
traces to a source". A future change to the subsidy percentage would also
bypass effective dating and the statutory-value guard.

**The unused 25% fraction.** Since DEC-002 took effect,
`entry_threshold_rent_board_fraction` (0.25) is declared, approved and
checked for week coverage by `_as_module_validation_failure`, but no code
consumes it. Tests assert that it is *not* in the trace. That invites
exactly the misuse DEC-002 forbids.

**Suggested fix.**

- Add a parameter such as `rent_board_subsidy_rate` (fraction 0.7,
  `as-social-security-act`, "Schedule 4 Part 7 cl 1-3", approved) and read
  it through `_param_value`. The trace then records it, and the AS rule
  list gains a "70% of positive excess, capped" rule.
- Either remove the 25% fraction or annotate it as retained but unused
  under DEC-002.
- Both changes go through the statutory-value process.

### F4 (P2): code identity comes from the ambient git state, not from the code that is running, so provenance can describe a different run

- **Proposed classification:** ARCHITECTURE_ISSUE together with
  CODE_ERROR.
- **Location:**
  - `src/poltika/scenarios/record.py:182-201` (`detect_code_identity`).
  - `src/poltika/api/household.py:46` (`_CODE_ROOT = parents[3]`) and
    line 94.
  - `src/poltika/scenarios/store.py:209` (`code=_code(stored.manifest)` in
    `replay`).

**Three ways the recorded code identity can be wrong:**

1. **Stale server.** `detect_code_identity()` runs on every request and
   returns whatever `git rev-parse HEAD` and `git status` say *now*. A
   long-running API process started at commit A keeps executing A's code
   after someone checks out commit B. From then on, runs record commit B
   as `source_tree_clean=True` and `reproducible=True`.
2. **Wheel installed inside the repository.**
   - From an installed wheel, `_CODE_ROOT` is `…/lib/python3.x`. If the
     virtual environment sits inside a git checkout (`uv`'s default
     `.venv`, which is gitignored), git walks up and reports the
     checkout's HEAD.
   - Reproduced: `detect_code_identity(Path('/private/tmp/poltika-343/.venv/lib/python3.12'))`
     returns `source_commit='1c69613…', source_tree_clean=True`.
   - Now point `POLTIKA_POLICY_SPECS_DIR` at that checkout, as the
     installed-artifact test does, and `policy_files_committed` also
     becomes True. The run then claims `reproducible=True` for wheel code
     that was never verified against that commit.
   - The installed probe avoids this only because its virtual environment
     is in `tmp_path`.
3. **Replay.** `ScenarioStore.replay()` passes the *stored* code identity
   into `run_scenario()`. The rerun therefore labels itself with the
   original commit whatever code is executing. It returns
   `reproduced=True` when outputs match, even under different code, and
   never reports that the code differed.

**Suggested fix.**

- Capture the code identity once, at import or at build time. For
  example, embed the commit in the wheel's metadata at build time, or hash
  the imported `poltika` package files.
- At request time, compare that captured identity with the checkout.
  Treat any mismatch, or any installed wheel, as non-reproducible.
- In `replay`, compute the current code identity, compare it with the
  stored one, and return `code_matches` alongside `reproduced`. Never
  relabel the rerun with the stored identity.

### F5 (P2): Task 32.4's code-change replay is not implemented, yet the traceability matrix records D6 and E2 as evidenced

- **Proposed classification:** TEST_ERROR (missing evidence) together with
  ARCHITECTURE_ISSUE.
- **Location:**
  - `BUILD_PLAN.md:1870-1881` (32.4), which says "Code-change replay runs
    as an opt-in test, like `installed_artifact`, and is exercised at
    least once in 34.2".
  - `review_packets/v0_1_traceability_matrix.md`, rows D6 (line 22) and E2
    (line 34).

**What is and is not implemented.**

- No test builds the retained revision. Searching `tests/` for
  `source_commit`, "retained revision" or "code change" finds only
  identity-unit tests.
- The 34.2 probe replays against the *same* installed code, and it asserts
  that installed runs are *never* reproducible. So the only end-to-end
  path through the deployed artifact cannot produce a reproducible run.
- Commit `4361a4e` says "Code replay uses the manifest's git commit and is
  exercised separately (Task 34.2)", but 34.2 (`f903b9e`) does not do it.
- The matrix does not list this as a gap. By 34.1's own rule, "any
  unevidenced bullet is a blocking gap".

**Suggested fix.** Either:

- add the opt-in test: check out the stored commit into a worktree, build
  it, replay, and compare; or
- record Pete's decision to defer it, and mark D6 and E2 "Evidenced with
  limitation".

### F6 (P3): stale or contradictory text left behind by 26a, 28.3 and DEC-003

- **Proposed classification:** SPEC_ERROR, cosmetic; one item is a
  CODE_ERROR in reason text.
- **Locations and problems:**
  - **`accommodation_supplement/policy.yaml`:**
    - lines 1-8 still say "why `parameters` below is deliberately empty";
    - lines 132-141 still say "Deliberately NOT included yet: the
      published rent/board entry thresholds…" directly above the 17
      populated values.
  - **`accommodation_supplement/specification.md`:**
    - step 3 (around lines 268-282) still describes
      `as_base_rate_<claimant>_<household>` with
      `review_status: needs_review`. The 26a section says it "replaces"
      step 3, but the approved sequence text was never updated.
    - The AS-10 row (line 42) still says "The MSD-paid WFF route is not
      established".
    - Lines 182-194 say it "remains open". DEC-003 resolved it.
  - **DEC-002 and DEC-003 `Status`:**
    - DEC-002 still says "Not yet an executable policy" and "independent
      contract review and implementation acceptance remain required".
    - DEC-003 has the same kind of wording.
    - Both are now executed under AS 0.1.1.
  - **`accommodation_supplement.py:228-246`:** the reason reads "pending
    independent recalculation of its dated source table (Task 24)", and
    the docstring says "until Task 26a.2 populates them". That is now
    wrong.
  - **`tests/unit/engines/simulator/test_accommodation_supplement.py:10-21`
    and `50-56`:** the docstrings still say the thresholds "do not exist
    in the real policy.yaml yet". 26a.3 asked for the new behaviour to be
    recorded deliberately.

**Suggested fix.** A docs-only sweep. The policy.yaml comment edits touch
a protected file, so they need a guard-visible PR.

### F7 (P3): the AS spec cases and benchmarks are still `status: pending_review`

- **Proposed classification:** SPEC_ERROR (acceptance metadata).
- **Location:**
  - `policy_specs/accommodation_supplement/spec_cases.yaml:10`.
  - `policy_specs/accommodation_supplement/benchmarks.yaml:5`.
- **The mismatch:**
  - WFF's equivalent files are `approved`, and the traceability matrix
    marks D1 "WFF + AS … benchmarked independently" as Evidenced.
  - The AS files, including the three assumption-free 26a.3 cases, were
    never moved to approved.
  - I found no acceptance record.
- **Suggested fix:** Pete either accepts them and flips the status, or D1
  records the limitation.

### F8 (P3): an omitted WFF `children` field is treated as verified "no children"; missing facts are coerced

- **Proposed classification:** CODE_ERROR.
- **Location:**
  - `src/poltika/api/wff.py:94` (`children: … = Field(default_factory=list)`).
  - `src/poltika/engines/simulator/wff.py:395`.
  - `policy_specs/working_for_families/policy.yaml:39-45`
    (`children.missing_outcome: needs_review`).
- **Omitted `children`.** POST `/wff/calculate` with no `children` returns
  `unsupported`, with the reason "no dependent child … outside WFF's
  family-scheme membership domain". That is a definite exclusion made from
  an omitted fact, when policy.yaml says the outcome should be
  `needs_review`. In `/household/calculate`, omitting WFF children while AS
  asserts 0 raises no disagreement.
- **Boolean coercion.** Pydantic's lax mode accepts
  `dependent_children_count: true` as 1. Reproduced: the request returns
  `calculated 155` under the one-child cl 2 cap.
- **Suggested fix:**
  - make `children` required, or `list | None` with None mapped to
    `needs_review`;
  - use `StrictInt` for counts.

### F9 (P3): the combined provenance report overstates what was applied and omits the combined runner's own inputs

- **Proposed classification:** CODE_ERROR (reporting).
- **Location:**
  - `src/poltika/engines/assurance/provenance.py:100-128` and `443-473`.
  - `src/poltika/scenarios/combined.py:209-211`.
- **Overstated rules and decisions.** A component that the runner replaced
  keeps its original trace. In the report, a `needs_review` component with
  no value is still shown with "Calculation rules applied" (including
  "r 19: a positive final weekly amount is rounded up") and "Decisions
  applied: DEC-002, DEC-001". Reproduced on g1 with the precondition set
  to `unknown`.
- **Missing inputs.** The report never shows the caller's assertion for
  `as_claimant_is_wff_claimant_or_partner`, nor which shared-fact checks
  were run. It shows only the contradiction strings. Task 31.1 requires
  every input used to be shown as the caller's assertion.
- **Suggested fix:**
  - label rules and decisions for replaced components as "from the
    original module result (superseded)";
  - add a `combined_inputs` section to the combined report.

### F10 (P3): identity is sensitive to child order, and a stored record is not re-verified when read

- **Proposed classification:** CODE_ERROR.
- **Location:**
  - `src/poltika/scenarios/record.py:111`.
  - `src/poltika/scenarios/store.py:170-185`.
- **Child order.** Swapping the order of two differently described
  `ChildFacts` (the calculators ignore order) produces a different
  `scenario_id` and `result_id` (`2d6f94ce…` versus `e451651e…`) for
  identical results. Task 30.3 says reordering inputs must not change the
  result, and the id is part of the reported result.
- **No check on read.** `get_run()` rebuilds the record from JSON but never
  checks that `scenario_id(record)` equals the stored key. A future drift
  in `record_from_plain` could make replay silently run a different
  scenario, for example a new dataclass field silently taking its default.
- **Suggested fix:**
  - canonicalise the child list order for identity, or document order as
    significant;
  - in `get_run()`, assert that the recomputed `scenario_id` matches the
    stored one.

### F11 (P3): the independence the plan required for 28.3, 28.5 and 29.2 was not achieved, and the review records are missing

- **Proposed classification:** REVIEWER_ERROR (process). F1 is concrete
  evidence of a shared blind spot.
- **Location:**
  - the `golden_households.yaml` header (lines 9-15);
  - BUILD_PLAN 28 and 29 status records;
  - `review_packets/`, which has no packet for 28.3, 28.5 or 29.4.
- **Independence.** 29.2 requires hand calculations "independent of the
  28.4/29.3 implementer". Claude Code implemented 28.4 and 29.3 and also
  wrote the 29.2 expected values. The only checks were same-family
  fresh-context subagents, and this 34.3 review is the same again.
- **Missing records.** The review doctrine requires recorded evidence,
  rationale, owner and date. The 28.3, 28.5 and 29.4 reviews are
  summarised only in BUILD_PLAN prose.
- **Suggested fix:**
  - add review packets for them;
  - have GPT/Codex re-derive at least the beneficiary and couple
    households before `v0.1.0`.

---

## Independent recalculation of the 29.2 golden households

I recomputed all nine households by hand from `policy.yaml` values and the
two specifications' calculation sequences. The AS amounts are rounded up
only at the final step, per r 19. The WFF abatement applies to complete
dollars of excess, per MD 13(3)(a).

- **g1:**
  - **WFF:**
    - FTC = 7921 + 6454 = 14375. Income 35000 ≤ 44900, so there is no
      abatement.
    - MFTC = 36604 − 35000 = 1604.
    - Best Start = 0 (child outside entitlement).
  - **AS:**
    - Threshold $168 (non-beneficiary sole parent). 0.7 × (450 − 168) =
      0.7 × 282 = 197.40.
    - Cap: cl 1 (sole parent with 2 children), Area 2 = 220, so it does
      not bind.
    - Assets 3000 < 5400, so imputed income is 0. Income 673 < 906, so
      there is no reduction.
    - ⌈197.40⌉ = **198**. ✓
- **g2:**
  - **WFF:**
    - 50000 + 20000 = 70000. Excess 25100 × 0.275 = 6902.50.
    - FTC = 14375 − 6902.50 = **7472.50**.
    - MFTC = max(0, 36604 − 70000) = 0.
  - **AS:**
    - Threshold $205. 0.7 × 395 = 276.50. Cap cl 1, Area 1 = 305.
    - Income excess 1346 − 1117 = 229, and 229 × 0.25 = 57.25.
    - 276.50 − 57.25 = 219.25, so ⌈219.25⌉ = **220**. ✓
- **g3:**
  - **WFF:** no child, so every component is unsupported.
  - **AS:**
    - Threshold $158. 0.7 × 142 = 99.40. Cap cl 2, Area 3 = 105.
    - Income 1000 < 1066. Assets 5000 < 5400 (the relationship
      threshold).
    - ⌈99.40⌉ = **100**. ✓
- **g4:**
  - **WFF:** unsupported.
  - **AS:**
    - Jobseeker Support single threshold $93. 0.7 × 157 = 109.90.
    - Capped at cl 3, Area 4 = **70**.
    - Assets 500 < 8100 ceiling. ✓
- **g5:**
  - **WFF:** 40000 < 44900, so FTC = 14375.
  - **AS:**
    - Supported Living Payment couple-with-children threshold $227.
      0.7 × 273 = 191.10.
    - Cap cl 1, Area 2 = 220. ⌈191.10⌉ = **192**. ✓
  - **Caveat:** the arithmetic is correct, but the FTC *outcome* is
    challenged in F1.
- **g6:**
  - **WFF:** FTC 7921; Best Start 4041 (28000 < 79000).
  - **AS:**
    - Sole Parent Support threshold $168. 0.7 × 432 = 302.40.
    - Capped at cl 2 (sole parent with 1 child), Area 1 = **235**. ✓
  - **Caveat:** the arithmetic is correct, but the FTC and Best Start
    *outcomes* are wrong under MD 14 and MG 4 (F1).
- **g7:**
  - **WFF:**
    - 45500 − 44900 = 600, and 600 × 0.275 = 165.
    - FTC = 7921 − 165 = **7756**.
  - **AS:**
    - Threshold $168. 0.7 × 252 = 176.40. Cap cl 2, Area 1 = 235.
    - Assets 7000 − 5400 = 1600, which is 16 complete $100 steps, so
      imputed income is $16.
    - Income 895 + 16 = 911, which is 5 over 906. 5 × 0.25 = 1.25.
    - 176.40 − 1.25 = 175.15, so ⌈175.15⌉ = **176**. ✓
- **g8:**
  - **WFF:**
    - 60000 − 44900 = 15100, and 15100 × 0.275 = 4152.50.
    - FTC = 7921 − 4152.50 = **3768.50**.
  - **AS:** homeowner, so unsupported. ✓
- **g9:**
  - **WFF:** partner income is unverified, so FTC, IWTC and MFTC are
    needs_review. Best Start is a verified 0.
  - **AS:**
    - Threshold $205. 0.7 × 295 = 206.50. Cap cl 1, Area 1 = 305.
    - Income 1100 < 1117. ⌈206.50⌉ = **207**. ✓

**DEC-001 flag.** Every AS income excess is whole-dollar (229 in g2 and 5
in g7), so no household depends on DEC-001. The file's "none" flag is
correct.

**Result.** All 29.2 arithmetic reproduces. The only defect is the fact
pattern behind the FTC and Best Start outcomes in g5 and g6 (F1).

---

## Checked and found sound

- **26a values: all 17 match the live official MSD tables.** I fetched
  each table on 25 September 2026, and each is labelled "at 1 April 2026".
  - Non-beneficiary (`as-msd-rates-2026`): 93, 158, 205 and 168 (for both
    sole-parent rows).
  - Jobseeker Support (`as-msd-jobseeker-rates-2026`): 93 (for both 18+
    rows), 158, 205 and 168. The protected woman-alone row is 96 and is
    correctly left without an id.
  - Sole Parent Support: 168.
  - Supported Living Payment: 106, 180, 227 and 184. The
    non-qualified-partner with-children row is also 227, which matches the
    ordinary-row reuse.
  - Income thresholds: 693, 1066, 1117 and 906, the same in all four
    areas. The cut-out columns were correctly not used.
  - Every value's interval is `2026-04-01` to `2027-04-01`, with no March
    backfill. I confirmed that March weeks resolve to `unsupported` (no
    interval), never zero, and that a week straddling 1 April is
    `needs_review`.
- **Statutory values re-read from the official text** (latest
  consolidations, browser user agent):
  - Schedule 4 Part 7 cl 1-3 caps (305/220/160/120, 235/155/105/80 and
    165/105/80/70), the 70% rate and the 25% rent/board wording;
  - r 15 ceilings of $16,200 and $8,100;
  - s 423(3) thresholds of $5,400 and $2,700 per $100;
  - r 17 paragraphs (b), (d) and (h), which say "maximum annual rate", and
    (f), which says "annual rate … payable". This confirms that DEC-002 is
    right to leave (f) unresolved.
  - r 18(2), (2A) and (3)(a)-(c), including the household-specific income
    level;
  - Schedule 3 cl 8(1)(a) and (l), which exclude tax credits under
    subparts MA-MG and MZ with no payer qualifier. This supports DEC-003's
    inference.
- **26b:** I fetched the official 2026 No 8 whole text. Section 2(43)
  commences s 105(2) by Order in Council, and s 2(44) is the 1 April 2027
  backstop. The page states "There is no secondary legislation made under
  this section currently on this website". Section 105(1) (5,070 → 7,670)
  commences 1 April 2026 under s 2(40), and s 105(2) reverses it. Keeping
  `in_work_base` at `needs_review` for the full 2026-27 interval follows
  from WFF's Task 10.2 table, and the code gates it.
- **28.1 and DEC-003:** the CW 33, MB 13(2)(l) and Schedule 3 cl 8 chain is
  correctly bounded: identified credits only, no asset exemption, and no
  generic payer gate for beneficiaries. The Task 28.1 note correctly warned
  about MD 14 and MG 4; the gap is only that 28.3 and 29 did not carry it
  forward (F1, F2).
- **Combined runner:**
  - it keeps native periods and has no total and no income coupling;
  - the week-inside-year check is present;
  - `unknown` precondition gives `needs_review`, and `excluded` gives
    `unsupported`;
  - an existing `unsupported` survives a flag;
  - originals and traces are preserved;
  - an unverified field on either side is not compared.
- **Precedence in the AS household gate:** known exclusions pre-empt
  unrelated unverified facts, including the r 15 ceiling and the Sole
  Parent Support combinations.
- **Silent zeros:** no silent zero found in either module. A missing
  income, cost, asset, count or area gives `needs_review`. Unverified
  exempt assets give `unsupported`, which is documented. An undeclared
  parameter gives `needs_review`.
- **API validation:** `Infinity` and `NaN` Decimal inputs are rejected
  with 422. Policy directories are pinned server-side.
- **Provenance:** the report refuses files changed after the run and
  refuses traces from mixed runs. The combined report requires the
  manifest to equal the verified files.
- **Store:** it is append-only, keyed by content, and verifies hashes on
  save and on restore. `record_from_plain` covers every current field of
  `WffScenario`, `ChildFacts` and `AsScenario`; I checked this by
  introspection.

## Not verified

- **PostgreSQL store and `/scenarios` routes.** All 9 related tests were
  skipped because no server binaries are installed. I reviewed them by
  reading the code only.
- **MB 2 annualisation.** Whether a given household's June income,
  annualised under MB 2, is below $44,900 cannot be established from the
  fixtures. F1 relies on the stated steady annual income. For g5, whether
  the Supported Living Payment recipient is the WFF person is unverified.
- **Remaining MD 14 and MD 15 text.** I did not read the rest of MD 14 and
  MD 15, nor the TAA 80KN-80KU route provisions, beyond what the
  repository cites. CW 33 and MB 13(2)(l) were not re-fetched. They are
  unverified by me, but I found no contrary evidence.
- **Area 1-4 SAU classification** (`as-msd-areas`) was not checked.
- **Installed-artifact and wheel build tests.** They are deselected by
  default and I did not run them.
