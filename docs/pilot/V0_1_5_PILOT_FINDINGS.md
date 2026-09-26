# v0.1.5 pilot: session script and findings

Tasks 8.3 and 8.4. Fill in the findings during and after the session. The
release gate needs at least one external pilot user, and no open P0 or P1
finding.

## Before the session (facilitator)

1. Run Poltika: `docker compose up --build`, then open
   `http://localhost:8000/analyst` (see `GUIDE.md`).
2. Brief the pilot user in two minutes, and no more:
   - Poltika calculates Working for Families and the Accommodation
     Supplement for one household, from facts you assert;
   - pick a case, press **Calculate**, then open **Why?**;
   - it is a conditional simulation, not an entitlement decision.
3. Do **not** explain the statuses, codes or panels. Where they get stuck is
   the finding.

## The session

The analyst page lists 15 pilot cases (`Pilot: p01` to `p15`), each with a
question. Aim for 10-20 cases in about an hour. For every case, record
where the user hesitated, what they misread and what they asked.

Then ask the user to pick one result they find surprising and answer, from
the page alone:

1. Do you believe it? Why, or why not?
2. Where did the number come from?
3. Which rule governs it?
4. What did Poltika take from you as fact?
5. What information is missing?

### Facilitator notes: what each case shows

For the facilitator only. Don't show this to the pilot user. The outcomes
are what Poltika produced on 26 September 2026 (WFF 0.1.0, AS 0.1.1), not
independently derived expectations.

| Case | Shows |
| --- | --- |
| p01 | Ordinary couple: family tax credit abated; in-work credit NEEDS REVIEW (rate pending); AS calculated |
| p02 | Sole parent: minimum family tax credit top-up; AS calculated under the cap |
| p03 | No children: WFF not modelled; AS limited by the area maximum |
| p04, p05 | Beneficiary households: WFF protected-credit paths not modelled; AS calculated |
| p06 | Cash assets impute income that reduces AS |
| p07 | Partner income missing: family tax credit NEEDS REVIEW and names the fact; in-work credit waits on it |
| p08 | Policies told different child counts: everything NEEDS REVIEW, disagreement shown |
| p09 | Assets over the ceiling: AS UNSUPPORTED, evidenced exclusion |
| p10 | Homeowner: AS UNSUPPORTED, not modelled |
| p11 | Area unknown: AS NEEDS REVIEW, never defaulted |
| p12 | High income: family tax credit abated to a calculated $0 |
| p13 | Main benefit received: in-work and minimum family tax credits UNSUPPORTED, evidenced exclusion |
| p14 | No accommodation costs: AS UNSUPPORTED, not a calculated $0 |
| p15 | Claimant link unverified: everything NEEDS REVIEW, waiting for that fact |

## Findings

Classify each finding:

- **P0:** a wrong answer.
- **P1:** a misleading explanation, label or status.
- **P2:** missing evidence.
- **P3:** confusing UX.
- **P4:** cosmetic.

v0.1.5 does not ship with an open P0 or P1.

| # | Case | What happened | Class | Owner | Disposition |
| --- | --- | --- | --- | --- | --- |
| F0 | p15 (found while building the pack, 26 Sep) | An unverified claimant link was coded as a disagreement between the policies | P1 | Claude Code | Fixed in Sprint 2 S2.2: now `COMBINED_CLAIMANT_LINK_UNVERIFIED`, naming the missing fact |
| F1 | | | | | |

## Pilot user

- Pilot user:
- Background (public policy, tax/welfare modelling, government analysis):
- Date:
- Facilitator:
- Could the user answer questions 1-5 unaided? For which cases?
