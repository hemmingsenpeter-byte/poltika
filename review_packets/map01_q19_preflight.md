# Review Packet: MAP-01 fix and Q19 (1), (2), (5) — 13 October 2026

**Label: author preflight, with two fresh same-model checks (`poltika-reviewer`).**
Not an independent GPT/Codex review. Claude Code wrote the change and its
rationale, so the author section below was not written blind.

## Review inputs

- Branch `fix/map01-overlapping-benefit-spells-20261013`; base `de76f26`
  (origin/main after #215). Commits `ec360cd`, `268a2ea` (MAP-01), `c5f73e9`
  (Q19 code), `f10d558` (records, DEC-004, B1–B3), `c846295` (preflight fixes).
- Finding and sources: [MAP-01](../reviews/2026-10-12-task5-6-mapping-codex.md)
  (Social Security Regulations 2018 r 17(1), r 18, as at 4 September 2026);
  [Q19 research](../docs/research/q19_household_mapping_readings.md);
  [B4 review](../reviews/2026-10-12-wff-as-boundary-proposal-codex.md);
  Pete's decisions: [2026-10-13 record](../docs/programme/2026-10-13-pete-approvals.md), D37, D38.
- Specification: `policy_specs/accommodation_supplement/specification.md`
  (s 423(3) note, Task 22 gates); AS DEC-001, DEC-004.
- Commands (local `.venv`, `PYTHONPATH=src`):
  - `pytest -q tests/unit/semantics tests/unit/scenarios tests/regression`:
    641 passed, 20 skipped, with `test_identity_is_the_same_in_a_separate_process`
    deselected. It fails locally only because its subprocess drops
    `PYTHONPATH` and imports the stale main checkout; CI runs it.
  - After `c846295`: `tests/unit/scenarios/test_combined.py tests/unit/semantics
    tests/unit/scenarios/test_household_roundtrip.py tests/regression`: 252 passed.
  - `ruff check src tests`: pass. `mypy --strict src`: no issues in 107 files.
  - `git diff --check`: clean.

## Independent review

### Expected behaviour (derived from the finding and Pete's decisions)

- Overlapping benefit spells for one person are invalid; adjacent spells are
  not; other people's spells are independent.
- AS: a covering spell beside any other receipt in the week is refused; a
  week not wholly covered by one spell gives category `None`; no mid-week rule.
- WFF: a main-benefit spell (JSS, SPS, SLP) of claimant or partner overlapping
  the tax year is refused only when in-work eligibility or MC 6(b) is
  verified; dates only, no apportionment.
- Combined pair: every existing fixture result unchanged.
- No calculated amount, protected value or fixture changes.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| Pass 1 (MAP-01): D37 cited Q19 for the mid-week question, which Q19 does not cover | SPEC_ERROR (nit) | Fixed `268a2ea` |
| Pass 1: no multi-person, unsorted or same-kind adjacent tests | TEST_ERROR (P3) | Fixed `268a2ea` |
| Author: the first Q19 (5) draft refused the `main_benefit_disagreement_flags_every_component` pair, breaking round-trip identity | CODE_ERROR (caught by the round-trip test) | `to_combined` leaves the claimant's assessment-week spell to `combined.py`'s per-component check (`c5f73e9`) |
| Pass 2: the pair-path skip had no end-to-end test (other kinds, week outside the year) | TEST_ERROR (P3) | Fixed `c846295` |
| Pass 2: the skip did not check the benefit kind, and the two main-benefit sets were linked by comment only | CODE_ERROR (P3, latent) | Kind check and set-equality test added `c846295` |
| Pass 2: the Task 5–6 packet still showed `NZD` UNRESOLVED | SPEC_ERROR (nit) | Dated update note added |
| Pass 2: DEC-004 "read directly by both reviews" was loose on dates | MISSING_SOURCE (nit) | Reworded |

No P1 or P2 remains.

## Author response

The pair-path skip is sound because `shared_fact_contradictions` always runs
the main-benefit check, and after MAP-01 the skipped spell always becomes the
AS claimant category. Partner spells and other claimant spells in the year are
still refused. `PeriodStatus.UNRESOLVED` is kept as vocabulary with no current
binding.

## Not verified

- No primary source was re-fetched for this PR; statutory readings rely on the
  cited Codex review and specification.
- The full suite was not run in a clean environment locally; CI is the check.

## Deferred Codex audit

Recheck the final head for: MAP-01 (`ec360cd`, `268a2ea`), clearing #207's
row; the Q19 (5) check and its pair-path skip (`c5f73e9`, `c846295`), which
changes which route a directly built household takes; DEC-004's wording
against the B4 review.
