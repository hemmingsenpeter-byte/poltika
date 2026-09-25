# Combined household provenance report

- Scenario id: `4b37f0b08a506cba8b9822be8edc96a650e5bdd03836276405f03e69dd393521`
- Result id: `c2156938f9c0811f4620478e8a77e756236ed1563d8f2ef140ffbe10f158a5f9`
- Reproducible from a committed source tree: yes
- Code: 0.1.0, commit 61564c35517fb1abf195b511af64f9d2d6defd2e, clean tree True
- Each policy is reported in its own period; there is no combined total.

## Combined-run inputs

- as_claimant_is_wff_claimant_or_partner: verified (asserted by caller)

## Shared-fact checks run

- precondition: AS claimant is the WFF claimant or their partner
- AS assessment week inside the WFF year
- partner status
- main benefit vs WFF in-work eligibility
- main benefit vs WFF MC 6(b)
- main benefit vs WFF MD 14/15 protected family tax credit
- main benefit vs WFF MG 4 protected Best Start
- dependent children count

## Shared-fact disagreements

None.

## Working for Families (annual)

### Provenance report: working_for_families 0.1.0

- Assessment period: 2026-04-01 to 2027-04-01 (end exclusive)
- Parameter lookup date: 2026-06-01
- Scenario SHA-256: `932cba880fa6ae424a9ccf77aac36ee31401ba8c0a1e3b6656b20f03fde851ba`
- Schema version: 0.1
- Code version: poltika 0.1.0
- Source catalogue as of: 2026-09-21 (the catalogue's date, not each source's check date)
- Every input below is the caller's own assertion. Poltika has not independently verified it, so each result is a conditional simulation, not an entitlement determination.

#### Artifacts

All bound when the run's parameters were loaded, and verified unchanged before this report was built.

| Path | SHA-256 |
| --- | --- |
| policy.yaml | `7f83084d52b37e0df1c19ef7e0d7232d2dbe2b56b5f9ef65eb837a2340c47745` |
| sources.yaml | `7775f9135c8b76e528f4d850518a1083e9c5c4a3e88af46f51e43742085995b3` |
| specification.md | `80afecc64fd5761b75787cbc337da2b089adc4b1dfd9ee15e9f0cd21e6d93ffd` |

#### Sources cited

### Taxation (Budget Measures) Act 2025 (`wff-budget-measures-2025`)

- Kind: amending_legislation
- URL: https://www.legislation.govt.nz/act/public/2025/26/en/latest/sections/LMS1441509/
- Checked on: not recorded as a structured field
- verification_status: relevant_clauses_checked_2026-09-21

### Taxation (Annual Rates for 2025-26, Compliance Simplification, and Remedial Measures) Act 2026 (`wff-iwtc-increase-act-2026`)

- Kind: amending_legislation
- URL: https://www.legislation.govt.nz/act/public/2026/8/en/latest/
- Checked on: 2026-09-24 (task_26b_check)
- Checked on: 2026-09-24 (task_28_2_check)
- verification_status: current_publication_checked_future_recheck_required
- order_check: On 2026-09-21, the official s 2 page's secondary-legislation link was disabled and stated that no secondary legislation made under that section was currently on the website; a targeted search found no reversal Order. This is an as-of observation, not proof that no later Order will be made. Recheck the official section and secondary-legislation record for every modelled period.
- task_28_2_check: {"checked_on": "2026-09-24", "claim": "The reversal can commence by Order, with a 1 April 2027 backstop; MF 4L addresses instalments if an earlier change date is set. A past parameter lookup date cannot certify the rest of an unfinished annual interval.", "locator": "Section 2(43)-(45); section 106 inserting MF 4L.", "scope": "Commencement mechanism checked only. This is not Task 26b's independent register search or a replacement of the existing order_check record; no rate-status change.", "source_version": "Official 2026 No 8 text retrieved on the check date.", "url": "https://www.legislation.govt.nz/act/public/2026/0008/latest/whole.html"}
- task_26b_check: {"checked_on": "2026-09-24", "disposition": "The 28.2 WFF interval is the full 2026-27 year [2026-04-01, 2027-04-01), which extends beyond this check. Under specification.md's Task 10.2 rate-status table (\"Interval extends beyond the last Order check\"), an unconditional annual in-work amount stays needs_review; in_work_base review_status is unchanged. Recheck for any later modelled interval; an Order commencing inside an interval invokes the unsupported split-period row.", "finding": "Section 2(43) says section 105(2) \"comes into force on a single date set by Order in Council\"; section 2(44) is the 1 April 2027 backstop. Immediately after section 2(45) the official page states \"There is no secondary legislation made under this section currently on this website.\" No reversal Order was published as at the check date.", "interval_evidence_covers": "2026-04-01 to 2026-09-24 (as-of observation only).", "limitation": "A targeted search of the secondary-legislation register was attempted but the search URL used returned 404, so the section's own record is the evidence relied on, the same method as the 21 September order_check. Not a Gazette search.", "locator": "Section 2(43)-(45) and the section's secondary-legislation record.", "source_version": "Official 2026 No 8 text, version as at 30 March 2026, retrieved on the check date.", "url": "https://www.legislation.govt.nz/act/public/2026/0008/latest/whole.html"}

### Income Tax (Tax Credit) Order 2025 (`wff-tax-credit-order-2025`)

- Kind: amending_legislation
- URL: https://www.legislation.govt.nz/regulation/public/2025/0260/latest/whole.html
- Checked on: not recorded as a structured field
- verification_status: relevant_clauses_checked_2026-09-21

#### family_tax_credit

- Outcome: **calculated**
- Value: 7472.500

### Specification rules

- WFF-01: The claimant must meet the family-scheme criteria for the relevant entitlement period: age, principal care of a dependent child, residence (or applicable emergency-benefit route), and continuing requirements. Relationships and shared care affect entitlement periods.
- WFF-02: Family scheme income begins with net income and requires the adjustments in subpart MB. It cannot be represented safely as wages alone; relationship periods, partner income, and child support paid or received matter.
- WFF-03: Family tax credit uses the eldest-child and additional-child annual amounts, prorated by eligible days. MD 2 applies family credit abatement first to family tax credit, then to in-work tax credit; protected-credit months are a separate path.
- WFF-07: Shared care is component-specific. IRD describes a principal-care threshold of 122 days per year or a third of a four-month period and different apportionment for family tax credit/Best Start, in-work tax credit, and minimum family tax credit.
- WFF-08: A main benefit may coexist with family tax credit and Best Start but normally prevents in-work and minimum family tax credit. Payment source can be IRD or MSD.

### Calculation rules applied

- MD 13(3)(a): the abatement rate applies to complete dollars of family scheme income over the threshold (excess floored to a whole dollar)
- MD 2(2)(c): abatement applies to family tax credit first; any remainder passes to in-work tax credit

### Parameters consulted

| Parameter | Outcome | Value | Unit | Effective | Review status | Source | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `family_tax_credit_eldest_child` | resolved | 7921 | NZD_per_tax_year | 2026-04-01 to 2027-04-01 | approved | `wff-tax-credit-order-2025` | clause 4; Income Tax Act s MD 3(4)(a) |
| `family_tax_credit_additional_child` | resolved | 6454 | NZD_per_tax_year | 2026-04-01 to 2027-04-01 | approved | `wff-tax-credit-order-2025` | clause 4; Income Tax Act s MD 3(4)(b) |
| `family_tax_credit_abatement_threshold` | resolved | 44900 | NZD_per_tax_year | 2026-04-01 to 2027-04-01 | approved | `wff-budget-measures-2025` | section 7; Income Tax Act s MD 13(3)(a)(i) |
| `family_tax_credit_abatement_rate` | resolved | 0.275 | NZD_per_complete_NZD_above_threshold | 2026-04-01 to 2027-04-01 | approved | `wff-budget-measures-2025` | section 7; Income Tax Act s MD 13(3)(a)(i) |

### Inputs read

| Input | Value | Asserted by |
| --- | --- | --- |
| `children` | [{"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}, {"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}] | caller |
| `household_eligibility` | "verified" | caller |
| `extra_instalment_status` | "verified" | caller |
| `mc6a_veterans_payment` | "verified" | caller |
| `ftc_iwtc_protected_or_direct_abatement` | "verified" | caller |
| `family_scheme_income` | {"claimant_amount": "50000", "partner_amount": "20000"} | caller |
| `partner_status` | "partnered" | caller |

#### in_work_tax_credit

- Outcome: **needs_review**
- Value: (none)
- Reason: parameter 'in_work_base' value effective 2026-04-01 has review_status 'needs_review', not 'approved' -- Task 11.4: this must reach the calculator contract, not be resolved to a number here
- Depends on: family_tax_credit

### Specification rules

- WFF-01: The claimant must meet the family-scheme criteria for the relevant entitlement period: age, principal care of a dependent child, residence (or applicable emergency-benefit route), and continuing requirements. Relationships and shared care affect entitlement periods.
- WFF-02: Family scheme income begins with net income and requires the adjustments in subpart MB. It cannot be represented safely as wages alone; relationship periods, partner income, and child support paid or received matter.
- WFF-04: In-work tax credit has additional age, care, residence, benefit-status, and earner conditions. The calculation varies with qualifying children and eligible weeks.
- WFF-08: A main benefit may coexist with family tax credit and Best Start but normally prevents in-work and minimum family tax credit. Payment source can be IRD or MSD.

### Parameters consulted

| Parameter | Outcome | Value | Unit | Effective | Review status | Source | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `in_work_base` | needs_review |  |  | 2026-04-01 to 2027-04-01 | needs_review | `wff-iwtc-increase-act-2026` | sections 2 and 105; Income Tax Act s MD 10(3)(a) |
| `family_tax_credit_eldest_child` | resolved | 7921 | NZD_per_tax_year | 2026-04-01 to 2027-04-01 | approved | `wff-tax-credit-order-2025` | clause 4; Income Tax Act s MD 3(4)(a) |
| `family_tax_credit_additional_child` | resolved | 6454 | NZD_per_tax_year | 2026-04-01 to 2027-04-01 | approved | `wff-tax-credit-order-2025` | clause 4; Income Tax Act s MD 3(4)(b) |
| `family_tax_credit_abatement_threshold` | resolved | 44900 | NZD_per_tax_year | 2026-04-01 to 2027-04-01 | approved | `wff-budget-measures-2025` | section 7; Income Tax Act s MD 13(3)(a)(i) |
| `family_tax_credit_abatement_rate` | resolved | 0.275 | NZD_per_complete_NZD_above_threshold | 2026-04-01 to 2027-04-01 | approved | `wff-budget-measures-2025` | section 7; Income Tax Act s MD 13(3)(a)(i) |

### Inputs read

| Input | Value | Asserted by |
| --- | --- | --- |
| `children` | [{"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}, {"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}] | caller |
| `household_eligibility` | "verified" | caller |
| `extra_instalment_status` | "verified" | caller |
| `mc6a_veterans_payment` | "verified" | caller |
| `ftc_iwtc_protected_or_direct_abatement` | "verified" | caller |
| `in_work_eligibility` | "verified" | caller |
| `mc6b_disqualifying_payment` | "verified" | caller |
| `family_scheme_income` | {"claimant_amount": "50000", "partner_amount": "20000"} | caller |
| `partner_status` | "partnered" | caller |

#### minimum_family_tax_credit

- Outcome: **calculated**
- Value: 0

### Specification rules

- WFF-01: The claimant must meet the family-scheme criteria for the relevant entitlement period: age, principal care of a dependent child, residence (or applicable emergency-benefit route), and continuing requirements. Relationships and shared care affect entitlement periods.
- WFF-05: Minimum family tax credit tops up qualifying after-tax family income for eligible full-time-earner weeks; it is separate from the abating family and in-work credits.
- WFF-08: A main benefit may coexist with family tax credit and Best Start but normally prevents in-work and minimum family tax credit. Payment source can be IRD or MSD.

### Parameters consulted

| Parameter | Outcome | Value | Unit | Effective | Review status | Source | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `minimum_family_prescribed_amount` | resolved | 36604 | NZD_per_tax_year_after_tax | 2026-04-01 to 2027-04-01 | approved | `wff-tax-credit-order-2025` | clause 5; Income Tax Act s ME 1(3)(a) |

### Inputs read

| Input | Value | Asserted by |
| --- | --- | --- |
| `children` | [{"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}, {"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}] | caller |
| `household_eligibility` | "verified" | caller |
| `extra_instalment_status` | "verified" | caller |
| `minimum_family_full_time_earner_weeks` | "verified" | caller |
| `mc6b_disqualifying_payment` | "verified" | caller |
| `partner_status` | "partnered" | caller |
| `family_scheme_income` | {"claimant_amount": "50000", "partner_amount": "20000"} | caller |
| `net_family_scheme_income_me3_attested` | true | caller |
| `net_family_scheme_income` | "70000" | caller |

#### best_start

- Outcome: **calculated**
- Value: 0

### Specification rules

- WFF-01: The claimant must meet the family-scheme criteria for the relevant entitlement period: age, principal care of a dependent child, residence (or applicable emergency-benefit route), and continuing requirements. Relationships and shared care affect entitlement periods.
- WFF-06: Best Start is a per-child credit during the first three years. Same-child parental leave or preterm baby payments, parental tax credit, and specified veterans' payments can exclude entitlement for a period under MC 6(c). For children born before 1 April 2026, the first year is exempt from income abatement; later birth cohorts can be abated from their first year.
- WFF-07: Shared care is component-specific. IRD describes a principal-care threshold of 122 days per year or a third of a four-month period and different apportionment for family tax credit/Best Start, in-work tax credit, and minimum family tax credit.

### Parameters consulted

None.

### Inputs read

| Input | Value | Asserted by |
| --- | --- | --- |
| `children` | [{"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}, {"best_start_cohort": "outside_best_start_entitlement", "best_start_no_disqualifying_payment": "verified", "qualifies_whole_year": "verified"}] | caller |
| `household_eligibility` | "verified" | caller |
| `extra_instalment_status` | "verified" | caller |
| `mc6a_veterans_payment` | "verified" | caller |
| `best_start_no_shared_care` | "verified" | caller |
| `best_start_protected_credit` | "verified" | caller |

## Accommodation Supplement (weekly)

### Provenance report: accommodation_supplement 0.1.1

- Assessment period: 2026-06-01 to 2026-06-08 (end exclusive)
- Parameter lookup date: 2026-06-01
- Scenario SHA-256: `1f9f84483411c3a9ee525c981697e660a0aab83067793d518f685c7b56785666`
- Schema version: 0.1
- Code version: poltika 0.1.0
- Source catalogue as of: 2026-09-21 (the catalogue's date, not each source's check date)
- Every input below is the caller's own assertion. Poltika has not independently verified it, so each result is a conditional simulation, not an entitlement determination.

#### Artifacts

All bound when the run's parameters were loaded, and verified unchanged before this report was built.

| Path | SHA-256 |
| --- | --- |
| decisions/DEC-001-income-excess-rounding.md | `36974df5ca3de1b28a83284fd55a62cb482a02f176737b3285b3b0786b8aa7e0` |
| decisions/DEC-002-published-thresholds-and-rate-scope.md | `5086c2fe0aed7433050be354d119f1094bfb240fb1aafe67b3121e961dd3d146` |
| decisions/DEC-003-msd-paid-wff-income-exclusion.md | `8ecb738044afef3b046c581c52b13c6d10719380dce700f12c2223ec8a55c8e2` |
| policy.yaml | `d46078bc9ab3cb6babdd304b752de9cc3cec3a2d304c3e6b09fd0bb45ecac180` |
| sources.yaml | `1063aea45898c771f2bf7af4db0830972288f74618914936c4dd66918a3256e2` |
| specification.md | `1ced44e69ee3b4aafabc3ed9f1cae4fcb8f8f2c224d7abd2880dd805f50156de` |

#### Sources cited

### Income cut-out points for non-beneficiaries (`as-msd-income-2026`)

- Kind: agency_rates
- URL: https://map.workandincome.govt.nz/map/deskfile/extra-help-information/accommodation-supplement-tables/income-cut-out-points-for-non-beneficiaries-curren.html
- Checked on: 2026-09-24 (task_26a_check)
- task_26a_check: {"checked_on": "2026-09-24", "finding": "The same four household-specific thresholds occur in every area, 693 (single), 1066 (childless couple), 1117 (couple with children), and 906 (sole parent). The income cut-out columns are separate and must not be loaded as these thresholds.", "limitation": "The single as_income_level_non_beneficiary ID cannot represent all these rows. No value promoted pending selector repair and the regulation 18(3) precision check.", "locator": "Income threshold column in each of Areas 1-4", "table_as_at": "2026-04-01"}

### Non-beneficiaries - entry thresholds and maximum rates (`as-msd-rates-2026`)

- Kind: agency_rates
- URL: https://map.workandincome.govt.nz/map/deskfile/extra-help-information/accommodation-supplement-tables/non-beneficiaries-current-01.html
- Checked on: 2026-09-24 (task_26a_check)
- Checked on: 2026-09-24 (task_28_2_check)
- task_26a_check: {"checked_on": "2026-09-24", "finding": "Published entry thresholds are 93 (single without children), 158 (couple without children), 205 (couple with children), and 168 (sole parent with one or multiple children). These are entry thresholds, not published regulation 17 base rates.", "limitation": "Live current page; not evidence for March rates or a future unchanged interval. Values not promoted to policy.yaml.", "locator": "Rent or board column, all five ordinary household rows", "table_as_at": "2026-04-01"}
- task_28_2_check: {"checked_on": "2026-09-24", "claim": "The table labels its amounts as weekly and applicable at 1 April 2026. It does not substantiate backdating these entries to the policy reference-period start of 2 March 2026.", "effective_from": "2026-04-01", "locator": "Opening sentence above the table.", "scope": "Date and unit checked only. Base-rate derivation, other claimant tables and parameter approval remain Task 26a.", "source_version": "Live MSD MAP table explicitly labelled at 1 April 2026."}

### Social Security Act 2018 (`as-social-security-act`)

- Kind: legislation
- URL: https://www.legislation.govt.nz/act/public/2018/32/en/latest/
- Checked on: 2026-09-24 (task_26a_check)
- Checked on: 2026-09-24 (task_28_1_check)
- task_26a_check: {"audit_version_url": "https://www.legislation.govt.nz/act/public/2018/32/en/2026-04-01/", "checked_on": "2026-09-24", "finding": "The single ordinary Jobseeker rate is 372.55, while Part 7 uses 25 percent of the regulation 17 base rate for rent or board. The statutory cap categories combine couples and sole parents; this does not establish that their base rates are equal.", "limitation": "Research only. No new runtime value or date selection approved.", "locator": "Schedule 2 Income Test 3; Schedule 4 Part 1 clause 1(d)-(g), (j); Part 7 clauses 1-3", "precision_cross_check": "The ordinary sole-parent Jobseeker rate is 521.52; the ordinary couple rates in Part 1 clause 1(j) are 633.94 without children and 669.40 with children. Income Test 3 reduces the relevant benefit by 70 cents per dollar of income over 160. Continuous-equation cut-outs are diagnostic only, not verified legal payment-prevention thresholds. See the audit's F3 section.", "versions_checked": ["2026-04-01", "2026-09-04"]}
- task_22_check: Official "latest" consolidated text checked directly 2026-09-22 (browser user-agent, bare fetch 403s). ss 65AAA, 66, 67, 68, 69, 423, and Schedule 4 Part 7 (cl 1-8) reviewed in full for Task 22's scoped contract; see specification.md's "Proposed Task 22 scoped calculation contract" section for what each provision supports. Schedule 3 cl 8's exact text was not independently re-fetched -- only its existence and cross-reference to "WFF tax credit" were confirmed. Recheck the operative version for every later modelled date. PR 24 review finding -- this is a single-session, single-party verification -- re-verified reproducible on a second, independent fetch (same day, same method, byte-identical body content aside from CSRF/timestamp noise) before this PR's response, but that is still the same author re-checking their own earlier read, not an independent party's read. A fresh-context reviewer must independently re-fetch and confirm the s 423(3) and Schedule 4 Part 7 cl 1-6 quotes below before either finding is treated as confirmed rather than author-asserted. Working method -- `curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" -L "https://www.legislation.govt.nz/act/public/2018/0032/latest/whole.html"` -- a bare fetch (no user-agent, or a non-browser user-agent) 403s on this site; this is the same access pattern the project already established for the Income Tax Act 2007 during WFF's Task 10/17 work.
- task_24_1_independent_check: Independently fetched both the official point-in-time Act version operative on the 2026-06-01 modelled date (Schedule 4 in the 2026-03-11 version; the site also identifies the 2026-04-01 version) and the latest consolidation on 2026-09-23, using the recorded browser user-agent method. Schedule 4 Part 7 clauses 1-3 state the twelve weekly caps exactly as populated in policy.yaml ($305/$220/$160/$120, $235/$155/$105/$80, and $165/$105/$80/$70), the 70% subsidy, and the 25%-of-base-rate rent/board entry threshold. Section 423(3) still states $1 weekly income for every $100 of cash assets over $5,400 for a person in a relationship or single person with dependent children, and over $2,700 for any other person. No discrepancy found across the 17 values sourced to this Act entry (12 caps, entry fraction, 2 thresholds, step, and amount per step).
- task_28_1_check: {"audit_version_url": "https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/", "checked_on": "2026-09-24", "finding": "Clause 8(1)(l) excludes tax credits or amounts under Income Tax Act subparts MA-MG and MZ without an IRD-only payer qualifier. Clause 8(1)(a) separately excludes benefits, grants, allowances and concessions under this Act, Part 6 of the Veterans' Support Act 2014 and Part 1 of the New Zealand Superannuation and Retirement Income Act 2001, not just main benefits. AS's dependent-child definition has its own orphan-benefit/unsupported-child-benefit exclusion.", "limitation": "The source map's earlier IRD-versus-MSD uncertainty is addressed by this text plus the TAA payment provisions, pending Pete's acceptance of the cross-Act interpretation after independent review. This does not establish a cash-assets exemption.", "locator": "Schedule 2 main benefit definition; Schedule 3 clause 8(1)(a), (l); Schedule 4 Part 7 clause 7", "version_as_at": "2026-09-04"}

### Social Security Regulations 2018 (`as-social-security-regulations`)

- Kind: regulations
- URL: https://www.legislation.govt.nz/regulation/public/2018/0202/latest/
- Checked on: 2026-09-24 (task_26a_check)
- Checked on: 2026-09-24 (task_28_1_check)
- task_26a_check: {"audit_version_url": "https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-03-02/", "checked_on": "2026-09-24", "finding": "Base-rate construction depends on benefit and relationship circumstances. Paragraphs 17(2)(b), (d), (h) expressly reference a maximum annual FTC rate; paragraph (f) says annual rate payable. All four reference an eldest dependent child under 16; paragraph (a) applies an age-25 benefit rate to a single beneficiary under 25. The non-beneficiary income level is household-dependent. Regulation 19 governs final AS rounding; no rule authorising inversion of rounded table thresholds into statutory base rates was established in these provisions.", "limitation": "The entry-threshold precision question remains unresolved; see docs/research/task_26a_as_rate_audit.md. DEC-001 addresses a different issue, rounding the income excess. The child-age condition and paragraph (f)'s different wording also require interpretation.", "locator": "Regulations 17(1)-(2), 18(3)(a)-(c), 19", "versions_checked": ["2026-03-02", "2026-09-04"]}
- task_22_check: Official "latest" consolidated text checked directly 2026-09-22 (browser user-agent, same method as the Act entry above; this URL redirects to /secondary-legislation/pco-drafted/2018/202/en/latest/). rr 15, 16, 17(reference only), 18, and 19 reviewed in full. r 18(2)'s income-excess rounding is confirmed genuinely silent (no "complete dollar" language, unlike WFF's MD 13(3)(a)) -- this is the escalated ambiguity in specification.md, not resolved here. r 19 confirmed to govern only the final accommodation-supplement amount, not any intermediate step. PR 24 review finding -- also re-verified reproducible on a second, independent fetch before this PR's response -- same single-session-author caveat as the Act entry above applies; a fresh-context reviewer should independently re-confirm r 18(2)'s exact wording, not take this citation on trust.
- task_24_1_independent_check: Independently fetched the official 2026-03-02 point-in-time Regulations version operative on the 2026-06-01 modelled date, and the latest consolidation, on 2026-09-23 using the recorded browser user-agent method. Regulation 15(1) states $16,200 for a person in a relationship or single person with dependent children and $8,100 in any other case. Regulation 18(2) still states a reduction of 25 cents for every $1 of relevant weekly income above the subclause (3) income level, with no intermediate-rounding instruction. No discrepancy found across the 3 values sourced to this Regulations entry (2 ceilings and reduction rate).
- task_28_1_check: {"audit_version_url": "https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-09-04/", "checked_on": "2026-09-24", "finding": "Regulation 17(2)(b), (d) and (h) expressly use a maximum annual FTC rate divided by 52. Paragraph (f) instead says annual rate payable; treating that as necessarily the same maximum is an unresolved interpretation. All four refer to an eldest child under 16. Regulation 18 concerns non-beneficiaries. The Best Start asset exemption is a narrowly defined historic arrears provision, not a general WFF cash-assets exclusion.", "limitation": "Do not infer income-to-assets equivalence. Current scoped exemption gates and Task 26a's unresolved base-rate work remain, including the paragraph (f) wording and child-age question.", "locator": "Regulations 16-18; Schedule 8 Part 1 item 15 and Part 21 clauses 36-37", "version_as_at": "2026-09-04"}

#### accommodation_supplement

- Outcome: **calculated**
- Value: 220

### Specification rules

- AS-01: Entitlement requires accommodation costs, satisfaction of the asset requirement, and no social-housing or other-funding exclusion. General residence and age rules, student-allowance alternatives, and actual occupancy also matter.
- AS-02: Rent, board, and home-ownership costs are distinct inputs. Service costs and arrears can be excluded; homeowners have defined eligible outgoings. A client generally claims one cost type at a time.
- AS-03: Weekly qualifying accommodation costs deduct the cost of any part of a property not lived in by the claimant, then accommodation income. For a boarder paying board, MSD treats 62% of their board as accommodation costs. A claimant receiving board normally deducts 62% of those receipts as accommodation income.
- AS-04: The rate starts from 70% of positive weekly qualifying costs above the applicable entry threshold, then is limited by household category and one of four geographic-area maxima. Rent/board and homeowner thresholds differ.
- AS-05: The area lookup uses Statistical Area Units, not a postal suburb or city name.
- AS-06: Cash assets above the statutory ceiling prevent entitlement. For non-beneficiaries, $1 weekly income is imputed per $100 of assets above a lower threshold. Partner assets can be included, subject to statutory exceptions.
- AS-07: A non-beneficiary's weekly chargeable income above the relevant threshold reduces the assessed rate by 25 cents per dollar. The base rate is capped before income reduction, and the final positive amount is rounded up to a whole dollar.
- AS-08: MSD says a claimant on a main benefit generally has no separate Accommodation Supplement income test; NZ Superannuation and Veteran's Pension recipients do.
- AS-09: Couples in a joint tenancy are treated as one joint tenant for their qualifying costs, income, and assets; community partners have special rate treatment.

### Calculation rules applied

- DEC-002: the published MSD rent/board entry threshold is subtracted directly (no base rate or 25% multiplication is computed)
- Schedule 4 Part 7 cl 1-3: 70% of the positive excess of costs over the entry threshold, capped at the household/area maximum
- DEC-002: the published non-beneficiary income threshold for the household row is the r 18(3) level
- s 423(3): imputed income counts only complete steps of cash assets over the threshold (floored)
- r 18(2): the reduction rate applies to the exact, unrounded income excess (DEC-001)
- r 19: a positive final weekly amount is rounded up to the complete dollar

### Decisions applied

- DEC-002 (`decisions/DEC-002-published-thresholds-and-rate-scope.md`)
- DEC-001 (`decisions/DEC-001-income-excess-rounding.md`)

### Parameters consulted

| Parameter | Outcome | Value | Unit | Effective | Review status | Source | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `asset_ceiling_relationship_or_dependent_children` | resolved | 16200 | NZD | 2026-03-02 to 2027-04-01 | approved | `as-social-security-regulations` | r 15(1)(a) |
| `as_entry_threshold_non_beneficiary_couple_with_dependent_children` | resolved | 205 | NZD_per_week | 2026-04-01 to 2027-04-01 | approved | `as-msd-rates-2026` | Rent or board entry threshold, row(s): Married, civil union or de facto couple, 1+ children |
| `area_cap_with_dependent_children_area1` | resolved | 305 | NZD_per_week | 2026-03-02 to 2027-04-01 | approved | `as-social-security-act` | Schedule 4 Part 7 cl 1(a) |
| `rent_board_subsidy_rate` | resolved | 0.7 | fraction | 2026-03-02 to 2027-04-01 | approved | `as-social-security-act` | Schedule 4 Part 7 cl 1-3 |
| `as_income_level_non_beneficiary_couple_with_dependent_children` | resolved | 1117 | NZD_per_week | 2026-04-01 to 2027-04-01 | approved | `as-msd-income-2026` | Income threshold column (same in Areas 1-4), row(s): Married, civil union or de facto couple, 1+ children |
| `asset_imputation_threshold_relationship_or_dependent_children` | resolved | 5400 | NZD | 2026-03-02 to 2027-04-01 | approved | `as-social-security-act` | s 423(3)(a) |
| `asset_imputation_step_size` | resolved | 100 | NZD | 2026-03-02 to 2027-04-01 | approved | `as-social-security-act` | s 423(3) |
| `asset_imputation_amount_per_step` | resolved | 1 | NZD_per_week | 2026-03-02 to 2027-04-01 | approved | `as-social-security-act` | s 423(3) |
| `income_reduction_rate` | resolved | 0.25 | fraction | 2026-03-02 to 2027-04-01 | approved | `as-social-security-regulations` | r 18(2) |

### Inputs read

| Input | Value | Asserted by |
| --- | --- | --- |
| `household_eligibility` | "verified" | caller |
| `claimant_category` | "non_beneficiary" | caller |
| `tenure_type` | "rent_contributions_or_board" | caller |
| `partner_status` | "ordinary_couple" | caller |
| `ordinary_rate_status` | "verified" | caller |
| `exempt_cash_asset_status` | "verified" | caller |
| `dependent_children_count` | 2 | caller |
| `eldest_dependent_child_under_16` | "verified" | caller |
| `cash_assets` | "2000" | caller |
| `statistical_area_unit` | "area1" | caller |
| `weekly_accommodation_costs` | "600" | caller |
| `weekly_income` | "1346" | caller |
