# v0.1 demo: one household, both policies, end to end (Task 35)

**The question (Task 35.1):** *A couple with two children earn $50,000 and
$20,000 a year. They rent in an Area 1 location for $600 a week and have
$2,000 in savings. What Working for Families (WFF) tax credits and what
Accommodation Supplement (AS) does Poltika calculate for them, and does
either payment reduce the other?*

This is golden household g2
(`policy_specs/wff_as_interaction/golden_households.yaml`). It was chosen
because it is inside both supported domains and exercises the most of
each policy: WFF abatement on a partnered income, AS's non-beneficiary
income reduction, and the interaction question itself. A beneficiary
household would not work here: since the Task 34.3 F1 correction, its WFF
components are `unsupported` (MD 14/15 and MG 4 protected months).

**The surface (Task 35.2):** the API plus the provenance report, as the
plan recommended. The run was made through `POST /scenarios` and stored in
PostgreSQL, then fetched and replayed.

## How it was run

- **Request:** [`request.json`](request.json). WFF uses the 2026-27 tax
  year (lookup date 1 June 2026). AS uses the week of 1 June 2026, from 1
  to 8 June with the end excluded. These are the Task 28.2 dates.
- **Steps:**
  1. `POST /scenarios` ran both policies and stored the run.
  2. `GET /scenarios/{result_id}` fetched it back.
  3. `POST /scenarios/{result_id}/replay` re-ran it against the stored
     policy files.
- **Code:** a clean checkout of commit
  `61564c35517fb1abf195b511af64f9d2d6defd2e`, so the run is marked
  reproducible.
- **Output:** [`response_summary.json`](response_summary.json) (results,
  ids and replay) and [`provenance_report.md`](provenance_report.md), the
  full report built from the stored run.
- **Identifiers:** scenario id `4b37f0b0…`, result id `c2156938…`.
- **Replay:** `reproduced: true` and `code_matches: true`.

## The answer

| Policy | Component | Period | Outcome | Amount |
| --- | --- | --- | --- | --- |
| WFF | Family tax credit | 2026-27 tax year | calculated | **$7,472.50 a year** |
| WFF | In-work tax credit | 2026-27 tax year | **needs_review** | none |
| WFF | Minimum family tax credit | 2026-27 tax year | calculated | $0 |
| WFF | Best Start | 2026-27 tax year | calculated | $0 |
| AS | Accommodation Supplement | week of 1 June 2026 | calculated | **$220 a week** |

Each policy stays in its own period. There is **no combined total**: an
annual tax-credit entitlement and one week's supplement are not added
together or converted into each other.

**How the amounts were reached** (the provenance report cites each
parameter's source):

- **Family tax credit:**
  1. The full rate is $7,921 for the eldest child plus $6,454 for the
     second, which gives $14,375.
  2. Family income is $70,000, which is $25,100 over the $44,900
     threshold. It abates at 27.5% of each complete dollar, a reduction of
     $6,902.50.
  3. $14,375 − $6,902.50 = **$7,472.50**.
- **Minimum family tax credit:** it tops income up to $36,604. Income is
  already above that, so it is $0.
- **Best Start:** neither child is in a Best Start entitlement period, so
  it is $0.
- **In-work tax credit:** `needs_review`. The 2026-27 base rate is
  uncertain because of a possible reversal Order in Council that has not
  been made (Task 26b), and Poltika does not guess it.
- **Accommodation Supplement:**
  1. The subsidy is 70% of the rent above the $205 entry threshold for a
     couple with children: 70% × ($600 − $205) = $276.50. That is under
     the $305 cap for Area 1.
  2. Weekly income is $1,346, which is $229 above the $1,117 income level.
     A quarter of that excess ($57.25) is deducted.
  3. $276.50 − $57.25 = $219.25, rounded up under r 19 to **$220**.
  4. Savings of $2,000 are below the $5,400 level at which income is
     imputed from assets.

**Does one payment reduce the other?** No:

- WFF tax credits are excluded from AS chargeable income, whichever agency
  pays them (Schedule 3 cl 8(1)(l); DEC-003).
- Non-taxable AS is excluded from WFF family scheme income (AS-10,
  `as-ird-other-income`).
- The combined run feeds neither amount into the other policy's
  calculation. Its shared-fact checks found no disagreements.

## Limitations: read these before using the numbers

- **A conditional simulation, not an entitlement determination.**
  - Every fact in the request is the caller's assertion. Poltika has not
    verified the incomes, the relationship, the children, the tenancy,
    the savings or the location.
  - IRD and MSD decide actual entitlement from their own verified
    information.
- **Inside the supported domain only.** Things v0.1 does not model:
  - shared care;
  - part-year children, and changes of circumstance during the year;
  - the protected-credit (MD 14/15, MG 4) and direct-abatement pathways;
  - homeowners, and board or lodging variations;
  - mixed-benefit couples;
  - NZ Superannuation;
  - payment timing, instalments and overpayments.

  A household outside that domain is reported as `unsupported` or
  `needs_review`, never as a guessed number.
- **The incomes are simplified.**
  - The WFF income is a synthetic, attested figure, with net income set
    equal to gross.
  - The AS weekly income ($1,346) is asserted directly rather than derived
    from the annual incomes.
  - Real households' figures would differ.
- **The in-work tax credit is not calculated** until the 2026-27 in-work
  base rate is confirmed. The WFF total for this family is therefore
  incomplete.
- **One week of AS.** $220 is the amount for the assessed week under the
  1 April 2026 tables, not a promise for later weeks.
- **Dates are fixed.** The results use the policy values effective on the
  stated dates. Changes after those dates are not reflected.
