"""Read `review_packets/review_queue.md` for the release gates
(`ROADMAP_REALIGNMENT.md` W1.5). A gate row skips, with the open PRs named,
while any merged PR for its release still awaits independent review. The
v0.1.5 gate treats rows only people can satisfy the same way, so a green run
with no skips means the gate is met."""

from __future__ import annotations

import re
from pathlib import Path

QUEUE = Path(__file__).resolve().parents[2] / "review_packets" / "review_queue.md"
_ROW = re.compile(r"^\|\s*(#\d+)\s*\|\s*(v[\d.]+)\s*\|.*\|\s*([^|]+?)\s*\|\s*$")


def open_reviews(release: str, text: str | None = None) -> list[str]:
    """PR numbers for `release` whose status doesn't start with `reviewed`."""
    rows = (QUEUE.read_text() if text is None else text).splitlines()
    return [
        m.group(1)
        for line in rows
        if (m := _ROW.match(line)) and m.group(2) == release and not m.group(3).startswith("reviewed")
    ]
