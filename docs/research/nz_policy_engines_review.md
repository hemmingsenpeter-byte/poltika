# Clean-room comparative review: NZ policy-modelling projects vs. Poltika

**Purpose:** understand the problem space, extract architectural lessons, and identify
possible gaps in Poltika's own architecture — not to recreate or port either external
project. External projects are evaluated **against** Poltika's already-documented
architecture (`ARCHITECTURE.md`, `BUILD_PLAN.md`, `REPOSITORY_STRUCTURE.md`, `ROADMAP.md`,
`doctrine/`); they do not define it.

**Method:** two-stage clean-room process. Stage 1 (external research) inspected public
repository metadata, READMEs, and directory listings only, at a conceptual level, with no
code/test/comment/documentation copying and no statutory values recorded as fact. Stage 2
(this document) was written independently against Poltika's own architecture, using Stage 1
only as a prompt for "has Poltika considered X," never as an implementation reference.

Poltika is currently at Week 0 of `BUILD_PLAN.md`: no `src/`, `data/`, or `tests/` exist yet.
Only doctrine, ADRs, and source-grounded specifications for Working for Families (WFF) and
Accommodation Supplement (AS) exist. This review is scoped accordingly — most findings are
about what to keep in mind while building, not about existing code to fix.

---

## 1. Repositories and revisions inspected

| Project | Repository | Revision inspected | Notes |
| --- | --- | --- | --- |
| OpenFisca Aotearoa | `github.com/digitalaotearoa/openfisca-aotearoa` | Commit `9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb` (2025-05-05) | Multiple related copies exist under `BetterRules/` and `ServiceInnovationLab/` GitHub orgs; **canonical/upstream status across the three was not verified** (see §11). |
| PolicyEngine New Zealand | `github.com/PolicyEngine/policyengine-nz` (linked from `policyengine.github.io/policyengine-nz/`) | Commit `fbd186bd9a40633d5fc106750838b9cae40e71c3` (HEAD of default branch, pinned 2026-09-21 via `git ls-remote`) | **Correction to an earlier draft of this review:** Stage 1 research initially concluded no NZ-specific PolicyEngine package existed. That was wrong — the user supplied the project's documentation URL directly, and it was verified as a genuine, actively-developed `PolicyEngine` organisation repository, not a third party's work. See the correction note below. |
| *(adjacent, not one of the two named targets)* | `TheAxiomFoundation/rulespec-nz` | not deeply inspected | A separate, unrelated third-party "PolicyEngine-style" NZ smoke-test surface, explicitly not an artifact of the PolicyEngine organisation and not treated as authoritative by its own description. Flagged for awareness only; out of scope for this review's two named repositories. Not to be confused with the genuine `PolicyEngine/policyengine-nz` above. |

### Correction note (added after initial publication of this review)

The original Stage 1 research pass searched the PolicyEngine GitHub organisation and its
public documentation and concluded no NZ package existed, based on the organisation's
repository listing at the time not surfacing `policyengine-nz` in search results. The user
supplied the actual documentation URL (`https://policyengine.github.io/policyengine-nz/`)
directly, which was then independently verified: `PolicyEngine/policyengine-nz` is a real,
current repository (17 commits on `main` as of the verification date, active GitHub Actions
test workflow), not the unrelated third-party `rulespec-nz` project. This review has been
corrected throughout to reflect the real project. This is logged here rather than silently
fixed, consistent with the doctrine of flagging rather than silently resolving a factual gap
in the source material.

---

## 2. Licence and copyright summary

### OpenFisca Aotearoa

- **Licence:** GNU Affero General Public License v3.0 (AGPL-3.0) — full text present in repo.
- **Copyright holder:** The LICENSE file carries only the FSF's own standard AGPL boilerplate
  copyright notice, not a project-specific one. No separate NOTICE file or project copyright
  header was located in the pages inspected. **Unconfirmed** — would need a direct check of
  source-file headers or a NOTICE file to identify the actual rights-holder(s) (e.g. DIA /
  Service Innovation Lab / individual maintainers).
- **What AGPL-3.0 permits:** use, modification, and redistribution, including commercial use;
  includes an express patent grant from contributors.
- **What AGPL-3.0 requires:** source availability to any user who interacts with the software
  over a network (the clause distinguishing AGPL from plain GPL — no "SaaS loophole");
  derivative/modified works must themselves be AGPL-3.0; copyright and licence notices must be
  preserved.
- **Practical consequence for Poltika:** this is a **strong, network copyleft** licence. Any
  Poltika code that incorporated, linked, or was a "modified version" of OpenFisca Aotearoa
  code would itself have to be released under AGPL-3.0 — including if only exposed as a
  network service (which is exactly Poltika's intended FastAPI deployment shape). This makes
  the licence unsuitable even for "convenient scaffolding," not just full ports. Poltika's
  existing `ip-doctrine.md` and ADR-0001 (reference/pattern-review only, never code reuse)
  already anticipates and covers this; this review confirms *why* that rule matters
  concretely for this specific repository.

### PolicyEngine New Zealand (`PolicyEngine/policyengine-nz`)

- **Repository confirmed:** `github.com/PolicyEngine/policyengine-nz`, commit
  `fbd186bd9a40633d5fc106750838b9cae40e71c3` (HEAD of `main`, pinned 2026-09-21).
- **Licence:** AGPL-3.0, per the repository's own README statement and LICENSE file.
- **Copyright holder:** Not independently confirmed beyond the standard AGPL licence text in
  this pass (the page fetch surfaced GitHub's own page-footer copyright, not a project-specific
  NOTICE); would need a direct LICENSE/NOTICE-file read to confirm the specific PolicyEngine
  entity named as rights-holder.
- **What AGPL-3.0 permits/requires:** identical terms to OpenFisca Aotearoa above — use,
  modification, and redistribution permitted; network-copyleft requirement (source must be made
  available to any user interacting with the software over a network); derivative/modified
  works must remain AGPL-3.0; copyright/licence notices preserved; express patent grant.
- **Practical consequence for Poltika:** the same as for OpenFisca Aotearoa, and arguably more
  pointed — `policyengine-nz` is built on `policyengine-core`, itself a fork of OpenFisca-Core,
  so it inherits the same lineage and the same licence family. It is **not** a lower-risk
  alternative to OpenFisca Aotearoa; both are equally unsuitable as anything but conceptual
  reference under Poltika's existing IP doctrine.
- **Note:** the general PolicyEngine platform (`policyengine-core`, `policyengine-app`) was
  also reviewed at a conceptual level in Stage 1 before this NZ-specific repository was found;
  that general-platform material remains accurate and is retained below, but should now be read
  as background to a real NZ implementation, not as a stand-in for a missing one.

### Distinguishing copyrightable expression from non-copyrightable material

| Category | Treatment in this review |
| --- | --- |
| Facts/concepts not copyrightable in themselves (e.g. "family scheme income aggregates a couple's income," "accommodation costs are compared to an area-based maximum") | Freely discussed below in Poltika's own words; these are policy facts, not the external project's expression. |
| Public government data and legislation (Income Tax Act 2007, Social Security Act 2018, IRD/MSD published tables) | Always the primary source; External-project structure only *pointed toward* which of these to check, never supplied the value. |
| Public interfaces/schemas (e.g. "a REST endpoint that accepts a household scenario and returns computed entitlements") | Treated as an interoperability/architecture pattern, safe to discuss abstractly. |
| Project documentation (READMEs, docs pages) | Read for orientation only; no passages copied or closely paraphrased. |
| Implementation code and other copyrightable expression | Not inspected beyond directory/README level; never a source for Poltika logic, values, or text. |

---

## 3. Capability matrix

Conceptual only — "✓" means the capability/pattern is present at an architectural level, not
that identical code exists.

| Capability | Poltika (documented architecture) | OpenFisca Aotearoa | PolicyEngine New Zealand |
| --- | --- | --- | --- |
| Dated/versioned policy parameters | ✓ (versioned YAML, `policy_specs/`) | ✓ | ✓ |
| Explicit calculation dependency graph | ✓ (documented as a target concept; not yet implemented) | ✓ | ✓ |
| Canonical semantic layer decoupled from source format | ✓ (`raw → processed → canonical variables → simulator`, frozen as doctrine) | Not confirmed at this depth of inspection | Not confirmed at this depth of inspection |
| Person/household/family entity model | Implied by "canonical semantic data layer," **not yet explicitly specified** | ✓ (framework-level person + group-entity pattern) | ✓ (people/household entities per README quick-start) |
| REST scenario API | ✓ (planned, FastAPI, gated behind pure-calculator acceptance per BUILD_PLAN Task 21) | ✓ (existing) | Package/API-reference documented; hosted-app exposure via the broader PolicyEngine platform |
| Baseline-vs-reform/counterfactual comparison | Not yet an explicit capability (scenario/version system exists but "diff two scenarios" isn't a named feature) | Not observed | ✓ (inherited PolicyEngine "reform" concept) |
| Deterministic core with LLM excluded from calculation | ✓ (frozen doctrine, `llm_boundaries.md`) | N/A (no LLM layer) | N/A (no LLM layer) |
| Three-class test doctrine (spec/benchmark/regression) with protected statutory values | ✓ (frozen, CI-protected) | Has *a* test suite (`make test`); exact taxonomy not confirmed at inspected depth | Has automated CI test workflow; exact taxonomy not confirmed at inspected depth |
| Source-first provenance discipline (sources.yaml, dated decision artifacts) | ✓ (already in active use for WFF/AS) | Not confirmed as an equivalent formal mechanism | Not confirmed as an equivalent formal mechanism |
| Explicit ambiguity-escalation process | ✓ (`review-doctrine.md`, decision artifacts) | Not observed/confirmed | Not observed/confirmed |
| Discovery / Hypothesis / Assurance capability tiers | ✓ (roadmapped, post-v0.2 for Discovery/Hypothesis; Assurance is v0.1) | Not an architectural concept in either project | Not an architectural concept in either project |
| Multi-country/jurisdiction abstraction | Explicitly not a goal (NZ-only) | N/A (NZ-specific by design) | N/A for this package (NZ-specific), but part of a multi-country platform (US/UK/Canada/NZ) |
| NZ Working for Families coverage | In progress (Week 0 spec complete, no implementation) | Directory-level evidence of an equivalent "family scheme" area exists | **Explicitly named** in README: Family Tax Credit, In-Work Tax Credit, Best Start |
| NZ Accommodation Supplement coverage | In progress (Week 0 spec complete, no implementation) | Directory-level evidence of an equivalent area exists | **Explicitly named** in README as a covered domain |
| Governance/maintenance continuity | N/A — too early to assess | Apparent maintenance discontinuity (suspended PyPI releases, incomplete install docs after a government→volunteer handover) | Appears actively maintained (organisation-backed, active CI); not deeply assessed |

Both external projects, not just OpenFisca Aotearoa, now directly overlap with Poltika's two
current vertical slices. This raises the same IP-doctrine caution twice, not once: neither
project's implementation, values, or tests may be used as a source for Poltika's WFF or AS
logic, regardless of how structurally close their named domains are to Poltika's own scope.

---

## 4. Important domain concepts discovered

These are described in Poltika's own words, as domain modelling problems to solve — not as
implementation patterns to copy.

1. **Individual-vs-group assessment split.** Several NZ payments are calculated primarily at
   an individual level but with relationship/household modifiers (e.g. family scheme income
   aggregates a couple's income under the Income Tax Act 2007; Accommodation Supplement
   treats joint tenants as one unit under the Social Security Act 2018 s 68). Poltika's
   canonical semantic layer will need an explicit entity model that distinguishes at least
   "person" from "assessment unit" (couple/family/household), because both of Poltika's
   current vertical slices depend on this distinction. This is not yet explicit in Poltika's
   current specs — see gap G1 below.

2. **Effective-dated, non-retroactive parameter change.** Both external projects and
   Poltika's own WFF/AS specifications show the same underlying problem: a statutory rate or
   threshold applies only from its legislated effective date, and a calculation for an
   earlier period must use the value that was in force then, not the current value. Poltika's
   `policy_specs` already captures this (e.g. WFF's "From 1 April 2026" vs. "From 1 April
   2027" rows); this confirms the pattern, it does not introduce a new requirement.

3. **Variable-depends-on-variable calculation ordering.** A benefit calculation is rarely a
   single formula — it is a graph of intermediate quantities (e.g. "qualifying accommodation
   costs" → "excess over threshold" → "70% rate" → "area/household cap" → "income reduction" →
   "rounding"), each potentially defined by different statutory provisions. This matches
   Poltika's own AS specification's "Calculation order and cross-policy boundary" section
   almost exactly. The external projects confirm this is a standard, unavoidable structure for
   this problem domain, not a Poltika-specific complexity.

4. **Cross-policy income definitions that are not identical.** Poltika's own AS specification
   already documents that IRD's treatment of Accommodation Supplement as non-taxable income
   (for WFF purposes) and MSD's treatment of IRD-paid WFF credits (for AS purposes) are
   *asymmetric, source-specific carve-outs*, not a single shared "family income" concept. Any
   system modelling both policies needs an explicit boundary here rather than a shared income
   variable reused naively across policies. This is a domain lesson independently confirmed by
   Poltika's own primary-source work, not something taken from either external project.

5. **Unsupported-input handling as a first-class outcome.** Poltika's own specifications
   already require that unsupported adjustment/exception paths return a "needs review"
   outcome rather than a false zero. This is a strong existing Poltika design decision; no
   external project practice should weaken it.

---

## 5. Relevant authoritative NZ Government sources

Already established and in active use in `policy_specs/*/sources.yaml`, not newly discovered
here — restated for completeness since this review touches the same domains:

- Income Tax Act 2007, Part M (Working for Families) — the governing primary source.
- Social Security Act 2018, ss 65AAA–69 and Schedule 4 Part 7; Social Security Regulations
  2018, rr 15–19 — Accommodation Supplement.
- IRD published interpretation statements and worked examples (family tax credit, in-work tax
  credit, minimum family tax credit, Best Start).
- MSD published rate tables and worked examples (rent/board examples, income-reduction
  examples, area/household rate tables).
- Statistics NZ Statistical Area Units — referenced by the AS geographic-area lookup (AS-05);
  this is the one dataset in Poltika's current scope that plausibly needs an external
  *dataset*, not just a legislated rate, and is already flagged in `BUILD_PLAN.md` Task 22a.

No new authoritative source was discovered via the external projects that Poltika's own
source-mapping had missed. The external projects' *directory structure* pointed at NZ concepts
(e.g. "family_scheme", "accommodation_supplement" as named areas) that happen to match
Poltika's already-independently-chosen scope — this is corroboration of scope, not a new
source lead.

---

## 6. Architectural lessons

1. **The "canonical variable, decoupled from source format" pattern is validated as an
   industry-standard shape**, not a speculative Poltika invention. Both external projects
   independently arrived at a variable/parameter/entity separation. Poltika's stricter
   layering rule (`data/ → semantics/ → policy/ → engines/ → scenarios/`, with an explicit
   "must not depend on" table) is *more* disciplined than what was observable in either
   external project's public documentation, and there is no reason found here to relax it.

2. **Government-run rules-as-code projects carry real continuity risk.** OpenFisca Aotearoa's
   history (Service Innovation Lab → closure → volunteer maintenance, with suspended package
   releases and incomplete install docs) is a concrete illustration of what can happen when a
   rules-as-code project's institutional backing lapses. This is a governance lesson for
   Poltika's own long-term source-provenance and maintenance planning, not an architecture
   change — but it reinforces the value of Poltika's `sources.yaml` + dated decision artifacts
   as a defence against provenance drift if Poltika's own stewardship ever changes hands.

3. **Canonical-repo ambiguity is a real failure mode, not a hypothetical one.** OpenFisca
   Aotearoa itself exists as multiple apparently-related copies across three GitHub
   organisations, with no easily discoverable canonical-upstream signal. This is direct
   evidence for why Poltika's own single-repository, dated-ADR, versioned-schema discipline
   matters: it is specifically the kind of provenance ambiguity Poltika's doctrine is designed
   to prevent from happening to Poltika itself.

4. **A reform/baseline comparison concept is a deliberate, separate design decision, not a
   free side-effect of a scenario system.** PolicyEngine's explicit "reform vs. baseline" layer
   is architecturally distinct from just "having scenarios." If Poltika wants this capability
   (comparing a policy-as-legislated run against a policy-as-proposed run), it should be
   scoped as its own decision against Poltika's scenario/version/provenance system — not
   assumed to already exist because a scenario system exists. See §7, G2.

5. **A self-documenting API surface is a low-cost, high-value operational pattern** (OpenFisca
   Aotearoa's `/spec`-style endpoint) that fits naturally under Poltika's already-chosen
   FastAPI + Pydantic stack (which can generate equivalent OpenAPI documentation essentially
   for free). Not a gap, just a reminder to actually turn it on when the API task is reached.

---

## 7. Potential gaps in Poltika's current architecture/specs

Classified per the required taxonomy: REQUIRED FOR V0.1 / CONSIDER POST-V0.1 / ALREADY
COVERED / REJECT.

**G1 — Explicit person-vs-assessment-unit entity model.**
Poltika's `ARCHITECTURE.md` and `REPOSITORY_STRUCTURE.md` name a "canonical semantic data
layer" but do not yet explicitly document an entity model distinguishing "person" from
"assessment unit" (couple/family/household), even though both WFF (family scheme income
aggregation) and AS (joint-tenant treatment) already require it per Poltika's own
specifications. This is a case where Poltika's *architecture doctrine* already implies the
need; the external review simply surfaces that it isn't written down yet.
**Classification: REQUIRED FOR V0.1** — it is squarely inside Task 4 ("Derive minimal
POLICY_SPECS v0.1 schema from both policies' actual requirements") and Task 11 (parameter
loader) already on the BUILD_PLAN, not a new scope addition; it should simply be made
explicit as the schema is derived, independently from primary sources (the Income Tax Act's
"family scheme" definitions and the Social Security Act's "joint tenant"/"spouse or partner"
provisions already cited in the existing specs) — never derived from OpenFisca Aotearoa's own
entity implementation.

**G2 — Baseline-vs-reform (counterfactual) comparison capability.**
Not currently named anywhere in Poltika's roadmap or architecture as an explicit feature of
the scenario system.
**Classification: CONSIDER POST-V0.1.** It is plausible future value (e.g. "what would this
household receive if the abatement threshold were raised") but is out of scope for the
Scope Doctrine's "deterministic correctness before probabilistic sophistication" framing and
is not needed to complete the WFF/AS vertical slices. If pursued, it should be designed from
Poltika's own scenario/version/provenance requirements, not copied from PolicyEngine's
mechanism.

**G3 — Self-documenting API introspection endpoint.**
**Classification: ALREADY COVERED (effectively).** FastAPI + Pydantic already generates
OpenAPI schema/documentation by default; no separate design work is implied. Worth a one-line
note in `ARCHITECTURE.md`'s API section when Task 21 is reached, but not a gap requiring new
design.

**G4 — Formal "coverage taxonomy" for what counts as a supported vs. unsupported input.**
Poltika's own WFF and AS specifications already require "needs-review, not a false zero" for
unsupported paths — this is arguably *ahead* of what was observed in either external project.
**Classification: ALREADY COVERED.**

**G5 — Explicit project-continuity/succession doctrine.**
Neither Poltika's current doctrine set nor either external project's public materials
describe what happens to a rules-as-code project if institutional support changes (this is
precisely what happened to OpenFisca Aotearoa).
**Classification: CONSIDER POST-V0.1** — not urgent at Week 0, but worth a short ADR at some
later point given the concrete cautionary example found; not a v0.1 blocker.

**G7 — A second, closer external structural comparator now exists for both current vertical
slices.**
`PolicyEngine/policyengine-nz` explicitly names Family Tax Credit, In-Work Tax Credit, Best
Start, and Accommodation Supplement as covered domains — a closer structural match to
Poltika's exact v0.1 scope than OpenFisca Aotearoa's broader area listing. This does not change
any doctrine: the IP Doctrine's Task-16 "external coverage-gap check" (structural/coverage
concepts only, strictly after each vertical slice's own test suite is complete) already
anticipates exactly this kind of comparator and already forbids treating it as a source of
logic or values. **Classification: ALREADY COVERED** by existing doctrine — but flagged so that
when Task 16 is actually performed for WFF and AS, `policyengine-nz` is included alongside
OpenFisca Aotearoa as a comparator, not overlooked because this review initially missed it.

**G6 — Multi-jurisdiction/country abstraction layer.**
Both external projects (well, PolicyEngine specifically) generalise across countries.
**Classification: REJECT.** Poltika's scope is explicitly NZ-only per Scope Doctrine and the
v1.0 definition in `BUILD_PLAN.md`; building a jurisdiction-abstraction layer now would be
exactly the "speculative abstraction" the Architecture Doctrine warns against. No evidence
from this review suggests NZ-only scope is insufficient for Poltika's stated goals.

---

## 8. Concepts explicitly rejected as inappropriate for Poltika

- **Multi-country/jurisdiction generalisation** (PolicyEngine's core design goal) — rejected;
  Poltika is deliberately and permanently NZ-scoped per Scope Doctrine, and generalising now
  would violate the Architecture Doctrine's "minimum abstraction demanded by two real
  policies" rule.
- **Adopting OpenFisca-Core or policyengine-core as a dependency** — rejected; Poltika's stack
  is already frozen (Python + FastAPI + Pydantic + versioned YAML, own `DomainEngine`
  interface), and both external cores carry AGPL-family licence obligations that are
  incompatible with treating them as a dependency without accepting network-copyleft
  consequences for the whole deployed system. Not evaluated further per doctrine — this was
  never a live option.
- **Treating either project's directory/folder structure as a template to reproduce
  wholesale** — rejected per explicit user instruction and Poltika's IP doctrine; only the
  *fact* that comparable NZ policy areas exist elsewhere was noted, never the structure
  itself.
- **Using `rulespec-nz` (the third-party "PolicyEngine-style" NZ project) as any kind of
  oracle** — rejected; it explicitly describes itself as non-authoritative, and Poltika's own
  benchmark-test doctrine (independently recalculated from IRD/MSD worked examples) is already
  a stronger validation mechanism.

---

## 9. Potential v0.1 implications

- G1 (entity model) should be considered while Task 4 (minimal POLICY_SPECS schema) and Task
  11 (parameter loader) are executed — it does not require new BUILD_PLAN tasks, just
  attention within tasks that already exist.
- No other finding in this review implies a new v0.1 task, a schema redesign, or a change to
  the frozen Development/Architecture/Scope/Test/Review/Data-Acquisition doctrines. The
  external review corroborates the current plan more than it challenges it.
- The AGPL-3.0 finding is a reason to *continue* the existing IP doctrine exactly as written
  (reference/pattern-review only, never code/text reuse) — it does not require a doctrine
  change, only confirms the existing one is well-founded and should not be loosened.

---

## 10. Post-v0.1 opportunities

- Consider a short ADR on baseline-vs-reform scenario comparison (G2) once the Hypothesis
  capability phase is reached (per the Roadmap Doctrine's capability-driven ordering) — this
  is conceptually closer to "Hypothesis" than to the deterministic Simulator.
- Consider a brief project-continuity/succession note (G5) at some point post-v0.1, informed
  by OpenFisca Aotearoa's observed maintenance-discontinuity history as a cautionary case, not
  as a template to copy.
- If Poltika ever wants a lightweight external cross-check tool (distinct from, and never a
  replacement for, the benchmark-test doctrine), the existence of `rulespec-nz` as a precedent
  for that *pattern* (not its content) could inform a future, separately-scoped decision.

---

## 11. Provenance/source notes

- Stage 1 research was conducted via WebSearch/WebFetch against public repository metadata,
  README/documentation pages, and directory listings only. No source code, tests, comments, or
  documentation passages were copied or closely paraphrased. No exact statutory rate,
  threshold, or eligibility value from either external project was recorded anywhere in the
  underlying research notes or this report.
- Full Stage 1 research notes (concept-by-concept records, per the required format) are
  preserved at
  `/private/tmp/claude-501/-Users-peterhemmingsen-Poltika/718795b0-5e68-4a7d-aee9-8aa1e45c9e18/scratchpad/stage1_research_notes.md`
  for this session; that path is a scratch location outside the Poltika repository and is not
  committed. If the research notes themselves need to be preserved for future audit, that
  should be a deliberate decision (e.g. copying them into `review_packets/` or an ADR
  attachment) rather than an automatic side-effect of this task.
- **Open uncertainties carried forward from Stage 1, not resolved by Stage 2 (flagging rather
  than assuming, per instructions):**
  1. Canonical-repo status among `digitalaotearoa/openfisca-aotearoa`,
     `BetterRules/openfisca-aotearoa`, and `ServiceInnovationLab/openfisca-aotearoa` was not
     verified; `digitalaotearoa` was treated as the likely current copy based on search-result
     framing only.
  2. OpenFisca Aotearoa's project-specific copyright holder (distinct from the AGPL's own FSF
     boilerplate) was not located; would need a NOTICE file or source-header check.
  3. `PolicyEngine/policyengine-nz`'s licence (AGPL-3.0) was confirmed via the repository's own
     README statement and LICENSE file, but its **specific copyright/rights-holder notice**
     was not independently confirmed beyond the standard licence boilerplate — would need a
     direct LICENSE/NOTICE-file read. The general `policyengine-core` platform's own licence was
     not separately re-verified after this correction, since the NZ package's own confirmed
     licence is now the operative fact for direct comparison purposes.
  4. This review initially, incorrectly, concluded no NZ-specific PolicyEngine package existed.
     That was corrected after the user supplied `https://policyengine.github.io/policyengine-nz/`
     directly; `PolicyEngine/policyengine-nz` is confirmed real (commit
     `fbd186bd9a40633d5fc106750838b9cae40e71c3`). This should be treated as a caution about this
     review's own search-based Stage 1 methodology — a negative "no such repo found" result from
     web search is not reliable evidence of non-existence, and should be stated as "not found by
     this search," not "does not exist," in any future review of this kind.
  5. OpenFisca Aotearoa's actual entity-model implementation and test-file format were not
     inspected beyond the generic OpenFisca framework pattern, per the hard stop rule for
     anything that would require close implementation study.

---

## 12. Clean-room compliance notes

- Poltika's own architecture (`ARCHITECTURE.md`, `BUILD_PLAN.md`, `REPOSITORY_STRUCTURE.md`,
  `ROADMAP.md`, `doctrine/`, and both current `policy_specs/*/specification.md` files) was read
  and understood **before** either external project was inspected, per the task's explicit
  ordering requirement.
- Stage 1 (external research) and Stage 2 (this synthesis) were kept separate: Stage 1 recorded
  conceptual observations only and explicitly avoided drawing Poltika-specific conclusions;
  Stage 2 was written independently against Poltika's own requirements and doctrine, using
  Stage 1 only to prompt "has Poltika considered X," never as an implementation template.
- No source code, tests, comments, or documentation passages from either external project were
  copied, translated, or closely paraphrased into this report or into any Poltika production
  file. No production code was written or modified as part of this task.
- No distinctive variable/class/function names from either external project were recorded,
  other than externally-defined NZ government terminology (e.g. "family scheme," "accommodation
  supplement") that Poltika's own specifications already use independently, sourced directly
  from the Income Tax Act 2007 and Social Security Act 2018.
- No statutory rate, threshold, or eligibility value from either external project was recorded
  as fact anywhere in the Stage 1 notes or this report; every policy-domain reference is at the
  level of "this project appears to have an area corresponding to NZ concept X," never a value.
- Per the IP Doctrine's post-suite exception (`BUILD_PLAN.md`), this review is a research/gap
  exercise, not the Task-16 external-coverage-gap check; that check remains a separate,
  narrower activity to be performed strictly after each vertical slice's own test suite is
  complete, per the frozen sequence.
- This report does not modify `BUILD_PLAN.md`. Proposed build-plan-adjacent notes are given
  separately below, for human review, and are not applied automatically.

---

## Proposed build-plan notes (for human review only — not applied)

These are observations, not edits to `BUILD_PLAN.md`. Pete/GPT should decide whether any of
these warrant an actual BUILD_PLAN or ADR change.

1. When Task 4 (minimal POLICY_SPECS v0.1 schema) is executed, consider explicitly naming an
   entity concept for "assessment unit" (couple/family/household) alongside "person," derived
   from the Income Tax Act 2007's family scheme provisions and the Social Security Act 2018's
   joint-tenant/partner provisions already cited in the existing specs — not from any external
   project's entity model.
2. Consider logging a one-line ADR confirming this review's Stage 1/Stage 2 sequence was
   followed, consistent with the IP Doctrine's instruction to "log a one-line ADR confirming
   this sequence was followed for both touchpoints" (the Task 3 structural-glance touchpoint
   and this post-hoc comparative-review touchpoint are distinct; this review is the latter and
   was performed ahead of WFF test-suite completion at the user's explicit request, which is a
   deliberate deviation from the doctrine's default "after WFF test suite is complete" timing —
   worth Pete/GPT explicitly acknowledging that sequencing choice in the ADR).
3. No change to the frozen Development/Architecture/Scope/Test/Review/Data-Acquisition
   doctrines is proposed by this review.
