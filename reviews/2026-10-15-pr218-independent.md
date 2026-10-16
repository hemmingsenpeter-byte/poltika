# PR #218 independent GPT/Codex recheck — 15 October 2026

## Findings and clearance

No new blocking finding or unresolved source interpretation was identified at reviewed head `f1c106a5ea48b40ca0cb87c553ef76df652d74f3`. Previous R1–R5 are verified fixed. This is independent review evidence for that exact Claude-authored head, not acceptance, a merge, approval of new statutory values, or clearance of a later integration head.

Merge clearance remains pending: GitHub reported `CONFLICTING` / `DIRTY`; the rebased final head has not been supplied on the PR. The current integration candidate `354aa8a` is unpublished and is not treated as final. A final-head author preflight, fresh-context reviewer, cross-model recheck, current-main reconciliation and green CI remain the coordinator's gates. The reviewer edited no implementation or protected files and posted no GitHub comment.

## Review inputs and provenance

- PR: <https://github.com/hemmingsenpeter-byte/poltika/pull/218>.
- Reviewed head: `f1c106a5ea48b40ca0cb87c553ef76df652d74f3`.
- Planning/current fetched main: `63359fecfe3b6659476528da021ea0ade0023537`.
- Actual fork point: `7342e528ad67b58984de5711ba2d195bdef97c67`; `git merge-base HEAD 63359fec...` confirms it. GitHub's baseRefOid also reported `7342e528...`, which is not evidence that main has remained there.
- Full review diff: `git diff 7342e528...HEAD`; 12 files, 896 insertions, 13 deletions, eight Claude-trailed commits. All changed production, tests, registry/card, plan, decision and review files were read, together with relevant callers and regression tests.
- Isolated worktree: `/private/tmp/poltika-pr218-independent-20261015`. It is separate from the author's and earlier Codex worktrees.
- Applied `pr-review` and NZ primary-source-check guidance, repository AGENTS/CLAUDE, programme Phase B and detailed Task 1.4, ADR-0017/0020, epistemic/test/review/IP/model-governance doctrine, WFF/AS source maps/specifications, D32/D36–D40 and Q19 records.
- Expected mapping contract was written to `/private/tmp/pr218-contract.txt` before reading the implementation diff, author preflight or GitHub review history. The accepted decision log was necessarily read as authority. This pass was not blind to the task's requested topics.

## Independently derived expected behaviour

1. ADR-0017 holds one family and each caller-resolved fact once; named mappings retain policy-specific definitions and unknowns. Existing requests, results and IDs remain reproducible. A pair check retires only when its contradiction is impossible.
2. WFF's accepted slice requires stable whole-year relationship/care and separately resolved WFF child facts. AS aggregate child counts cannot establish identities. D38 Q19(2) authorizes synthetic first-N adapter markers only as an aggregate round-trip device. Consequently their count-disagreement gate stays, including after serialization; explicit per-child assertions may instead explain a definitional difference.
3. A claimant or partner JS/SPS/SLP spell with any overlap in the WFF year contradicts verified whole-year in-work/MC6(b) absence assertions (D38 Q19(5)). An interval ending exactly at the year start, or beginning exactly at its end, does not overlap. No apportionment follows.
4. D40 accepts the conservative protected-month guard over either adult's main-benefit spell anywhere in the year. MC6(b) speaks of the person, MD8 includes their partner, and MD14/MG4 require benefit receipt plus monthly income conditions: the guard withholds results rather than determining protected entitlement from a spell alone.
5. A person's overlapping benefit statuses, including duplicate same-kind and NO_BENEFIT alongside benefit, are rejected (MAP-01/D37). The AS mapper must not select a covering status beside another receipt. Adjacent mid-week statuses leave the weekly category unknown; no mid-week rule is invented.
6. Income spells must tile the exact native period. Straddling amounts are refused; gaps are unknown. AS assets remain a caller-asserted stock for the week. There is no weekly/annual scaling, automatic gross/net conversion, or WFF/AS sum.
7. D40 accepts changed-relationship refusal of the whole household before a carried unknown claimant link or incomplete child list, with unknown relationship fact leaving existing WFF eligibility gates intact. Carried unknown/excluded links are honored. The tax year must match the policy before any refusal can hide it.
8. Existing pair calls keep default checks. Retained contradictions preserve original results and traces, and unsupported outranks needs_review. IWTC remains gated; there is no WFF total.

### Dated primary source checks

Retrieved independently on **15 October 2026**, first using web tools (some legislation endpoints inaccessible), then official HTML with a browser user agent via `urllib.request`. These checks verify the mapping semantics; they are not a new whole-year rate/Order audit or approval of expected amounts.

| Source and exact version | Locator | What independently checked |
| --- | --- | --- |
| [Income Tax Act, 1 April 2026, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-04-01/parts/DLM1518405/), also [4 September 2026, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1518405/) | MC6(b), MD8, MD14(1)–(2), MG4(1)–(2) | MC6(b) main-benefit exclusion is person/relationship-period specific; MD8 includes spouse/partner; protected credits depend on calendar month, receipt and family-scheme income, annualised under MB2. The clauses agree across fetched versions. |
| [Social Security Act, 1 April 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-04-01/), also [4 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/) | Schedule 4 Part 7 cl7; Schedule 2 context | AS dependent-child exclusion for orphan/unsupported-child benefit is explicit and distinct from WFF's qualification inputs. No first-N identity rule is provided. |
| [Social Security Regulations, 2 March 2026](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-03-02/) | rr17(1), 18(1)–(2A) | Being paid a main benefit determines beneficiary category; r18 non-beneficiary reduction must not be chosen after dropping a conflicting part-week receipt. |
| [IRD in-work guidance](https://www.ird.govt.nz/working-for-families/types/in-work-tax-credit) | Government payments; How the in-work tax credit works; changing family situation; full-year entitlement wording | Agency guidance independently distinguishes work weeks/full-year entitlement and changing family circumstances. It does not authorize the adapter's synthetic child identity or ungate future-year IWTC. |
| [MSD Accommodation Supplement](https://www.workandincome.govt.nz/products/a-z-benefits/accommodation-supplement.html), page updated 24 July 2026 | Who can get it; How much you can get; changes in circumstances | Weekly payment with partner income/assets and family circumstances; supports keeping the assessment period and household facts explicit. |

The authoritative statuses stay unchanged: accepted existing mapping decisions govern these boundaries; candidate or unresolved policy amounts are not promoted. Every expected status in the additional probe is source/spec/decision-derived. No new statutory expected amount was created and no simulator output was adopted as an expected value.

## Prior findings and author response

Existing PR review summaries, inline comments and replies were read after deriving the contract and inspecting code. The author reports fixes in `7251a4c` (rebased as `ac72872`) for R1–R4 and `f1c106a` for R5. Independently verified:

| ID | Prior class/severity | Current disposition |
| --- | --- | --- |
| R1 | P2 CODE_ERROR | Fixed: `Family.as_child_statuses_from_count` survives adapter serialization; aggregate origin retains gate, explicit per-child statuses report difference. |
| R2 | P2 CODE_ERROR | Fixed: `run_household` is registered as a `combined_runner` wrapper, test link and purpose updated. |
| R3 and #216 P3 | P3 CODE_ERROR | Fixed: canonical ordering controls both protected-credit diagnostics and Q19(5) refusal. |
| R4 | P3 CODE_ERROR | Fixed: message counts WFF list entries and separately verified whole-year qualification; unknown qualification stays gated. |
| R5 | P2 ARCHITECTURE_ISSUE | Fixed: model-specific change log records contract, rationale, decisions, evidence, validation and approval; generated card matches. |

No new blocking CODE_ERROR, TEST_ERROR, SPEC_ERROR, SOURCE_CONFLICT, INTERPRETATION_AMBIGUITY, MISSING_SOURCE or ARCHITECTURE_ISSUE is proposed. An inherited diagnostic observation is recorded below.

## Inherited nonblocking observation (P3, proposed CODE_ERROR)

`src/poltika/scenarios/household_mappings.py:150` still selects the first straddling **income** spell in input tuple order. This loop predates #218: base blame attributes it to `cbc4f380` on 11 October 2026. The new wrapper forwards the old mapping refusal at line 606. Two adults' WFF family-scheme income spells, claimant `[2026-03-31, 2027-04-01)` and partner `[2026-03-30, 2027-04-01)`, both with total 100, can be reversed without changing `Household.content_sha256()`. `to_wff` and the new `run_household` then return different refusal reason strings (one names 31 March, the other 30 March). Both retain `needs_review` / `HOUSEHOLD_SPELL_PERIOD_MISMATCH`; no amount is calculated or converted. This is the same diagnostic determinism issue family as prior R3, inherited on a separate path. It is not proposed as a #218 merge blocker. Suggested bounded follow-up: choose income evidence in a stable order and cover this reproduction; preserve the refusal and existing statutory gates.

Reproduced on the reviewed SHA with `PYTHONPATH=src:. .venv/bin/python reviews/2026-10-15-pr218-income-order-probe.py`. Both hashes are `38bd9d6fc61ce98e2b352f263ed1ecd712c221efbcfa52823fe4a5480a1e0f2d`; `Equal to_wff refusal: False`, `Equal run_household refusal: False`. Canonical refusal JSON differs only at the named income start date, 31 March versus 30 March. Both have `missing_facts: []`. No source interpretation is implicated.

Impact boundary: this violates diagnostic consistency under the canonical Household identity. No present stored-run/replay corruption route was found: `ScenarioRecord.household` is `CombinedHouseholdScenario` (`record.py:70`), and `run_scenario` calls the unchanged pair runner. `Household.content_sha256()` has no current production consumer outside its definition; current `run_household` has no API caller. The returned `MappingRefusal` has neither a trace nor a result ID. Existing `result_payload` does include component reasons and hashes them into result IDs (`record.py:146,207`), but accepts `CombinedResult`, not `MappingRefusal`; that path is not reached here. The suggested P3 severity is therefore specific to this demonstrated current diagnostic path, not a claim that reason nondeterminism is always harmless.

## Verification

Commands executed from the isolated worktree; `UV_CACHE_DIR=/private/tmp/poltika-pr218-uv-cache` avoids the sandbox's inaccessible default cache. The first non-escalated dependency installation failed on network DNS; approved network-enabled `uv sync --locked --extra dev` then succeeded. This was an environment retry, not a product finding.

| Exact command (with cache prefix where used) | Result |
| --- | --- |
| `uv sync --locked --extra dev` | Passed: locked environment installed. |
| `uv run --extra dev ruff check src tests` | Passed. |
| `uv run --extra dev mypy --strict src` | Passed: no issues in 107 source files. |
| `uv run --extra dev python -m poltika.engines.assurance.evidence policy_specs/working_for_families policy_specs/accommodation_supplement` | Passed; WFF 10 parameters / 9 approved, AS 38 / 38 approved; no problems. |
| `uv run --extra dev pytest -q -rs` | Interrupted at coordinator request after 690.57s: 81 passed, 1 skipped (no external pilot user recorded), 2 deselected, no failure printed before Ctrl-C; exit 130. This is not a full-suite pass. |
| `uv run --extra dev python -m poltika.engines.assurance.model_cards --check` | Passed. |
| `git diff --check 7342e528...HEAD` | Passed. |
| `PYTHONPATH=src:. .venv/bin/python -m pytest -q /private/tmp/test_pr218_independent.py` | **116 passed** in 129.34s. Three pytest deprecation warnings relate solely to iterator parametrization in this independent scratch probe. Reproducible artifact: `reviews/2026-10-15-pr218-probes.py`. |

Focused regression command completed successfully on the unchanged reviewed head:

```sh
UV_CACHE_DIR=/private/tmp/poltika-pr218-uv-cache uv run --extra dev pytest -q -rs tests/unit/scenarios/test_household_run.py tests/unit/scenarios/test_household_roundtrip.py tests/unit/scenarios/test_combined.py tests/unit/scenarios/test_interaction_spec_cases.py tests/unit/scenarios/test_golden_households.py tests/unit/semantics tests/regression/test_household_mapping_review_findings.py tests/regression/test_golden_result_snapshot.py tests/regression/test_golden_trace_snapshot.py tests/regression/test_wff_as_interaction_leaks.py tests/unit/engines/assurance/test_model_registry.py
```

Result: **290 passed in 174.57s**, exit 0, no skips. This covers household/run/adapter/period semantics, legacy scenario/result-ID round trips, protected golden outputs/traces, interaction specifications and MAP-01 regression, plus registry discovery and card contracts. It is separate from the interrupted broad run and does not claim full local CI replication. Installed-artifact/code-replay/PostgreSQL and web/security checks rely on the existing successful exact-head CI rather than being rerun locally in this bounded review.

Additional adversarial coverage: 36 combinations of main-benefit kind, claimant/partner and exclusive year edges; all 36 pairs of overlapping benefit statuses (normal validation and defensive mapper); all 36 adjacent two-status pairs; four relationship/link precedence states; both serialized child-status origins; both AS income-straddling directions.

Test sensitivity used runtime-only monkeypatches, without editing implementation files. Script: `reviews/2026-10-15-pr218-test-bite.py`. Commands were `PYTHONPATH=src:. .venv/bin/python /private/tmp/pr218_mutation_check.py <mode>`:

| Mode | Deliberately removed behaviour | Expected failure observed |
| --- | --- | --- |
| `relationship` | Relationship-change refusal | 1 failed: relationship case no longer refused. |
| `child_origin` | Count-derived child contradiction | 1 failed: missing count disagreement. |
| `canonical_order` | Canonical spell ordering | 2 failed: equivalent household hashes produced different diagnostics/refusals. |
| `protected_month` | Protected-credit main-benefit flags | 2 failed: both protected-month guard tests detected absent contradiction. |

These six intentional failures establish test sensitivity; they are not failures on the unmodified reviewed head. No monkeypatch persists between commands.

### Live and integration limitations

Observed PR checks at `f1c106a`: test, web, image-inputs, pilot-image, immutable-snapshot guard, link check, pip-audit, source-currency, Bandit, statutory path guard, npm audit and zizmor completed successfully. Fork-blocked, external-links/report-only and issue publishing were skipped by their workflow conditions. One non-check status entry has no status/conclusion. GitHub still reports conflicting branch.

The unpublished `354aa8a` candidate was inspected read-only: changed implementation files, new tests and registry/card are byte-identical to `f1c106a`; its PR diff against `63359fec` has the same 12-file statistics. This comparison is supporting evidence only; it does not substitute for final-head review or CI and has not cleared that candidate.

Remaining source/decision gate: no new one found for this bounded mapping change; existing IWTC, tax, benefit, interaction and disposable-income gates remain unchanged. Next work item: Claude resolves/publishes the final integration head, then renew exact-head checks and final review evidence. No merge recommendation is made while that head is unavailable.
