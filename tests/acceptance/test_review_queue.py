"""W1.5: the review-queue reader the release gates use."""

from __future__ import annotations

from tests.acceptance.review_queue import QUEUE, open_reviews

SAMPLE = """
| PR | Release | Scope | Touches | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| #1 | v0.2 | a | b | High | open |
| #2 | v0.2 | a | b | Low | reviewed (reviews/x.md) |
| #3 | v0.1.5 | a | b | Low | open; in audit |
| #4 | v0.2 | a | b | Low | open |
"""


def test_reader_picks_open_rows_for_one_release() -> None:
    assert open_reviews("v0.2", SAMPLE) == ["#1", "#4"]
    assert open_reviews("v0.1.5", SAMPLE) == ["#3"]
    assert open_reviews("v0.3", SAMPLE) == []


def test_real_queue_parses() -> None:
    assert QUEUE.is_file()
    rows = open_reviews("v0.2") + open_reviews("v0.1.5") + open_reviews("v0.1.6")
    assert all(r.startswith("#") for r in rows)
