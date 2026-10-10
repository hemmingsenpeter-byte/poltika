# DEC-003 — apparent IR3G worksheet discrepancy

**Policy:** Personal income tax, D11 salary/wage slice.
**Date:** 2026-10-08 (record raised).
**Decision owner:** Pete
**Decision date:** none.
**Status:** open; `needs_review`. **Raised by:** GPT/Codex.
**Class:** AI hypothesis; proposed `SOURCE_CONFLICT`.

## Ambiguity

An earlier-year IR3G worksheet threshold appears inconsistent with the
statutory per-dollar bands. Its interpretation and benchmark use are open.

## Evidence considered

The [IRD IR3G 2026 guide](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir1---ir99/ir3g/ir3g-2026.pdf?modified=20260331185539),
retrieved 8 October, printed p 43, has an extracted-text row for the
$78,101–$180,000 band showing threshold A **$78,101**, rate B **.33** and
accumulated tax C **$15,650.50**. Printed p 44 directs subtracting A,
multiplying by B, then adding C. [ITA Schedule 1 Part A Table 1](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
allocates each dollar above the prior band's $78,100 endpoint to the
next band. The worksheet threshold appears inconsistent with that
instruction; this is an author inference requiring review, not a revised
official value or benchmark expectation.

The guide's printed p 7 covers **1 April 2025 to 31 March 2026**, not the
commissioned 2026–27 period. The web reader labels the retrieved cover
August 2026. The query's modified timestamp is not a document version or
immutable snapshot. Web screenshot requests yielded no viewable image.
The directly retrieved PDF was then rendered with macOS PDFKit: the author
visually confirmed the same threshold/rate/accumulated-tax cells on printed
p 43. The source observation is confirmed; the conflict's interpretation
and disposition still require independent review and Pete.

## Arithmetic evidence

Reviewer-derived arithmetic (class: Model output from the Table 1 rates and
thresholds as stated in the specification; the inference drawn from it is an
AI hypothesis under `doctrine/epistemic-constitution.md`, not an IRD
statement). Statutory tax on the first $78,100 under Table 1 is
15,600 x 0.105 + (53,500 - 15,600) x 0.175 + (78,100 - 53,500) x 0.30
= 1,638 + 6,632.50 + 7,380 = **$15,650.50**. That equals the IR3G
worksheet's column C for the row starting A = $78,101. Using A = $78,101
with C = $15,650.50 therefore omits tax on the $78,101st dollar
(0.33 x $1 = $0.33), whereas the worksheet's previous row uses A = $53,500
(the threshold itself, not threshold + 1), so the fourth row is internally
inconsistent with the third. This adds evidence only: the decision, its
`needs_review` status and the Q18 escalation are unchanged, and no value is
adopted.

## Decision

No worksheet cell has been silently repaired or adopted into fixtures. No
2026–27 benchmark is inferred from this earlier-year guide. All numeric
work remains blocked by DEC-001/002 regardless of this candidate guide.

**Smallest Pete action:** review the visually confirmed row independently
and obtain an official correction/clarification or a separately retained,
period-matched benchmark;
review that evidence independently before any expected-result adoption.
See PETE_QUEUE Q18.
