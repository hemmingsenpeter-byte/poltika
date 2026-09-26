"""Stats NZ, Births and deaths: year ended March (the release page).

The release publishes its headline counts in its "Key facts" text rather
than a download, so the snapshot is the release page as published (v0.2
Task 3.3). The transformation reads the key-facts sentence comparing the
release year with the year before, for example "In the year ended March
2026 compared with the year ended March 2025: 57,027 live births were
registered, down from 58,539", and returns both years' counts. These are
**registrations**, not births by date of birth.
"""

from __future__ import annotations

import html
import re
from datetime import date
from decimal import Decimal

from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, transformation

UNIT = "live births registered"
VARIABLES: dict[str, str] = {"population.live_births_registered": UNIT}

_YEARS = re.compile(r"In the year ended March (\d{4}) compared with the year ended March (\d{4})")
_BIRTHS = re.compile(r"([\d,]+) live births (?:were )?registered, (?:up|down) from ([\d,]+)")


class BirthsPageError(ValueError):
    pass


def _year_ended_march(year: int) -> tuple[date, date]:
    return date(year - 1, 4, 1), date(year, 4, 1)


@transformation("stats_nz_births_release", version=1)
def births_release(raw: bytes, manifest: DatasetManifest) -> list[Row]:
    text = html.unescape(raw.decode("utf-8"))
    years = _YEARS.search(text)
    if years is None:
        raise BirthsPageError(f"{manifest.manifest_name}: no key-facts year comparison found")
    births = _BIRTHS.search(text, years.end())
    if births is None:
        raise BirthsPageError(f"{manifest.manifest_name}: no live-births key fact after the year comparison")
    current, previous = int(years.group(1)), int(years.group(2))
    return [
        Row("population.live_births_registered", *_year_ended_march(previous), _count(births.group(2)), UNIT),
        Row("population.live_births_registered", *_year_ended_march(current), _count(births.group(1)), UNIT),
    ]


def _count(text: str) -> Decimal:
    return Decimal(text.replace(",", ""))
