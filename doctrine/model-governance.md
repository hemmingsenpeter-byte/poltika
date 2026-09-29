# Model governance and the validity ladder

**In force from 29 September 2026** (`BUILD_PLAN_PROGRAMME.md` Steps
1.5-1.6, ADR-0018). The ladder is Pete's direction. The drafting is Claude
Code's. Only Pete changes this document, and each change is recorded in
an ADR.

## Rule

Every model Poltika uses is registered, versioned, validated and given a
level. Nothing changes silently. Poltika moves up the validity ladder
only when the current level has shown sufficient validity, never because
the code is finished.

## 1. What counts as a model

Anything that turns inputs into a number Poltika shows or stores:

- a policy engine (the WFF and Accommodation Supplement engines today);
- a runner that combines engines (the combined household runner, the
  population runner);
- the population generator and its calibration;
- later: the accounts, the state store's derivations, the baseline and
  transition functions, domain models, the implementation of a causal
  estimate, uncertainty propagation, and the decision tools (cost of
  delay, value of information, optimisation).

## 2. The registry entry

Each model has one entry, from its first use. Task 1.5 places the
registry and records the location in REPOSITORY_STRUCTURE.md. An entry
records:

- id, version, owner and purpose;
- its inputs and outputs, as registered variables (Step 2);
- the evidence classes it consumes (`doctrine/epistemic-constitution.md`);
- its level on the ladder (section 4), and the decision that set it;
- its validation status, linked to its validation cases (Step 6);
- known limitations and failure modes;
- its change log.

## 3. Change control

A change record is required for any change to a rule, parameter,
relationship, engine or calibration that can alter an output. It
records:

- what changed, and the new version;
- why: the source, finding or diagnosis behind it;
- the evidence for the new behaviour;
- the validation cases re-run, and their results;
- who approved it, under the working agreement.

A change proven output-preserving (every golden household, spec case and
snapshot byte-identical) records that proof instead of a new version. A
change made to improve a validation or ledger score needs the same record
as any other change. Scores are monitored, never targeted.

## 4. The validity ladder

`executable rules → observable state → explanatory model → predictive model → integrated model → decision instrument → digital twin`

| Level | Burden of proof to reach it |
| --- | --- |
| 1. Executable rules | Legally correct. Every rule's golden, boundary, contradiction and regression cases pass, benchmarks match official worked examples, and the specification is independently reviewed. |
| 2. Observable state | Poltika's picture of New Zealand matches what is observed: published aggregates, the state store's sources and the Crown's published accounts, within stated tolerances. |
| 3. Explanatory model | Poltika explains observed history. The baseline reproduces Treasury's projection or attributes every difference. Historical replays reproduce past outcomes, given the shocks that actually happened, better than naive baselines. Stated intervals cover history at their stated rates. |
| 4. Predictive model | Out of sample: registered forecasts resolve inside their intervals at their stated rates and beat naive and statistical baselines, over a record long enough to judge. |
| 5. Integrated model | The coupled system keeps every invariant and reproduces history at least as well as its parts do separately. |
| 6. Decision instrument | Decision outputs are robust across the stated uncertainty, reproducible, and have survived independent scrutiny. |
| 7. Digital twin | The state estimate updates continuously from observations, with a sustained, published forecast record. |

A newly registered model is **not yet graduated** until its first
graduation.

- **Graduation** is a decision by Pete, recorded against the model's
  validation evidence. The tolerances for each level are set when that
  level is first reached (P18) and apply to every later model.
- **Demotion** follows when validation evidence stops supporting a
  level: a failed re-run, a ledger record that no longer supports it, or
  a change that invalidates it. The model is relabelled, and so is every
  output it produced from then on.
- **Labels.** Every output carries the level of the least mature model it
  relies on.
- **Language follows level.** Nothing is described as predictive before
  Level 4. Poltika is not called a digital twin before Level 7. An output
  from a model that is not yet graduated says so.

## 5. Model cards

Each registered model has a card, generated from its registry entry and
validation reports: its methods, validation, limitations, known failure
modes and uncertainty treatment. A card is never written by hand where
the registry or a report holds the fact.

## Applies to

Every engine, runner, generator and model under `src/poltika/`, and every
output, page, report and forecast that states a number.
