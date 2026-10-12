# GPT/Codex research briefs, 12 October 2026

Prepared by Claude Code on Pete's instruction of 12 October 2026, which
commissioned these readings
([record](../docs/programme/2026-10-12-pete-approvals.md): Q2, Q3 and Q19).
Each brief asks for a dated, sourced reading. None of them decides anything:
Pete reviews each result and decides.

## Ground rules for all three

- **Sources:** primary New Zealand sources only, such as legislation.govt.nz
  versions, official agency publications and published agreements. Give the
  URL, the version or "as at" date, the locator (section, clause or page), and
  what the passage actually supports.
- **Model memory is not authority.** A claim with no retrieved source is
  marked unverified (`CLAUDE.md`, "Ground truth").
- **Evidence classes:** classify every claim with the eight classes in
  `doctrine/epistemic-constitution.md`. Where sources conflict or are
  ambiguous, set out the competing readings and do not choose between them
  (`doctrine/review-doctrine.md`).
- **No external policy engine.** Do not use OpenFisca, PolicyEngine or similar
  implementations (`doctrine/ip-doctrine.md` and the clean-room skill).
- **No outreach.** Do not contact anyone, and do not lodge or start any
  application or form.
- **Output:** write to the path named in each brief. End with a short "What
  Pete decides" section of options. Open one PR per brief and add a row to
  `review_packets/review_queue.md`.

## Brief 1 (Q2): Māori data governance

**Question.** Which governance obligations and expectations apply before
Poltika produces outputs disaggregated by ethnicity or iwi, or uses Māori
microdata? Who has standing to be engaged?

**Read.** The current versions of at least:
- Te Mana Raraunga's Māori data sovereignty principles;
- Stats NZ's Ngā Tikanga Paihere guidelines;
- any Stats NZ and iwi data agreements that are in force;
- the Data and Statistics Act 2022 and the Privacy Act 2020, where they apply
  to a non-government analytical tool.

Include any later framework the sources point to.

**Deliver** `docs/research/q2_maori_data_governance.md`:
- what each source requires or recommends, and from when;
- which Poltika capabilities it touches, and which it does not touch (the
  existing interim ban stays in place);
- the bodies or roles the sources say should be engaged, with how each source
  describes them;
- options for Pete. Name no individual.

## Brief 2 (Q3): IDI access route

**Question.** What is the current route, timeline and cost for an
Integrated Data Infrastructure project of Poltika's kind? What must be in
place before applying?

**Read.** Stats NZ's current microdata access pages and guidance:
- eligibility;
- the project application and its assessment criteria;
- researcher requirements and any accreditation;
- the access-safety framework;
- output-checking rules;
- charges;
- the data-lab or remote-access arrangements;
- expected processing times.

**Deliver** `docs/research/q3_idi_access_route.md`:
- the steps in order, with a source for each;
- what Poltika would need to prepare: the project scope, people, security and
  outputs;
- how IDI output-checking rules would constrain Poltika's published
  aggregates;
- open questions to put to Stats NZ, as a list for Pete. Do not send them.

## Brief 3 (Q19 parts 1, 2 and 5): household mapping readings

**Context.** These are the unresolved Task 5–6 mapping questions:
- `review_packets/task5_6_unit_binding_household_mapping.md`;
- `PETE_QUEUE.md` Q19;
- Pete's decisions on Q10 and D32: no apportionment, and each policy period
  gets its own amount.

**Questions.**

1. **Stock amounts in the Accommodation Supplement.** Is each stock amount
   (`NZD`) measured at a point in time or for the assessment week? This covers
   the cash-asset limits, the imputation thresholds and `cash_assets`. When is
   it measured?
2. **Dependent child.** Compare the dependent-child definitions in Working for
   Families and in the Accommodation Supplement, and say how they differ.
   Should `ChildFacts` hold one fact or two? What is the governing source on
   the AS side?
3. **Main benefit and the WFF tax year.** For the restated main-benefit check,
   how does a weekly main-benefit spell relate to the WFF tax year? Which
   provisions govern how a main benefit affects each WFF component during part
   of a year?

**Read.** Locate the governing provisions yourself in the current versions
of the Income Tax Act 2007, the Social Security Act 2018 and the Social
Security Regulations 2018, plus the agencies' operational guidance where the
statute leaves a point open. Cite the version dates.

**Deliver** `docs/research/q19_household_mapping_readings.md`. For each
question give:
- the reading;
- the sources it rests on;
- its evidence class;
- whether it confirms or conflicts with the current mapping (with file and
  line);
- any change it implies.

Changing a mapping or a refusal waits for Pete's review of this reading.
