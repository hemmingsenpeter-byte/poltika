# Review Packet: v0.2 real data, population and cross-validation (PRs #111, #113, #114, #117, #118) — 27 September 2026

Author: Claude Code, under Pete's goal "accept and proceed on all — keep
working without interruption on v0.2". Each PR merged, or will merge, with
CI green after an author preflight only. This packet hands GPT/Codex the
independent review of the three open v0.2 queue rows
(`review_packets/review_queue.md`) and the checks v0.2 assigns to it:
Tasks 3.1-3.2 (tables and acquisition), 9.3 (hand-calculated population
cases) and the GPT/Codex half of 9.4 (cross-validation).

## Review inputs

- **PRs:** #111 (Stats NZ snapshots, four transformations, 54 canonical
  variables), #113 (the derived population spec, `calibration.py`,
  `calibrate_cli.py`), #114 (IRD and MSD snapshots, `data/xlsx.py`,
  `crossval.py`, `crossval_cli.py`, v0.2 release documents), #117 (Task 9.3
  author cases in `tests/acceptance/test_v0_2_hand_calculated.py`; Task 2.3
  author check in `reviews/2026-09-27-v0-2-task-2-3-author-check.md`;
  assumption A12), #118 (fixes from the fresh same-model check).
- **Prior checks, to read only after your independent section:** the fresh
  same-model check (`reviews/2026-09-27-v0-2-fresh-same-model-check.md`,
  seven findings, F6 and part of F5 still open) and the Task 2.3 author
  check. Neither is an independent review.
- **Review debt:** these are the five open v0.2 implementation rows in
  `review_packets/review_queue.md`, which is at its cap. No implementation
  PR merges until rows are cleared.
- **Sources:** every snapshot under `data/raw/` with its manifest under
  `data/metadata/datasets/`; the publications' URLs are in the manifests.
  Re-fetch each and compare its SHA-256.
- **Records:** `docs/research/v0_2_task_3_1_calibration_tables.md`,
  `docs/releases/V0_2_POPULATION_METHODOLOGY.md`,
  `docs/releases/V0_2_CROSS_VALIDATION.md`.
- **Tests:** `tests/unit/data/test_real_snapshots.py`,
  `tests/unit/scenarios/microsim/test_calibration.py`,
  `tests/unit/scenarios/microsim/test_crossval.py`,
  `tests/acceptance/test_v0_2_release_gate.py`. Full suite at #114's head:
  952 passed, 14 skipped (PostgreSQL not available locally).

## Independent review

Complete this section before reading the author notes.

### Independently derived expected behaviour

(reviewer derives from the publications and `BUILD_PLAN_v0_2.md`)

### Questions to answer

1. **Snapshots (#111, #114).** Is each file byte-identical to the
   publication at its URL? Is every manifest field supported by the
   publication itself (vintage, observation period, units, geography)? In
   particular: the MSD fact sheets' Accommodation Supplement count recorded
   as recipients in the quarter; the IRD tax year mapped to 1 April-31
   March; the births counts as registrations.
2. **Transformations.** Does each read the right rows? Check:
   - HES Table 10's `household.count.total` as the sum of bands P001 and
     P002 (complementary: under 25%, 25% or more);
   - HES Table 3's CSV codes (`M0001`/`1001A`) differing from the workbook;
   - IRD values rounded to published precision (0.1 thousand, $1 million),
     because some cells store float noise;
   - the births regex against both release pages.
3. **HES Table 5 counts people, not households** (total 5,205.2 thousand).
   Agree or refute.
4. **Derivation rules D1-D7 and assumptions A1-A9** (`calibration.py`).
   Are they stated correctly, applied as stated, and the least-bad choices
   the published tables allow? A9's claim (the top rent band's bound can't
   change any AS amount) is tested against the AS policy's caps and entry
   thresholds; check the test's logic.
5. **Data boundary.** `calibrate_cli.py` and `crossval_cli.py` are the only
   `ALLOWED` importers of `poltika.data` outside it. Is anything else
   reaching raw files?
6. **Cross-validation (9.4).** Are the modelled figures the right weighted
   baseline quantities? Are the published figures the right comparators?
   Is every stated reason for a gap true (for example, WFF-06 on the first
   year's abatement exemption)? Is any gap left unexplained?
7. **Task 9.3.** Build small hand-calculated populations and check totals,
   deciles and winner counts against the runner and analysis modules.

### Findings

(ordered by severity, classified under the Review Doctrine)

## Author notes (read after the independent section)

- The first D6 rule, fitting the open rent band to HES's 2018 mean rent,
  failed: the 2018 Census bands already exceed that mean because the two
  publications measure rent differently. A9 replaced it.
- Two unsupported claims were caught in author preflight and removed from
  the cross-validation reasons: "most AS recipients are beneficiaries" (the
  MSD table has no split) and "board is unsupported" (board is inside the
  rent/board branch).
- 2023 Census tables were not acquired: Aotearoa Data Explorer needs a
  registered API key. That is why AS area shares are assumed (A5).
- The MSD Accommodation Supplement area page was acquired and then dropped
  before merge: it has no counts, and it is already the `as-msd-areas`
  policy source.
