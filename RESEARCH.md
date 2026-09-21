# Research landscape

External papers and prior art that inform Poltika's *architecture and
methodology* — never its policy logic, values, or rules. Per
[doctrine/ip-doctrine.md](doctrine/ip-doctrine.md), nothing below may be used
as, or treated as, the source for a rate, threshold, eligibility rule,
abatement formula, or effective date. Where an entry names an external
system (OpenFisca, BetterRules), inspection of it is still bound by the
timing windows in BUILD_PLAN.md's IP Doctrine.

Compiled 2026-09-21.

## Rules as Code

Closest conceptual match to Poltika's core premise — legislation expressed
as versioned, machine-executable rules alongside (not instead of) the
human-readable law.

- [Better Rules and Legislation as Code](https://serviceinnovationlab.github.io/projects/legislation-as-code/) — NZ's own Better Rules initiative (Service Innovation Lab); already named as a structural reference in doctrine/ip-doctrine.md
- [Cracking the Code — OECD Working Papers on Public Governance No. 42](https://ggp.stanford.edu/complaw/readings/rules_as_code.pdf)
- [Rules as code and the rule of law: ensuring effective judicial review of administration by software](https://www.tandfonline.com/doi/abs/10.1080/17579961.2024.2313801) — risks of ossification and separation-of-powers concerns when legislation and code are drafted in parallel
- [Representing legislative Rules as Code: Reducing the problems of 'scaling up'](https://www.sciencedirect.com/science/article/abs/pii/S0267364922001157)

## Tax-benefit microsimulation architecture

Validates Poltika's separation of a generic calculation engine from
versioned policy parameters.

- [EUROMOD: the European Union tax-benefit microsimulation model](https://microsimulation.pub/articles/00075) — policy rules coded separately from a generic "engine" that runs them against input data, plus a validation process
- [Towards a multi-purpose framework for tax-benefit microsimulation: Lessons from EUROMOD](https://microsimulation.pub/articles/00016) — relevant to Architecture Doctrine's "minimum abstraction demanded by two real policies," since it's the same multi-country generalization problem
- [Quality assessment of microsimulation models: the case of EUROMOD](https://microsimulation.pub/articles/00178) — parallels the Spec/Benchmark/Regression test doctrine

## LLM-as-orchestrator over a deterministic engine

Validates the "LLM never calculates" architectural rule.

- [It's not the Language Model, it's the Tool: Deterministic Mediation for Scientific Workflows](https://arxiv.org/html/2605.13245.pdf) — "typed mediation": the model orchestrates deterministic tools rather than generating analytical code itself; structurally maps to Poltika's `ScenarioRequest → deterministic engine` boundary
- [Evaluating Semantic and Syntactic Understanding in Large Language Models for Payroll Systems](https://arxiv.org/html/2601.18012v2) — evaluates LLMs on the exact failure mode Poltika's architecture is designed around: combining language understanding with exact deterministic computation

## Legislation-to-code encoding methodology and provenance

Relevant to the source-first / provenance doctrine and to the
INTERPRETATION_AMBIGUITY review category.

- [Encoding legislation: a methodology for enhancing technical validation, legal alignment and interdisciplinarity](https://link.springer.com/article/10.1007/s10506-023-09350-1) — studies the interpretive difficulties (syntactic ambiguity, intertextuality) that arise converting statute to code
- [Specification languages for computational laws versus basic legal principles](https://arxiv.org/pdf/2503.09129)
- [Computational Law: Datasets, Benchmarks, and Ontologies](https://arxiv.org/html/2503.04305v2) — survey of formal-specification approaches and how correctness gets benchmarked

## Named prior art (structural reference only)

Subject to the IP Doctrine's timing windows (BUILD_PLAN.md Task 3, Task 16)
— never a source of policy values or logic.

- [OECD OPSI: About OpenFisca](https://oecd-opsi.org/wp-content/uploads/2022/09/Whitepaper-Attachment-02-About-OpenFisca.pdf) — structural overview of OpenFisca
- [OpenFisca Aotearoa](https://github.com/digitalaotearoa/openfisca-aotearoa) — active but small (14 stars, 9 open issues, last push 2025-05-05), community-maintained, not IRD/MSD-endorsed. Has a WFF module (`working_for_families.py`, `minimum_family_tax_credit.yaml`, `family_scheme/eligibility.yaml`). Traces to the 2018 Better Rules discovery project, which also produced two real operational services (SmartStart, Rates Rebate) — a genuine outcome, not purely theoretical, but an independent assessment ([Legislation as Code report](https://hamish.dev/research/lac/appendix1)) characterizes the wider NZ Rules-as-Code programme as still "primarily experimental and pilot-stage," not comprehensive statutory coverage.
- [PolicyEngine NZ](https://github.com/PolicyEngine/policyengine-nz) — more actively structured than OpenFisca Aotearoa: WFF is split into separate variables/parameters per component (`family_tax_credit.py`, `in_work_tax_credit.py`, `best_start.py`, with matching rate/income-test parameter files), plus a wider system (income tax, ACC levy, GST, Jobseeker Support, NZ Super, Accommodation Supplement, Winter Energy Payment, KiwiSaver). Caveats: 0 stars, 0 open issues (very low external scrutiny for its claimed coverage), and its README advertises a `pip install policyengine-nz` PyPI package that does not actually exist on PyPI — a sign the repo's polish outruns what's verified. Company/community-built, not government-endorsed; same evidentiary status as OpenFisca Aotearoa.

## Considerations for Task 13 onward (not yet actioned)

Structural/methodological ideas surfaced by the above, offered for Pete/GPT
to weigh when reaching the relevant task — **not a retroactive critique of
Tasks 1–12**, and none of this authorizes acting outside the IP Doctrine's
timing windows or without explicit approval per Architecture Doctrine. Each
item names a category only; if pursued, primary-source derivation and the
normal review process still apply in full.

- **Task 13 (spec tests) / Task 14 (benchmark tests):** EUROMOD's own
  [quality-assessment methodology](https://microsimulation.pub/articles/00178)
  is a possible reference point for what a mature validation process checks
  beyond pass/fail — e.g. distributional/edge-case coverage — worth a look
  when designing what "done" means for these test classes, not a suggestion
  to change the frozen three-class Test Doctrine itself.
- **Task 16 (external coverage-gap check):** currently scoped to OpenFisca
  Aotearoa by name. Given PolicyEngine NZ's more granular WFF
  component split (rates vs. income-test vs. abatement as separate
  parameter files) is a second, differently-structured data point, it may be
  worth deciding whether Task 16's coverage-gap check should name it
  alongside OpenFisca Aotearoa — a scoping question for whoever owns Task 16,
  not something to add unilaterally. Same category-only rule applies: it can
  suggest what to go check against primary sources, never a value or formula
  to adopt directly.
- **Task 17 (independent adversarial review):** the
  [computational-law encoding-methodology paper](https://link.springer.com/article/10.1007/s10506-023-09350-1)'s
  ambiguity taxonomy (syntactic ambiguity vs. intertextuality) could be a
  useful cross-check against the Review Doctrine's `INTERPRETATION_AMBIGUITY`
  category during fresh-context review — worth having read beforehand, not a
  proposal to change the frozen taxonomy.
- **Task 20 (simulator integration) / future `llm/` layer:** the "typed
  mediation" pattern from
  [Deterministic Mediation for Scientific Workflows](https://arxiv.org/html/2605.13245.pdf)
  is effectively a formal name for the `ScenarioRequest → deterministic
  engine` boundary ARCHITECTURE.md already specifies — useful vocabulary,
  not a design change. Relatedly, none of the frozen Test Doctrine's three
  classes test whether NL→`ScenarioRequest` translation is faithful (as
  opposed to whether the policy calculation is correct); the payroll-LLM
  evaluation paper on that failure mode
  ([link](https://arxiv.org/html/2601.18012v2)) is worth keeping in mind
  once the `llm/` layer is actually built (post-v0.1 per the module
  contract), as a possible fourth, separate test concern — not a change to
  the frozen three.
- **Task 23 (AS calculator) / Task 25 (schema stress-test):** EUROMOD's
  [multi-country generalization lessons](https://microsimulation.pub/articles/00016)
  are relevant reading right before this is the point Architecture
  Doctrine's "minimum abstraction demanded by two real policies" actually
  gets tested — useful context for that decision, not a formula or schema to
  copy.
- **General / ongoing:** the Rules-as-Code critique literature's ossification
  and judicial-review concerns are a product-framing note rather than a
  code change — worth confirming Poltika's outputs are consistently framed
  as simulated estimates, not binding determinations, somewhere user-facing
  (README/UI), whenever that surface gets built.

## The "digital twin" north star — competitive/prior-art landscape

BUILD_PLAN.md's north star describes Poltika's long-run destination as "a
progressively improving executable digital twin of the New Zealand policy
system." This section checks who else is already there or close to it.
Compiled 2026-09-21.

### Nearest existing NZ system (not a digital twin, but the direct comparison point)

- [Treasury's TAWA model](https://www.treasury.govt.nz/information-and-services/financial-management-and-advice/revenue-expenditure/tax-and-welfare-analysis-tawa-model) — real, operational, actively used for WFF reform advice, child poverty reporting, and effective-marginal-tax-rate analysis. The closest thing NZ already has to what Poltika is building, and the system a reviewer would ask "why not just use that?" about.
  - Structurally different: runs on linked survey microdata (Household Economic Survey + IRD/MSD data in the IDI) to produce *population-representative distributional/fiscal estimates*, operated by Treasury specialists internally.
  - Not provenance-first rules-as-code, no natural-language interface, not designed to answer an arbitrary household scenario on demand or to be inspected/extended outside Treasury.

### "Policy/economic digital twin" as an academic field — active, but pre-operational

- [Design of policy digital twins incorporating multi-level agent-based modelling](https://arxiv.org/abs/2607.13766) (2026) — combines deterministic calculation with agent-based modelling, human-in-the-loop; had a real government pilot (Newcastle City Council, energy transition/heat-pump policy). Authors call it a "pre-operational demonstrator" — "live data flows conspicuously absent." Different domain (energy, not tax/benefit) and different country.
- [DigEcoTwin — Policy Advice by Digital Economic Twins](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6336459) (Pobuda & Andrae, SSRN, Feb 2026) — closest by name to "digital twin of the economy": agent-based modelling + AI for forecasting/policy advice, human oversight kept central. Still a working paper, not a shipped system, not built around a specific country's statutory rules.
- [LLM-Powered Social Digital Twins: A Framework for Simulating Population Behavioral Response to Policy Interventions](https://arxiv.org/html/2601.06111v1) (2026) — uses LLMs to simulate population *behavioral response* to policy. Different angle from Poltika: predicting how people react, not calculating what they're statutorily entitled to.
- Recurring finding across multiple sources: digital twins are described as "largely absent from administrative workflows and policymaking" despite years of proposals — a field policymakers say they want that hasn't actually been built and adopted yet.

### Assessment

Each individual ingredient of Poltika's approach has prior art somewhere:
rules-as-code (Better Rules/OpenFisca), microsimulation (EUROMOD/TAWA/
PolicyEngine), LLM-orchestration-over-deterministic-tools (typed mediation),
and policy digital twins (the arxiv/SSRN work above). No system found
combines all of them: statutory rules-as-code with source-cited provenance
as ground truth, a hard architectural wall where the LLM only translates
language into structured requests and never calculates, benchmarking against
real IRD/MSD worked examples rather than survey calibration, progressively
extended toward whole-system scenario propagation — for New Zealand or any
other country. This looks like genuinely open territory rather than solved
ground, but it's a landscape read, not a guarantee; worth re-checking
periodically as this is an actively moving research area (multiple cited
papers are from within the last few months).

## Stats NZ microdata access (HES/HILS, IDI) — data acquisition landscape

Relevant to the Data Acquisition Doctrine, not to WFF (Task 10a already
closed: WFF needs no external statistical dataset) — this is forward-looking
for Task 22a (Accommodation Supplement's Stats NZ geography data) and v0.2's
"authoritative data foundation." **Caveat: compiled from a secondary AI-Mode
search conversation the user pasted in, not read directly from Stats NZ's
own documentation.** Two claims were spot-checked against stats.govt.nz
directly and confirmed (Five Safes framework, Data Lab environment; the
HES→HILS transition from July 2024/2025). Specific figures below (fees,
timeframes, portal names) were not independently re-verified line-by-line
and should be checked against the current stats.govt.nz pages before being
relied on for an actual Task 22a+ acquisition decision — per the Ground
Truth rule in CLAUDE.md, this is not itself a primary source.

### TAWA is not agentic

Confirms the comparison in the digital-twin section above: TAWA is a
deterministic microsimulation model — fixed accounting/tax/welfare formulas
applied to a static Household Economic Survey/HILS snapshot, no autonomous
goal-setting, no behavioural adaptation/learning in its baseline form. This
sharpens (doesn't change) the earlier assessment: TAWA and Poltika's
LLM-orchestration-over-deterministic-core direction are structurally
distinct approaches, not overlapping ones.

### HES/HILS and IDI access is tightly gated, not an open dataset

Stats NZ evaluates all microdata access requests under the **Five Safes**
framework: Safe People (vetted researcher, technical competence), Safe
Projects (clear public-interest purpose; commercial use generally
prohibited), Safe Settings (a monitored, no-internet **Data Lab**
environment — physical or remote terminals, not a download), Safe Data
(de-identified/encrypted), Safe Outputs (every output manually cleared by
Stats NZ checking officers before it leaves the Lab).

- Application → peer/supplier review → Government Statistician approval →
  mandatory secrecy training/lifetime statutory declaration, reportedly a
  multi-week process with an application fee for non-government applicants,
  plus possible server/storage charges.
- No sanitised, download-anywhere version exists for commercial use — under
  the Data and Statistics Act 2022, Stats NZ cannot release raw/granular
  microdata for commercial profit purposes.
- Named alternative pathways: **Customised Data Services** (Stats NZ runs
  the query and hands back an aggregated, cleared table, at an hourly
  charge-out rate), a **Group Project** pathway (multiple orgs pool funding
  to sponsor one approved researcher's Data Lab access), **CURFs**
  (Confidentialised Unit Record Files — a heavily modified flat file usable
  outside the Data Lab for some historical survey datasets), and
  **Synthetic Unit Record Files (SURFs)** — algorithmically generated
  fake-but-statistically-representative individual records, zero privacy
  risk, used elsewhere for testing/model-building without touching real
  microdata.
- Free, no-application public portals exist for aggregate (non-microdata)
  statistics: **Infoshare** and **NZ.Stat**.

### Relevance to Poltika

This is a strong argument for the Data Acquisition Doctrine's existing
discipline (minimum datasets only, versioned raw snapshots, canonical
variables downstream) rather than a reason to change it: full IDI/HES-HILS
microdata access is a heavyweight, public-interest-gated research process,
not something Poltika should assume it can casually acquire for population-
representative calibration. If Poltika's roadmap ever needs
population-representative data (distributional/fiscal aggregation, closer
to what TAWA already does), the realistic acquisition paths are Customised
Data Services or a sponsored Group Project — not a direct download — and
that should be scoped as its own explicit decision when the relevant task
(v0.2+) is reached, not assumed available today.

## Process note

This list was compiled as general landscape research, not tied to either of
the IP Doctrine's permitted inspection windows. Nothing in it was used as,
or should be treated as, a source for any rate, threshold, or eligibility
rule. A future structural inspection of OpenFisca Aotearoa for the Task 16
coverage-gap check is a separate, narrower exercise and should log its own
one-line ADR per doctrine/ip-doctrine.md.
