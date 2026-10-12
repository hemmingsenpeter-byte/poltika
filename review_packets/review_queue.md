# Independent review queue

Historical origin: `ROADMAP_REALIGNMENT.md` W1.1 (archived). Current review
sequencing follows `BUILD_PLAN_PROGRAMME.md` Phase A and ADR-0020. This lists every merged PR whose independent
(cross-model) review or resulting fixes remain outstanding. They merged on Claude Code's author
preflight under Pete's recorded delegation, which the working agreement
allows. The review-debt cap was suspended on 29 September 2026
(`doctrine/development-doctrine.md`, `BUILD_PLAN_PROGRAMME.md` retained decision P17): open
rows no longer stop merges, but every one is still listed here, and
release gates skip, naming them, until review and required fixes are complete.

**Final-head cross-model reviews completed 6 October 2026:** the Codex-authored
source scopes [#148](https://github.com/hemmingsenpeter-byte/poltika/pull/148),
[#151](https://github.com/hemmingsenpeter-byte/poltika/pull/151),
[#172](https://github.com/hemmingsenpeter-byte/poltika/pull/172) and
[#175](https://github.com/hemmingsenpeter-byte/poltika/pull/175) were reviewed by Claude with
primary-source re-derivation and merged (`reviews/2026-10-06-pr148.md`, `pr151.md`,
`pr172.md`, `pr175.md`; train coverage in `reviews/2026-10-06-integration-train.md`).
[#163](https://github.com/hemmingsenpeter-byte/poltika/pull/163) merged at `f9c69d8` and
[#164](https://github.com/hemmingsenpeter-byte/poltika/pull/164) at `94df1a0`.

**Current merged review debt, 7 October 2026 (closeout, `main` `4c33c63`): 5 open scopes out of 11.**
The single table below retains #177's seven Claude-only scopes and adds
#177's own Claude-authored records commit. Independent Codex re-checks of
the merged snapshot `a8b214f` clear six bounded scopes. #174 and #162 retain
reproduced P2 findings; their Claude fixes are in #179 and #181, and each row
stays open until Codex reviews the fix's exact final head. #179 and #181 are
Claude-authored rows awaiting the same Codex recheck, as is #182 (the
self-hosted CI runner, authored by Pete's local Claude session). Same-model checks, author preflight and CI remain
supporting evidence. This is review clearance, not acceptance of a release
or independent review of the new Codex-authored documentation PR.

Reconciliation of `codex/review-debt-end-train-20261006` (`da50926`) against
current main: its #171/#174/#176 scopes were already in #177's list, so no
duplicate rows or stale #164 state are carried forward. The old branch is
retained; its queue-correction purpose is superseded by this one list.
These programme rows do not reopen historical release tags or imply
release acceptance.

Work the queue in risk order:

- **High:** it changes shared engine, loader or data-boundary code.
- **Medium:** it adds calculation-adjacent logic that has its own tests.
- **Low:** interface, documentation or process.

Record each review in `reviews/` using `review_packets/TEMPLATE.md`,
classify findings under the Review Doctrine, and change the row's status
to `reviewed (reviews/<file>)` once blocking findings are cleared. A finding
is fixed by a new PR, never by editing history.

Historical snapshot at 5 October 2026: no open implementation assurance rows
(#128 closed by #152 at `fe67875`). This does not clear later programme debt.
Independent GPT/Codex review of #128 is recorded in `reviews/2026-10-03-pr128.md`.
Its four P2 fixes were independently Claude-reviewed, tested, accepted by
Claude/Opus under Tier A and integrated through #150 at `3bea73f`. Latest-head
CI passed at `ea87240` before merge. The original review and its fixes are
complete; this is not release approval or completion of deferred capabilities.
GPT/Codex reviewed #124-127 in `reviews/2026-09-28-pr122-127.md`; their
reviewer-authored fixes were accepted under Pete's explicit cross-model
waiver on 2 October 2026. #132 and #133 are reviewed in
`reviews/2026-10-02-pr132.md` and `reviews/2026-10-02-pr133.md`, with the
same waiver for their fixes. That waiver did not cover the #128 follow-up, which was reviewed and accepted separately (see the #128 row).
Review packet: `review_packets/v0_3_phase_1b_codex_audit.md`.
GPT/Codex reviewed #121 (`reviews/2026-09-27-pr121.md`); Claude Code
checked its two fixes.
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
| #189 | programme | Task B0.1.4: web scenario flow, confirmation panel and workspace rendering of stored amounts (formatting, outcome markers, units) | Web frontend | Medium | merged 11 October 2026 at `8380f4b` with the remaining review requirements waived by Pete (decision log D30). A Claude fresh-context review of the delta `5be777c..2fc06ed` found no P1/P2 and one P3 (broad `except ValidationError` in `api/v1_scenarios.py`). GPT/Codex clearance of the final head was not obtained; the earlier record ([GPT/Codex at `5be777c`](../reviews/2026-10-08-pr189-final-codex.md)) stays frozen to its head |
| #193 | programme | Task 7: 2026–27 ordinary salary/wage source-linked specification, IT-01–IT-08; GPT/Codex authored | policy_specs, source/decision records | High | merged 11 October 2026 at `aa0c9c6` with the remaining review requirements waived by Pete (decision log D30). Claude primary-source reviews: `reviews/2026-10-09-pr193-source-recheck.md` and a second, independent one on 11 October ([record](../reviews/2026-10-11-pr193-independent-source-review.md), at `2cc00c8`: no P1, two P2 already gated in the spec as `needs_review`, three P3). GPT/Codex clearance is still owed before any Task 7 engine work, and Pete's Q16–Q18 remain open. The merged specification is not an approved specification |
| #188 | programme | Task B0.1.3: web shell, Home, Models and Data | Web frontend | Medium | reviewed — GPT/Codex at `dd6377e` found no blocking issues ([record](../reviews/2026-10-09-pr188.md)); squash-merged to main on 10 October 2026 as `9a79a2e`. A Claude fresh-context post-merge review at `dd6377e` found no P1 ([comment](https://github.com/hemmingsenpeter-byte/poltika/pull/188#issuecomment-6089654898)); its P2 (Dependabot runner and Actions-budget load) is an open follow-up: a Dependabot pause is prepared but not yet in a PR |
| #176 | programme | Mechanical main-update exemption; squash `7c0f67e`, final head `0df6008`; Claude commits `be7ca4e`/`0df6008` | Governance, review skills | Low | reviewed ([reviews/2026-10-07-codex-recheck-review-rule.md](../reviews/2026-10-07-codex-recheck-review-rule.md)); bounded Claude-authored scope |
| #174 | programme | XLSX DTD/entity guard; squash `0d115b4`, final head `3f43c0b`; Claude commits `427e6b6`/`ad4ca88` | Data reader | High | open — R1 P2 CODE_ERROR: malformed declarations reach ElementTree; [finding](../reviews/2026-10-07-codex-recheck-xlsx.md). Fix merged in #179 (Claude-authored `bb19ef8`/`41ce431`; final head `527dbb7`, squash `eacc5a2`): the shared guard fails closed. Awaits Codex recheck of that head |
| #171 | programme | Entity vocabulary and identifier schemes; squash `b176ddc`, final head `486f376` | Semantics, errors, tests | Medium | reviewed ([reviews/2026-10-07-codex-recheck-entities.md](../reviews/2026-10-07-codex-recheck-entities.md)); bounded Claude-authored scope |
| #167 | programme | Approval records and conflicted integrations; squash `1b64d0e`; Claude commits `cb32c81`/`ecb9f13`/`912f8e9`/`02e84a4`/`52cf02e` | Decisions, programme records | Low | reviewed ([reviews/2026-10-07-codex-recheck-records.md](../reviews/2026-10-07-codex-recheck-records.md)); bounded Claude-authored scope |
| #151 | programme | Repository-map conflict resolution; squash `38e5629`, final head `c4c4b2a` | Repository map | Low | reviewed ([reviews/2026-10-07-codex-recheck-records.md](../reviews/2026-10-07-codex-recheck-records.md)); bounded Claude-authored scope |
| #177 | programme | Integration-train records; squash `0046be0`, Claude head `40b3386` | Reviews, research records, entity citation | Low | reviewed ([reviews/2026-10-07-codex-recheck-records.md](../reviews/2026-10-07-codex-recheck-records.md)); bounded Claude-authored scope; nonblocking R1 P3 conflict count corrected in #181 |
| #161 | programme | Units registry; squash `9e67009`, final head `f4465d6`; later exact-rescale correction #169 retained | Semantics, tests | Medium | reviewed ([reviews/2026-10-07-codex-recheck-units.md](../reviews/2026-10-07-codex-recheck-units.md)); bounded Claude-authored scope |
| #179 | programme | Shared `common/safe_xml.py` DTD guard (fails closed), Stats NZ SDMX DTD refusal, response-size cap (D20), Bandit MEDIUM gate; squash `eacc5a2`, final head `527dbb7`; Claude commits `d88daa4`/`e8af4b3`/`bb19ef8`/`41ce431` | Data reader, acquisition, CI | High | open — merged on same-model `poltika-reviewer` passes (no P1/P2) and `/security-review`; Pete chose not to wait for a Codex security pass (not rule 4). Awaits Codex recheck of `527dbb7` |
| #181 | programme | Integration-train follow-ups: review wording, `pr-review` skill, review-rule entry-point test, household id `\Z`, model-card policy versions, FastAPI telemetry, #162 R1 and #177 R1 fixes; Claude-authored | Docs, skills, semantics, assurance cards, API, acceptance tests | Medium | open — awaits Codex recheck of its final head |
| #182 | programme | Self-hosted Mac CI runner (D21): `runs-on: [self-hosted, poltika]`, `pilot-image` hosted only on image-input changes; squash `dd2c485`, final head `342d469`; Claude-authored (Pete's local session) | CI workflows, decision log | Medium | open — merged on same-model `poltika-reviewer` passes (no P1/P2; P3s deferred to a follow-up) and author preflight. Awaits Codex recheck of `342d469` |
| #162 | programme | Mechanical never-build checks; squash `5a8c17e`, final head `e637daa` | Acceptance tests | Low | open — R1 P2 TEST_ERROR: unrelated negation masks a prohibited milestone claim; [finding](../reviews/2026-10-07-codex-recheck-never-build.md). Fix in #181 (Claude-authored): negation bound to its clause. Awaits Codex recheck of #181's final head |
| #132 | pilot | Hosted hardening: security headers, body and request limits, cache admission, declined-label validation and CI smoke check | API, CI | Medium | reviewed (reviews/2026-10-02-pr132.md) |
| #133 | workbench | Analyst workbench backend (ADR-0018, proposed): `api/workbench*.py` registry, check, tabbed results, xlsx/csv export; `scenarios/microsim/worked_examples.py`; `execute_reform` extracted in `api/microsim.py`; `openpyxl`. Author preflight: `review_packets/workbench_backend_preflight.md` | API, microsim | Medium | reviewed (`reviews/2026-10-02-pr133.md`) |
| #128 | v0.3 | Tasks 1b.2d, 1b.1c: `scenarios/conditional_text.py` verified summary, `resolution.summary`, v0.3 release-gate test | Scenarios, API, tests | Medium | reviewed (reviews/2026-10-03-pr128.md); #150 fixes independently Claude-reviewed and accepted/merged at 3bea73f |
| #127 | v0.3 | Task 1b.6: `scenarios/microsim/ranges.py` population ranges; `fiscal_ranges` on `/microsim/runs`; Fiscal tab | Microsim, API | Medium | reviewed (reviews/2026-09-28-pr122-127.md) |
| #126 | v0.3 | Tasks 1b.2b, 1b.3b-1b.3d: `FactEntry.monotone`, `resolve(ranges=...)`, `Bounds.kind`; property tests | Scenarios, fact schema, API | Medium | reviewed (reviews/2026-09-28-pr122-127.md) |
| #125 | v0.3 | Task 1b.5: `resolution` on `/household/calculate`, stateless `POST /household/intake`, the analyst page's "Ask me first" | API, analyst page | Medium | reviewed (reviews/2026-09-28-pr122-127.md) |
| #124 | pilot | Hosted pilot: `api/access.py` HTTP Basic password (fail-closed in the image), `/healthz`, `$PORT`, built-in population, CI smoke test | API middleware, deploy | Medium | reviewed (reviews/2026-09-28-pr122-127.md) |
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
| #187 | programme | Task B0.1.2: durable reform scenarios and the web workspace view (which stored amounts appear, in which units, and how not-calculated values read) | API, scenarios store, migration 0002 | Medium | reviewed ([reviews/2026-10-08-pr187.md](../reviews/2026-10-08-pr187.md)); Claude-authored `278ef3d` reviewed by Codex, Codex fixes independently Claude-reviewed through implementation head `199ba20`; no unresolved P1/P2. Final-head CI remains required |
| #211 (boundary proposal only) | programme | Six WFF and AS boundary cases proposed by Claude Code ([proposal](wff_as_boundary_cases_proposal.md)); proposal only | `review_packets/` only | Low | independently reviewed — [Codex review](../reviews/2026-10-12-wff-as-boundary-proposal-codex.md), #211 head `f7313bedb52c747433b86daf2b5d72b6a7e44f5e`, baseline `1c19f64`: conditional arithmetic supported; B1–B3 P3 documentation/input caveats; B4 P2 INTERPRETATION_AMBIGUITY decided by Pete 13 October 2026: complete $100 steps (AS DEC-004, D38). No protected values or tests promoted; this row clears the owed proposal review, not any interpretation or protected-value gate |
| #207 | programme | Task 5 unit binding and Task 6 household mappings (ADR-0017 1.1–1.3); Claude Code authored; merged as `cbc4f380` | `src/poltika/semantics`, `src/poltika/scenarios/household_mappings.py`, tests | Medium | independently reviewed — **not cleared**: GPT/Codex [mapping review](../reviews/2026-10-12-task5-6-mapping-codex.md), final PR head `77ffc71f964060ee9c9a0fb5b8400ca0f53d539d`, baseline `1c19f64`; **MAP-01 P2 CODE_ERROR** (partial-week contradictory benefit spell ignored); fix in #216, awaiting Codex recheck of its final head. 218 focused tests passed; fixtures unchanged. [Q19 (1), (2), (5) research](../docs/research/q19_household_mapping_readings.md) awaits Pete; no interpretation or amount accepted |

**13 October 2026 update:** #215 merged as `de76f26` after Claude's cross-model review ([comment](https://github.com/hemmingsenpeter-byte/poltika/pull/215#issuecomment-6126446079)); MAP-01's fix is in #216, awaiting its Codex recheck; B4 is decided (AS DEC-004, D38).

**12 October 2026 targeted update:** #207 is merged and its Codex review is complete but not cleared (MAP-01 P2); #211's proposal-only review is complete, with B4's interpretation gate retained. The earlier 7 October count is a historical closeout snapshot, not a recount of these later scopes.

## Open PRs awaiting pre-merge review (not merged review debt)

| PR | Release | Scope | Touches | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| [#216](https://github.com/hemmingsenpeter-byte/poltika/pull/216) | programme | MAP-01 fix (overlapping benefit spells); Q19 (5) main-benefit date check in `to_wff`; Q19 (1), (2) wording and `NZD` binding; AS DEC-004 (B4); Pete's 13 October records | `src/poltika/semantics`, `src/poltika/scenarios/household_mappings.py`, tests, `policy_specs/accommodation_supplement/decisions/`, records | Medium | open — **GPT/Codex review required before merge** (changes which route a directly built household takes; rechecks MAP-01 for #207's row). Claude author preflight with two fresh same-model passes: no P1/P2 ([packet](map01_q19_preflight.md)). No calculated amount, protected value or fixture changes |

## Plan and decision PRs (not counted against the cap)

| PR | Scope | Status |
| --- | --- | --- |
| #90 | v0.1.6 and v0.2 plans; ADR-0014 | Pete accepted; independent review optional |
| #101 | ADR-0015, `ROADMAP_REALIGNMENT.md`, v0.3 plan | Pete accepted; independent review optional |

## Recorded deferrals (not review debt)

| From | Item | Why deferred | Picked up by |
| --- | --- | --- | --- |
| #151 R1 P3 | A schema for `coverage_limits` (`reviews/2026-10-06-pr151.md`) | Only one test reads the key; a schema belongs with its first consumer | The first benefit specification that consumes `coverage_limits` |
| #167 | Preflight hashes recorded in #167's records | They name heads superseded by #167's three conflicted integrations; they are kept as historical evidence and not recomputed | None: labelled historical; later heads carry their own final-head reviews |
| #154 (closed, D22) | Codex recheck of the Claude-authored test commits `ff28a9b`/`0b3f2aa`/`5a45719`; P3 R3 (control characters break the chart SVG; a lone surrogate raises `UnicodeEncodeError`) and R4 (standalone population tables carry no synthetic label) | #154 was closed unmerged and parked for Phase F Task 24 (D22), so it is not merged review debt | Task 24, if the branch `codex/reporting-review-fixes` is revived |
