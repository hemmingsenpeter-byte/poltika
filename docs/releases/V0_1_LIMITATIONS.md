# What Poltika v0.1 does not calculate

v0.1.5 Task 0.3. This is one list, gathered from the policies' own declared
`unsupported` domains (`policy.yaml` → `assessment.unsupported`), their
specifications, the decision records and the release notes.

A household in any of these cases gets `unsupported` or `needs_review`,
with a reason and a code. It never gets a guessed number or a false zero.

## Across both policies

- **Facts are asserted, not verified.** Every input is the caller's claim.
  Poltika checks no government record, so a result is a conditional
  simulation, not an entitlement decision.
- **Unknown facts.** A missing or `unknown` fact stops the component that
  needs it (`needs_review`, with the facts it is waiting for). It is never
  defaulted.
- **Administrative judgement.** Discretionary decisions are not modelled,
  such as MSD's s 69 refusal, reduction or cancellation grounds, or IRD's
  Commissioner-determined employment periods (ME 2(2)-(4)).
- **Periods.** Only the 2026-27 tax year (WFF) and weeks inside the AS
  reference period are covered. Another period is `needs_review`, or has no
  rate for the date.
- **No combined total.** WFF (annual) and AS (weekly) are never added or
  converted. There is no income coupling between them (AS DEC-003).
- **Instalments and debts.** Payment timing, instalments, overpayments and
  debts are not modelled.

## Working for Families (2026-27)

- **No WFF total.** The in-work tax credit base rate is `needs_review`: the
  temporary 2026-27 rate can be reversed early by Order in Council (Task
  26b). The in-work tax credit is therefore never calculated, and neither is
  the total.
- **Changes during the year:** a relationship change, a child who qualifies
  for only part of the year, a birth or third birthday in the year, and the
  MC 9 extension past age 18.
- **Care arrangements:** shared care, a competing claimant or MC 7
  allocation, and a residence route other than MC 5(2).
- **Protected and alternative pathways:** MD 14/15 protected family tax
  credit, the direct-abatement pathway, MG 4 protected Best Start months,
  and a Tax Administration Act s 80KW extra-instalment year.
- **Best Start:** later birth cohorts, and more than one child in the
  supported cohort.
- **Evidenced ineligibility is not always $0** (WFF DEC-001). For example,
  "not a full-time earner" stays `unsupported`, because the same fact can
  describe a partly entitled household.
- **Net family scheme income** must be supplied and attested as an ME 3
  derivation. Poltika does not derive it from tax records.

## Accommodation Supplement (weekly)

- **Housing:** homeowners, social housing, joint tenancy, a community
  spouse or partner, and accommodation income or business use of the home.
- **Claimant categories:** NZ Superannuation, Veteran's Pension and
  mixed-benefit couples. Other published rate subtypes are also out of
  scope, such as the protected Jobseeker woman-alone rate and special care
  or residential rates.
- **Exclusions:** other-funding exclusions (including disability and care,
  and the Student Allowance exclusion or exception), and any exempt cash
  asset, whose determination is not modelled.
- **Location:** the Statistical Area Unit's Area 1-4 must be verified; it
  is never inferred or defaulted to Area 4.
- **Household rows:** parent rows need the eldest dependent child to be
  under 16 for the whole week. Sole Parent Support rows need a single
  claimant with a child.
- **Changes within a week** are not modelled.

## Engineering limits

- **No coverage beyond the two policies,** and no statistical data or
  population estimates (v0.2).
- **Code identity from an installed wheel.** Runs from an installed wheel
  or a container are recorded as not reproducible: there is no git checkout
  to identify the code.
