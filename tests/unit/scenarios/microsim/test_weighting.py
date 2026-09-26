"""v0.2 Task 5.1: weighted statistics on populations whose answers are known
by hand."""

from __future__ import annotations

from decimal import Decimal as D

import pytest
from hypothesis import given
from hypothesis import strategies as st

from poltika.scenarios.microsim.weighting import (
    weighted_count,
    weighted_mean,
    weighted_median,
    weighted_quantile,
    weighted_quantile_cuts,
    weighted_total,
)

# Values 10, 20, 30 with weights 1, 2, 1: total weight 4, total 80, mean 20.
PAIRS = [(D(10), D(1)), (D(20), D(2)), (D(30), D(1))]


def test_totals_counts_and_mean() -> None:
    assert weighted_count(PAIRS) == D(4)
    assert weighted_total(PAIRS) == D(80)
    assert weighted_mean(PAIRS) == D(20)


def test_quantiles_by_hand() -> None:
    # Cumulative weight: 10 -> 1, 20 -> 3, 30 -> 4 (of 4).
    assert weighted_quantile(PAIRS, D("0.25")) == D(10)  # 1 >= 1
    assert weighted_quantile(PAIRS, D("0.26")) == D(20)
    assert weighted_median(PAIRS) == D(20)  # 3 >= 2
    assert weighted_quantile(PAIRS, D("0.75")) == D(20)  # 3 >= 3
    assert weighted_quantile(PAIRS, D("0.76")) == D(30)
    assert weighted_quantile(PAIRS, D(1)) == D(30)


def test_order_does_not_matter() -> None:
    assert weighted_median(list(reversed(PAIRS))) == D(20)


def test_empty_is_none_not_zero() -> None:
    assert weighted_mean([]) is None
    assert weighted_median([]) is None
    assert weighted_total([]) == D(0)


@pytest.mark.parametrize("bad", [[(D(1), D(0))], [(D(1), D(-1))]])
def test_non_positive_weights_rejected(bad: list[tuple[D, D]]) -> None:
    with pytest.raises(ValueError, match="positive"):
        weighted_total(bad)


@pytest.mark.parametrize("q", [D(0), D("1.01"), D(-1)])
def test_q_out_of_range(q: D) -> None:
    with pytest.raises(ValueError, match="q must be"):
        weighted_quantile(PAIRS, q)


def test_decile_cuts_on_equal_weights() -> None:
    pairs = [(D(v), D(1)) for v in range(1, 101)]
    assert weighted_quantile_cuts(pairs, 10) == [D(v) for v in range(10, 100, 10)]
    with pytest.raises(ValueError):
        weighted_quantile_cuts(pairs, 1)
    with pytest.raises(ValueError):
        weighted_quantile_cuts([], 10)


values = st.decimals(min_value=-1000, max_value=1000, places=2, allow_nan=False)
weights = st.integers(min_value=1, max_value=50).map(D)


@given(st.lists(st.tuples(values, weights), min_size=1, max_size=30))
def test_invariants(pairs: list[tuple[D, D]]) -> None:
    doubled = [(v, w * 2) for v, w in pairs]
    assert weighted_total(doubled) == 2 * weighted_total(pairs)
    assert weighted_mean(doubled) == weighted_mean(pairs)
    assert weighted_median(doubled) == weighted_median(pairs)
    lo, hi = min(v for v, _ in pairs), max(v for v, _ in pairs)
    median = weighted_median(pairs)
    assert median is not None and lo <= median <= hi
    assert median in {v for v, _ in pairs}
