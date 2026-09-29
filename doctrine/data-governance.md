# Data governance

**Interim, from 29 September 2026** (`BUILD_PLAN_PROGRAMME.md` Step 1.4,
decision P5). The constraints Poltika must meet are still being sourced
and settled with the people who have standing to settle them. Until then,
the interim rules below hold.

## Rule

Māori data governance, privacy, confidentiality and Te Tiriti
considerations constrain Poltika's architecture from the start. They are
not an approval sought just before launch. A capability that can't meet
them isn't built.

## In force now

1. **No output disaggregated by ethnicity or iwi** until the governance
   process is agreed (P5). No population schema, analysis table, API
   response or page groups or filters results that way. A test enforces
   it (Step 1.4).
2. **No household-level record leaves a secure environment.** Unit
   records are never committed to this repository. The secure-environment
   runner exports only checked aggregates (`BUILD_PLAN_v0_3.md` Phase 6,
   `ROADMAP_REALIGNMENT.md` W3.3).
3. **Confidentiality rules come from their publisher.** Output checks
   such as minimum cell counts, rounding and dominance apply Stats NZ's
   published rules, each cited. A threshold is never a default
   (W3.1, W3.4).
4. **No caller chooses a population.** The API reads only the population
   an operator sets, and refuses a request that names one (v0.2 Task
   10.1).
5. **People decide.** Objectives, interpretations of law, and promoting
   any claim into a model are human decisions
   (`doctrine/epistemic-constitution.md`).

## To be established (Step 1.4)

- **GPT/Codex** records, from the documents themselves, with locators:
  - the commitments of the Algorithm Charter for Aotearoa New Zealand,
    including its Partnership commitment and what it says about Māori
    data sovereignty;
  - the Privacy Act 2020's information privacy principles that apply to
    Poltika's inputs and outputs;
  - Stats NZ's microdata and IDI access and output rules (with W3.1);
  - published Māori data governance frameworks.
- **Pete** engages people with standing in Māori data governance, and
  agrees with them:
  - who decides about Māori data, and about outputs that describe Māori;
  - which disaggregations need that decision;
  - how Poltika's governance is reviewed over time.

Each constraint then replaces or extends the interim rules above, with
its source. This document then stops being interim.

## Applies to

`src/poltika/semantics/population.py`, `src/poltika/scenarios/microsim/`,
the secure-environment runner and its exports, `src/poltika/api/`, and
every published table, forecast or report.
