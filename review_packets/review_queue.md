# Independent review queue

`ROADMAP_REALIGNMENT.md` W1.1. This lists every merged PR that has not had
an independent (GPT/Codex) review. They merged on Claude Code's author
preflight under Pete's recorded delegation, which the working agreement
allows. The review-debt cap (`doctrine/development-doctrine.md`) counts the
**open implementation** rows. At five or more, no further implementation
PR merges. Plan, documentation and review-fix PRs are exempt.

Work the queue in risk order:

- **High:** it changes shared engine, loader or data-boundary code.
- **Medium:** it adds calculation-adjacent logic that has its own tests.
- **Low:** interface, documentation or process.

Record each review in `reviews/` using `review_packets/TEMPLATE.md`,
classify findings under the Review Doctrine, and change the row's status
to `reviewed (reviews/<file>)`. A finding is fixed by a new PR, never by
editing history.

**As of 26 September 2026: 17 open implementation rows. The cap is
reached.**

| PR | Release | Scope | Touches | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| #94 | v0.2 | Validation, weighting, reforms; optional preloaded `parameters` on `run_wff_module`, `run_as_module`, `run_combined_household`; `check_preloaded_parameters` | Engines, loader | High | open |
| #95 | v0.2 | Population runner; `load_bound_policy_spec` parse cache keyed by SHA-256 | Loader | High | open |
| #93 | v0.2 | Data layer, manifest, registry, snapshot guard; population schema; `record_from_plain` moved to `record.py`; `data/raw/` no longer gitignored | Data boundary, scenario records | High | open |
| #82 | v0.1.5 | Calculation steps recorded in traces (`record_step`) | Engines | High | open; in `v0_1_5_codex_audit.md` |
| #83 | v0.1.5 | Reason codes, `missing_facts`, unsupported categories | Engines, outcomes | High | open; in `v0_1_5_codex_audit.md` |
| #84 | v0.1.5 | Deterministic explanations and `verify()` | Assurance | Medium | open; in `v0_1_5_codex_audit.md` |
| #86 | v0.1.5 | Source types, authority rank, evidence coverage check | Assurance, source schema | Medium | open; in `v0_1_5_codex_audit.md` |
| #100 | v0.2 | v0.2 release-gate test; exact six-decimal synthetic weights | Generator | Medium | open |
| #98 | v0.2 | Seeded synthetic population generator and CLI | Scenarios | Medium | open |
| #96 | v0.2 | Analysis tables, withdrawal paths, sweeps | Scenarios | Medium | open |
| #97 | v0.2 | Verified population explanations; overridden-parameter evidence in the run | Scenarios | Medium | open |
| #92 | v0.1.6 | Source-currency report and weekly workflow | Assurance, CI | Low | open |
| #99 | v0.2 | `/microsim` API and `/analyst/microsim` page | API | Low | open |
| #85 | v0.1.5 | Analyst page and pilot container | API, deploy | Low | open; in `v0_1_5_codex_audit.md` |
| #87 | v0.1.5 | Phase 7 hardening, household form, case metadata, working agreement | Tests, API, doctrine | Low | open; in `v0_1_5_codex_audit.md` |
| #88 | v0.1.5 | Per-policy routes return explanations; audit packet | API | Low | open; in `v0_1_5_codex_audit.md` |
| #89 | v0.1.5 | Pilot pack, findings template, executable release gate | Tests, docs | Low | open |

## Plan and decision PRs (not counted against the cap)

| PR | Scope | Status |
| --- | --- | --- |
| #90 | v0.1.6 and v0.2 plans; ADR-0014 | Pete accepted; independent review optional |
| #101 | ADR-0015, `ROADMAP_REALIGNMENT.md`, v0.3 plan | Pete accepted; independent review optional |
