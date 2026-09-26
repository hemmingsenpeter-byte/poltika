# Review Packet: v0.1.5 build (PRs #82-#88) — 25 September 2026

Independent implementation review recorded on 27 September 2026 in
`reviews/2026-09-27-queued-pr-audit.md`, including the #89 corrections.
That record supersedes the pending code-review placeholders below; separate
source-currency and statutory-source review tasks are not closed by it.

Author: Claude Code, under Pete's delegation ("approve each step yourself and
keep going"). Each PR merged with CI green after an author preflight only.
This packet hands GPT/Codex the deferred independent audit, and its open
v0.1.5 tasks (`BUILD_PLAN_v0_1_5.md`: 0.5, 0.6, 1.2, 2.3).

## Review inputs

- **PR/diff:** hemmingsenpeter-byte/poltika PRs #82 (calculation steps), #83
  (reason codes and categories), #84 (explanations and verification), #85
  (analyst page, pilot container), #86 (evidence model, limitations, baseline),
  #87 (hardening, form, working agreement), #88 (per-policy explanations).
  Base for the whole set: `v0.1.0` at `e41871d`.
- **Primary sources and source-map paths:** `policy_specs/*/sources.yaml`
  (unchanged by these PRs).
- **Specification paths and clauses:** the rule rows (WFF-01…09, AS-01…11) in
  `policy_specs/*/specification.md`; WFF DEC-001 (the `unsupported` category
  rule).
- **Test command and output:** `uv run --extra dev pytest -q` with PostgreSQL:
  654 passed; `-m installed_artifact`: passed. The CI jobs are `test`,
  `pilot-image` and `check-protected-paths`.

## Independent review

Complete this section before reading the author response.

### Independently derived expected behaviour

(reviewer derives from sources and spec)

### Task 2.3: calculation step to specification rule

For each row, check that the step's arithmetic is what the cited rule and
its provisions require, and that the rule id is the right one.

| Step id | Rule | What the step does |
| --- | --- | --- |
| `WFF_FTC_GROSS` | WFF-03 | eldest-child amount plus the additional-child amount for each other child |
| `WFF_FTC_INCOME_EXCESS` | WFF-03 | complete dollars of family scheme income over the abatement threshold |
| `WFF_FTC_ABATEMENT` | WFF-03 | abatement rate times the income excess |
| `WFF_FTC_NET` | WFF-03 | gross family tax credit less abatement, not below zero |
| `WFF_FTC_REMAINING_ABATEMENT` | WFF-03 | abatement left after family tax credit, passed to in-work tax credit (MD 2(2)(c)) |
| `WFF_IWTC_GROSS` | WFF-04 | in-work base plus the additional amount for each child beyond three |
| `WFF_IWTC_NET` | WFF-03 | gross in-work tax credit less the abatement remaining after family tax credit |
| `WFF_MFTC_TOPUP` | WFF-05 | prescribed amount less net family scheme income, not below zero |
| `WFF_BS_INCOME_EXCESS` | WFF-06 | complete dollars of family scheme income over the Best Start threshold |
| `WFF_BS_ABATEMENT` | WFF-06 | Best Start abatement rate times the income excess |
| `WFF_BS_NET` | WFF-06 | annual Best Start amount less abatement, not below zero |
| `AS_QUALIFYING_COSTS` | AS-03 | weekly qualifying costs: the verified weekly costs (plain case) |
| `AS_COST_EXCESS` | AS-04 | weekly qualifying costs less the entry threshold |
| `AS_COST_BASED_AMOUNT` | AS-04 | no positive excess over the entry threshold |
| `AS_SUBSIDY` | AS-04 | subsidy rate times the positive excess |
| `AS_AREA_CAP` | AS-04 | the subsidy, limited to the household and area maximum |
| `AS_ASSET_IMPUTATION` | AS-06 | cash assets at or below the imputation threshold impute no income |
| `AS_ASSET_IMPUTATION` | AS-06 | income imputed per complete step of cash assets over the imputation threshold |
| `AS_TOTAL_INCOME` | AS-07 | weekly income plus imputed asset income |
| `AS_INCOME_REDUCTION` | AS-07 | income at or below the income level gives no reduction |
| `AS_INCOME_REDUCTION` | AS-07 | reduction rate times the exact income excess (DEC-001) |
| `AS_REDUCED_AMOUNT` | AS-07 | cost-based amount less the income reduction, not below zero |
| `AS_ROUNDING` | AS-04 | a positive weekly amount rounded up to the complete dollar (r 19) |

### Task 1.2: source classification

`src/poltika/semantics/schemas/source_catalog.py` ranks every catalogue
`kind`: legislation 1, regulation or order 2, official operational
material 3, official guidance 4. Check that every existing source's `kind`
(and therefore its rank) is right, especially the `agency_rates` tables
that AS parameters rest on under DEC-002.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| | | |

## Author response

Questions the author could not settle alone:

1. `AS_ROUNDING` cites AS-04 because no rule row names r 19's rounding.
   Should a rule row cite r 19, or should the step cite another rule?
2. `WFF_IWTC_NET` cites WFF-03, where MD 2's abatement order is stated,
   rather than WFF-04, the in-work tax credit row.
3. The `unsupported` categories follow WFF DEC-001. In particular, the
   AS household-exclusion bundle (`AS_HOUSEHOLD_EXCLUSION`) is marked
   `evidenced_exclusion`, and WFF in-work ineligibility is marked
   `not_modelled`.
4. The analyst page and the explanations state facts as "asserted by the
   caller, not verified by Poltika". Is that wording right against
   ARCHITECTURE.md's conditional-simulation statement?

### Author check (Claude Code, 26 September 2026; not the independent review)

The questions checked against the specifications:

1. **`AS_ROUNDING` cited AS-04: corrected to AS-07** (proposed class:
   CODE_ERROR, a wrong citation). AS-07 is the only rule row that cites
   r 19 ("the final positive amount is rounded up to a whole dollar",
   Regulations rr 17-19). The golden traces were regenerated: 8 rule ids
   changed, nothing else.
2. **`WFF_IWTC_NET` citing WFF-03: kept.** WFF-03 states MD 2's order: family
   tax credit first, then in-work tax credit.
3. **`AS_HOUSEHOLD_EXCLUSION` was `evidenced_exclusion`: corrected to
   `not_modelled`** (proposed class: CODE_ERROR). The bundled fact also
   covers s 69 discretionary reduction, which the AS specification says is
   "not an ordinary zero-rate branch". Under DEC-001's rule, a fact that can
   describe a partly entitled household is `not_modelled`. WFF in-work
   ineligibility as `not_modelled` follows the same rule, and is kept.
4. **The "asserted by the caller, not verified by Poltika" wording: kept.**
   It matches the API's own description: "the caller's own assertion that
   the underlying fact has been verified elsewhere -- this API does not
   itself confirm any fact".

The rest of the step-to-rule table was checked against the rule rows (WFF-03,
-04, -05, -06; AS-03, -04, -06, -07), with no other change. The independent
review of all of the above remains open.

## Resolution

(what happened to each discrepancy)
