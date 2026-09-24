# v0.1 traceability matrix (Task 34.1)

Drafted by Claude Code, 25 September 2026, against `feat/task33-2-scenario-routes`
(Tasks 32 and 33.2 are in open PRs #63 and #64). **GPT/Codex verifies each row's
evidence** (BUILD_PLAN.md Task 34.1). Any row marked **Gap** blocks v0.1
acceptance until it is evidenced or Pete records a decision.

Status key: **Evidenced** (artifact exists and was checked by the drafter),
**Evidenced with limitation** (evidenced, with a stated scope limit Pete has
already accepted), **Pending** (evidence depends on a step not yet done),
**Gap** (no evidence).

## Definition of Done (BUILD_PLAN.md)

| # | Bullet | Evidence | Status |
| --- | --- | --- | --- |
| D1 | WFF + Accommodation Supplement both correctly modelled and benchmarked independently | WFF: `policy_specs/working_for_families/{specification.md,policy.yaml,spec_cases.yaml,benchmarks.yaml}`; `tests/unit/engines/simulator/test_wff{,_spec_cases,_benchmarks,_module}.py`; Task 17 review packet `review_packets/wff_task17.md`. AS: `policy_specs/accommodation_supplement/*`; `tests/unit/engines/simulator/test_{accommodation_supplement,as_spec_cases,as_benchmarks,as_module,as_rate_selectors}.py`; Task 24.4 packet `review_packets/as_task24_4.md`; Task 26a rate repair `review_packets/task_26a_as_rate_audit.md`, `docs/research/task_26a_as_rate_audit.md` | Evidenced with limitation: the WFF in-work tax credit (`in_work_base`) stays `needs_review` for the v0.1 interval (Task 26b, commit `5389f52`); it is reported, never silently computed |
| D2 | Cross-policy interaction verified | Interaction sources `docs/research/task_28_1_wff_as_interactions.md`, `review_packets/task_28_1_interaction_sources.md`; period reconciliation `docs/research/task_28_2_period_reconciliation.md`, `review_packets/task_28_2_period_reconciliation.md`; contract in `policy_specs/accommodation_supplement/specification.md` (Task 28.3, revised after fresh-context review, `81d476a`); DEC-003; `policy_specs/wff_as_interaction/spec_cases.yaml` with `tests/unit/scenarios/test_interaction_spec_cases.py`; `tests/regression/test_wff_as_interaction_leaks.py`; golden households g1-g9 (`policy_specs/wff_as_interaction/golden_households.yaml`, `tests/unit/scenarios/test_golden_households.py`) | Pending: Codex review of the 28.4 runner and 29.3 (34.3) |
| D3 | Effective-dated, provenance-tagged POLICY_SPECS (schema v0.1, stress-tested by two structurally different policies) | ADR-0002; `src/poltika/semantics/schemas/policy_spec.py`; `src/poltika/policy/loader.py` (effective intervals, source ids, artifact hashes); `tests/unit/policy/test_loader*.py`; both policies' `sources.yaml`; Task 25 finding and Pete's Task 27.1(a) decision recorded in BUILD_PLAN.md | Evidenced |
| D4 | Three-layer testing in place, statutory values CI-protected | Spec: `test_*_spec_cases.py`, `test_interaction_spec_cases.py`. Benchmark: `test_*_benchmarks.py`. Regression: `tests/regression/` including `test_golden_result_snapshot.py` (frozen `tests/fixtures/golden_results_v0_1.json`). Protection: `.github/workflows/statutory-value-guard.yml`, ADR-0007 (supersedes ADR-0005), `doctrine/test-doctrine.md` | Evidenced with limitation: the guard is **visibility only** (ADR-0007: branch protection is unavailable on the repo's plan). **Gap to decide:** no CI workflow runs the test suite; the three layers run locally only (last full run: 381 passed, 25 September 2026). Pete decides whether "CI-protected" is met by ADR-0007 as accepted, or a test workflow is added before the tag |
| D5 | Interpretation ambiguity has a recorded decision artifact (evidence, rationale, owner, date) | `policy_specs/accommodation_supplement/decisions/DEC-001` (income-excess rounding), `DEC-002` (published thresholds and rate scope), `DEC-003` (MSD-paid WFF income exclusion); `docs/research/2026_09_24_scope_resolution.md`; WFF has no DEC records (`policy_specs/working_for_families/decisions/README.md`); the in-work credit is gated rather than interpreted (26b) | Pending: Codex confirms no unrecorded interpretation remains (34.3). Drafter found none, but did not re-audit every rule |
| D6 | One real cross-policy household scenario answerable end to end, deterministically, with provenance | `POST /household/calculate` and `POST /scenarios` (`src/poltika/api/{household,scenarios}.py`); deterministic ids and code identity (`src/poltika/scenarios/record.py`, `tests/unit/scenarios/test_scenario_record.py`); combined provenance (`src/poltika/engines/assurance/provenance.py`); storage and replay (`src/poltika/scenarios/store.py`, `tests/unit/scenarios/test_store.py`); **34.2 end-to-end test through the installed wheel**: `tests/installed_artifact/` (request → both modules → PostgreSQL persistence → replay → provenance report checked against the stored manifest and deployed file hashes) | Evidenced for the mechanism; the *chosen* real question is Task 35.1 (Pete) |
| D7 | Minimum external statistical datasets frozen, or a recorded determination that none is needed | Task 10a/10b closed N/A for WFF (BUILD_PLAN.md, line ~569); Task 22a closed N/A for AS, 22 September 2026; replay rests on retained policy artifacts and hashes (Tasks 30, 32, ADR-0013) | Evidenced |

## ROADMAP.md v0.1 exit gate

> A supported household scenario runs end to end with deterministic,
> source-traceable results for both policies and passes the frozen v0.1 review
> and test gates.

| # | Clause | Evidence | Status |
| --- | --- | --- | --- |
| E1 | Supported household scenario runs end to end | D6 | Evidenced |
| E2 | Deterministic | Canonical-JSON ids, golden snapshot, `replay` reproduces (`test_store.py`, installed probe) | Evidenced |
| E3 | Source-traceable for both policies | Combined provenance report resolves source, rule and decision ids against hash-bound artifacts (`tests/unit/engines/assurance/`) | Evidenced |
| E4 | Passes the frozen v0.1 test gates | Local full suite and installed-artifact test green; see D4's CI gap | Pending on D4 decision |
| E5 | Passes the frozen v0.1 review gates | Independent reviews outstanding: Codex has not reviewed #60-#64 (Tasks 30, 31.6, 32, 33) or the Claude-authored slices of 34.3; the Claude fresh-context review of 26a, 26b, 28.1, 28.3, 29.2 (34.3) has not run | **Gap** until 34.3-34.4 complete |

## Open items for Pete

1. D4: accept ADR-0007 visibility-only protection plus local test runs, or
   add a CI test workflow before `v0.1.0`.
2. E5: schedule the 34.3 cross-review (both directions).
3. Task 35.1-35.2: choose the demo question and surface.
