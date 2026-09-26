# Legislation currency and in-work base re-check (v0.1.5 Tasks 0.5 and 0.6)

- **Date:** 26 September 2026
- **Checked by:** Claude Code, at Pete's request, on a local machine that can
  reach `www.legislation.govt.nz` (the cloud session could not). This is an
  **author check**, not the independent GPT/Codex check the plan assigns.
- **Method:** official HTML from legislation.govt.nz, fetched with curl and a
  browser user agent (a bare fetch returns 403), the method the source
  catalogues already record.
- **Recorded in:** `task_0_5_check` and `task_0_6_check` entries in
  `policy_specs/accommodation_supplement/sources.yaml` and
  `policy_specs/working_for_families/sources.yaml`.

## Result

No v0.1 parameter, rule or expected value is affected. No reversal Order for
the in-work tax credit has been published, so `in_work_base` stays
`needs_review`.

## Task 0.5: legislation currency

| Source | Latest official version (26 Sep 2026) | Change since recorded checks | Effect on v0.1 |
| --- | --- | --- | --- |
| Social Security Act 2018 | As at 4 September 2026 (same as recorded) | 2026 No 55 replaced s 67(d)(i)-(ii); already in the 4 September consolidation. 2026 No 65 changes only a Schedule 2 definition | None: s 67(d) is a caller-asserted eligibility gate |
| Social Security Regulations 2018 | As at 4 September 2026 (same as recorded) | 2026 No 55 replaced r 162(c)(iii), not an AS regulation; rr 15-19 unchanged. Old URL now 404s | None |
| Income Tax Act 2007 | As at 4 September 2026 (same as recorded) | 2026 No 55 renamed CW 52B headings and inserted CW 52B(3); already consolidated. No Part M provision used by v0.1 amended | None: family scheme income is a verified input |
| Tax Administration Act 1994 | As at 4 September 2026 (same as recorded) | None found | None |

**The September 2026 Accommodation Supplement legislation** named in
`BUILD_PLAN_v0_1_5.md` is the Social Security (Jobseeker Support and
Accommodation Supplement) Amendment Act 2026 (2026 No 54), enacted
3 September 2026 and still labelled "Not yet in force":

- Section 2: Part 1 commences **2 November 2026**; Part 2 commences
  **1 April 2027** (and Schedule 1 Part 18 cl 132 applies it on and after
  that date).
- Part 1 adds a parental income requirement for young Jobseeker Support
  applicants. Its Schedule 3 amendments concern parental income and do not
  touch clause 8, which the WFF-AS interaction relies on.
- Part 2 replaces Schedule 4 Part 7 clauses 4-6A: the **homeowner** entry
  threshold rises from 30% to 40% of the base rate, except 30% for a
  "specified person" (Supported Living Payment on restricted work capacity,
  total blindness or caring grounds, NZ Superannuation or Veteran's Pension,
  or their partner). Caps are unchanged.
- Effect: none on v0.1, which covers rent or board only and weeks ending
  before 1 April 2027. For weeks from 2 November 2026, Jobseeker Support
  eligibility tightens for young applicants, but v0.1 takes the claimant
  category as a caller-asserted fact. This matters to the 2027-28 year
  (`BUILD_PLAN_v0_1_6.md`) only if homeowners are ever supported.

**Scope of the search:** public Acts 2026 Nos 55-69 were scanned for
references to these four statutes (Nos 55 and 65 matched). Nos 67 and 70-75
returned 404, and No 71 returned 504 then 404. Earlier 2026 Acts were covered
by the recorded 4 September consolidations and were not re-read.

## Task 0.6: in-work tax credit base

Taxation (Annual Rates for 2025-26, Compliance Simplification, and Remedial
Measures) Act 2026 (2026 No 8), latest version as at 30 March 2026:

- Section 2(43): s 105(2), which reverses the temporary $7,670 base to
  $5,070, commences on a date set by Order in Council; s 2(44) is the
  1 April 2027 backstop.
- Immediately after s 2(45) the official page still states: "There is no
  secondary legislation made under this section currently on this website."
- **Disposition:** no early reversal as at 26 September 2026. The WFF year
  runs to 1 April 2027, beyond this check, so under the specification's
  Task 10.2 rate-status table `in_work_base` stays `needs_review`. It can be
  settled only once the year has ended (`BUILD_PLAN_v0_1_6.md`).
- **Limitation:** a Gazette search URL returned 404, so the section's own
  record is the evidence, the same method as the 21 and 24 September checks.

## Still open

- The independent GPT/Codex re-check of Tasks 0.5 and 0.6.
- Task 1.2 (source classification review) was not part of this check.
