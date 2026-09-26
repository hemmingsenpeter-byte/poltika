"""v0.2 Task 5.1: weighted statistics, each defined once.

Every function takes `(value, weight)` pairs with positive weights. Callers
decide what is excluded (unknown values, `needs_review` results) and report
the exclusion. Nothing here treats a missing value as zero. All arithmetic
is `Decimal`.

**Weighted quantile.** For `0 < q <= 1`, the smallest value `v` whose
cumulative weight (all values `<= v`) reaches at least `q` times the total
weight: the lower inverse of the weighted distribution function. The
weighted median is `q = 1/2`. No interpolation, so the result is always one
of the observed values.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal

Pair = tuple[Decimal, Decimal]


def _checked(pairs: Iterable[Pair]) -> list[Pair]:
    items = list(pairs)
    if any(w <= 0 for _, w in items):
        raise ValueError("weights must be positive")
    return items


def weighted_count(pairs: Iterable[Pair]) -> Decimal:
    return sum((w for _, w in _checked(pairs)), Decimal(0))


def weighted_total(pairs: Iterable[Pair]) -> Decimal:
    return sum((v * w for v, w in _checked(pairs)), Decimal(0))


def weighted_mean(pairs: Iterable[Pair]) -> Decimal | None:
    """`None` for no observations, never zero."""
    items = _checked(pairs)
    count = weighted_count(items)
    return None if count == 0 else weighted_total(items) / count


def weighted_quantile(pairs: Iterable[Pair], q: Decimal) -> Decimal | None:
    if not Decimal(0) < q <= Decimal(1):
        raise ValueError("q must be in (0, 1]")
    items = sorted(_checked(pairs))
    if not items:
        return None
    target = q * weighted_count(items)
    cumulative = Decimal(0)
    for value, weight in items:
        cumulative += weight
        if cumulative >= target:
            return value
    return items[-1][0]  # unreachable: the last cumulative equals the total


def weighted_median(pairs: Iterable[Pair]) -> Decimal | None:
    return weighted_quantile(pairs, Decimal(1) / 2)


def weighted_quantile_cuts(pairs: Sequence[Pair], groups: int) -> list[Decimal]:
    """The `groups - 1` cut points dividing the weighted distribution into
    equal-weight groups (9 cuts for deciles)."""
    if groups < 2:
        raise ValueError("need at least two groups")
    cuts = [weighted_quantile(pairs, Decimal(k) / groups) for k in range(1, groups)]
    if any(c is None for c in cuts):
        raise ValueError("no observations to cut")
    return [c for c in cuts if c is not None]
