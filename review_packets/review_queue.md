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

**As of 27 September 2026: 1 open implementation review row (#124).** GPT/Codex reviewed #121 (`reviews/2026-09-27-pr121.md`); Claude Code checked its two fixes.
Pete confirmed on 27 September 2026 that GPT/Codex cleared every PR up to
#120 ("Yes all cleared by codex"), and approved all prior work. #111, #113,
#114, #118 and #120 are marked reviewed on that confirmation; their review
records, other than #117's (`reviews/2026-09-27-pr117.md`), are Codex's to
commit under `reviews/`.
PR #109's review is recorded in `reviews/2026-09-27-pr109.md`. Its
Codex-authored fixes (#112) were independently checked by Claude Code
with no blocking findings (#112 comment), accepted by Pete, and merged.
The independent reviews and 11 findings are recorded in
`reviews/2026-09-27-queued-pr-audit.md`. Their fixes (#108, Codex-authored)
were independently reviewed by Claude Code with no blocking findings
(#108 comment) and merged. This is not release approval.
#103 originally merged under Pete's explicit exemption ("Exempt 103").

| PR | Release | Scope | Touches | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| #124 | pilot | Hosted pilot: `api/access.py` HTTP Basic password (fail-closed in the image), `/healthz`, `$PORT`, built-in population, CI smoke test | API middleware, deploy | Medium | open |
| #121 | v0.3 | Intake planner (`scenarios/intake.py`), `Resolution.ranked`/`unblocks` (Task 1b.4); Codex fixes F1-F2 checked by Claude Code | Scenarios | Medium | reviewed (reviews/2026-09-27-pr121.md) |
| #120 | v0.2 | Fresh-check F6 fix: every transformation version kept (`TRANSFORMATION_VERSIONS`), `DataContext` reads the manifest's version; IRD WFF reader v2 at published precision with a v2 manifest | Data layer | Medium | reviewed (GPT/Codex; Pete confirmed 27 Sep 2026) |
| #118 | v0.2 | Fixes from the fresh same-model check: cross-validation reason codes and children measure, A3/A13, dictionary meanings, boundary test | Assurance, spec sources, data-boundary test | Low | reviewed (GPT/Codex; Pete confirmed 27 Sep 2026) |
| #117 | v0.2 | Task 9.3 hand-calculated population cases; Task 2.3 author check; assumption A12 named in the population spec's sources | Tests, spec sources | Low | reviewed (reviews/2026-09-27-pr117.md) |
| #114 | v0.2 | Cross-validation (Task 9.4): IRD WFF and MSD fact-sheet snapshots, `data/xlsx.py` reader, `crossval.py` report | Data boundary, assurance | Medium | reviewed (GPT/Codex; Pete confirmed 27 Sep 2026) |
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
| #109 | v0.3 | Fact catalogues and conditional answers (`scenarios/conditional.py`), ADR-0016 | Scenarios, policy loader, policy_specs | Medium | reviewed (reviews/2026-09-27-pr109.md) |
| #111 | v0.2 | Stats NZ snapshots, manifests, four transformations and 54 canonical variables (Tasks 3.1-3.2) | Data | Medium | reviewed (GPT/Codex; Pete confirmed 27 Sep 2026) |
| #113 | v0.2 | Synthetic development population derived from #111 (`calibration.py`, `calibrate_cli.py`, spec); fresh same-model check in the PR comment, A10-A11 named in the release-docs PR | Scenarios, data boundary | Medium | reviewed (GPT/Codex; Pete confirmed 27 Sep 2026) |
| #112 | v0.3 | Codex-authored fixes F1-F3 for #109 and the catalogue wording review | Scenarios, policy_specs | Medium | reviewed (Claude Code, PR #112 comment) |

## Plan and decision PRs (not counted against the cap)

| PR | Scope | Status |
| --- | --- | --- |
| #90 | v0.1.6 and v0.2 plans; ADR-0014 | Pete accepted; independent review optional |
| #101 | ADR-0015, `ROADMAP_REALIGNMENT.md`, v0.3 plan | Pete accepted; independent review optional |
