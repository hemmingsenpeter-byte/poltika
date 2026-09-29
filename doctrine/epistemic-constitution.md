# Epistemic constitution

**In force from 29 September 2026** (`BUILD_PLAN_PROGRAMME.md` Step 1.1,
ADR-0018). The content is Pete's direction and decisions P2, P3 and P5,
approved with the programme plan. The drafting is Claude Code's. Only Pete
changes this document, and each change is recorded in an ADR.

## Rule

Every number Poltika shows or stores says what kind of claim it is, where
it came from, how uncertain it is and what it depends on. No later step,
model or interface may break the rules below.

## 1. Evidence classes

Every value belongs to exactly one class.

| Class | What it is | May it enter a calculation? |
| --- | --- | --- |
| `fact` | A directly sourced observation (a published statistic, an administrative total). | Yes, with its lineage. |
| `rule` | Deterministic law, regulation or accounting identity: a statutory rate, threshold, rounding or formula, or a decided interpretation of one. | Yes, only when `approved`. |
| `estimate` | An empirically estimated relationship, from New Zealand evidence. | Yes, from the causal library (Step 12), with its grade and range. |
| `transferred_estimate` | An estimate borrowed from another population or country, transferred explicitly. | Yes, with the transfer recorded. |
| `assumption` | Something we don't know, stated. | Yes, labelled, and listed wherever it is used. |
| `scenario` | A deliberately chosen hypothetical: a reform setting, or a caller-described household (P2). | Yes, labelled. |
| `model_output` | A calculated consequence of the classes above. | Yes, as another calculation's input. It keeps its dependencies. |
| `ai_hypothesis` | Something generated for investigation. | **Never**, until promoted (section 7). |

A `model_output` is never stronger than what it rests on. Its dependencies
list the classes it used. A figure that rests on any `assumption`,
`scenario` or `transferred_estimate` says so wherever it is shown.

## 2. What every number carries

Every quantity is X = (x̂, D_x, E_x): its value x̂, its uncertainty D_x,
and the evidence E_x for it. In full, it carries eleven fields:

| Field | Meaning |
| --- | --- |
| value | The number, at full stored precision. |
| unit | For example `NZD per tax year`, `NZD per week`, `persons`, `percent`. |
| reference period | The interval the value is for: a tax year, an assessment week, a quarter. |
| geography | Where it applies: New Zealand, an area, or `household` for a single household's result. |
| population | Whom it covers: one described household, a weighted population with its grade (P4), or a published statistic's population. |
| source | Source ids and locators, a dataset and vintage, or the run that produced it. |
| method | How it was obtained: `statute`, `observation`, `calculation` with its rule ids, `estimation` with its design, `stated`. |
| evidence class | One of the eight in section 1. |
| uncertainty (D_x) | `exact` (a Rule output, or a Rule applied to scenario inputs); `interval` with its kind (true bounds, or values at chosen points, as `Bounds` records); `distribution` (quantiles at least, accepted by the data model from Step 2 and propagated from Step 11); or `unquantified`, with the reason. |
| model version | The model's registry id and version (`doctrine/model-governance.md`), the code commit, and the policy version and file hashes the calculation used. |
| dependencies | The ids of the parameters, facts, datasets, assumptions and results it rests on. |

A field that can't apply says why: it is never left blank or silently
defaulted. A missing fact is never zero.

## 3. The four non-negotiables

1. **No result without provenance.** A number without the section 2
   fields is refused, never shown, as a failing `verify()` is.
2. **No false precision** (P3).
   - A single household's `rule` or `model_output` resting only on
     `rule` and `scenario` inputs keeps the precision the law sets.
   - Population, baseline and estimate-dependent figures are shown to
     three significant figures, with their range where one exists.
   - Stored values keep full precision, so every run still reproduces.
   - A large uncertainty is never shown as a point alone.
3. **No AI-generated claim enters a model without validation.** Section 7
   sets the gate for each kind of artifact.
4. **No model expansion without tests.** No new rule, relationship or
   engine without spec, benchmark and regression tests
   (`doctrine/test-doctrine.md`), and, from Step 5, a complete
   conformance matrix: golden, boundary, contradiction and regression
   cases for every rule. No model is used without a registry entry and
   validation cases (`doctrine/model-governance.md`).

## 4. Objectives belong to people

Poltika measures consequences. It doesn't decide what New Zealand ought
to value.

- It holds no default or hidden objective. Every objective or constraint
  it searches against is stated by a person and shown with the result.
- It never scores or ranks a party, a politician or a plan, and never
  declares a winner.
- Value of information comes before optimisation: Poltika says when an
  answer hinges on poorly evidenced parameters (Step 19).
- Optimisation returns the set of options that meet the constraints a
  person supplied, with their trade-offs, and never a recommendation
  (Step 20).

## 5. What Poltika never builds

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins".
- No secret normative objective function.
- No black-box AI forecast of GDP, or of anything else.
- No silently changing models: every change to a rule, parameter,
  relationship or engine is a recorded change
  (`doctrine/model-governance.md`), and registered forecasts are never
  revised.
- No point estimate where the uncertainty is large.
- No synthetic population presented as reality: every population result
  carries its grade (P4).
- No policy optimisation before causal relationships are credible.
- No "digital twin" branding before Level 7 of the validity ladder
  (`doctrine/model-governance.md`).
- **Never optimise the model instead of the country.** Ledger and
  backtest scores are monitored, never targeted. A change made to improve
  a score needs the same diagnosis record as any other change.

## 6. How today's concepts map to the classes

| Today | Class |
| --- | --- |
| An `approved` value in `policy.yaml`: a rate, threshold, rounding rule | `rule` |
| A `needs_review` value with recorded candidates (v0.3 1b.2c) | Not usable as a `rule`. Each candidate branch is an `assumption`. |
| A decided interpretation (`policy_specs/<policy>/decisions/`) | `rule`, citing the decision |
| A caller-asserted household fact (verified, excluded, unknown or a value) | `scenario` (P2). `unknown` stays unknown. |
| A reform override (`review_status: scenario_assumption`) | `scenario` |
| An `Observation` with its `Lineage` (Stats NZ, IRD, MSD) | `fact` |
| A synthetic generator rule or calibration assumption (D1-D7, A1-A12) | `assumption` |
| A synthetic population's weights and records | `assumption`, with the Development grade |
| A `ComponentResult` value, a WFF total, a run total, a decile table | `model_output` |
| A cross-validation ratio of modelled to published figures | `model_output`, comparing a `model_output` with a `fact` |
| Conditional branches and bounds (ADR-0016) | `model_output` resting on `scenario` inputs: each branch conditions on a hypothetical answer ("if X, then ...") and never asserts it |
| A specification row, value or case drafted by a model, before review | `ai_hypothesis` |

## 7. The AI-hypothesis gate

AI writes most of Poltika: Claude Code and GPT/Codex draft sources,
specifications, values, cases and code. Everything they draft is an
`ai_hypothesis` until it passes the gate for its kind.

| Artifact | Leaves `ai_hypothesis` when | Enforced by |
| --- | --- | --- |
| Source entry (`sources.yaml`) | It has an identifier, locator, retrieval date and source kind, from which its authority rank follows | `SourceCatalog` schema; the `provenance` skill |
| Statutory value (`policy.yaml`) | It cites a source of rank 3 or better with a locator, is independently reviewed, and is set `approved` | The loader refuses any non-`approved` value; the evidence coverage check in CI; the statutory-value guard; `doctrine/test-doctrine.md` |
| Specification rule | It cites primary legislation or a rank 1-2 source | The evidence coverage check |
| Interpretation of ambiguous law | Pete decides a decision record | `doctrine/review-doctrine.md`; `policy_specs/DECISION_TEMPLATE.md` |
| Expected test value | It is hand-calculated from the specification and independently reviewed | The statutory-value guard; `doctrine/test-doctrine.md` |
| Fact-catalogue question | Its wording is reviewed | The v0.3 release gate's wording row |
| Monotonicity declaration | It cites the rule that implies it | `FactEntry` schema; property tests |
| Dataset or observation | It has a manifest and SHA-256 | The dataset registry; the data-snapshot guard |
| Population assumption | It is stated in the population's sources and the population carries its grade | The generator requires `sources`; the synthetic label |
| Causal relationship (Step 12) | It is a graded, reviewed library entry | The library schema (Step 12) |
| Code | It passes CI and is reviewed, or listed in the review queue until it is | `tests.yml`; `review_packets/review_queue.md` |
| Explanation text | Every figure in it matches the calculation | `verify()` |
| Model or engine | It is registered with validation cases, and its level is a recorded decision | `doctrine/model-governance.md` (Steps 1.5-1.6) |
| Runtime LLM output (Step 22) | Never, for a number or a relationship | `doctrine/llm_boundaries.md` |

Model memory is never a source (CLAUDE.md, "Ground truth").

## 8. Data governance

Māori data governance, privacy, confidentiality and Te Tiriti
considerations are architectural constraints from the start, not an
approval before launch. See `doctrine/data-governance.md`.

## 9. Models and the validity ladder

Every model is registered, versioned and validated, and Poltika climbs
from executable rules to a digital twin only as each level shows
sufficient validity. An output carries the level of the least mature
model it relies on, and its wording never claims more than that level.
See `doctrine/model-governance.md`.

## Applies to

Everything: every engine, population run, API response, page, stored
run, forecast, report and document that states a number.
