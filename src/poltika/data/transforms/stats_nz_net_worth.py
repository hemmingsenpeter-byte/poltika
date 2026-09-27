"""Stats NZ, Household net worth statistics (CSV release).

Reads the release's CSV exactly as published (v0.2 Task 3.3). Only Table
1.01's "Currency and deposits" (AsCode W21) median (EstCode E1) and mean
(E3) per household are used. The release's CSV dictionary defines those
codes; the estimates are in thousands of dollars (the same row's total, E5,
is recorded in thousands too). Each value is copied.
"""

from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal

from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, transformation

UNIT = "NZD thousands per household"
_ESTIMATES = {
    "E1": "household.currency_and_deposits.median",
    "E3": "household.currency_and_deposits.mean",
}
VARIABLES: dict[str, str] = {v: UNIT for v in _ESTIMATES.values()}


@transformation("stats_nz_household_net_worth", version=1)
def net_worth(raw: bytes, manifest: DatasetManifest) -> list[Row]:
    rows: list[Row] = []
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        if r["Table"] == "T1.01" and r["AsCode"] == "W21" and r["EstCode"] in _ESTIMATES:
            year = int(r["Year"])  # year ended June
            rows.append(
                Row(
                    _ESTIMATES[r["EstCode"]],
                    date(year - 1, 7, 1),
                    date(year, 7, 1),
                    Decimal(r["Estimate"]),
                    UNIT,
                )
            )
    return rows
