# DEC-004: s 423(3) asset imputation counts complete $100 steps

**Policy:** accommodation_supplement
**Date:** 13 October 2026
**Decision owner:** Pete

## Ambiguity

Social Security Act 2018 s 423(3) says "the following must be treated as $1 a
week of income: (a) every $100 of cash assets over $5,400 held by [a person
in a relationship, or a single person with a dependent child or children];
and (b) every $100 of cash assets over $2,700 held by any other person." It
does not say how an incomplete $100 of excess is treated. Three readings are
possible:

- **complete steps:** only whole $100 steps of the excess count ($2,799.99
  imputes $0);
- **proportional:** the fraction counts ($2,799.99 imputes $0.9999);
- **started step:** any part of a $100 counts as a step ($2,700.01 imputes $1).

The Task 22 contract (22 September 2026, `specification.md`) adopted the
complete-steps reading by inference and asked for an independent re-read. The
GPT/Codex re-read of 12 October 2026 (finding B4,
[review](../../../reviews/2026-10-12-wff-as-boundary-proposal-codex.md)) found
the text does not settle it and escalated it.

## Evidence considered

- s 423(3) as at 1 April and 4 September 2026 (legislation.govt.nz), read
  directly by both reviews: "every $100", with no partial-step wording.
- MSD's non-beneficiary asset guidance and worked example (`as-msd-assets`;
  retrieved 12 October 2026): an exact $400 excess imputes $4. It has no
  fractional example, so it cannot distinguish the readings.
- WFF's MD 13(3)(a) and MG 3(2)(a) say "complete dollars" explicitly. That is a
  drafting comparison only. DEC-001 shows that where Parliament leaves an
  intermediate step unrounded (r 18(2)), this project does not insert a floor,
  so the analogy cuts both ways and is not relied on alone.

## Decision

Count only complete $100 steps of cash assets over the threshold, as the
engine already does (`accommodation_supplement.py`, `AS_ASSET_IMPUTATION`,
floored `complete_steps`). No calculated amount changes.

## Rationale

"Every $100 ... must be treated as $1" counts hundreds: it states a
quantity per whole unit. The proportional reading turns it into $0.01 per
dollar, which the provision could have said and does not. The started-step
reading imputes a whole dollar for a single cent of excess and has no
textual support. DEC-001 is not contradicted: r 18(2) applies a rate to an
amount ("25 cents for every $1 ... in excess"), where an exact fraction is a
natural reading, while s 423(3) converts a counted stock into income. The
difference in issue is at most $1 a week of imputed income for a
non-beneficiary whose asset excess is not a whole number of hundreds.

## Confidence

medium. The reading follows the wording, but no agency example with a
fractional excess, and no direct MSD confirmation, was found. Pete did not
authorise contacting MSD for this. Revisit if a published fractional example
or an official statement shows SWIFTT computes otherwise.
