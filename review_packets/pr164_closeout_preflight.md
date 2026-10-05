# PR #164 closeout: author preflight

Date: 5 October 2026. Corrective author: GPT/Codex. This is not independent
approval of Codex's corrections. Original independent review and acceptance
choices: `reviews/2026-10-05-pr164.md`. Exact final SHA and fresh Claude reviewer
result are attached to the PR after the final integration commit.

Inputs: model-governance doctrine, accepted epistemic constitution,
ADR-0020/0021, registry/card files, linked approved spec/benchmark cases,
release limitations, and corresponding simulator/composition/microsim code.

Using `PYTHONPATH=src` with the existing development environment, the focused
106-test run passed registry/cards, WFF/AS spec and benchmarks, interaction and
golden households, frozen results, and both independent/author population
arithmetic cases. Ruff: all checks passed. Strict mypy: no issues in 82 source
files. An additional direct negative async-discovery test was added after that
run; the complete 10-test registry suite passed.

Adversarial cases: absent engine and absent package fail; async unregistered
entry point fails; missing/stale/orphan cards fail; lowered dependency grade
propagates to the population label. Paths and declared case counts were checked.
Cards were regenerated from the accepted registry, then checked for currency.
No calculated amount, protected expected value or statistical source changed.

Exact pushed-tree preflight at `97365245de8b96d34553a516b419f4d51d7bc8b5`
in separate detached checkout `/private/tmp/poltika-pr164-closeout-preflight`:
10 registry tests passed, generated-card `--check` passed, ruff passed,
strict mypy reported no issues in 82 source files, and base-to-head whitespace
checks passed. Later phase-reference commits regenerated the affected card
and passed the 10-test registry suite again; final-head CI/review is required.

The duplicate local default-suite run was stopped with SIGTERM (exit 143)
to preserve the one-hour budget; partial progress showed no failure but is not
claimed as a pass. The required GitHub CI full suite is the merge gate. The
registry proves coverage of the stated discovery convention and current card
currency, not source truth or empirical national accuracy. Package versions are
labelled as such. Runtime output labels and diff/change-record correlation
remain deferred and are not reported as implemented.

## 6 October 2026 card-fix preflight

Corrective author: GPT/Codex. The existing PR rationale and earlier review
were known before this pass; this is author preflight, not independent review.
Integration base: `240da13838857ee0b2e1686a2fba6f7c8b0b4adc`.

Findings recorded before the final correction:

| Finding | Proposed class | Severity | Disposition |
| --- | --- | --- | --- |
| YAML treated the unquoted `#14` and `#21` as comments, truncating the WFF change-log evidence in generated cards. | SPEC_ERROR | P3 | Quote both source strings and regenerate the cards (`1d25960`). |
| Combined-runner validation did not identify which reviewer checked each set. | SPEC_ERROR | P3 | State Claude checked all five interaction cases and nine golden households, while Codex checked all five interaction cases and g2/g5/g6/g7/g9; verified against both linked handoff packets (`1d25960`). |
| The combined card said a contradiction makes every component `needs_review`, omitting preserved `unsupported` outcomes. | SPEC_ERROR | P2 | Match `combined.py`'s documented precedence and existing contradiction tests; regenerate the card. |

Actual commands/results after the card fixes and integration refresh:

- `PYTHONPATH=src .venv/bin/python -m poltika.engines.assurance.model_cards`: exit 0; regenerated cards.
- The same command with `--check`: exit 0; all four cards current.
- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/engines/assurance/test_model_registry.py tests/unit/scenarios/test_combined.py tests/unit/scenarios/test_interaction_spec_cases.py -p no:cacheprovider`: 36 passed, no skips, exit 0.
- `.venv/bin/ruff check src tests`: all checks passed, exit 0.
- Direct YAML count checks: WFF 23 spec/9 benchmark, AS 26 spec/4 benchmark, interaction 5 and golden households 9; all match. Both WFF PR references survive YAML loading.
- `git diff origin/main...HEAD --check` and working diff checks: exit 0.

No engine, policy specification, protected expected value or statistical source
changes in this follow-up. National empirical validation and runtime labels
remain explicitly pending. Required CI and a fresh Claude `poltika-reviewer`
pass must cover the final pushed head; their results are recorded in the PR.
