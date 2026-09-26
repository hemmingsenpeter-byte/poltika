"""Stats NZ, 2018 Census totals by topic: national highlights (CSV zip).

Reads two of the zip's tables exactly as published (v0.2 Task 3.3): weekly
rent paid by household (households in rented occupied private dwellings)
and tenure of household (households in occupied private dwellings). Every
value is a count copied from the file. The observation is census night,
6 March 2018.
"""

from __future__ import annotations

import csv
import io
import zipfile
from datetime import date
from decimal import Decimal

from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, transformation

HOUSEHOLDS = "households"
CENSUS_NIGHT = (date(2018, 3, 6), date(2018, 3, 7))

RENT = {
    "01": "under_50",
    "02": "from_50_to_74",
    "03": "from_75_to_99",
    "04": "from_100_to_124",
    "05": "from_125_to_149",
    "06": "from_150_to_174",
    "07": "from_175_to_199",
    "08": "from_200_to_249",
    "09": "from_250_to_299",
    "10": "from_300_to_349",
    "11": "from_350_to_399",
    "12": "from_400_to_449",
    "13": "from_450_to_499",
    "14": "from_500_to_549",
    "15": "from_550_to_599",
    "16": "from_600",
    "TotalStated": "total_stated",
}
TENURE = {
    "10": "owned_mortgage_not_further_defined",
    "11": "owned_mortgage_payments_made",
    "12": "owned_mortgage_payments_not_made",
    "20": "not_owned_rental_not_further_defined",
    "21": "not_owned_rent_payments_made",
    "22": "not_owned_rent_payments_not_made",
    "30": "family_trust_mortgage_not_further_defined",
    "31": "family_trust_mortgage_payments_made",
    "32": "family_trust_mortgage_payments_not_made",
    "99": "not_stated",
    "TotalStated": "total_stated",
}

RENT_VARIABLES = {code: f"household.renting.weekly_rent_band.{slug}" for code, slug in RENT.items()}
TENURE_VARIABLES = {code: f"household.tenure_2018.{slug}" for code, slug in TENURE.items()}
VARIABLES: dict[str, str] = {
    v: HOUSEHOLDS for v in (*RENT_VARIABLES.values(), *TENURE_VARIABLES.values())
}

_FILES = (
    ("weekly-rent-paid-by-household-2018-census-csv.csv", RENT_VARIABLES),
    ("tenure-of-household-2018-census-csv.csv", TENURE_VARIABLES),
)


@transformation("stats_nz_census_2018_national", version=1)
def census_2018_national(raw: bytes, manifest: DatasetManifest) -> list[Row]:
    rows: list[Row] = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for name, variables in _FILES:
            # The files are Windows-1252 (their band labels use an en dash).
            reader = csv.reader(io.StringIO(archive.read(name).decode("cp1252")))
            next(reader)
            for code, _label, count in reader:
                if code in variables:
                    rows.append(Row(variables[code], *CENSUS_NIGHT, Decimal(count), HOUSEHOLDS))
    return rows
