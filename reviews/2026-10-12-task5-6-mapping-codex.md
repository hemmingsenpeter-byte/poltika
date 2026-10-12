# Task 5–6 unit binding and household mapping: independent Codex review

Date: 12 October 2026. Reviewer: GPT/Codex; author: Claude Code.

**Disposition: not cleared. One P2 (`MAP-01`) remains.** The existing fixture
round trips pass; they do not exercise a contradictory partial-week benefit
spell. Q19 (1), (2) and (5) remain with Pete; the subsequent reading is
[q19_household_mapping_readings.md](../docs/research/q19_household_mapping_readings.md).

## Scope and evidence classes

The reviewed implementation is #207, final head
`77ffc71f964060ee9c9a0fb5b8400ca0f53d539d`, base
`7695965eb9d4b6ab214c79088401a55207ac60ba`, merged as
`cbc4f380fa3b63c2e3960aebeda317d3bdef3468`. Review baseline is
`1c19f64`. The three implementation files `unit_binding.py`, `household.py`
and `household_mappings.py` have no diff between the final PR head and that
baseline. These are **AI hypotheses, candidate Facts**, verified by local
Git inspection; no independent acceptance is claimed for this review itself.

Unless a paragraph/table explicitly gives another class, this document's
source readings, review conclusions and proposed fixes are **AI hypothesis**.
“Candidate Rule” describes the proposed destination for a legal reading,
not promotion under the epistemic constitution. The probe input below is
**Scenario**; its observed mapping is **Model output**, dependent on that
Scenario and the reviewed code. Existing decisions are cited as project
authority, not as primary statutory evidence.

Primary provisions were retrieved and read before the packet's “Author
response”; the expected behaviour below was derived separately. No external
policy engine was inspected. No code, specification, protected value or test
case was changed.

## Primary-source register

Retrieved 12 October 2026. Each source claim is **AI hypothesis** pending its
promotion gate; the final column states its candidate class and exact scope.

| ID | URL and version/as-at date | Locator | What it supports |
| --- | --- | --- | --- |
| M1 | [Income Tax Act 2007, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1518405/), version as at 4 September 2026 | MC 8–11; MD 3(2),(5); MD 6(2)–(3); MD 8; MD 10(2),(3)(d); MD 13; MD 14–15; ME 1–3; MG 1–4 | Candidate Rule: WFF has entitlement/relationship periods inside a tax year, distinct component tests and income definitions. Annual rates do not establish an annual/weekly amount conversion. |
| M2 | [Income Tax Act 2007, Part Y](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1520573/), version as at 4 September 2026 | YA 1, `child`, `dependent child`, `financially independent` | Candidate Rule: WFF's child definition and component-specific exceptions; it is not one universal child-membership rule shared with AS. |
| M3 | [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/), version as at 26 September 2026 | ss 65AAA, 65, 68–69, 103A–103F, 423(3); Schedule 2 definitions; Schedule 4 Part 7 cl 7 | Candidate Rule: accommodation costs, assets held and partner assets, imputation into weekly income, AS dependent children and the new turning-18 rules. These are current-law readings, not certification of every earlier week of 2026–27. |
| M4 | [Social Security Regulations 2018](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-09-04/), version as at 4 September 2026 | rr 15–19 | Candidate Rule: the AS asset requirement, separate exemptions, beneficiary/non-beneficiary definitions, weekly income reduction and rounding. |
| M5 | [MSD, Change in assets](https://map.workandincome.govt.nz/map/income-support/extra-help/accommodation-supplement/changes-and-reviews-accommodation-supplement/change-in-assets-01.html), live guidance as at 12 October 2026; no revision date displayed | introductory paragraph; Increase; Reduce, suspend or cancel; False or misleading information | Candidate Fact about official guidance: a change in assets triggers review, with different effective-date treatment by action. It does not establish one universal beginning/end-of-week observation date. |
| M6 | [IRD, Government payments that affect your Working for Families](https://www.ird.govt.nz/working-for-families/types/government-payments), last updated 9 April 2026 | main-benefit row; payments added to family income | Candidate Fact about guidance: main benefits can coexist with FTC and Best Start; IWTC and MFTC have exclusions. The table alone does not determine a part-year amount. |

The legislation site returned 403 through the browsing interface; the
official pages were retrieved directly with a browser user agent. Versions
were checked in the returned official text/metadata. This access method does
not elevate an interpretation into a reviewed Rule.

## Independently derived expected behaviour

### Units, periods and qualifiers — candidate Rules/design conclusions

| Packet A row | Independent expectation | Comparison |
| --- | --- | --- |
| `NZD_per_tax_year` | Currency amount in the caller's tax-year view; statutory component formulae still refer to their entitlement periods (M1). | Supported for the declared full-year slice. |
| `NZD_per_tax_year_after_tax` | Same currency/period, with the ME 3 income basis retained; generic net earnings cannot attest ME 3 (M1, ME 3). | Supported: qualifier is retained; mapping distinguishes attested and plain net income. |
| `NZD_per_child_per_tax_year` | Currency/period plus a per-child role qualifier; membership is component-specific (M1–M2). | Supported as a unit binding, not verification of any child's eligibility. |
| `NZD_per_complete_NZD_above_threshold` | Money reduced per money of excess income is a ratio; the complete-dollar operation remains calculation logic (M1, MD 13/MG 3). | Supported: no time period is added to the coefficient. |
| `fraction` | Dimensionless coefficient; AS r 18(2)'s income-reduction coefficient is not an income amount (M4). | Supported. |
| `NZD_per_week` | AS has a weekly assessment/income view (M3, Schedule 4 Part 7 cl 7; M4, rr 17–18). | Supported; the explicit arbitrary seven-day assessment-week contract comes from the existing Poltika specification, not a claim about MSD pay-week anchors. |
| `NZD` | Asset stock/threshold or monetary step, with policy applicability dates separate from an amount's dimension. A stock is not a weekly flow (M3, s 423(3); M4, r 15). | Dimension supported; actual observation/effective-date relation unresolved. `UNRESOLVED` is a conservative placeholder, not verified timing. |

`full_tax_year`/`tax_year`, `assessment_week` and lookup `day` are explicitly
named views in the existing policy contract. `unit_binding.py` checks those
declared names against its table, including mismatched parameter periods.
It performs no conversion. `check_input` deliberately accepts an unresolved
stock under a declared period; it does not prove the stock was observed then.

### Household-to-policy fields — candidate Rules/design conclusions

WFF's family scheme income (subpart MB), ME 3 net family scheme income and
AS r 18's income are different figures. The caller can supply each in its
own policy basis/period; gross earnings by type do not establish them.
The mapping's distinct bases and preservation of missing amounts are
supported. `[start,end)` spells that exactly tile the requested period may
be summed without scaling. Gaps remain unknown and straddling spells must be
refused under **Pete's Q10/D32 contract**, even where the statute describes
an annualisation within a component's legal calculation. The legal formula
is not authority to bypass that standing modelling decision.

WFF `children` is a complete list in the existing engine input; an incomplete
canonical list cannot establish even a known zero child count. The separate
`wff_children_complete` and `as_children_complete` checks preserve that
distinction. `None` child facts become unknown. WFF's nine and AS's four
bundle assertions are transported as **Scenario** assertions; they are
not derived or independently verified by the adapter.

For AS, the partner arrangement matters separately from whether a partner
exists (M3, ss 68–69; Schedule 4 Part 7). Unknown arrangements correctly
stay unverified. AS r 17's category depends on benefit receipt in the
assessed circumstances. A recorded conflict during any part of the requested
week cannot be discarded merely because another spell spans the whole week.
The rule used to resolve a real mid-week category change remains outside
this review; refusing contradictory evidence requires no policy choice.

Separate AS and WFF child facts are supported, but “two definitions” is
incomplete for full WFF coverage: YA 1 and MD 6 have component exceptions.
AS's governing source is Schedule 2 of the **Act**, as applied through
Schedule 4 Part 7 cl 7 and, from 4 September 2026, ss 103A–103F where
applicable. Counts do not establish child identities or prove one set is a
subset of the other. The adapter's first-N assignment at
`household_mappings.py:445–491` is a synthetic reconstruction for round
tripping; it is not source-derived person-level verification. Q19 (2) must
settle its treatment before those reconstructed labels drive new logic.

### Refusals and identity — candidate Facts/design conclusions

Multi-family refusal follows the recorded ADR-0017 supported domain, not a
statutory ineligibility. Partner conflicts, unattached partner income and an
attestation without an amount cannot preserve an exact original input, so
refusal is supported. AS count greater than the WFF list is an **adapter
representation refusal**, not proof that the policy facts contradict: the
canonical WFF mapping currently reads every listed child. The old pair
path remains available and applies its conservative checks.

Synthetic identifiers are authorised by Pete's 12 October record/D36. No
real identifier scheme is necessary for these fixture-only adapters. This
does not authorise guessing which real child an AS aggregate refers to.

## Finding

### MAP-01 — P2 — CODE_ERROR

**Location:** `src/poltika/scenarios/household_mappings.py:278–285`; relevant
validation omission at `src/poltika/semantics/household.py:381–392`.

**Evidence:** a normally validated household can contain `NO_BENEFIT` for
the whole week `[2026-06-01,2026-06-08)` and `JOBSEEKER_SUPPORT` for
`[2026-06-03,2026-06-04)` for the same claimant. `to_as` returns
`claimant_category=NON_BENEFICIARY`. Its set comprehension ignores the
partial-week contradictory spell; the `len(categories)>1` check therefore
never sees it. The household validator checks income-spell overlaps but
does not reject benefit-spell overlaps. The implementation files are
identical at #207's final head and review baseline; the probe was run against
the baseline. **Scenario input; Model output observation; AI hypothesis
finding.**

**Expected behaviour:** preserve the unresolved category or return a
mapping refusal. `NO_BENEFIT` is documented as verified absence of a
benefit over its spell, so overlapping positive receipt contradicts it.
M4 r 17 distinguishes being paid a main benefit from non-beneficiary
status, and r 18 applies the latter's income reduction. The selected
category can therefore direct a household through the wrong calculation
route. No numeric entitlement has been derived for this contradictory case.
P2 reflects the narrowly reproduced mapping defect: existing supplied
fixtures remain unchanged and no live API/calculated amount was demonstrated.
This is not final-head clearance or a claim that the defect is harmless.

**Suggested fix:** Claude Code should examine all benefit spells overlapping
the assessment week before accepting a full-week category; reject or leave
unknown conflicting receipt, including a partial-week `NO_BENEFIT` conflict.
An engineering regression should cover this trigger in the implementation
fix. This documentation PR adds no test case and chooses no mid-week
entitlement rule.

**Executable reproduction (Scenario, not a new test case):** from the
review baseline worktree, run with the installed development environment:

```sh
PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python - <<'PY'
from datetime import date
from poltika.semantics.household import (
    Household, Person, Family, BenefitSpell, BenefitKind,
)
from poltika.semantics.population import PersonRole
from poltika.scenarios.household_mappings import to_as
from poltika.engines.simulator.accommodation_supplement import AssessmentWeek

week = AssessmentWeek(date(2026, 6, 1), date(2026, 6, 8))
household = Household(
    household_id="probe",
    persons=(Person(person_id="claimant", role=PersonRole.CLAIMANT),),
    families=(Family(claimant_id="claimant"),),
    benefit_spells=(
        BenefitSpell(person_id="claimant", benefit=BenefitKind.NO_BENEFIT,
                     start=week.start, end=week.end),
        BenefitSpell(person_id="claimant", benefit=BenefitKind.JOBSEEKER_SUPPORT,
                     start=date(2026, 6, 3), end=date(2026, 6, 4)),
    ),
)
print("validated benefit spells:", len(household.benefit_spells))
print("mapped category:", to_as(household, week).claimant_category.value)
PY
```

Observed output (**Model output**, dependencies: Scenario above and the
reviewed code):

```text
validated benefit spells: 2
mapped category: non_beneficiary
```

## Verification and disposition

**AI hypotheses, candidate Facts:** the focused command
`PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q tests/unit/semantics tests/unit/scenarios/test_household_roundtrip.py tests/regression`
passed **218 tests**. A fresh `uv run` could not fetch dependencies under
the network sandbox; the installed development environment ran the suite.
`/Users/peterhemmingsen/Poltika/.venv/bin/ruff check src tests` also passed.
`PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/mypy --strict src`
passed with no issues in 107 source files.
No fixture expected value was edited.

The round-trip test reads the nine golden households, interaction cases,
WFF spec cases/benchmarks and AS spec cases/benchmarks. All pass with exactly
the listed `interaction:disagreement_keeps_existing_unsupported_components`
adapter refusal. Combined cases compare scenario ID, canonical result
payload and result ID. WFF/AS standalone cases compare scenario equality;
AS and WFF spec cases also compare calculator results. WFF benchmark entries
do not independently compare result IDs or rerun every result; equal input
is the deterministic round-trip argument there. These tests establish
compatibility of the supplied fixtures, not complete semantic coverage.

No P1 was found. MAP-01 prevents clearing #207's mapping row. The unknown,
zero, gap, tiling and straddle handling is supported within validated
households; Q19 timing and child-membership choices remain unresolved.
Neither this review nor the subsequent research clears an interpretation
or authorises retirement of the pairwise checks.

## What Pete decides

- Q19 (1): keep stock timing unresolved, or approve a dated stock-observation
  contract after reviewing the legal/operational effective-date limits.
- Q19 (2): retain separately asserted supported-slice WFF/AS facts, or
  commission component-specific child membership and a treatment for
  count-only adapters; synthetic first-N labels need an explicit status.
- Q19 (5): retain whole-year assertions/refusals, or commission a sourced
  relationship/entitlement-period design. Q10/D32 continues to prohibit
  apportionment; retirement of household pairwise checks waits for this.
