# DEC-002: Published thresholds and bounded ordinary-rate scope

**Policy:** Accommodation Supplement
**Date:** 2026-09-24
**Decision owner:** Pete; modelling choice recorded by Codex under the
explicit "resolve and proceed" delegation.
**Status:** Selected modelling convention; independent contract review and
implementation acceptance remain required. Not yet an executable policy.

## Ambiguity

Exact statutory base construction and the displayed MSD entry thresholds
differ: 25% of 372.55 is 93.1375, while MSD publishes 93. Income Test 3's
continuous zero is also not MSD's displayed income level. No authoritative
intermediate rounding instruction has been established. Regulation
17(2)(f)'s annual-rate wording and the under-16 condition have separate
unresolved interpretation questions. The old IDs also conflate distinct
households; that is SPEC_ERROR, not a choice between equivalent designs.

## Evidence considered

- `as-social-security-act`: Schedule 4 Part 1 and Part 7; Schedule 2
  Income Test 3. [Dated Act](https://www.legislation.govt.nz/act/public/2018/32/en/2026-04-01/).
- `as-social-security-regulations`: regulations 17-19.
  [Dated regulations](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-03-02/).
- `as-msd-jobseeker-rates-2026`, `as-msd-sole-parent-rates-2026`,
  `as-msd-supported-living-rates-2026`, `as-msd-rates-2026`: April 2026
  rent/board entry-threshold rows, not statutory base-rate amounts.
- `as-msd-income-2026`: income-threshold column, not area-dependent cut-out
  points. Non-beneficiary and income tables rechecked 24 September 2026.
- PR 46 audit and Claude's independent confirmation of the source mismatch.

## Decision

Use the published tables directly for the bounded ordinary v0.1 branch.
Represent amounts as `as_entry_threshold_<claimant>_<rate_household>` and
`as_income_level_non_beneficiary_<rate_household>`, in NZD/week. Do not
infer a base rate, multiply by an entry fraction, or derive a rounding
algorithm by matching table rows. No pre-April value is inferred.

Retain the statutory cap, subsidy, asset and final-rounding rules and
DEC-001's exact income-excess convention. Reports must identify DEC-002
and the table source as the entry/income basis; they must not call those
amounts exact regulation-17 bases or imply every ambiguity is resolved.

The four rate categories and fail-closed input contract are specified in
the Task 26a repair section of `specification.md`. Protected Jobseeker,
special/mixed-benefit rate cases and unsupported Sole Parent combinations
are excluded rather than assigned ordinary values. Parent cases require
an eldest dependent child verified under 16 throughout the week. This is
a conservative domain restriction, not a ruling on entitlement at 16+.

Do not decide that paragraph (f) means maximum as a statement of law.
Its published ordinary table row is the selected modelling input; a later
exact statutory branch must resolve the wording before implementing it.
AS has its own source evidence; no runtime lookup into WFF is authorised.

## Rationale and residual risk

The tables and worked examples document MSD's administrative amounts.
Using them explicitly is more auditable than inventing exact bases from
rounded thresholds. This remains a model convention, not proof that the
legal precision discrepancy is eliminated. Replace it if stronger primary
evidence establishes a different operative method, through a new reviewed
decision and policy revision. Do not adjust protected results merely to
make tests pass. No numeric parameter is approved by this artifact alone.

## Confidence

High that the tables state these kinds of amounts; medium that this is
the appropriate bounded modelling convention. Exact legal equivalence
and excluded subtype interpretations remain unverified.
