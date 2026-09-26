"""Stats NZ, Household income and housing-cost statistics (HES), CSV release.

Reads the release's own zip exactly as published (v0.2 Task 3.3). Codes are
the CSV files' codes; `inc-csv-codes.xlsx` in the same zip defines them.
Every value is copied, except `household.count.total`, which adds Table 10's
two complementary bands (housing costs under 25% of disposable income, and
25% or more) for the "Total number of households" row (DwCode D003A).

Table 5 counts **people** in households of each kind (its total, H001A,
equals the population), not households.
"""

from __future__ import annotations

import csv
import io
import zipfile
from datetime import date
from decimal import Decimal

from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, transformation

PEOPLE = "thousands of people"
HOUSEHOLDS = "thousands of households"
INCOME = "NZD per household per year"
WEEKLY = "NZD per household per week"

# Table 5 HdCode -> variable (people in households of that kind), 2025.
TABLE_5 = {
    "H001A": "household.people.all_households",
    "H003A": "household.people.couple_only",
    "H003B": "household.people.couple_one_dependent_child",
    "H003C": "household.people.couple_two_dependent_children",
    "H003D": "household.people.couple_three_plus_dependent_children",
    "H003F": "household.people.one_parent_dependent_children",
    "H003I": "household.people.one_person_household",
    "H007A": "household.people.region.northland",
    "H007B": "household.people.region.auckland",
    "H007C": "household.people.region.waikato",
    "H007D": "household.people.region.bay_of_plenty",
    "H007E": "household.people.region.gisborne_hawkes_bay",
    "H007F": "household.people.region.taranaki",
    "H007G": "household.people.region.manawatu_whanganui",
    "H007H": "household.people.region.wellington",
    "H007I": "household.people.region.tasman_nelson_marlborough_west_coast",
    "H007J": "household.people.region.canterbury",
    "H007K": "household.people.region.otago",
    "H007L": "household.people.region.southland",
}

VARIABLES: dict[str, str] = {
    **{v: PEOPLE for v in TABLE_5.values()},
    "household.count.total": HOUSEHOLDS,
    "household.gross_income.mean": INCOME,
    "household.gross_income.median": INCOME,
    "household.rent.weekly_mean_paying_households": WEEKLY,
}


def _year_ended_june(year: int) -> tuple[date, date]:
    return date(year - 1, 7, 1), date(year, 7, 1)


def _table(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    text = archive.read(name).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


@transformation("stats_nz_hes_tables", version=1)
def hes_tables(raw: bytes, manifest: DatasetManifest) -> list[Row]:
    rows: list[Row] = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        # Table 5 covers the release year only (year ended June 2025).
        start, end = _year_ended_june(2025)
        for r in _table(archive, "Table 5.csv"):
            if r["QuintCode"] == "Q006" and r["HdCode"] in TABLE_5:
                rows.append(Row(TABLE_5[r["HdCode"]], start, end, Decimal(r["Estimate"]), PEOPLE))

        totals: dict[int, Decimal] = {}
        for r in _table(archive, "Table 10.csv"):
            if r["DwCode"] == "D003A" and r["PerCode"] in ("P001", "P002"):
                year = int(r["Year"])
                totals[year] = totals.get(year, Decimal(0)) + Decimal(r["Estimate"])
        for year, total in sorted(totals.items()):
            rows.append(Row("household.count.total", *_year_ended_june(year), total, HOUSEHOLDS))

        for r in _table(archive, "Table 3.csv"):
            if r["IncCode"] == "1001A" and r["Estimate"].strip():
                variable = {"M0001": "household.gross_income.mean", "M0002": "household.gross_income.median"}
                rows.append(
                    Row(variable[r["MsCode"]], *_year_ended_june(int(r["Year"])), Decimal(r["Estimate"]), INCOME)
                )

        for r in _table(archive, "Table 9.csv"):
            if r["ExpCode"] == "E003" and r["MsCode"] == "M001" and r["Estimate"].strip():
                rows.append(
                    Row(
                        "household.rent.weekly_mean_paying_households",
                        *_year_ended_june(int(r["Year"])),
                        Decimal(r["Estimate"]),
                        WEEKLY,
                    )
                )
    return rows
