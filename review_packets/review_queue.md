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

**As of 27 September 2026: 1 open implementation row (#109).**
The independent reviews and 11 findings are recorded in
`reviews/2026-09-27-queued-pr-audit.md`. Their fixes (#108, Codex-authored)
were independently reviewed by Claude Code with no blocking findings
(#108 comment) and merged. This is not release approval.
#103 originally merged under Pete's explicit exemption ("Exempt 103").

| PR | Release | Scope | Touches | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| #94 | v0.2 | Validation, weighting, reforms; optional preloaded `parameters` on `run_wff_module`, `run_as_module`, `run_combined_household`; `check_preloaded_parameters` | Engines, loader | High | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #95 | v0.2 | Population runner; `load_bound_policy_spec` parse cache keyed by SHA-256 | Loader | High | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #93 | v0.2 | Data layer, manifest, registry, snapshot guard; population schema; `record_from_plain` moved to `record.py`; `data/raw/` no longer gitignored | Data boundary, scenario records | High | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #82 | v0.1.5 | Calculation steps recorded in traces (`record_step`) | Engines | High | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #83 | v0.1.5 | Reason codes, `missing_facts`, unsupported categories | Engines, outcomes | High | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #84 | v0.1.5 | Deterministic explanations and `verify()` | Assurance | Medium | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #86 | v0.1.5 | Source types, authority rank, evidence coverage check | Assurance, source schema | Medium | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #100 | v0.2 | v0.2 release-gate test; exact six-decimal synthetic weights | Generator | Medium | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #98 | v0.2 | Seeded synthetic population generator and CLI | Scenarios | Medium | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #96 | v0.2 | Analysis tables, withdrawal paths, sweeps | Scenarios | Medium | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #97 | v0.2 | Verified population explanations; overridden-parameter evidence in the run | Scenarios | Medium | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #92 | v0.1.6 | Source-currency report and weekly workflow | Assurance, CI | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #99 | v0.2 | `/microsim` API and `/analyst/microsim` page | API | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #85 | v0.1.5 | Analyst page and pilot container | API, deploy | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #87 | v0.1.5 | Phase 7 hardening, household form, case metadata, working agreement | Tests, API, doctrine | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #88 | v0.1.5 | Per-policy routes return explanations; audit packet | API | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #89 | v0.1.5 | Pilot pack, findings template, executable release gate | Tests, docs | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #103 | v0.2 | Release-gate review rows (`tests/acceptance/review_queue.py`); currency workflow discovers every policy. Merged under Pete's exemption | Tests, CI | Low | reviewed (reviews/2026-09-27-queued-pr-audit.md) |
| #108 | v0.2 | Codex-authored fixes F1-F11 from the queued-PR audit | Data, scenarios, assurance, API | High | reviewed (Claude Code, PR #108 comment) |
| #109 | v0.3 | Fact catalogues (`facts.yaml`, drafted wording) and conditional answers (`scenarios/conditional.py`), ADR-0016 | Scenarios, policy loader, policy_specs | Medium | open (wording and resolver review) |

## Plan and decision PRs (not counted against the cap)

| PR | Scope | Status |
| --- | --- | --- |
| #90 | v0.1.6 and v0.2 plans; ADR-0014 | Pete accepted; independent review optional |
| #101 | ADR-0015, `ROADMAP_REALIGNMENT.md`, v0.3 plan | Pete accepted; independent review optional |
