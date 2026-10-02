# ADR-0018: The analyst workbench is driven by the specs, and shows generic blocks

**Date:** 28 September 2026
**Status:** proposed. Drafted by Claude Code from Pete's front-end brief of
28 September 2026; for Pete's acceptance.

## Context

Pete asked for a professional costing front end for WFF and the
Accommodation Supplement that can take new instruments later without being
redesigned, and whose numbers all trace to a run ID. The repo already has
the pieces: parameter files with sources (`policy_specs/`), population runs
with run IDs (`/microsim`), and household examples. It has no way for a page
to learn which instruments and parameters exist, and its two pages each carry
their own knowledge of WFF and AS.

## Decision

1. **The registry is read from the specs.** `GET /workbench/registry` scans
   the specs directory. Each directory with a `policy.yaml` is an instrument;
   its parameters, units, dated values, review status, sources
   (`sources.yaml`) and decisions (`decisions/`) are returned as written. An
   instrument is *runnable* only if the engines model it
   (`reform.MODELLED_POLICIES`), and otherwise is listed read-only. A broken
   spec is reported and hides nothing.
2. **Results are generic blocks.** `POST /workbench/results` returns tables,
   a fiscal-year strip and lists per tab. A page renders blocks and knows no
   instrument. The Excel and CSV exports are written from the same blocks, so
   the totals on screen and in the file are the same strings.
3. **Presentation config is separate from policy.** `workbench_config.py`
   holds tabs (with deferred slots), fiscal-year slots, measures, family
   types (golden household ids), and winner/loser thresholds. It holds no
   statutory value.
4. **No new arithmetic across units.** Amounts stay in their own unit (WFF
   per tax year, AS per week) and are never added or converted. There is no
   total row: the in-work tax credit is `needs_review`, so there is no WFF
   total, and WFF and AS are never added. A component that was not calculated
   shows `not calculated` or its outcome, never zero.
5. **Only 2026-27 is modelled.** Later fiscal years are labelled slots, not
   estimates, until their parameters exist in `policy_specs/`.
6. **Runs are kept in memory** (as `/microsim/runs` already does). An export
   or permalink names a run ID, and a run gone after a restart is rerun from
   its reform, which reproduces the same ID.

## Consequences

- Adding an instrument is adding a spec directory. It appears in the
  registry with no code change; making it runnable is engine work.
- An output tab is a builder in `workbench_tables.py` plus a `TABS` entry.
- The winner/loser thresholds are presentation settings, one per unit; $52 a
  tax year is $1 a week only because the config says so.
- Population runs take seconds on a laptop and will be slower on a small
  hosted instance; results are not cached beyond the run store.
- A natural-language front end is a separate decision. It would sit in front
  of these routes and stay inside `doctrine/llm_boundaries.md` and ADR-0016:
  it translates a question into a request, asks the planner's questions, and
  explains an engine result, and never produces a number.
