# Epistemic constitution

**Status:** draft by Claude Code, awaiting Pete's approval (Task 1.1 of
`BUILD_PLAN_PROGRAMME.md`). Nothing here is in force until Pete approves it.

## Rule

Every number Poltika shows is one of eight kinds of claim, and it says which.
It carries its provenance, its uncertainty and its model version. No AI-generated
claim becomes a fact, a rule or a model input without a cited primary source,
independent review and, for protected values and interpretations, Pete's
decision. People choose
objectives. Poltika measures consequences.

This doctrine states what kinds of claim exist. It states no rate, threshold or
policy value. Those come from cited primary NZ sources under `policy_specs/`
(see "Ground truth" below).

## Applies to

- Every output, test expectation, dataset, specification and estimate Poltika
  holds or produces.
- Every later step. The constitution is permanent. It changes only with Pete's
  approval, recorded in the repository.

## The eight evidence classes

Every claim has exactly one class. If a claim seems to fit two, it is two
claims, and each is classed on its own.

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
  Until then, Poltika says it is unknown (`needs_review`) and never uses zero.
- An AI hypothesis enters a model only through the AI gate (Task 1.2). The
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

Task 2.6 will define the quantity type, using the National Variable Registry
(Step 2). Its design accepts intervals and distributions; their propagation
starts at Step 11. This is a planned type, not a claim that the existing
output schemas already carry all eleven fields.

Task 2.6 already assigns the fields: x̂ is the value at full stored precision;
D_x is the uncertainty; E_x carries evidence class, sources, method,
dependencies and model version. Unit, reference period, geography and
population come from the registry as the quantity's context. This follows
the approved plan without adding an allocation decision.

## The four non-negotiables

1. **No result without provenance.** A result names its sources, parameters,
   facts, rules, decisions and model version. A citation that cannot be
   resolved stops the report. A report with a silent gap is worse than none.
2. **No false precision.** A single household's Rule output keeps the precision
   the law sets. Estimate-dependent figures show their range (the precision rule,
   Task 1.3). A point estimate is never shown where the uncertainty is large.
3. **No AI-generated claim enters a model without validation.** An AI
   hypothesis is promoted only through the AI gate (Task 1.2). The existing
   boundary stays: the LLM layer never calculates policy outcomes or recalls
   statutory values (`doctrine/llm_boundaries.md`).
4. **No model expansion without tests.** A new rule, parameter, relationship or
   engine arrives with its tests and, from Step 6, its validation cases
   (`doctrine/test-doctrine.md`). Protected expected values keep their
   process.

## People choose objectives

Poltika holds no default objective and no hidden one. It does not rank
outcomes by a weighting of its own.

- It measures consequences: who gains or loses, what it costs, through what
  mechanism, with what confidence, and compared with what.
- It never scores a party, a plan or a manifesto. It never says a plan wins.
  Step 26 analyses proposals without scoring them.
- Where an objective is needed, a person states it, and the output shows that
  it was stated. Poltika may show trade-offs among objectives people name. It
  never names the objective for them.
- Ledger and validation scores are monitored and never targeted. A change
  made to improve a score needs the same diagnosis record as any other change.

## What Poltika never builds

This list is the plan's ("What Poltika never builds"). The mechanical checks
for it are Task 1.6.

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins".
- No secret normative objective function.
- No black-box AI forecast of GDP, or of anything else.
- No silently changing models. Every change is a recorded change (Tasks 1.5
  and Step 18).
- No point estimate where the uncertainty is large.
- No synthetic population presented as reality.
- No policy search before causal relationships are credible.
- No "digital twin" branding before Phase 5's milestone.
- No AI claim promoted into a model without validation.
- Never optimise the model instead of the country.

## Mapping today's concepts to the classes

Each row is derived from the file cited. The class is where the concept fits
today. "For Pete:" marks a place where the repository or the plan allows more
than one answer. It is not settled here.

| Concept in the repository | Where | Class |
| --- | --- | --- |
| A caller-asserted household fact: an input to a run, including a fact marked `verified` | `FactStatus` in `src/poltika/engines/simulator/outcome.py`; `policy_specs/*/facts.yaml` | Scenario (decision P2) |
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
| A v0.2 data snapshot and its manifest | `data/metadata/datasets/*.yaml`, `data/raw/` | See "For Pete: data snapshots" below |
| A canonical variable definition | `data/metadata/variables/dictionary.yaml`; `src/poltika/semantics/variables.py` | Not a claim. It is the definition behind unit, period, geography, population (Step 2 seed) |

**For Pete: expected values in tests.** A `spec_cases.yaml` expected value is
calculated by hand from an approved specification
(`policy_specs/working_for_families/spec_cases.yaml`,
`policy_specs/accommodation_supplement/spec_cases.yaml`,
`policy_specs/wff_as_interaction/spec_cases.yaml`). A `benchmarks.yaml` value
is a figure from an independently published worked example
(`policy_specs/working_for_families/benchmarks.yaml`,
`policy_specs/accommodation_supplement/benchmarks.yaml`). Golden households
(`policy_specs/wff_as_interaction/golden_households.yaml`) carry independently
hand-calculated expected values from approved specifications and parameters.
Golden snapshots (`tests/fixtures/golden_results_v0_1.json`) freeze run
results. Options:
(a) spec cases are Model output (by hand), benchmarks are Fact (a published
observation of what the agency says), golden files are Model output;
(b) all four are validation cases with no class of their own, and Step 6 gives
them one; (c) benchmarks are Rule illustrations, since a worked example is
guidance (rank 4), not law.

**For Pete: data snapshots.** The v0.2 snapshots are tables published by Stats NZ,
IRD and MSD. Options: (a) Fact, because each is sourced to the publication
and E_x carries the publisher's own caveats; (b) Fact for registrations and
administrative counts, and Estimate for survey-based figures such as household
income and net worth (`data/metadata/datasets/stats_nz_household_income_housing_costs.v1.yaml`,
`data/metadata/datasets/stats_nz_household_net_worth.v1.yaml`). Option (b)
needs a per-dataset class in each manifest.

**For Pete: decisions.** `DEC-*.md` files record a person's reading of an
ambiguity (`policy_specs/working_for_families/decisions/DEC-001-evidenced-ineligibility-outcome.md`,
`policy_specs/accommodation_supplement/decisions/DEC-001-income-excess-rounding.md`,
`DEC-002-published-thresholds-and-rate-scope.md`,
`DEC-003-msd-paid-wff-income-exclusion.md`). Options: (a) Rule, an authorised
interpretation of law, with the decider and date as E_x; (b) Assumption, a
choice made where the law is silent, kept visible and revisable. Some decisions
may be one and some the other, so the class may need to be written in each
decision.

**For Pete: synthetic population records.** The seeded population
(`src/poltika/scenarios/microsim/synthetic.py`,
`data/metadata/populations/nz_synthetic_development.v1.yaml`) draws shares from
published tables (Fact or Estimate, as above), adds listed assumptions (A1-A8
in its manifest) and draws households at random from a seed. Options: (a) the
population is a Scenario (a deliberately chosen hypothetical, always labelled
with `SYNTHETIC_LABEL` in `src/poltika/semantics/population.py`); (b) it is a
Model output of the generator; (c) the inputs keep their own classes and the
records are a Scenario. In every option, it is never presented as an estimate
for New Zealand.

**For Pete: explanations.** An explanation is rendered from the recorded result and
trace, with fixed templates and no LLM
(`src/poltika/engines/assurance/explanation.py`). It adds no claim. This
doctrine proposes that it inherits the class of the result it explains. The
alternative is to class it as Model output in its own right. The plan doesn't
say.

**For Pete: Rule or Fact for agency-published rates.** A parameter can cite an
agency rates page (rank 3) instead of an Act or order (ranks 1-2); the release
gate allows ranks 1-3 (`src/poltika/engines/assurance/evidence.py`). Options:
(a) such a parameter is still a Rule, with rank 3 in E_x; (b) it is a Fact about
what the agency published until a rank 1-2 source confirms it.

**For Pete: Assumption versus unknown.** The plan defines Assumption as
"something we don't know". This draft proposes requiring an explicit value
before an unknown is used as an Assumption. Alternatively, an unknown could
itself be classed as an Assumption with no value. That choice is still open.

The existing `needs_review` outcome is a calculation gate, not an evidence
class or a declaration that no candidate value is recorded. WFF's
source-linked `in_work_base`, for example, retains a value after independent
review while its future period remains unverified (`BUILD_PLAN.md` Task
10.2/10.3). The gate suppresses an authoritative result until the condition
is resolved. Neither option above removes that gate or changes an unknown
into zero.

## LLM and AI output today

No `src/poltika/llm/` exists yet. When it does, everything it generates (a
translation of a question, a draft source, a suggested value, an
interpretation, an estimate) is an AI hypothesis. The same holds for anything
Claude Code or GPT/Codex drafts into the repository. The AI gate (Task 1.2)
names the gate for each kind of artifact. This doctrine only fixes the rule:
no AI output is a source.

## Ground truth

`CLAUDE.md` says policy rules must be derived from cited primary NZ sources,
and that model memory is never authority. In this draft's words: a Rule
needs a cited primary source and independent review. An AI-authored claim
presented as a Fact or Rule remains an AI hypothesis until its promotion
gate passes. Caller Scenarios, explicit Assumptions and calculated Model
outputs keep their labels and trace their dependencies; lacking an
independent statutory source does not itself turn them into AI hypotheses.
`CLAUDE.md`'s "Ground truth" identifies this framework as a pending draft.

## Hooks for later tasks

| Task | What it adds to this doctrine |
| --- | --- |
| 1.2, the AI gate | The gate for each kind of artifact, each enforced by a check |
| 1.3, the precision rule (P3) | The display rule for non-negotiable 2 |
| 1.4, data governance | `doctrine/data-governance.md`. The interim rule (P5): no output disaggregated by ethnicity or iwi |
| 1.5, model governance | `doctrine/model-governance.md` and the registry. The model-version and change-record parts of E_x |
| 1.6, mechanical checks | The release-gate rows that enforce the never-build list |
| 1.7, the `evidence-classes` skill | How every later task applies this doctrine |
| 2.6, the quantity type | The code form of X |
| 6, the validation framework | The class and home of test expectations |
