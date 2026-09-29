# ADR-0017: Shared household model

**Date:** 27 September 2026
**Status:** accepted. Pete approved it on 29 September 2026 with the
three recommended answers below ("Approve and proceed all",
`BUILD_PLAN_PROGRAMME.md` Decisions). v0.3 Phase 1, `ROADMAP_REALIGNMENT.md`
W6. Drafted by Claude Code.

## Context

Each policy takes its own input type: `WffScenario` and `AsScenario`,
combined in `CombinedHouseholdScenario` (`scenarios/combined.py`). A fact
the two share is held twice and cross-checked pair by pair
(`shared_fact_contradictions`, Task 28.3):

- partner status (WFF `PartnerStatus`, AS `PartnerType` and the
  mixed-benefit category);
- the number of dependent children (the WFF child list, AS
  `dependent_children_count`);
- main-benefit receipt (the AS claimant category against four WFF
  exclusion facts);
- the claimant link (`as_claimant_is_wff_claimant_or_partner`);
- the AS week inside the WFF year.

Income tax and three main benefits join in v0.3. Each shares partner
status, children, income and benefit receipt with the others. Pairwise
checks grow with every pair of every shared fact. v0.2's population
schema (`semantics/population.py`) already has persons, but its facts are
the per-policy scenario forms.

## Decision

### 1. One household record in `semantics/`

A `Household` holds each fact once, with its own verification status and
period:

- **People:** each person with an id, a role (claimant, partner,
  dependent child, other), and the facts about them: the per-child facts
  WFF asks for today (whole-year qualification, Best Start cohort and
  payments), and for adults their income by type and benefit receipt.
- **Families:** who is whose partner and whose dependent child, by person
  id. v0.3 supports one family per household, as v0.2 does; a
  multi-family household is refused with a reason, not guessed.
- **Housing:** tenure, weekly costs, the verified AS area, cash assets.
- **Facts with a period:** a fact that depends on time carries its period
  (the WFF tax year, the AS assessment week, a benefit's weeks). Two
  policies reading the same fact for different periods read it through
  their mapping, never by assuming the week stands for the year.

A fact is `verified`, `excluded` or `unknown` (or a value with its
assertion), exactly as the engines take it now. An unknown stays unknown
through every mapping.

### 2. Named mappings to each policy's input

`to_wff(household) -> WffScenario` and `to_as(household) -> AsScenario`,
and one per new policy. Each is a reviewed function citing the rule that
makes each field what it is (for example, the AS dependent-child count is
the number of the family's dependent children under the AS definition).
The engines don't change: they keep taking their own input types.

Where two policies define a concept differently (a dependent child under
WFF and under AS), the household records the underlying facts, and each
mapping applies its own definition. The difference is then visible in the
mapping, not hidden in a shared field.

### 3. Byte-identical proof

Every golden household, spec case and golden snapshot is expressed as a
`Household`, mapped back, and run. Results and result ids must be
identical to today's. The existing request formats (`/household/calculate`,
stored scenarios, population facts) become adapters onto the household,
so no caller has to change.

### 4. Which pairwise checks retire

| Check | With one household |
| --- | --- |
| Partner status | Impossible: one family, one partner fact. Retired. |
| Dependent-children count | Impossible as a count mismatch. Retired, but a definitional difference (above) is reported by the mappings. |
| Claimant link | Impossible: both policies read the same family. Retired. |
| Main benefit vs WFF exclusions | Still meaningful: the AS week and the WFF year are different periods. Kept, restated as a period check on one benefit-receipt fact. |
| AS week inside the WFF year | Still meaningful. Kept. |

A check is retired only when a test shows its contradiction can no longer
be constructed.

## Questions for Pete

1. **Periods.** Record benefit receipt and income as dated spells (from,
   to, amount), and derive each policy's period view in its mapping?
   Recommended: yes, since income tax (annual) and benefits (weekly) need
   both views of the same income.
2. **Multi-family households.** Keep v0.2's one-family limit for v0.3,
   refused with a reason? Recommended: yes; the specifications for the
   Tier 1 benefits decide whether more is needed.
3. **API.** Keep today's request formats as adapters, and add the
   household form as a new request later? Recommended: yes, so v0.3
   changes no caller.

## Consequences

- Adding a policy means writing its mapping and its facts, not a new set
  of pairwise checks.
- The fact catalogues (ADR-0016) key on the household's facts once, so a
  question is asked once even if three policies need the answer.
- The mapping functions are policy content in code: each needs the same
  independent review as an engine, against its specification.
- Cost: every golden and snapshot must pass through the new path
  unchanged before anything else uses it. That is Phase 1's exit check
  (`BUILD_PLAN_v0_3.md` 1.3).
