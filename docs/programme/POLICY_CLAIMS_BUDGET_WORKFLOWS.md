# Campaign-policy and New Zealand Budget analysis workflows

**Status:** Approved product-direction proposal; documentation-only roadmap overlay (9 October 2026). No capability is implemented, gate passed or release date promised by this document.
**Authority:** [BUILD_PLAN_PROGRAMME.md](../../BUILD_PLAN_PROGRAMME.md), under ADR-0021, remains the **only** master build order. [PROGRAMME_STATUS.md](../../PROGRAMME_STATUS.md) is the live task tracker. These are subordinate use-case tasks, not a new roadmap or implementation workstream.

## Product goal and boundaries

Apply one consistent, independent and auditable analytical workflow to (a) policy proposals announced by New Zealand political parties, ministers or other proponents, including campaign statements, and (b) successive New Zealand Budgets. A source's assertion is not the model's conclusion. An announced proposal is not enacted law. The system can report verifiable source facts, describe assumptions and calculate **only** outputs backed by approved model coverage. Do not make electoral recommendations, party/plan rankings or normative scores.

One product architecture, not a campaign app plus a Budget app:

1. Retain original publisher documents and metadata, with content identity, observation/retrieval time and legal/policy status.
2. Extract proposed measures as **untrusted candidate descriptions**; verify source text and policy parameter mapping independently, with a human approval/refusal.
3. Reuse existing Policy Specs and the C 14 scenario contract: status quo, proposal, explicit cohorts, effective periods, versions, assumptions and supported/unsupported status.
4. Run the deterministic approved models; the frontend formats results but never computes values.
5. Use existing model assurance, evidence, scenario runs, analyst exports and F reports as their respective gates are met.
6. Retain one explanation, comparative result, limitations and reproduction bundle linked to exact source and run identities.

Optional LLM extraction may be explored **later** with a human promotion gate; it is not an early prerequisite or numerical/statutory authority. Do not promote raw source-archive records directly into the governed data path (ADR-0022).

## Shared source-to-scenario contract (C14a)

Minimum reviewable fields per claim/measure:

| Group | Required information |
| --- | --- |
| Identity | Stable claim/measure ID, originating document and URL, publisher/speaker as attributed, exact relevant text and locator/page, content hash/retrieval timestamp |
| Time/status | Statement/publication date, observation date, policy validity/effective dates, forecast/financial and tax years, announcement/proposal/bill/enacted status separately |
| Proposed change | Affected instrument, base-rule or counterfactual parameters, denominators, units, cohort definition, interactions and explicit assumptions |
| Evidence | Source class, authoritative rule references (if modelled), evidence-review status, named reviewer, conflicts and primary-source links |
| Model coverage | Supported/partial/unsupported/not applicable; why; missing facts, sensitivity and interpretation questions; reviewer disposition |
| Reproducibility | Approved scenario/run IDs, model/spec/data/code versions and vintages, baseline, assumptions, export links, discrepancy record |

Treat a quoted cost or macroeconomic assertion as an **attributed published estimate**, not a proven result. Source verification (“the publisher made this statement”), calculation reproducibility, empirical plausibility and eventual outcome validation are different questions. Never replace unknown amounts with zero. Where a claim bundles multiple measures, preserve one parent claim and distinct individually reviewable measures. A cancelled, revised or enacted proposal creates a new dated state; do not overwrite history.

**Acceptance C14a:** independently reviewed original quotation and mapping; supported proposal runs as a replayable household example with matching displayed/exported values, while unsupported, contradictory or underspecified proposals fail closed with visible reasons. Regressions exercise dates, provenance, partial coverage, source conflict, labels, no ranking, and no proposal being mistaken for current law. C 14 and core B coverage remain prerequisites for simulation, not for passive research.

## Optional campaign-policy Pilot 1 extension (D16a)

Choose one or two bounded tax/transfer proposals whose actual proposed parameter changes can be independently sourced. Reuse Task 16's real-analyst question, consent, baseline, release/commit/run IDs, export and reproduction evidence. Show before/after outcomes for supported **example** households and mark all other effects unavailable.

**Acceptance D16a:** at least one external analyst can independently trace a quoted proposal to verified input values, inspect the household result and its limitations, and reproduce an export. Record feedback, erroneous mapping attempts and follow-ups. This is **optional** to Gate D and can be skipped if campaign announcements are underspecified. No aggregate national cost, whole-manifesto evaluation, party score or suggested vote is allowed from this pilot.

## Recurring Budget release workflow (F24a)

**Early preparation is allowed:** register an existing Budget's official source set and build a manually checked initiative/coverage catalogue without claiming F's fiscal output. Do not divert B–D engineering or make a new intake app. Budget-runner implementation begins **after** E's representative inputs and F's validated direct fiscal/distributional report components for the chosen measure. A bounded rehearsal can feed a future Pilot 2 question but does not block G.

A release run follows a stable sequence:

1. **Release register:** official Budget statements, votes/appropriations, fiscal strategy, economic and fiscal forecasts, initiative tables, supporting legislation and corrigenda **as applicable**, each with URL, hash, publisher, publication/retrieval time, financial year, source licence and supersession information.
2. **Initiative inventory:** stable initiative identifier, budget measure, type (tax/transfer, service expenditure, capital allocation, financing, macro assumption or other), fiscal years, proposed/enacted/effective status, scope and original published amount/basis where any.
3. **Scope gate:** supported, partially supported, unsupported or non-microsimulation; distinguish allocations and funding envelopes from modelled beneficiary entitlements, forecast tax receipts, aggregate operating balances and true additional expenditure.
4. **Scenario execution:** source-approved parameters only; coherent status quo and reform, population vintage and model/data/code versions, validated run identities, calibration/coverage gates and stated behavioural exclusions.
5. **Comparable checks:** identify the official figure's scope, population, reference period, currency and price basis, annualisation, take-up/behaviour, initiative grouping and tax treatment before calling it a comparator. No mechanical reconciliation of incomparable figures; no cross-unit sum.
6. **Output package:** index and coverage ledger for **all** inventoried initiatives; for supported ones, fiscal/distributional tables, comparable official figures, differences and attributed explanatory hypotheses, trace, tests, versioned export and reproducibility instructions.
7. **Corrections/update:** append new official releases, revised forecasts and legislative effective dates as additional source states. Never silently overwrite the original Budget or historical run.

**Acceptance F24a:** analyse a selected historical published NZ Budget with a clearly bounded set of instruments; an independent analyst can reproduce the declared supported coverage and explain discrepancies against comparable official numbers. A new Budget can use the same pipeline/configuration with a new release register and source reviews, not new bespoke calculation code. If only 2 of 100 initiatives are supported, report that coverage explicitly and do not title the result an analysis of the other 98. Full Budget coverage is neither the gate nor a release-day guarantee.

## Historical Budget as-of replay (I29a)

The test is **what Poltika could have calculated using information available at the time of that Budget**. Distinguish policy validity, observed economic periods, publication/retrieval time, model code and data vintages; record later revisions separately. Reproduce retained supported runs for a chosen Budget and distinguish forecast errors, modelling omissions, subsequent policy changes and incomparable scope. Hindsight-contaminated backcasts may inform diagnosis but do not establish a prospective forecast track record. I 30's prediction ledger requires a **prospectively registered** forecast before its outcome.

**Acceptance I29a:** independently repeatable as-of report, sources/hashes, vintages, discrepancy classification and missing evidence; new hindsight information is labelled and cannot silently affect the as-of run.

## Later scope and product presentation

- E–F: national static fiscal and distributional consequences only after representative datasets, validation, classification and annualisation gates.
- H: add statutory domains only from demonstrated pilot/Budget demand and a maintenance plan; no broad manifesto coverage by default.
- J–L: empirically validated behavioural, dynamic, debt, productivity, employment and GDP consequences only with appropriate models and uncertainty. Unsupported multi-year economic promises remain unassessed, not guessed.
- O 51: public/research explorer after access, security, licensing/IP and trust/publication decisions. It **reuses** the analyst outputs and source trail; it is not when calculations first begin.
- P: optional AI explanation and source-intake aids above verified deterministic results; no LLM-authored values, automatic policy promotion, electoral guidance or uncontrolled autonomous publication.

The B0.1 web app remains the only product surface. C 15 completes its Analyst Workbench. Later proposal/Budget navigation should be feature gated and reuse existing scenario results, evidence, assumptions, audit and export blocks; this plan does not expand the B0.1 implementation acceptance criteria.

## Release-quality and neutrality safeguards

- Side-by-side comparisons may show **documented settings and quantified supported consequences**, but must not rank parties or plans, compute political merit scores or declare a preferred vote or party. Maintain consistent modelling assumptions for comparable scenarios.
- Every figure carries its provenance and the applicable evidence/model class, units, price/period basis, policy/data/code versions and coverage. Modelled outputs must be distinguishable from an official estimate, a political claim and a forecast.
- Statutory source and parameter review remains governed by primary NZ authority, independent reviewer rules and protected values. A proposal is *not* an authoritative source for law; it is an authoritative source only for what was **proposed**.
- Protect original copyrighted documents, licences and access restrictions; preserve source pointers/hashes and only ingest/export where permitted. Keep privacy/Māori data governance and microdata constraints unchanged.
- No unreviewed source claim enters a simulator, no result appears from unimplemented models, and no publication or public-access approval is inferred from this plan.

## Dependencies, execution order and non-goals

| Work | Earliest prerequisite | Implement as |
| --- | --- | --- |
| C14a | B's approved relevant policy slice; C 14 scenario contract | Separate narrowly reviewed intake/mapping PR(s), not a new UI/framework |
| D16a | C14a + Task 16 pilot capacity | Optional extra real analyst case, not a Gate D blocker |
| Early Budget source rehearsal | ADR-0022/source review boundaries | Documentation and source register only; no fiscal/national claims |
| F24a | E 17–21 + F 22–24 for the **specific** measures | Budget release/inventory, reviewed mapping, supported report, comparison tests in bounded PRs |
| I29a | I 27–29; I 30 for prospective tracking | As-of replay and discrepancy analysis |
| O 51 | Proven supported analyses + Gate O | Public facing explorer of existing evidence/results |

No election date, Budget date, performance SLA, full-source ingestion, universal economic model or extra pilot/release is promised. Tasks are recorded as **Not started** in the live status file until individually implemented and reviewed.
