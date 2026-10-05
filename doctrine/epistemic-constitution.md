# Epistemic constitution

**Status:** approved by Pete on 2 October 2026 (historical Task 1.1,
now permanent doctrine under `BUILD_PLAN_PROGRAMME.md` Phase A), with the seven classification decisions under
"Decisions" below. Drafted by Claude Code; reviewed by GPT/Codex
(`reviews/2026-10-02-pr136.md`).

## Sequencing references (ADR-0021)

The approved classifications and seven decisions below remain unchanged.
Historical task numbers refer to the preserved ADR-0019 programme. Current
execution follows the sole `BUILD_PLAN_PROGRAMME.md`: bounded governance in A,
minimum household contracts in B, model/benchmark validation in C, population
contracts in E, historical/prediction records in I, uncertainty propagation in J,
national state in K and the validated digital-twin gate in M. They do not impose
an abstract foundation phase before household modelling.

## Rule

Every number Poltika shows is one of eight kinds of claim, and it says which.
It carries its provenance, its uncertainty and its model version. No AI-generated
claim becomes a fact, a rule or a model input without a cited primary source,
independent review and, for protected values and interpretations, Pete's
decision. People choose
objectives. Poltika measures consequences.

Validation expectations follow the temporary classification deferral in
Decision 1.

This doctrine states what kinds of claim exist. It states no rate, threshold or
policy value. Those come from cited primary NZ sources under `policy_specs/`
(see "Ground truth" below).

## Applies to

- Every output, test expectation, dataset, specification and estimate Poltika
  holds or produces.
- Every later step. The constitution is permanent. It changes only with Pete's
  approval, recorded in the repository.

## The eight evidence classes

Every claim has exactly one class, except the validation expectations in
Decision 1, whose classification is deferred to Phase C validation (old Step 6). If a claim seems
to fit two, it is two claims, and each is classed on its own.

| Class | Meaning |
| --- | --- |
| Fact | A directly sourced observation. |
| Rule | Deterministic law, regulation or accounting identity. |
| Estimate | An empirically estimated relationship. |
| Transferred estimate | Evidence borrowed from another population or country. |
| Assumption | Something we don't know, and have written down. |
| Scenario | A deliberately chosen hypothetical. |
| Model output | A calculated consequence of the other classes. |
| AI hypothesis | Generated for investigation. Never automatically promoted to fact. |

Four consequences:

- A Model output carries the classes of everything it depends on (its
  dependencies field), so a reader can see which inputs are Rules and which
  are Assumptions or Scenarios.
- An unknown is not an Assumption until someone writes down a value for it.
  Until then, Poltika reports it as unknown (a missing fact gives
  `needs_review`) and never uses zero.
- An AI hypothesis enters a model only through the AI gate (bounded Phase A work; old Task 1.2). The
  other classes enter labelled with their class, never relabelled.
- A Transferred estimate is always labelled as borrowed. It is never shown as
  an Estimate for New Zealand.

## The quantity: X = (x̂, D_x, E_x)

Every quantity Poltika carries has a value x̂, an uncertainty D_x and the
evidence E_x for it. Together they carry eleven fields:

1. value
2. unit
3. reference period
4. geography
5. population
6. source
7. method
8. evidence class
9. uncertainty
10. model version
11. dependencies

A quantity with a field missing is incomplete. It is never filled with a
default.

The historical quantity-type task (2.6) proposed a typed representation of
these fields. Under ADR-0021, representation grows from actual model contracts
in B/E; formal uncertainty propagation is in J. The allocation remains: x̂ is
the value at full stored precision; D_x is uncertainty; E_x carries evidence
class, sources, method, dependencies and model version. Unit, reference period,
geography and population provide context. This is not a claim that existing
output schemas already carry all eleven fields, or a requirement to merge the
parked generic type before household work. None of the metadata, uncertainty,
precision or no-default constraints above is waived.

## The four non-negotiables

1. **No result without provenance.** A result names its sources, parameters,
   facts, rules, decisions and model version. A citation that cannot be
   resolved stops the report. A report with a silent gap is worse than none.
2. **No false precision.** A single household's Rule output keeps the precision
   the law sets. Estimate-dependent figures show their range (the precision rule,
   old Task 1.3, retained P3). A point estimate is never shown where the uncertainty is large.
3. **No AI-generated claim enters a model without validation.** An AI
   hypothesis is promoted only through the AI gate (bounded Phase A work; old Task 1.2). The existing
   boundary stays: the LLM layer never calculates policy outcomes or recalls
   statutory values (`doctrine/llm_boundaries.md`).
4. **No model expansion without tests.** A new rule, parameter, relationship or
   engine arrives with its tests and, in Phase C, its validation cases
   (`doctrine/test-doctrine.md`). Protected expected values keep their
   process.

## People choose objectives

Poltika holds no default objective and no hidden one. It does not rank
outcomes by a weighting of its own.

- It measures consequences: who gains or loses, what it costs, through what
  mechanism, with what confidence, and compared with what.
- It never scores a party, a plan or a manifesto. It never says a plan wins.
  Phase O analyses proposals without scoring them.
- Where an objective is needed, a person states it, and the output shows that
  it was stated. Poltika may show trade-offs among objectives people name. It
  never names the objective for them.
- Ledger and validation scores are monitored and never targeted. A change
  made to improve a score needs the same diagnosis record as any other change.

## What Poltika never builds

This list is the plan's ("What Poltika never builds"). The mechanical checks
for it are bounded Phase A work (old Task 1.6).

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins".
- No secret normative objective function.
- No black-box AI forecast of GDP, or of anything else.
- No silently changing models. Every change is a recorded change (bounded governance work in A
  and state estimation in M).
- No point estimate where the uncertainty is large.
- No synthetic population presented as reality.
- No policy search before causal relationships are credible.
- No "digital twin" branding before Phase M's validated digital-twin milestone.
- No AI claim promoted into a model without validation.
- Never optimise the model instead of the country.

## Mapping today's concepts to the classes

Each row is derived from the file cited. The class is where the concept fits
today. Where the repository or the plan allowed more than one answer, Pete
decided it; see "Decisions" below.

| Concept in the repository | Where | Class |
| --- | --- | --- |
| A caller-asserted household fact: an input to a run, including a fact marked `verified` | `FactStatus` in `src/poltika/engines/simulator/outcome.py`; `policy_specs/*/facts.yaml` | Scenario (Programme decision P2, `BUILD_PLAN_PROGRAMME.md`) |
| An answer to a missing-fact question, and each branch the conditional resolver tries | `src/poltika/scenarios/conditional.py` | Scenario |
| A policy parameter with `source_id` and `review_status: approved` | `policy_specs/*/policy.yaml` | Rule |
| A policy parameter with `review_status: needs_review`, or either draft status | `policy_specs/*/policy.yaml`; `ParameterReviewStatus` in `src/poltika/semantics/schemas/policy_spec.py` | The evidence class follows the claim's sources and review, not this operational gate alone. An unpromoted AI-authored draft is an AI hypothesis; `needs_review` also gates reviewed values with unresolved period coverage |
| A reform override with `review_status: scenario_assumption` and no statutory source | `src/poltika/scenarios/microsim/reform.py` | Scenario: an explicit hypothetical, never an approved statutory Rule |
| A source catalogue entry | `policy_specs/*/sources.yaml` | Not a claim. It is E_x: the source and its authority rank (1-4, from `kind`) |
| A `calculated` component result | `ComponentResult` in `src/poltika/engines/simulator/outcome.py` | Model output |
| A `needs_review` or `unsupported` outcome | same file | Not a quantity. It has no x̂. It says why no number exists |
| Conditional `Bounds` (low and high) | `src/poltika/scenarios/conditional.py`; `src/poltika/scenarios/microsim/ranges.py` | Model output with D_x. Never labelled `calculated` |
| A run's `scenario_id`, `result_id` and artifact hashes | `src/poltika/scenarios/record.py` | E_x for a Model output (model version, dependencies) |
| A provenance report | `src/poltika/engines/assurance/provenance.py` | E_x, rendered |
| A v0.2 data snapshot and its manifest | `data/metadata/datasets/*.yaml`, `data/raw/` | Fact or Estimate, by dataset (decision 2) |
| A canonical variable definition | `data/metadata/variables/dictionary.yaml`; `src/poltika/semantics/variables.py` | Not a claim. It is the definition behind unit, period, geography, population (existing registry seed; expanded from model contracts in B/E) |

### Decisions (Pete, 2 October 2026)

1. **Test expectations are validation cases.** `spec_cases.yaml` values
   (hand-calculated from an approved specification), `benchmarks.yaml`
   values (from published worked examples), golden households
   (`policy_specs/wff_as_interaction/golden_households.yaml`, independently
   hand-calculated) and golden snapshots
   (`tests/fixtures/golden_results_v0_1.json`, frozen run results) have no
   evidence class of their own yet. The validation framework (old Step 6, now Phase C) gives
   them one. Their protected-value process is unchanged.
2. **Data snapshots are Fact or Estimate, by dataset.** Administrative
   counts and registrations are Fact. Survey-based figures, such as
   household income and net worth
   (`data/metadata/datasets/stats_nz_household_income_housing_costs.v1.yaml`,
   `data/metadata/datasets/stats_nz_household_net_worth.v1.yaml`), are
   Estimate, because they carry sampling error. Each dataset manifest will
   record its class as the contracts are extended (B/E; old Step 2).
3. **Each decision record states its own class.** A `DEC-*.md` is a Rule
   where it chooses between readings of the law's text, with the decider
   and date in E_x. It is an Assumption where the law is silent, and stays
   visible and revisable. New decision records state their class. Existing
   ones are classed in a later change for Pete's confirmation. Their
   hash-bound files are not edited to do it.
4. **Synthetic population: the inputs keep their classes, and the records
   are a Scenario.** The published shares the generator draws on keep their
   class (decision 2). Its listed assumptions (A1-A13 in
   `data/metadata/populations/nz_synthetic_development.v1.yaml`) are
   Assumptions. The household records it draws
   (`src/poltika/scenarios/microsim/synthetic.py`) are a Scenario, always
   carrying `SYNTHETIC_LABEL` (`src/poltika/semantics/population.py`). They
   are never presented as an estimate for New Zealand.
5. **An explanation inherits the class of the result it explains.** It is
   rendered from the recorded result and trace with fixed templates and no
   LLM (`src/poltika/engines/assurance/explanation.py`), and adds no claim.
6. **A rate cited from an agency page (rank 3) is a Rule.** Its rank is
   recorded in E_x, so a reader sees that it rests on an agency publication
   rather than an Act or Order. The release gate already accepts ranks 1-3
   (`src/poltika/engines/assurance/evidence.py`).
7. **An Assumption needs a written value.** An unknown becomes an
   Assumption only when someone writes down a value for it, with who chose
   it and why. Until then it is unknown, and is never zero.

The existing `needs_review` outcome is a calculation gate, not an evidence
class or a declaration that no candidate value is recorded. WFF's
source-linked `in_work_base`, for example, retains a value after independent
review while its future period remains unverified (`BUILD_PLAN.md` Task
10.2/10.3). The gate suppresses an authoritative result until the condition
is resolved. Decision 7 neither removes that gate nor turns an unknown
into zero.

## LLM and AI output today

No `src/poltika/llm/` exists yet. When it does, everything it generates (a
translation of a question, a draft source, a suggested value, an
interpretation, an estimate) is an AI hypothesis. The same holds for anything
Claude Code or GPT/Codex drafts into the repository. The AI gate (bounded Phase A work; old Task 1.2)
names the gate for each kind of artifact. This doctrine only fixes the rule:
no AI output is a source.

## Ground truth

`CLAUDE.md` says policy rules must be derived from cited primary NZ sources,
and that model memory is never authority. In this doctrine's words: a Rule
needs a cited primary source and independent review. An AI-authored claim
presented as a Fact or Rule remains an AI hypothesis until its promotion
gate passes. Caller Scenarios, explicit Assumptions and calculated Model
outputs keep their labels and trace their dependencies; lacking an
independent statutory source does not itself turn them into AI hypotheses.
`CLAUDE.md`'s "Ground truth" points here.

## Hooks for current capabilities

| Current capability (historical origin) | What it adds to this doctrine |
| --- | --- |
| A: AI gate (1.2) | The promotion gate for each artifact, enforced by checks |
| A/C: precision (1.3, P3) | Household legal precision; population/baseline/estimate-dependent figures shown to three significant figures with their range; stored values keep full precision |
| Permanent governance, E/M where applicable (1.4) | Sourced constraints and Pete's agreed governance; interim P5 prohibits ethnicity/iwi disaggregation |
| A/C: bounded model governance (1.5) | Model versions, validation records and recorded changes |
| A/C: mechanical checks (1.6) | Checks enforcing permanent constraints without a speculative infrastructure gate |
| A: evidence-classes skill (1.7, PR #138) | Applying the approved classifications; do not duplicate in-flight work |
| B/E: model-required quantity contracts (2.6) | Representation of X from actual needs; general wrappers are deferred |
| C: validation framework (6) | Class and home of validation expectations; Decision 1's temporary deferral stays in force until resolved |
| J: uncertainty propagation (11) | Formal propagation over supported empirical/behavioural models |
