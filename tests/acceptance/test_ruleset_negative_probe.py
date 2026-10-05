"""Deliberately invalid CI probe. This branch must never merge."""

import os


def test_ruleset_negative_probe() -> None:
    """The unused import above deliberately fails Ruff in the required test job."""
