# DEC-001: Regulation 18(2) income-excess rounding before the 25% reduction

**Policy:** accommodation_supplement
**Date:** 22 September 2026
**Decision owner:** Pete

## Ambiguity

Social Security Regulations 2018 r 18(2) reduces the assessed base rate "by
25 cents for every $1 of the relevant weekly income... in excess of the
income level specified in subclause (3)." Unlike WFF's MD 13(3)(a), which
explicitly says "0.275 times the number of **complete dollars** by which
family-scheme income exceeds" the threshold, r 18(2) contains no equivalent
"complete dollar" instruction for the income excess. Regulation 19
("Rounding") states only that "the accommodation supplement must be rounded
up to the complete dollar" -- confirmed, by its own wording and by s 423(1)(f)'s
enabling power, to govern the *final* accommodation supplement amount only,
not this intermediate step.

Two MSD pages read this two different ways: `as-msd-income-method`'s general
worksheet rounds the excess weekly income down to a whole dollar before
multiplying by 25%; `as-msd-student-partner-example`
(`as-msd-student-partner-example`) applies the 25% reduction directly to a
fractional $54.14 excess, with no rounding step shown. Neither the Act nor
the Regulations state which is correct.

## Evidence considered

- Regulation 18(2)'s own text (Social Security Regulations 2018), checked
  directly against the official consolidated text (legislation.govt.nz,
  browser user-agent, 2026-09-22, independently re-verified reproducible on
  a second fetch) -- no "complete dollar" or rounding language for the
  income excess.
- Regulation 19's text, confirmed to apply only to "the accommodation
  supplement" (the final assessed amount), by its own wording.
- s 423(1)(f) of the Social Security Act 2018, the enabling power for r 19,
  confirmed to speak only of rounding "assessed amounts of accommodation
  supplement" -- the final figure, not an intermediate income calculation.
- WFF's MD 13(3)(a)/MG 3(2)(a), as a same-project precedent for how this
  drafting convention reads when the drafters *do* intend a complete-dollar
  floor -- they say so explicitly, which r 18(2) does not.
- `as-msd-income-method`'s general worksheet (rounds the excess down first)
  versus `as-msd-student-partner-example` (applies the reduction to the
  exact $54.14 excess) -- a direct conflict between two MSD-published
  descriptions of the same rule, not resolved by either agency page citing
  the other.

## Decision

Apply the 25% reduction to the exact, unrounded weekly income excess --
matching MSD's student-partner worked example, not the general worksheet's
floor-first convention. `income_excess` in the scoped calculation sequence
(specification.md step 5) is not floored to a whole dollar before the 25%
reduction is applied; only the *final* accommodation supplement amount is
rounded (up, per r 19), after all other steps.

## Rationale

Textual: r 18(2) omits the "complete dollars" language WFF's MD 13(3)(a)
uses explicitly for the same kind of step (an abatement/reduction applied to
an income excess) -- the drafters demonstrably know how to write a
complete-dollar instruction when they mean one, in the same overall body of
social-assistance drafting conventions this project already has direct
evidence for. r 19 already states the *one* place rounding happens in this
regulation (the final amount); reading silence elsewhere in r 18(2) as "round
here too" would insert a step the drafters did not write, not merely fill an
acknowledged gap. The student-partner example is also the more specific,
worked authority for exactly this calculation, where the general worksheet
is a simplified public explainer of unstated provenance.

**Residual risk, not fully closed by this decision:** MSD's general
worksheet floors the excess first, and if that worksheet reflects how MSD's
production payment system actually calculates entitlements (rather than
being a simplified public explainer that itself omits a step), this reading
could diverge from real-world payments in edge cases with a fractional
excess. Before this convention is promoted from "best-reading default" to a
protected benchmark value (Task 24), find at least one more independently
published worked example with a fractional income excess, or a direct MSD
confirmation, that corroborates the unrounded reading -- the student-partner
example alone is the only currently-known agency source stating it this way.

## Confidence

medium -- textually well-supported and consistent with this project's own
established drafting-convention precedent (WFF), but resting on a single
worked example against a general-worksheet source that states the opposite
convention; not yet corroborated by a second independent agency example or
direct confirmation.
