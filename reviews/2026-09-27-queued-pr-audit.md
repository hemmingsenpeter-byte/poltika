# Review Packet: queued implementation PRs - 27 September 2026

Independent GPT/Codex review of the 18 implementation rows in
`review_packets/review_queue.md`. Fixes below are Codex-authored and need
the other model's review; this record does not approve those fixes or a release.

## Review inputs

Integrated checkout: `f4d8a93`. Historical PR diffs were checked against
their recorded base/head commits; reproductions and regression checks used
the integrated checkout. GitHub reported SUCCESS for all 18 original PR heads.
There were no existing review threads on these PRs.

Contracts: `BUILD_PLAN_v0_2.md` Phases 1-10, R3-R8 and D8-D9;
`BUILD_PLAN_v0_1_5.md` Phases 1-7; `BUILD_PLAN_v0_1_6.md` Task 2.1;
`ROADMAP_REALIGNMENT.md` W1.5/W5.2; `REPOSITORY_STRUCTURE.md`;
the WFF and AS `specification.md`, `policy.yaml` and existing decision artifacts.
Source maps remain `policy_specs/{working_for_families,accommodation_supplement}/sources.yaml`.
This is an implementation review against accepted contracts, not a fresh
legislation-currency audit or independent re-derivation of statutory amounts.

## Independent review

### Independently derived expected behaviour

Unknown facts must not become verified inputs or amounts. Reform assumptions
remain separate from law. Preloading and caching preserve date, version and
artifact checks. Population order must not change run identity. Aggregation
counts each selected component once and keeps annual and weekly amounts apart.
Invalid households are reported without crashing. Explanations and coverage
checks must detect missing or altered evidence. Synthetic weights and reports
must agree. Fetching a run must not depend on another caller's measure selection.

### PR results

Base/head abbreviations identify the exact Git objects. Finding IDs refer to
the discrepancies below; “none” means no additional actionable finding.

| PR | Base / head | Review scope and result |
| --- | --- | --- |
| #94 | 54b2e86 / 0e32e25 | Parameter preloading, reform validation, record consistency and weighted statistics. F2, F3. Date/version/hash guards and identity reform remain intact. |
| #95 | 1165939 / b52e909 | Batch loading, delta coverage, run hashing and copied cached specs. F4; file-hash checks and cache-copy isolation retained. |
| #93 | 70f989c / e7010f4 | Manifest paths/hashes, registry, lazy transformations, dependency boundary and record adapter. F1, F2; decoder relocation preserves stored-record fields. |
| #82 | 2951758 / 0f81e2e | Arithmetic instrumentation and step/rule links. AS rounding originally cited AS-04; already corrected to AS-07 in #89. No remaining arithmetic finding. |
| #83 | 11980c0 / f8b4b3a | Reason codes, missing facts and unsupported categories. Bundled AS household exclusion originally overclaimed evidenced exclusion; already corrected in #89. |
| #84 | cadcd71 / 4a1189d | Templates, evidence, verifier and household responses. F7. |
| #86 | 9049917 / e77c58a | Kind-to-rank schema, citation coverage, CI command and baseline documentation. F8. Ranking mechanics reviewed; no new source-authority or legal interpretation approved. |
| #100 | 5b16f56 / a20964b | Release invariants and rounded synthetic weights. F9, F10. Real-population gate remains pending. |
| #98 | 689b067 / 3b65345 | Seeded generation, explicit assumptions, labels, calibration and CLI. Recurring-weight drift was subsequently addressed in #100; F9/F10 cover remaining rounding issues. |
| #96 | 2066a50 / e4aa4dc | Fiscal/group tables, weighted cuts, withdrawal paths and sweeps. F5, F6. Unit separation and clearing stale net income are correct. |
| #97 | 6d4f1a9 / e6bda2d | Override evidence and population explanations. F6 affects the all-invalid path. |
| #92 | 9521446 / fc30628 | Currency-report date boundaries, unresolved rates, stale checks and issue workflow. None; the report correctly requests a source recheck rather than claiming to perform one. |
| #99 | dcb5b04 / edcd73a | Operator-owned population, API validation, run retention and analyst tables. F11; F5/F6 also surfaced through this API. |
| #85 | 35b5fe6 / c3f7e8d | Analyst endpoints, safe text rendering, packaging, non-root pilot image and migration entrypoint. None. Browser/container runtime confirmation is limited to existing tests and CI. |
| #87 | 636d8e7 / 9c9ed4b | Schema-driven form, trace fixtures, metadata tests, protected-path workflow and operating agreement. None beyond F7 inherited from #84. |
| #88 | b4edd34 / 83e1e3b | Per-policy explanation responses, decimal serialization and trace-bearing stubs. None. |
| #89 | 32a2d84 / 279f367 | Pilot cases, release checks, claimant-link reason and prior audit corrections. No additional finding; AS-07 and not_modelled corrections agree with accepted specifications. |
| #103 | b38d5d2 / 25c415a | Queue reader, pending-review release skips and automatic policy discovery for currency reporting. None. Pending gates remain skips, not release approval. |

### Discrepancies found

Classifications are proposed under the Review Doctrine. Paths are relative to
`src/poltika/`; regression tests pin the reproductions.

| ID | Severity / classification | Trigger, impact and resolution |
| --- | --- | --- |
| F1 | P1 / CODE_ERROR | `data/context.py::_transform` read snapshot bytes again after registry validation without rehashing. Editing 105 to 999 before the first read returned 999 with the old lineage hash. Hash the exact bytes passed to the transform. Fixed in `9dec7f2`. |
| F2 | P1 / CODE_ERROR | `scenarios/population.py::scenario_record` trusted canonical primitive types in externally supplied facts. Attestation string `"false"` was truthy; fractional/bool child counts and infinite money also passed validation. Reject these as invalid households. Fixed in `9dec7f2`. |
| F3 | P2 / CODE_ERROR | `scenarios/microsim/reform.py::_overridden` accepted zero `asset_imputation_step_size`; households above the imputation threshold crashed with DivisionByZero. Reject a zero divisor for set/add/multiply. Fixed in `ce8217c`. |
| F4 | P2 / CODE_ERROR | `semantics/population.py::content_sha256` hashed household list order. Reversing records changed run_id with identical results_sha256. Sort households by their unique IDs for hashing. Fixed in `ce8217c`; existing population/run hashes can consequently change. |
| F5 | P2 / CODE_ERROR | `scenarios/microsim/analysis.py::component_set_unit` accepted duplicate components. Repeating FTC doubled the test population's change from 15180 to 30360. Reject duplicates, including API requests. Fixed in `ce8217c`. |
| F6 | P2 / CODE_ERROR | `analysis.overall` omitted its all group when no household ran; `explain_population` then raised KeyError. Return an empty summary with zero calculated weight; retain the invalid-record counts. Fixed in `ce8217c`. |
| F7 | P2 / CODE_ERROR | `engines/assurance/explanation.py::verify` accepted an AS-07 citation on an FTC step, omitted evidence/assumptions and an invented summary payment. Compare citations and all deterministic explanation fields with the recorded result. Fixed in `c7c7a9c`. |
| F8 | P2 / CODE_ERROR | `engines/assurance/evidence.py::evidence_coverage` checked only rows it could parse. Deleting AS-07 left no reported problem although policy.yaml still referenced it. Check declared rule references against parsed rows. Fixed in `c7c7a9c`. |
| F9 | P3 / CODE_ERROR | `SyntheticSpec.represents` allowed sub-millionth totals that six-decimal weights silently truncated (1.0000001 became 1.000000). Reject precision the declared weighting scheme cannot represent. Fixed in `0da7f4a`. |
| F10 | P2 / CODE_ERROR | `synthetic._calibration` counted records equally after #100 made remainder weights unequal. Three records representing 0.000004 can report a one-third share for weight one-half. Accumulate actual weights, including per-child draws. Fixed in `0da7f4a`. |
| F11 | P2 / CODE_ERROR | `api/microsim.py` stored a selected summary under a measure-independent run_id. Posting AS after FTC silently replaced the earlier GET response. Retain the run and select measures with repeatable `component_set` query parameters (FTC default). Fixed in `5f3d61c`. |

## Author response

The reviewer implemented the narrow fixes after reproducing the findings.
No statutory values, source classifications, policy approvals or golden
fixtures were changed. F7 checks faithful rendering from the trace; it does
not independently prove the trace's arithmetic.

## Resolution and verification

- Initial full suite: `uv run --extra dev pytest -q`: **844 passed, 17 skipped,
  2 deselected**. Skips are not evidence of completed release requirements.
- Thirteen targeted regression cases failed before fixes and passed afterwards.
  Additional assurance, precision and API regressions also exposed their defects.
- Final focused suite: **333 passed**:
  `.venv/bin/pytest -q tests/unit/data tests/unit/scenarios/microsim
  tests/unit/scenarios/test_population.py
  tests/unit/engines/assurance/test_explanation.py
  tests/unit/engines/assurance/test_evidence.py
  tests/unit/api/test_microsim_api.py --tb=short`.
- `.venv/bin/ruff check src tests`: passed.
- `.venv/bin/mypy --strict src`: passed, 55 source files.
- Evidence CLI for both policies: no problems; 48 parameter values and 20 rules.
- Final PR CI supplies the full-suite, PostgreSQL, installed-wheel, code-replay
  and container checks. Those deployment checks were not rerun locally.

All 18 queued implementation reviews are recorded here. Optional plan PRs
#90/#101 were not re-reviewed. These fixes await independent review and merge
through their new PR. External pilot acceptance, source-currency work and
real-population/calibration release work remain separate requirements.
