"""The committed snapshots (v0.2 Tasks 3.2-3.3) read end to end.

Every manifest's transformation is registered at the manifest's version and
produces every variable the manifest maps, and `DataContext` accepts every
row (units, periods, no overlaps). The spot values are figures printed in
the publications themselves, so a transformation that misreads a file
fails here.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from poltika.data.context import DataContext
from poltika.data.registry import DatasetRegistry
from poltika.data.transform import TRANSFORMATIONS

REPO_DATA = Path(__file__).resolve().parents[3] / "data"
BIRTHS_2025 = "Year ended March 2025 (release page dated 15 May 2025)"


@pytest.mark.parametrize("snapshot", DatasetRegistry(REPO_DATA).snapshots(), ids=lambda s: s.manifest.manifest_name)
def test_each_snapshot_produces_every_mapped_variable(snapshot) -> None:  # type: ignore[no-untyped-def]
    m = snapshot.manifest
    t = TRANSFORMATIONS[m.transformation_id]
    assert t.version == m.transformation_version
    produced = {row.variable_id for row in t.fn(snapshot.path.read_bytes(), m)}
    assert produced == set(m.canonical_variable_mapping)


@pytest.mark.parametrize(
    ("variable", "on", "vintage", "value"),
    [
        # HES year ended June 2025: Table 10 bands P001 1134.2 + P002 891.2.
        ("household.count.total", date(2025, 1, 1), None, "2025.4"),
        ("household.people.all_households", date(2025, 1, 1), None, "5205.2"),
        ("household.people.couple_only", date(2025, 1, 1), None, "1020.1"),
        ("household.gross_income.median", date(2025, 1, 1), None, "109556"),
        ("household.rent.weekly_mean_paying_households", date(2018, 1, 1), None, "340.5"),
        ("household.renting.weekly_rent_band.from_600", date(2018, 3, 6), None, "53151"),
        ("household.tenure_2018.not_owned_rent_payments_made", date(2018, 3, 6), None, "527853"),
        ("household.currency_and_deposits.median", date(2024, 1, 1), None, "16"),
        ("population.live_births_registered", date(2026, 1, 1), None, "57027"),
        ("population.live_births_registered", date(2025, 1, 1), None, "58539"),
        ("population.live_births_registered", date(2024, 1, 1), BIRTHS_2025, "56277"),
    ],
)
def test_published_figures_read_through_the_context(
    variable: str, on: date, vintage: str | None, value: str
) -> None:
    assert DataContext(REPO_DATA).get(variable, on, vintage).value == Decimal(value)
