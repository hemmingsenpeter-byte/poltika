# Population run scaling model

`ROADMAP_REALIGNMENT.md` W4.1. This measures what the current
per-household engine costs, to inform the batch-engine decision (W4.3)
due by the start of v0.4.

## Measured (26 September 2026)

- **Method.** A toy synthetic population of 2,000 households (the test
  spec in `tests/unit/scenarios/microsim/test_synthetic.py`) run on the
  current engines with preloaded parameters, on Python 3.12.3, single
  process. Each figure is the minimum of repeated runs, divided by the
  household count.

| Measure | Time per household |
| --- | --- |
| WFF module, one run | 0.63 ms |
| Accommodation Supplement module, one run | 0.95 ms |
| Full population run: validation, baseline and reform, both policies | 3.46 ms |

## Projection

Assume each added policy costs about the mean of the two measured modules
(0.8 ms per household per run). **That is an assumption:** income tax and
benefits may cost more or less. For `H` households, `P` policies, `Y`
years and `D` draws, a baseline-and-reform run is about
`H × P × Y × D × 2 × 0.8 ms` on one core.

| Households | Policies | Years | Draws | One core | Four cores |
| --- | --- | --- | --- | --- | --- |
| 100,000 | 2 | 1 | 1 | about 5 minutes | about 1.3 minutes |
| 100,000 | 5 | 10 | 1 | about 2.2 hours | about 33 minutes |
| 100,000 | 5 | 10 | 100 | about 9 days | about 2.3 days |
| 100,000 | 10 | 30 | 1,000 | about 1.5 years | about 4.5 months |

## What it means for W4.3

- **Deterministic runs are fine.** Single-year and multi-year runs
  without uncertainty stay practical on the current engine through
  v0.4, especially parallelised across households.
- **Monte Carlo at population scale is not.** v0.5 needs one of two
  things:
  - a batch engine, which W4.2 prototypes and differential-tests against
    this one;
  - far fewer draws or households per uncertainty run, which needs a
    stated statistical justification.
- **Re-measure after each new policy.** The per-policy cost is the
  weakest assumption here. Re-measure it after income tax is
  implemented (v0.3), before W4.3 is decided.
