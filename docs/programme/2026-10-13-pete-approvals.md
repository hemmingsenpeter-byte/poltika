# Pete approval record — 13 October 2026

Recorded by Claude Code from Pete's instruction in a Claude Code session on
13 October 2026. The instruction approved the session's written
recommendations in full; they are restated below as the approved decisions.
This records Pete's decisions. It does not independently verify a statutory
rule, approve a protected expected value, or clear a PR's review or CI.

## The instruction

**"approve and proceed on all"**, on the session's recommendations for the
open items raised by #215's research and reviews: B4, Q19 (1), (2) and (5),
Q2 and Q3. Earlier in the session Pete also approved posting the #215 review,
merging #215 and starting the MAP-01 fix ("yes").

## Decisions

| Item | Decision | Remaining action |
| --- | --- | --- |
| B4 (incomplete $100 asset blocks) | s 423(3) counts only complete $100 steps over the threshold, as the engine already does. Recorded as AS [DEC-004](../../policy_specs/accommodation_supplement/decisions/DEC-004-asset-imputation-complete-steps.md). MSD is not contacted. | The part-hundred boundary rows (2,799.99; 5,499.99) are no longer blocked by the interpretation; they go through the test-doctrine process with the other boundary cases. |
| Q19 (1) | An AS stock amount has no period. A parameter (ceiling, threshold, step) applies over its validity dates; a household's `cash_assets` is the balance the caller asserts for the assessment week. Poltika chooses no snapshot date and averages nothing. | Done in the MAP-01/Q19 PR: unit binding `NZD` is `NONE`, with the wording in `household.py` and `household_mappings.py`. |
| Q19 (2) | Keep the separate caller-resolved WFF and AS child facts. The adapter's marking of the first N synthetic children as AS children is an engineering device for an unchanged aggregate round trip, not child membership. Component-specific WFF membership waits for part-year WFF work. | Labelled in `household_mappings.py`. Nothing reads those ids as membership today. |
| Q19 (5) | Keep the whole-year WFF assertions. A main-benefit spell (Jobseeker Support, Sole Parent Support, Supported Living Payment) of the claimant or partner inside the tax year contradicts a verified whole-year no-benefit assertion (in-work eligibility, MC 6(b)) and is refused: dates only, nothing apportioned (Q10, D32). Part-year cases stay `needs_review`/`unsupported`; combined.py's conservative protected-credit flags stay. | Done in the MAP-01/Q19 PR. Task 6 step 1.4 (retire the pairwise checks for household inputs, D36 (4)) is now unblocked and is Claude Code's next Task 6 step. |
| Q2 | Keep Q2 parked and the interim ban on ethnicity- and iwi-disaggregated outputs in force. Name nobody yet: no dataset or use exists to scope. Reference frameworks for a future proposal: Ngā Tikanga Paihere and the Te Mana Raraunga principles, with Te Kāhui Raraunga's Māori Data Governance Model as further reading. Poltika does not claim to adopt them unilaterally. | Trigger: the first proposed use of Māori data or an IDI project. Then commission a bounded governance proposal and decide whom to engage (Pete). |
| Q3 | Keep the IDI application deferred; no contact with Stats NZ. | Trigger: Gate E (population calibration) in view. Then commission a one-page project scope and dataset-feasibility check that first asks whether public aggregates or a CURF would answer the question. Contact and lodging stay Pete's. |
| B1–B3 (P3s) | Fix the three documentation notes in the boundary proposal. | Done in the MAP-01/Q19 PR. |
