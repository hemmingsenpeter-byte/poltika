# ADR-0016: Intake questions and conditional answers for missing facts

**Date:** 26 September 2026
**Status:** proposed. Drafted by Claude Code from Pete's request of
26 September 2026, for Pete's decision (`BUILD_PLAN_v0_3.md` D5).

## Context

Today a component whose fact is unknown returns `needs_review` with its
`missing_facts` (v0.1.5 Task 4.4), and no amount. That is honest, but not
useful. The user learns only that something is missing, not which
question matters, and not what the answer would be either way.

Pete asked for two things:

1. **Ask follow-up questions before running.** Work out what the question
   needs, and ask for it first.
2. **When something is still missing, don't stop at `needs_review`.**
   Say what is missing and give the most complete answer possible
   without it.

Both must keep the rules that make Poltika trustworthy:

- a missing fact is never zero or a default (CLAUDE.md, SCHEMA.md);
- the deterministic engine is the only thing that calculates
  (`doctrine/llm_boundaries.md`);
- a result is never presented as more certain than it is.

## Decision

If accepted, three pieces are added. All three sit *around* the engines,
which don't change. Every number still comes from an ordinary engine run.

### 1. Fact catalogue (per policy)

`policy_specs/<policy>/facts.yaml` holds one entry per input fact, keyed
by the same id the engine already puts in `missing_facts`
(`claimant_category`, `children.best_start_cohort`, and so on). It sits
outside `policy.yaml`, so wording changes never touch a protected,
hash-bound file.

| Field | Meaning |
| --- | --- |
| `id` | The `missing_facts` id |
| `question` | Plain-language question, reviewed like any specification text |
| `domain` | Admissible values: the engine's enum members, `verified`/`excluded`, or a number with unit and a valid range |
| `rule` | The specification rule id that makes this fact matter |
| `monotone` | Optional, per component: `increasing` or `decreasing` in this fact, with the rule id that implies it. Enforced by a property test. |

A test fails if an engine can emit a `missing_facts` id that has no
catalogue entry, or if an entry's `domain` doesn't match the engine's
input type.

### 2. Intake: questions before the run

A deterministic question planner (`scenarios/intake.py`):

1. takes the facts supplied so far and the question asked (which
   policies, or components);
2. runs the engine and collects every `missing_facts` id that blocks the
   asked components;
3. ranks the missing facts by **impact**: rerun the engine once per
   admissible value of each fact (section 3), and measure how far the
   asked result can move. Facts that decide eligibility, or move the
   amount most, come first. Ties go by specification rule order;
4. returns the next question from the catalogue, with its admissible
   answers.

The caller answers and the planner runs again. It stops when nothing that
blocks the asked components is missing, or when the user says "don't
know" or "skip".

- "Don't know" is recorded explicitly (`unknown`, asked and declined),
  which is different from never asked.
- An answer is the caller's assertion, exactly as today's API treats every
  `verified` input.

An LLM front end may phrase the catalogue question conversationally and
map a free-text reply onto one of the admissible values. It must confirm
any mapping that isn't exact, and it never chooses a value itself or
skips a question on the user's behalf (`doctrine/llm_boundaries.md`,
ROADMAP v0.7). The planner, not the LLM, decides what to ask.

### 3. Conditional answers: what can be said without the missing facts

When facts are still missing, the response keeps each blocked
component's `needs_review` outcome and adds a `resolution` block. The
tri-state contract is unchanged, and nothing conditional is ever labelled
`calculated`.

- **`known`:** the components calculated regardless (as today).
- **`missing`:** each unresolved fact, with its catalogue question, its
  admissible values, the components it blocks, and its impact.
- **`branches`** (finite domains): the household rerun through the engine
  once per admissible assignment of the missing facts. Each branch
  records its assignment, every component's outcome and value, and its
  own verified explanation.
  - For example: "If a main benefit is received: family tax credit
    $X, in-work tax credit not available. If not: family tax credit $X,
    in-work tax credit $Y."
  - Assignments are joint: one assignment is applied to every component
    at once, so a total is only ever summed within one assignment.
  - Branches are capped (proposed: 32). Past the cap, Poltika branches on
    the highest-impact facts and lists the rest as unresolved.
- **`bounds`:**
  - When every branch is calculated: the minimum and maximum of each
    component and of each total ("between $A and $B").
  - When some branch is `unsupported` or `needs_review`: the calculated
    branches' range, plus the branches it excludes ("$A to $B if
    eligible; not calculable if …"). It is never folded into a single
    number.
- **Numeric unknowns** (income, costs, assets) have no finite branches.
  The caller may give a range.
  - Where the catalogue declares the component monotone in that fact,
    the range endpoints are evaluated and are true bounds (enforced by a
    property test).
  - Otherwise Poltika evaluates chosen points only, labelled "values at
    these points, not bounds".
  - With no range, the fact is listed as missing with no branch.
- **Unresolved parameters** (a rate that is itself `needs_review`, such
  as the 2026-27 in-work base) branch only over candidate values the
  specification records (the rate-status contract), each labelled a
  scenario assumption. Nothing is invented.
- **`next_question`:** the single missing fact whose answer would narrow
  the range most.

The plain-language rendering always says the answer is conditional:
"Poltika can't give one figure without X. If X is …, the result is …".

### Population runs

The microsimulation can use `bounds` per household, and report fiscal
cost as:

- the calculated total;
- the range contributed by `needs_review` households (low and high);
- the weight still unboundable.

That replaces leaving them out entirely. The calculated total and the
range are always reported separately and never added together.

## Consequences

- **Every branch equals a real run.** A differential test checks that
  each branch's results equal an ordinary engine run with that fact
  supplied. That makes conditional answers exactly as trustworthy as
  calculated ones, for their stated assumption.
- **No new policy logic.** Branching, bounds and ranking only rerun the
  engines. Monotonicity is a declared property with a rule id, and a test
  checks it holds.
- **New policies build their catalogue from the start.** `facts.yaml` is
  part of PR 2 in `.claude/skills/new-policy/SKILL.md`, and question
  wording is reviewed with the specification.
- **Cost.** A household with k unresolved finite facts needs up to the
  product of their domain sizes in reruns, which is why branches are
  capped. Intake ranking costs one rerun per admissible value per missing
  fact. At the measured 1-4 ms per run (`docs/releases/V0_2_SCALING_MODEL.md`)
  that is well under a second for a single household. For population
  runs, the bounds are computed only for `needs_review` households.
- **The API grows.**
  - `resolution` is added to calculation responses.
  - An intake route is added (`POST /household/intake`, returning the
    next question or "ready").
  - The analyst page shows questions first, then branches and ranges.
