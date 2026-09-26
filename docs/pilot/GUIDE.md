# Poltika pilot guide (v0.1.5)

For a pilot user who did not build Poltika. It covers running Poltika,
asking it a household question, and reading the answer.

## What Poltika is, and is not

Poltika calculates two New Zealand payments for one household:

- Working for Families for the 2026-27 tax year: family tax credit, in-work
  tax credit, minimum family tax credit and Best Start;
- the Accommodation Supplement for one week.

Every rate and threshold comes from a cited primary source.

A result is a **conditional simulation**: it assumes the facts you enter are
true. Poltika does not check them against any government record, and a
result is not an entitlement decision.

## Run it

With Docker installed, from the repository:

```sh
docker compose up --build
```

Then open <http://localhost:8000/analyst>. The API's own documentation is at
<http://localhost:8000/docs>. The policy files served are the ones in this
repository's `policy_specs/`, mounted read-only.

## Ask a question

1. On the analyst page, pick a case. The `Pilot:` cases each come with a
   question to answer; the `Golden:` cases are the reviewed golden
   households.
2. Edit the request if you want, for example incomes, rent, the number of
   children or the area.
3. Select **Calculate**.

Every fact is one you assert. `verified` means you are asserting you have
checked it; `unknown` means you haven't. An unknown fact is never treated as
zero or as "no".

## Read the answer

Each payment shows one of three statuses:

| Status | Meaning |
| --- | --- |
| **CALCULATED** | An amount, from the facts you asserted. $0 is a real, calculated zero. |
| **NEEDS REVIEW** | No amount. A fact or a rate is not verified; the page says which ("Waiting for"). |
| **UNSUPPORTED** | No amount, for one of two reasons. **Evidenced exclusion:** a verified fact excludes it, for example cash assets over the ceiling. **Not modelled:** the case is outside what this version calculates. |

Select **Why?** under any payment to see:

- **Calculation:** every arithmetic step, with the rule it applies (for
  example `WFF-03`) and the intermediate amounts.
- **Facts you asserted:** exactly which of your inputs the result used.
- **Rates and sources:** each rate or threshold, the dates it is in force,
  its source and legal provision, and its review status.

The explanation is generated from the calculation itself, and is checked by
tests to agree with it number for number.

**Download case report** saves the full response, including the provenance
report, as JSON.

## Known limits

- There is no Working for Families total. The in-work tax credit base rate
  for 2026-27 can be reversed early by Order in Council, so it stays
  NEEDS REVIEW, and a total is only given when every part is calculated.
- Each payment is shown in its own period (a tax year, or one week). The two
  are never added together.
- For the full list of what v0.1 does not calculate, see the limitations in
  `CHANGELOG.md` and each policy's specification.

## Challenge an answer

Pick one result and try to answer, from the page alone:

1. Do you believe it?
2. Where did the number come from?
3. Which rule governs it?
4. What did Poltika take from you as fact?
5. What is missing?

Record anything you couldn't answer. Those are the findings this pilot is
for (`docs/pilot/V0_1_5_PILOT_FINDINGS.md`).
