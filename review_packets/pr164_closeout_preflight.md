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
